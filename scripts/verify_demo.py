"""Full local pipeline smoke check. API and worker must already be running."""

import time
import httpx

base = "http://127.0.0.1:8000/api/v1"
with httpx.Client(timeout=45) as client:
    body = {"plot_id": "tomato_plot_001", "scenario": "drying", "speed": 15}
    client.post(f"{base}/simulation/start", json=body).raise_for_status()
    try:
        for _ in range(30):
            status = client.get(f"{base}/plots/tomato_plot_001/status").json()
            if status.get("reading"):
                break
            time.sleep(1)
        assert status["reading"]["provenance"] == "synthetic"
        initial = status["reading"]["moisture_vwc"]
        body["scenario"] = "irrigation"
        client.post(f"{base}/simulation/start", json=body).raise_for_status()
        time.sleep(3)
        after = client.get(f"{base}/plots/tomato_plot_001/status").json()
        assert after["reading"]["moisture_vwc"] > initial
        forecast = client.get(f"{base}/plots/tomato_plot_001/forecast").json()
        assert forecast["data_source"] == "synthetic"
        assert forecast["validation_status"] == "not_field_validated"
        print("PASS: simulation ingestion, persisted observations, irrigation response, forecast and honest source labeling.")
    finally:
        client.post(f"{base}/simulation/pause", json=body).raise_for_status()
