import numpy as np
import pandas as pd
import pytest
from ml.pipeline import features, split, baseline_balance, FEATURES, predict
from backend.app.aquamind import water_balance


def dataset(n=600):
    time = pd.date_range("2025-01-01", periods=n, freq="h", tz="UTC")
    return pd.DataFrame(
        {
            "timestamp": time,
            "moisture_vwc": 0.3 + 0.02 * np.sin(np.arange(n) / 10),
            "provenance": "historical_observed",
            "forecast_available_at": time - pd.Timedelta(hours=1),
            "forecast_rain_mm": 1.0,
            "forecast_et0_mm": 4.0,
            "temperature_c": 28.0,
            "humidity_pct": 70.0,
            "recent_irrigation_mm": 0.0,
            "kc": 0.85,
            "rooting_depth_m": 0.3,
            "field_capacity_vwc": 0.35,
        }
    )


def test_exact_alignment_and_purged_split():
    data = dataset()
    result = features(data)
    assert result.iloc[0].lag_24h == data.iloc[0].moisture_vwc
    train, val, test = split(result)
    assert train.target_timestamp.max() < val.index.min()
    assert val.target_timestamp.max() < test.index.min()
    assert set(FEATURES).issubset(result.columns)


def test_synthetic_and_future_weather_rejected():
    data = dataset()
    data.loc[0, "provenance"] = "synthetic"
    with pytest.raises(ValueError, match="authentic"):
        features(data)
    data = dataset()
    data["forecast_available_at"] = data.timestamp + pd.Timedelta(hours=1)
    with pytest.raises(ValueError, match="leakage"):
        features(data)


def test_missing_hours_do_not_shift_target():
    data = dataset().drop(index=100)
    result = features(data)
    assert pd.Timestamp("2025-01-04T04:00:00Z") not in result.index  # its +24h target is missing


def test_insufficient_data_and_input_schema():
    with pytest.raises(ValueError, match="Insufficient"):
        split(features(dataset(80)))
    with pytest.raises(ValueError, match="finite"):
        predict({}, {"bad": 1})


def test_water_balance_consistency():
    row = dataset(1)
    expected = water_balance(0.3, 1, 4, 0.85, 0.3, 0.35)
    assert baseline_balance(row).iloc[0] == pytest.approx(expected)
    assert water_balance(0.3, 1000, 0, 1, 0.3, 0.35) == 0.35


def test_training_artifact_roundtrip_is_always_experimental(tmp_path):
    # Generated fixtures verify software, never field performance. Artifacts stay in pytest tmp_path.
    from ml.pipeline import train, load_artifact

    source = tmp_path / "software_test_fixture.csv"
    dataset().to_csv(source, index=False)
    report = train(source, "Generated software test fixture; NOT actual field evidence", tmp_path / "artifacts")
    assert set(report["results"]) == {"persistence", "water_balance", "random_forest"}
    artifact = load_artifact(tmp_path / "artifacts" / "model.joblib")
    values = features(dataset()).iloc[-1][FEATURES].to_dict()
    result = predict(artifact, values)
    assert 0 <= result["predicted_vwc"] <= 1
    assert result["field_approved"] is False
