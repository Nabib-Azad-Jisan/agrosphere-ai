"""Measured VWC forecasting with horizon-purged chronological evaluation."""

import argparse
import hashlib
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

FEATURES = [
    "moisture_vwc",
    "lag_1h",
    "lag_6h",
    "lag_24h",
    "slope_6h",
    "forecast_rain_mm",
    "forecast_et0_mm",
    "temperature_c",
    "humidity_pct",
    "recent_irrigation_mm",
    "kc",
    "rooting_depth_m",
]
REQUIRED = [
    "timestamp",
    "moisture_vwc",
    "provenance",
    "forecast_available_at",
    "forecast_rain_mm",
    "forecast_et0_mm",
    "temperature_c",
    "humidity_pct",
    "recent_irrigation_mm",
    "kc",
    "rooting_depth_m",
    "field_capacity_vwc",
]


def features(frame):
    missing = set(REQUIRED) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    frame = frame.copy()
    if not frame.provenance.isin(["historical_observed", "live_sensor"]).all():
        raise ValueError("Only authentic measured observations can enter model evaluation")
    if "device_id" in frame and frame.device_id.nunique() != 1:
        raise ValueError("Train per device; mixed sensor series must be grouped explicitly")
    frame["timestamp"] = pd.to_datetime(frame.timestamp, utc=True)
    frame["forecast_available_at"] = pd.to_datetime(frame.forecast_available_at, utc=True)
    frame = frame.sort_values("timestamp").set_index("timestamp")
    if frame.index.duplicated().any():
        raise ValueError("Duplicate observation timestamps")
    if (frame.forecast_available_at > frame.index).any():
        raise ValueError("Future weather information leakage")
    if not frame.moisture_vwc.between(0, 1).all() or not (frame.rooting_depth_m > 0).all():
        raise ValueError("Invalid VWC or rooting depth")
    if not np.isfinite(frame[FEATURES[:1] + REQUIRED[4:]].select_dtypes("number")).all().all():
        raise ValueError("Non-finite feature values")
    for hours in [1, 6, 24]:
        # Exact timestamp alignment; irregular/missing samples are not silently treated as hourly.
        frame[f"lag_{hours}h"] = frame.moisture_vwc.reindex(frame.index - pd.Timedelta(hours=hours)).to_numpy()
    frame["slope_6h"] = (frame.moisture_vwc - frame.lag_6h) / 6
    frame["target"] = frame.moisture_vwc.reindex(frame.index + pd.Timedelta(hours=24)).to_numpy()
    frame["target_timestamp"] = frame.index + pd.Timedelta(hours=24)
    return frame.dropna(subset=FEATURES + ["target"])


def split(frame):
    if len(frame) < 240:
        raise ValueError("Insufficient aligned measured data: need at least 240 rows after feature alignment")
    a, b = int(len(frame) * 0.6), int(len(frame) * 0.8)
    train = frame.iloc[:a]
    validation = frame.iloc[a:b]
    test = frame.iloc[b:]
    train = train[train.target_timestamp < validation.index.min()]
    validation = validation[validation.target_timestamp < test.index.min()]
    if min(len(train), len(validation), len(test)) < 20:
        raise ValueError("Insufficient rows after purging 24-hour target overlap")
    return train, validation, test


def baseline_balance(frame):
    return np.clip(
        frame.moisture_vwc + (frame.forecast_rain_mm - frame.kc * frame.forecast_et0_mm) / (frame.rooting_depth_m * 1000),
        0,
        frame.field_capacity_vwc,
    )


def metrics(target, predicted):
    return {"mae": float(mean_absolute_error(target, predicted)), "rmse": float(root_mean_squared_error(target, predicted))}


def train(path, attribution, output="ml/artifacts"):
    path = Path(path)
    prepared = features(pd.read_csv(path))
    training, validation, test = split(prepared)
    candidates = []
    for depth in [5, 10]:
        model = RandomForestRegressor(n_estimators=150, max_depth=depth, min_samples_leaf=5, random_state=42, n_jobs=-1)
        model.fit(training[FEATURES], training.target)
        candidates.append((mean_absolute_error(validation.target, model.predict(validation[FEATURES])), model))
    _, model = min(candidates, key=lambda x: x[0])
    result = {
        "status": "experimental_measured_evaluation_not_field_approved",
        "unit": "vwc_m3_m3",
        "horizon_hours": 24,
        "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "attribution": attribution,
        "split": {
            name: {"rows": len(part), "start": part.index.min().isoformat(), "end": part.index.max().isoformat()}
            for name, part in [("train", training), ("validation", validation), ("test", test)]
        },
        "results": {
            "persistence": metrics(test.target, test.moisture_vwc),
            "water_balance": metrics(test.target, baseline_balance(test)),
            "random_forest": metrics(test.target, model.predict(test[FEATURES])),
        },
        "feature_importance": dict(zip(FEATURES, map(float, model.feature_importances_))),
        "limitations": [
            "Dataset provenance is supplied by importer, not independently verified",
            "No field deployment approval",
            "No calibrated prediction interval",
            "One sensor series only",
        ],
    }
    result["model_version"] = f"random-forest-v1-{result['dataset_sha256'][:12]}"
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    artifact = {"model": model, "features": FEATURES, "schema_version": "1.0", "field_approved": False, "metadata": result}
    joblib.dump(artifact, out / "model.joblib")
    version_dir = out / result["model_version"]
    version_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, version_dir / "model.joblib")
    (version_dir / "evaluation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (out / "evaluation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(test.index, test.target, label="Measured +24h target")
    ax.plot(test.index, model.predict(test[FEATURES]), label="Random Forest estimate")
    ax.set_ylabel("VWC (m³/m³)")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out / "evaluation.png", dpi=150)
    plt.close(fig)
    return result


def load_artifact(path):
    # Only load trusted locally produced joblib files; pickle can execute arbitrary code.
    artifact = joblib.load(path)
    if artifact.get("schema_version") != "1.0" or artifact.get("features") != FEATURES:
        raise ValueError("Incompatible model artifact")
    return artifact


def predict(artifact, values):
    if set(values) != set(FEATURES) or not all(np.isfinite(v) for v in values.values()):
        raise ValueError("Inference requires all finite, prediction-time features")
    frame = pd.DataFrame([values], columns=FEATURES)
    return {
        "predicted_vwc": float(np.clip(artifact["model"].predict(frame)[0], 0, 1)),
        "validation_status": "experimental_not_field_approved",
        "field_approved": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset")
    parser.add_argument("--attribution", required=True)
    parser.add_argument("--output", default="ml/artifacts")
    args = parser.parse_args()
    print(json.dumps(train(args.dataset, args.attribution, args.output), indent=2))
