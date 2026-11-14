import secrets
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from .config import settings
from .database import aware, utcnow
from .models import Device, Calibration, Reading, AuditLog
from .schemas import ReadingIn
from .security import token_hash

MODES = {
    "simulation": {"simulator"},
    "historical": {"historical_import"},
    "hardware": {"esp32", "external_sensor_api"},
    "hybrid": {"simulator", "historical_import", "esp32", "external_sensor_api"},
}
PROVENANCE = {
    "simulator": "synthetic",
    "historical_import": "historical_observed",
    "esp32": "live_sensor",
    "external_sensor_api": "live_sensor",
}


def ingest(db, payload: ReadingIn, token: str):
    device = db.get(Device, payload.device_id)
    if not device or not device.active or not secrets.compare_digest(device.token_hash, token_hash(token)):
        raise HTTPException(401, "Invalid device credentials")
    if device.plot_id != payload.plot_id or device.source != payload.source:
        raise HTTPException(403, "Device plot/source mismatch")
    if payload.source not in MODES[settings.data_source_mode]:
        raise HTTPException(409, "Source is disabled by DATA_SOURCE_MODE")
    timestamp = payload.timestamp.astimezone(utcnow().tzinfo)
    duplicate = db.scalar(select(Reading).where(Reading.device_id == device.id, Reading.timestamp == timestamp))
    if duplicate:
        raise HTTPException(409, "Duplicate device timestamp")
    values = payload.measurements.model_dump()
    vwc = values["soil_moisture_vwc"]
    flags = ["synthetic"] if payload.source == "simulator" else []
    if payload.calibration_id:
        cal = db.get(Calibration, payload.calibration_id)
        if not cal or cal.device_id != device.id:
            raise HTTPException(422, "Calibration does not belong to this device")
        raw = values["soil_moisture_raw"]
        if raw is not None:
            if not min(cal.raw_dry, cal.raw_wet) <= raw <= max(cal.raw_dry, cal.raw_wet):
                flags.append("calibration_extrapolation")
            derived = cal.vwc_dry + (raw - cal.raw_dry) / (cal.raw_wet - cal.raw_dry) * (cal.vwc_wet - cal.vwc_dry)
            if not 0 <= derived <= 1:
                raise HTTPException(422, "Calibration maps outside valid VWC range")
            if vwc is not None and abs(vwc - derived) > 0.01:
                raise HTTPException(422, "Reported VWC conflicts with calibration")
            vwc = derived
        if not cal.verified:
            flags.append("calibration_unverified")
    elif payload.source != "simulator":
        flags.append("calibration_missing")
    if vwc is None:
        flags.append("moisture_unavailable")
    if (utcnow() - timestamp).total_seconds() > settings.stale_minutes * 60:
        flags.append("stale_at_ingestion")
    if payload.battery_percent is not None and payload.battery_percent < 20:
        flags.append("low_battery")
    reading = Reading(
        device_id=device.id,
        plot_id=payload.plot_id,
        timestamp=timestamp,
        source=payload.source,
        provenance=PROVENANCE[payload.source],
        measurements=values,
        moisture_vwc=vwc,
        calibration_id=payload.calibration_id,
        battery_percent=payload.battery_percent,
        quality_flags=flags,
    )
    db.add(reading)
    device.last_seen = utcnow()
    db.add(AuditLog(action="reading.accepted", entity_id=device.id, details={"source": payload.source}))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Duplicate reading or invalid association") from None
    return reading


def serialize(row):
    result = {column.name: getattr(row, column.name) for column in row.__table__.columns if column.name != "token_hash"}
    for key, value in result.items():
        if hasattr(value, "isoformat"):
            result[key] = aware(value).isoformat()
    return result
