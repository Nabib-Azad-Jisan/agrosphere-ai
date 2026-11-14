"""Explicit PostgreSQL integration check, separate from isolated unit tests."""

import os
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values

values = dotenv_values(".env")
os.environ["DATABASE_URL"] = (
    f"postgresql+pg8000://{values.get('POSTGRES_USER', 'agrosphere')}:"
    f"{values['POSTGRES_PASSWORD']}@127.0.0.1:5432/{values.get('POSTGRES_DB', 'agrosphere')}"
)
os.environ["LOCAL_DEMO"] = "true"
os.environ["API_BASE_URL"] = "http://127.0.0.1:8001/api/v1"
subprocess.run([sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head"], check=True)
subprocess.run([sys.executable, "-m", "backend.app.seed"], check=True)

import time  # noqa: E402
import httpx  # noqa: E402
from backend.app.worker import tick  # noqa: E402
from backend.app.database import SessionLocal  # noqa: E402
from backend.app.models import Reading  # noqa: E402
from sqlalchemy import select  # noqa: E402

log = Path("postgres-integration.log").open("w", encoding="utf-8")
process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8001"], stdout=log, stderr=log
)
try:
    for attempt in range(40):
        try:
            if httpx.get("http://127.0.0.1:8001/api/v1/health", timeout=1).status_code == 200:
                break
        except httpx.HTTPError:
            pass
        time.sleep(0.25)
    else:
        raise RuntimeError("PostgreSQL-backed API did not start")
    with httpx.Client(base_url="http://127.0.0.1:8001/api/v1", timeout=10) as client:
        body = {"plot_id": "tomato_plot_001", "scenario": "drying", "speed": 15}
        client.post("/simulation/start", json=body).raise_for_status()
        tick()
        result = client.get("/plots/tomato_plot_001/status").json()
        assert result["reading"]["provenance"] == "synthetic"
        reading_id = result["reading"]["id"]
        client.post("/simulation/pause", json=body).raise_for_status()
    # A fresh DB session proves persisted storage independently of the response cache.
    with SessionLocal() as db:
        assert db.scalar(select(Reading.id).where(Reading.id == reading_id)) == reading_id
    print("PASS: PostgreSQL migrations, seed, worker -> HTTP ingestion -> persistent reading -> status.")
finally:
    process.terminate()
    process.wait(timeout=10)
    log.close()
