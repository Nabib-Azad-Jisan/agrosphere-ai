from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Float, DateTime, ForeignKey, JSON, Boolean, UniqueConstraint, CheckConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base, utcnow


def uid():
    return str(uuid4())


class Farm(Base):
    __tablename__ = "farms"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(160))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Plot(Base):
    __tablename__ = "plots"
    __table_args__ = (CheckConstraint("low_vwc < high_vwc", name="ordered_thresholds"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    farm_id: Mapped[str] = mapped_column(ForeignKey("farms.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    crop: Mapped[str] = mapped_column(String(80), default="Tomato")
    crop_stage: Mapped[str] = mapped_column(String(80), default="Vegetative")
    soil_type: Mapped[str] = mapped_column(String(80), default="Loam")
    planting_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    rooting_depth_m: Mapped[float] = mapped_column(Float, default=0.3)
    kc: Mapped[float] = mapped_column(Float, default=0.85)
    low_vwc: Mapped[float] = mapped_column(Float, default=0.20)
    high_vwc: Mapped[float] = mapped_column(Float, default=0.40)
    field_capacity_vwc: Mapped[float] = mapped_column(Float, default=0.35)
    thresholds_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    threshold_notes: Mapped[str] = mapped_column(String(500), default="Illustrative simulation settings; not field calibrated")


class Device(Base):
    __tablename__ = "devices"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    source: Mapped[str] = mapped_column(String(32))
    token_hash: Mapped[str] = mapped_column(String(64))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Calibration(Base):
    __tablename__ = "device_calibrations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    raw_dry: Mapped[float] = mapped_column(Float)
    raw_wet: Mapped[float] = mapped_column(Float)
    vwc_dry: Mapped[float] = mapped_column(Float)
    vwc_wet: Mapped[float] = mapped_column(Float)
    soil_type: Mapped[str] = mapped_column(String(80))
    notes: Mapped[str] = mapped_column(String(1000))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Reading(Base):
    __tablename__ = "sensor_readings"
    __table_args__ = (UniqueConstraint("device_id", "timestamp", name="unique_device_timestamp"),)
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    source: Mapped[str] = mapped_column(String(32), index=True)
    provenance: Mapped[str] = mapped_column(String(32))
    schema_version: Mapped[str] = mapped_column(String(8), default="1.0")
    measurements: Mapped[dict] = mapped_column(JSON)
    moisture_vwc: Mapped[float | None] = mapped_column(Float, nullable=True)
    moisture_unit: Mapped[str] = mapped_column(String(24), default="vwc_m3_m3")
    calibration_id: Mapped[str | None] = mapped_column(ForeignKey("device_calibrations.id"), nullable=True)
    battery_percent: Mapped[float | None] = mapped_column(Float, nullable=True)
    quality_flags: Mapped[list] = mapped_column(JSON, default=list)


class Irrigation(Base):
    __tablename__ = "irrigation_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    amount_mm: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(32), default="farmer_reported")
    notes: Mapped[str] = mapped_column(String(500), default="")


class WeatherForecast(Base):
    __tablename__ = "weather_forecasts"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    provider: Mapped[str] = mapped_column(String(32), default="open_meteo")
    payload: Mapped[dict] = mapped_column(JSON)


class ForecastRun(Base):
    __tablename__ = "forecast_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    reading_id: Mapped[str | None] = mapped_column(ForeignKey("sensor_readings.id"), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON)


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    kind: Mapped[str] = mapped_column(String(64))
    message: Mapped[str] = mapped_column(String(500))
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SimulationSession(Base):
    __tablename__ = "simulation_sessions"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), unique=True)
    scenario: Mapped[str] = mapped_column(String(32), default="drying")
    running: Mapped[bool] = mapped_column(Boolean, default=False)
    speed: Mapped[int] = mapped_column(Integer, default=1)
    step: Mapped[int] = mapped_column(Integer, default=0)
    last_tick: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(500), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    action: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[str] = mapped_column(String(64))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=uid)
    plot_id: Mapped[str] = mapped_column(ForeignKey("plots.id"), index=True)
    condition: Mapped[str] = mapped_column(String(32))
    notes: Mapped[str] = mapped_column(String(1000), default="")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
