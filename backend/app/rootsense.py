from sqlalchemy import select
from .models import Reading
from .database import utcnow, aware
from .config import settings
from .ingestion import MODES, serialize


def status(db, plot):
    latest = db.scalar(
        select(Reading)
        .where(Reading.plot_id == plot.id, Reading.source.in_(MODES[settings.data_source_mode]))
        .order_by(Reading.timestamp.desc())
        .limit(1)
    )
    result = {
        "plot": serialize(plot),
        "reading": serialize(latest) if latest else None,
        "data_source_mode": settings.data_source_mode,
        "status": "unavailable",
        "age_minutes": None,
        "trend_per_hour": None,
        "thresholds_verified": plot.thresholds_verified,
    }
    if latest is None:
        return result
    age = max(0, (utcnow() - aware(latest.timestamp)).total_seconds() / 60)
    result["age_minutes"] = round(age, 1)
    if age > settings.stale_minutes:
        result["status"] = "stale"
    elif latest.moisture_vwc is None:
        result["status"] = "uncalibrated"
    elif latest.source != "simulator" and any(
        f in latest.quality_flags for f in ["calibration_missing", "calibration_unverified", "calibration_extrapolation"]
    ):
        result["status"] = "review_required"
    elif latest.source != "simulator" and not plot.thresholds_verified:
        result["status"] = "monitoring"
    elif latest.moisture_vwc < plot.low_vwc:
        result["status"] = "low"
    elif latest.moisture_vwc > plot.high_vwc:
        result["status"] = "excessive"
    else:
        result["status"] = "adequate"
    previous = db.scalar(
        select(Reading)
        .where(
            Reading.plot_id == plot.id,
            Reading.source == latest.source,
            Reading.device_id == latest.device_id,
            Reading.timestamp < latest.timestamp,
            Reading.moisture_vwc.is_not(None),
        )
        .order_by(Reading.timestamp.desc())
        .limit(1)
    )
    if previous and latest.moisture_vwc is not None:
        hours = (aware(latest.timestamp) - aware(previous.timestamp)).total_seconds() / 3600
        if hours > 0:
            result["trend_per_hour"] = round((latest.moisture_vwc - previous.moisture_vwc) / hours, 5)
    return result
