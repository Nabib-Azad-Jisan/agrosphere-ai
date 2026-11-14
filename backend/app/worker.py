"""Run one worker process separately from web workers: python -m backend.app.worker."""

import json
import logging
from datetime import timedelta
import httpx
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import select
from .database import SessionLocal, utcnow, aware
from .config import settings
from .models import SimulationSession, Device, Reading, Plot, Notification
from .adapters import SimulatorAdapter
from .security import new_token, token_hash
from .rootsense import status
from .weather import weather, next_24h

logger = logging.getLogger("agrosphere.worker")
logging.basicConfig(level=logging.INFO, format="%(message)s")
logging.getLogger("apscheduler").setLevel(logging.WARNING)


def tick():
    if settings.data_source_mode not in {"simulation", "hybrid"}:
        return
    with SessionLocal() as db:
        for session in db.scalars(select(SimulationSession).where(SimulationSession.running.is_(True))):
            if session.last_tick and (utcnow() - aware(session.last_tick)).total_seconds() < max(1, 15 / session.speed):
                continue
            device_id = f"sim_{session.plot_id}"[:64]
            device = db.get(Device, device_id)
            token = new_token()
            if not device:
                device = Device(
                    id=device_id,
                    plot_id=session.plot_id,
                    name="Virtual root-zone station",
                    source="simulator",
                    token_hash=token_hash(token),
                )
                db.add(device)
            elif device.source != "simulator" or device.plot_id != session.plot_id:
                session.last_error = "Reserved simulator device ID is already in use"
                db.commit()
                continue
            else:
                device.token_hash = token_hash(token)
            db.commit()
            latest = db.scalar(select(Reading).where(Reading.device_id == device_id).order_by(Reading.timestamp.desc()).limit(1))
            initial = latest.moisture_vwc if latest and latest.moisture_vwc is not None else 0.32
            payload = SimulatorAdapter(device_id, session.plot_id, session.scenario, session.step, initial).read()
            session.last_error = None
            if payload:
                try:
                    response = httpx.post(f"{settings.api_base_url}/readings", json=payload, headers={"X-Device-Token": token}, timeout=10)
                    if response.status_code != 201:
                        session.last_error = f"Ingestion rejected: HTTP {response.status_code} (expected for invalid scenario)"
                except httpx.HTTPError:
                    session.last_error = "Ingestion API unavailable; retrying next tick"
            session.step += 1
            session.last_tick = utcnow()
            db.commit()


def monitor():
    with SessionLocal() as db:
        for plot in db.scalars(select(Plot)):
            result = status(db, plot)
            kind = result["status"]
            if kind in {"adequate", "monitoring"}:
                continue
            recent = db.scalar(
                select(Notification)
                .where(Notification.plot_id == plot.id, Notification.kind == kind, Notification.created_at > utcnow() - timedelta(hours=1))
                .limit(1)
            )
            if not recent:
                prefix = "Simulation: " if result["reading"] and result["reading"]["provenance"] == "synthetic" else ""
                db.add(
                    Notification(
                        plot_id=plot.id,
                        kind=kind,
                        message=f"{prefix}{plot.name}: {kind.replace('_', ' ')}. Inspect soil and device before irrigation decisions.",
                    )
                )
        db.commit()


def weather_alerts():
    with SessionLocal() as db:
        for plot in db.scalars(select(Plot)):
            outlook = weather(db, plot)
            totals = next_24h(outlook)
            if not outlook.get("usable"):
                kind, message = (
                    "weather_unavailable",
                    "Weather is missing or outdated. Advisories use the persistence baseline until a usable forecast returns.",
                )
            elif totals and totals["rain_mm"] >= 20:
                kind, message = (
                    "forecast_rain",
                    f"Forecast rainfall totals {totals['rain_mm']} mm over the next 24 hours. Inspect drainage and verify field conditions.",
                )
            else:
                continue
            recent = db.scalar(
                select(Notification)
                .where(Notification.plot_id == plot.id, Notification.kind == kind, Notification.created_at > utcnow() - timedelta(hours=6))
                .limit(1)
            )
            if not recent:
                db.add(Notification(plot_id=plot.id, kind=kind, message=message))
        db.commit()


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(tick, "interval", seconds=1, max_instances=1, coalesce=True)
    scheduler.add_job(monitor, "interval", seconds=30, max_instances=1)
    scheduler.add_job(weather_alerts, "interval", minutes=15, max_instances=1, coalesce=True)
    logger.info(json.dumps({"event": "worker.started", "mode": settings.data_source_mode}))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)
