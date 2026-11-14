from .database import utcnow
from .models import ForecastRun
from .rootsense import status
from .weather import weather, next_24h

ADVICE = {
    "inspect": {
        "en": "Inspect the root-zone soil and verify sensor readings before deciding whether irrigation is needed.",
        "bn": "সেচের সিদ্ধান্ত নেওয়ার আগে শিকড়ের এলাকার মাটি পরীক্ষা করুন এবং সেন্সরের পাঠ যাচাই করুন।",
    },
    "monitor": {
        "en": "Continue monitoring. Check soil conditions before changing irrigation.",
        "bn": "পর্যবেক্ষণ চালিয়ে যান। সেচ পরিবর্তনের আগে মাটির অবস্থা পরীক্ষা করুন।",
    },
    "unavailable": {
        "en": "Reliable moisture data is unavailable. Inspect the soil and check the device.",
        "bn": "নির্ভরযোগ্য আর্দ্রতার তথ্য নেই। মাটি পরীক্ষা করুন এবং যন্ত্রটি যাচাই করুন।",
    },
    "wet": {
        "en": "Inspect drainage and root-zone conditions before adding water.",
        "bn": "পানি দেওয়ার আগে নিষ্কাশন ও শিকড়ের এলাকার মাটির অবস্থা পরীক্ষা করুন।",
    },
}


def water_balance(vwc, rain_mm, et0_mm, kc, depth_m, field_capacity):
    # Simplified bucket; no runoff, capillary rise, or deep-soil transport model.
    return max(0.0, min(field_capacity, vwc + (rain_mm - kc * et0_mm) / (depth_m * 1000)))


def forecast(db, plot):
    monitoring = status(db, plot)
    reading = monitoring["reading"]
    result = {
        "plot_id": plot.id,
        "issued_at": utcnow().isoformat(),
        "horizon_hours": 24,
        "method": "persistence_baseline",
        "model_version": "baseline-v1",
        "model_mode": "Baseline",
        "validation_status": "not_field_validated",
        "ml_status": "not_validated",
        "risk_level": "unknown",
        "persistence_vwc": None,
        "water_balance_vwc": None,
        "predicted_vwc": None,
        "data_source": reading["provenance"] if reading else "unavailable",
        "reasons": [],
        "limitations": ["No field performance or water savings demonstrated", "Prediction intervals have not been calibrated"],
        "advice": ADVICE["unavailable"],
        "weather": None,
    }
    if monitoring["status"] in {"unavailable", "stale", "uncalibrated", "review_required"}:
        result["reasons"].append("Missing, stale, or unverified moisture measurement")
        return result
    vwc = reading["moisture_vwc"]
    result["persistence_vwc"] = vwc
    result["predicted_vwc"] = vwc
    outlook = weather(db, plot)
    totals = next_24h(outlook)
    result["weather"] = {k: v for k, v in outlook.items() if k != "data"}
    if totals:
        result["weather_totals"] = totals
        estimate = water_balance(vwc, totals["rain_mm"], totals["et0_mm"], plot.kc, plot.rooting_depth_m, plot.field_capacity_vwc)
        result.update(water_balance_vwc=round(estimate, 4), predicted_vwc=round(estimate, 4), method="water_balance_baseline")
        result["reasons"].append(f"Next 24h: {totals['rain_mm']} mm forecast rain; {totals['et0_mm']} mm reference ET0")
    else:
        result["reasons"].append("Weather unavailable or stale; persistence baseline only")
    trend = monitoring["trend_per_hour"]
    if trend is not None:
        result["reasons"].append("Observed moisture is declining" if trend < 0 else "Observed moisture is stable or increasing")
    predicted = result["predicted_vwc"]
    is_demo = reading["provenance"] == "synthetic"
    if is_demo or plot.thresholds_verified:
        result["risk_level"] = "high" if predicted < plot.low_vwc else "excessive" if predicted > plot.high_vwc else "low"
    else:
        result["reasons"].append("Thresholds lack documented field calibration; risk remains unknown")
    if is_demo:
        result["reasons"].append("Simulation: illustrative moisture and thresholds, not field evidence")
    result["advice"] = ADVICE["inspect" if result["risk_level"] == "high" else "wet" if result["risk_level"] == "excessive" else "monitor"]
    return result


def save_forecast(db, plot):
    result = forecast(db, plot)
    latest = status(db, plot)["reading"]
    run = ForecastRun(plot_id=plot.id, reading_id=latest["id"] if latest else None, payload=result)
    db.add(run)
    db.commit()
    return result
