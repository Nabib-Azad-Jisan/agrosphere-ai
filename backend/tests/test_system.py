from datetime import datetime, timedelta, timezone
import pytest
from backend.app.database import utcnow
from backend.app.config import settings
from backend.app.weather import client as weather_client


def payload():
    return {
        "schema_version": "1.0",
        "device_id": "device",
        "plot_id": "plot",
        "timestamp": utcnow().isoformat(),
        "source": "simulator",
        "measurements": {"soil_moisture_vwc": 0.25, "soil_temperature_c": 28},
        "battery_percent": 90,
        "calibration_id": None,
    }


def post(client, data=None, token="test-secret"):
    return client.post("/api/v1/readings", json=data or payload(), headers={"X-Device-Token": token})


def test_ingestion_persistence_history_export(client):
    assert post(client).status_code == 201
    status = client.get("/api/v1/plots/plot/status").json()
    assert status["reading"]["provenance"] == "synthetic"
    assert status["reading"]["moisture_vwc"] == 0.25
    assert len(client.get("/api/v1/plots/plot/readings").json()["items"]) == 1
    assert "synthetic" in client.get("/api/v1/plots/plot/export").text


def test_duplicate_and_auth(client):
    data = payload()
    assert post(client, data, token="wrong").status_code == 401
    assert post(client, data).status_code == 201
    assert post(client, data).status_code == 409


@pytest.mark.parametrize("change", ["range", "naive", "future", "empty", "nan", "schema"])
def test_invalid_readings(client, change):
    data = payload()
    if change == "range":
        data["measurements"]["soil_moisture_vwc"] = 1.1
    if change == "naive":
        data["timestamp"] = "2026-01-01T10:00:00"
    if change == "future":
        data["timestamp"] = (utcnow() + timedelta(hours=1)).isoformat()
    if change == "empty":
        data["measurements"] = {}
    if change == "nan":
        data["measurements"]["soil_moisture_vwc"] = "NaN"
    if change == "schema":
        data["schema_version"] = "2.0"
    assert post(client, data).status_code == 422


def test_missing_stale_hardware_mode(client, monkeypatch):
    assert client.get("/api/v1/plots/plot/status").json()["status"] == "unavailable"
    data = payload()
    data["timestamp"] = (utcnow() - timedelta(hours=2)).isoformat()
    assert post(client, data).status_code == 201
    assert client.get("/api/v1/plots/plot/status").json()["status"] == "stale"
    assert client.get("/api/v1/plots/plot/forecast").json()["risk_level"] == "unknown"
    monkeypatch.setattr(settings, "data_source_mode", "hardware")
    assert client.get("/api/v1/plots/plot/status").json()["reading"] is None
    assert post(client).status_code == 409


def test_weather_failure_baseline(client, monkeypatch):
    def unavailable(*args):
        raise ValueError("offline")

    monkeypatch.setattr(weather_client, "fetch", unavailable)
    assert post(client).status_code == 201
    result = client.get("/api/v1/plots/plot/forecast").json()
    assert result["method"] == "persistence_baseline"
    assert result["predicted_vwc"] == 0.25
    assert result["validation_status"] == "not_field_validated"
    assert client.get("/api/v1/weather/current?plot_id=plot").json()["available"] is False


def test_hardware_calibration_raw_is_preserved(client, monkeypatch):
    monkeypatch.setattr(settings, "data_source_mode", "hybrid")
    device = client.post("/api/v1/devices", json={"id": "esp32", "name": "Field", "plot_id": "plot", "source": "esp32"}).json()
    calibration = client.post(
        "/api/v1/devices/esp32/calibrations",
        json={
            "raw_dry": 3000,
            "raw_wet": 1000,
            "vwc_dry": 0.1,
            "vwc_wet": 0.4,
            "soil_type": "Loam",
            "notes": "Two physically measured soil-specific calibration points",
            "verified": False,
        },
    ).json()
    data = payload()
    data.update(device_id="esp32", source="esp32", calibration_id=calibration["id"], measurements={"soil_moisture_raw": 2000})
    response = post(client, data, device["device_token"])
    assert response.status_code == 201
    assert response.json()["moisture_vwc"] == pytest.approx(0.25)
    assert response.json()["measurements"]["soil_moisture_raw"] == 2000
    assert "calibration_unverified" in response.json()["quality_flags"]
    assert "token_hash" not in client.get("/api/v1/devices").text


