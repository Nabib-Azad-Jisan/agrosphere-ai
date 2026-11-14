from abc import ABC, abstractmethod
from datetime import timedelta
import math
from .database import utcnow
from .schemas import ReadingIn


class SourceAdapter(ABC):
    @abstractmethod
    def read(self) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def source_info(self) -> dict:
        raise NotImplementedError


class SimulatorAdapter(SourceAdapter):
    def __init__(self, device_id, plot_id, scenario="drying", step=0, initial=0.32):
        self.device_id, self.plot_id, self.scenario, self.step, self.initial = device_id, plot_id, scenario, step, initial

    def source_info(self):
        return {"source": "simulator", "provenance": "synthetic", "field_validated": False}

    def read(self):
        if self.scenario == "disconnected":
            return None
        value = {
            "drying": self.initial - 0.006,
            "normal": 0.30 + 0.015 * math.sin(self.step / 4),
            "rainfall": min(0.60, self.initial + 0.025),
            "irrigation": min(0.60, self.initial + 0.035),
            "wet": 0.46 + 0.008 * math.sin(self.step),
            "stale": self.initial,
            "invalid": 1.5,
        }[self.scenario]
        timestamp = utcnow() - timedelta(hours=2) if self.scenario == "stale" else utcnow()
        return {
            "schema_version": "1.0",
            "device_id": self.device_id,
            "plot_id": self.plot_id,
            "timestamp": timestamp.isoformat(),
            "source": "simulator",
            "measurements": {
                "soil_moisture_vwc": round(max(0.05, value), 4),
                "soil_temperature_c": 27 + math.sin(self.step / 6),
                "air_temperature_c": 30 + math.sin(self.step / 5),
                "air_humidity_percent": 72 + 5 * math.sin(self.step / 7),
            },
            "battery_percent": 100,
            "calibration_id": None,
        }


class HistoricalAdapter(SourceAdapter):
    def __init__(self, row):
        self.row = row

    def source_info(self):
        return {"source": "historical_import", "provenance": "historical_observed"}

    def read(self):
        return ReadingIn.model_validate({**self.row, "source": "historical_import"}).model_dump(mode="json")


class HardwareAdapter(SourceAdapter):
    def __init__(self, payload):
        self.payload = payload

    def source_info(self):
        return {"source": self.payload["source"], "provenance": "live_sensor"}

    def read(self):
        reading = ReadingIn.model_validate(self.payload)
        if reading.source not in {"esp32", "external_sensor_api"}:
            raise ValueError("Expected hardware source")
        return reading.model_dump(mode="json")
