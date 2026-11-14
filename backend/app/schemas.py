from datetime import timedelta, date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime, model_validator
from .database import utcnow

Source = Literal["simulator", "historical_import", "esp32", "external_sensor_api"]
Scenario = Literal["drying", "normal", "rainfall", "irrigation", "wet", "disconnected", "stale", "invalid"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Measurements(StrictModel):
    soil_moisture_raw: float | None = Field(default=None, ge=0, le=65535)
    soil_moisture_vwc: float | None = Field(default=None, ge=0, le=1)
    soil_temperature_c: float | None = Field(default=None, ge=-40, le=85)
    air_temperature_c: float | None = Field(default=None, ge=-50, le=65)
    air_humidity_percent: float | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def not_empty(self):
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("At least one measurement is required")
        return self


class ReadingIn(StrictModel):
    schema_version: Literal["1.0"] = "1.0"
    device_id: str = Field(min_length=1, max_length=64)
    plot_id: str = Field(min_length=1, max_length=64)
    timestamp: AwareDatetime
    source: Source
    measurements: Measurements
    battery_percent: float | None = Field(default=None, ge=0, le=100)
    calibration_id: str | None = None

    @model_validator(mode="after")
    def timestamp_not_future(self):
        if self.timestamp > utcnow() + timedelta(minutes=5):
            raise ValueError("Timestamp is more than five minutes in the future")
        return self


class FarmIn(StrictModel):
    name: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=160)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class PlotIn(StrictModel):
    farm_id: str
    name: str = Field(min_length=1, max_length=120)
    crop: str = Field(default="Tomato", min_length=1, max_length=80)
    crop_stage: str = Field(default="Vegetative", max_length=80)
    soil_type: str = Field(default="Loam", max_length=80)
    planting_date: date | None = None
    rooting_depth_m: float = Field(default=0.3, ge=0.05, le=3)
    kc: float = Field(default=0.85, ge=0.1, le=2)
    low_vwc: float = Field(default=0.20, ge=0, le=1)
    high_vwc: float = Field(default=0.40, ge=0, le=1)
    field_capacity_vwc: float = Field(default=0.35, ge=0, le=1)
    thresholds_verified: bool = False
    threshold_notes: str = Field(default="Illustrative settings; not field calibrated", max_length=500)

    @model_validator(mode="after")
    def ordered(self):
        if self.low_vwc >= self.high_vwc:
            raise ValueError("low_vwc must be below high_vwc")
        if self.thresholds_verified and len(self.threshold_notes.strip()) < 15:
            raise ValueError("Verified thresholds require calibration/context notes")
        return self


class DeviceIn(StrictModel):
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    plot_id: str
    name: str = Field(min_length=1, max_length=120)
    source: Source


class CalibrationIn(StrictModel):
    raw_dry: float = Field(ge=0, le=65535)
    raw_wet: float = Field(ge=0, le=65535)
    vwc_dry: float = Field(ge=0, le=1)
    vwc_wet: float = Field(ge=0, le=1)
    soil_type: str = Field(min_length=1, max_length=80)
    notes: str = Field(min_length=15, max_length=1000)
    verified: bool = False

    @model_validator(mode="after")
    def valid_points(self):
        if self.raw_dry == self.raw_wet or self.vwc_dry >= self.vwc_wet:
            raise ValueError("Calibration requires distinct raw points and increasing VWC")
        return self


class SimulationIn(StrictModel):
    plot_id: str
    scenario: Scenario = "drying"
    speed: int = Field(default=1, ge=1, le=60)


class IrrigationIn(StrictModel):
    timestamp: AwareDatetime
    amount_mm: float = Field(gt=0, le=500)
    notes: str = Field(default="", max_length=500)


class FeedbackIn(StrictModel):
    plot_id: str
    condition: Literal["dry", "wet", "adequate", "sensor_issue"]
    notes: str = Field(default="", max_length=1000)


class ReadingOut(BaseModel):
    id: str
    schema_version: Literal["1.0"]
    device_id: str
    plot_id: str
    timestamp: AwareDatetime
    received_at: AwareDatetime
    source: Source
    provenance: Literal["synthetic", "historical_observed", "live_sensor"]
    measurements: Measurements
    moisture_vwc: float | None = Field(ge=0, le=1)
    moisture_unit: Literal["vwc_m3_m3"]
    calibration_id: str | None
    battery_percent: float | None = Field(ge=0, le=100)
    quality_flags: list[str]


class PlotOut(PlotIn):
    id: str


class RootSenseOut(BaseModel):
    plot: PlotOut
    reading: ReadingOut | None
    data_source_mode: Literal["simulation", "historical", "hardware", "hybrid"]
    status: Literal["unavailable", "stale", "uncalibrated", "review_required", "monitoring", "low", "excessive", "adequate"]
    age_minutes: float | None
    trend_per_hour: float | None
    thresholds_verified: bool


class AdvisoryText(BaseModel):
    en: str
    bn: str


class ForecastOut(BaseModel):
    model_config = ConfigDict(extra="allow")
    plot_id: str
    issued_at: AwareDatetime
    horizon_hours: Literal[24]
    method: Literal["persistence_baseline", "water_balance_baseline"]
    model_version: str
    model_mode: Literal["Baseline"]
    validation_status: Literal["not_field_validated"]
    ml_status: Literal["not_validated"]
    risk_level: Literal["unknown", "high", "excessive", "low"]
    persistence_vwc: float | None = Field(ge=0, le=1)
    water_balance_vwc: float | None = Field(ge=0, le=1)
    predicted_vwc: float | None = Field(ge=0, le=1)
    data_source: str
    advice: AdvisoryText
    reasons: list[str]
    limitations: list[str]