def test_source_spoofing_and_device_health(client):
    data = payload()
    data["source"] = "esp32"
    assert post(client, data).status_code == 403
    assert client.get("/api/v1/devices/device/health").json()["connection"] == "disconnected"


def test_simulation_reset_only_synthetic(client):
    assert post(client).status_code == 201
    body = {"plot_id": "plot", "scenario": "drying", "speed": 15}
    assert client.post("/api/v1/simulation/start", json=body).json()["running"]
    assert not client.post("/api/v1/simulation/pause", json=body).json()["running"]
    assert client.post("/api/v1/simulation/reset", json=body).status_code == 200
    assert client.get("/api/v1/plots/plot/status").json()["reading"] is None


def test_rate_limit_and_protected_actions(client, monkeypatch):
    monkeypatch.setattr(settings, "ingestion_limit_per_minute", 1)
    assert post(client).status_code == 201
    assert post(client).status_code == 429
    monkeypatch.setattr(settings, "local_demo", False)
    monkeypatch.setattr(settings, "admin_token", "a" * 32)
    assert client.post("/api/v1/farms", json={"name": "Farm", "location": "Dhaka", "latitude": 24, "longitude": 90}).status_code == 401


def test_timezone_ordering(client):
    data = payload()
    earlier = utcnow() - timedelta(hours=1)
    data["timestamp"] = earlier.astimezone(timezone(timedelta(hours=6))).isoformat()
    assert post(client, data).status_code == 201
    later = payload()
    assert post(client, later).status_code == 201
    returned = client.get("/api/v1/plots/plot/status").json()["reading"]["timestamp"]
    assert datetime.fromisoformat(returned) == datetime.fromisoformat(later["timestamp"])


def test_no_artifact_remains_baseline_only(client, monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "model_path", str(tmp_path / "missing.joblib"))
    assert client.post("/api/v1/models/predict", json={}).status_code == 409
    assert client.get("/api/v1/models").json()["ml_status"] == "not_validated"


def test_weather_notifications_are_deduplicated(client, monkeypatch):
    from contextlib import contextmanager
    from backend.app import worker
    from backend.app.main import app
    from backend.app.database import get_db

    @contextmanager
    def database():
        yield from app.dependency_overrides[get_db]()

    monkeypatch.setattr(worker, "SessionLocal", database)
    monkeypatch.setattr(worker, "weather", lambda db, plot: {"usable": False})
    worker.weather_alerts()
    worker.weather_alerts()
    notices = client.get("/api/v1/notifications?plot_id=plot").json()
    assert len(notices) == 1
    assert notices[0]["kind"] == "weather_unavailable"


def test_rain_and_irrigation_do_not_decrease_already_wet_simulated_soil():
    from backend.app.adapters import SimulatorAdapter

    for scenario in ["rainfall", "irrigation"]:
        reading = SimulatorAdapter("virtual", "plot", scenario=scenario, initial=0.46).read()
        assert reading["measurements"]["soil_moisture_vwc"] > 0.46


def test_real_readings_do_not_use_unverified_demo_thresholds(client, monkeypatch):
    monkeypatch.setattr(settings, "data_source_mode", "hybrid")

    def unavailable(*args):
        raise ValueError("offline")

    monkeypatch.setattr(weather_client, "fetch", unavailable)
    device = client.post("/api/v1/devices", json={"id": "field", "name": "Field fixture", "plot_id": "plot", "source": "esp32"}).json()
    cal = client.post(
        "/api/v1/devices/field/calibrations",
        json={
            "raw_dry": 3000,
            "raw_wet": 1000,
            "vwc_dry": 0.1,
            "vwc_wet": 0.4,
            "soil_type": "Loam",
            "notes": "Reviewed calibration fixture for software testing only",
            "verified": True,
        },
    ).json()
    data = payload()
    data.update(device_id="field", source="esp32", calibration_id=cal["id"], measurements={"soil_moisture_raw": 3000})
    assert post(client, data, device["device_token"]).status_code == 201
    assert client.get("/api/v1/plots/plot/status").json()["status"] == "monitoring"
    outlook = client.get("/api/v1/plots/plot/forecast").json()
    assert outlook["predicted_vwc"] == 0.1
    assert outlook["risk_level"] == "unknown"
