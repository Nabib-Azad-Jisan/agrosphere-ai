import csv
import io
import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Request, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select, delete, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from .config import settings
from .database import get_db, utcnow, aware
from .models import Farm, Plot, Device, Calibration, Reading, Irrigation, SimulationSession, Notification, AuditLog, Feedback, ForecastRun
from .schemas import (
    FarmIn,
    PlotIn,
    DeviceIn,
    ReadingIn,
    CalibrationIn,
    SimulationIn,
    IrrigationIn,
    FeedbackIn,
    ReadingOut,
    RootSenseOut,
    ForecastOut,
)
from .security import require_admin, new_token, token_hash, limiter
from .ingestion import ingest, serialize, MODES
from .rootsense import status
from .aquamind import save_forecast
from .weather import weather, client

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("agrosphere")
DB = Annotated[Session, Depends(get_db)]
Admin = Depends(require_admin)


@asynccontextmanager
async def lifespan(app):
    if not settings.local_demo and len(settings.admin_token) < 32:
        raise RuntimeError("Non-demo mode requires ADMIN_TOKEN of at least 32 characters")
    yield


app = FastAPI(title="ZYNTRIX AgroSphere AI", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-Device-Token"],
)


@app.middleware("http")
async def request_guard(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and (not length.isdigit() or int(length) > settings.max_body_bytes):
        return JSONResponse(status_code=413, content={"error": {"code": "body_too_large", "message": "Request body exceeds limit"}})
    if request.method in {"POST", "PATCH", "PUT"}:
        size = 0
        chunks = []
        async for chunk in request.stream():
            size += len(chunk)
            if size > settings.max_body_bytes:
                return JSONResponse(status_code=413, content={"error": {"code": "body_too_large", "message": "Request body exceeds limit"}})
            chunks.append(chunk)
        request._body = b"".join(chunks)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    logger.info(json.dumps({"event": "http", "method": request.method, "path": request.url.path, "status": response.status_code}))
    return response


@app.exception_handler(HTTPException)
async def http_error(_, exc):
    return JSONResponse(
        status_code=exc.status_code, content={"error": {"code": str(exc.status_code), "message": exc.detail}}, headers=exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_error(_, exc):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Invalid request",
                "details": [{"field": ".".join(map(str, e["loc"])), "message": e["msg"]} for e in exc.errors()],
            }
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_error(_, exc):
    logger.error(json.dumps({"event": "database_error", "type": type(exc).__name__}))
    return JSONResponse(status_code=503, content={"error": {"code": "database_unavailable", "message": "Storage temporarily unavailable"}})


@app.exception_handler(Exception)
async def unexpected_error(_, exc):
    logger.error(json.dumps({"event": "unexpected_error", "type": type(exc).__name__}))
    return JSONResponse(
        status_code=500, content={"error": {"code": "internal_error", "message": "An unexpected error occurred. Please retry."}}
    )


def get_plot(db, plot_id):
    plot = db.get(Plot, plot_id)
    if not plot:
        raise HTTPException(404, "Plot not found")
    return plot


def store(db, model, values):
    row = model(**values)
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Resource already exists or invalid reference") from None
    return serialize(row)


@app.get("/api/v1/health")
def health(db: DB):
    db.execute(text("SELECT 1"))
    return {"ok": True, "data_source_mode": settings.data_source_mode, "local_demo": settings.local_demo}


@app.get("/api/v1/farms")
def farms(db: DB):
    return [serialize(x) for x in db.scalars(select(Farm).order_by(Farm.created_at).limit(500))]


@app.post("/api/v1/farms", dependencies=[Admin], status_code=201)
def create_farm(payload: FarmIn, db: DB):
    return store(db, Farm, payload.model_dump())


@app.patch("/api/v1/farms/{farm_id}", dependencies=[Admin])
def update_farm(farm_id: str, payload: FarmIn, db: DB):
    row = db.get(Farm, farm_id)
    if not row:
        raise HTTPException(404, "Farm not found")
    for k, v in payload.model_dump().items():
        setattr(row, k, v)
    db.commit()
    return serialize(row)


@app.get("/api/v1/plots")
def plots(db: DB):
    return [serialize(x) for x in db.scalars(select(Plot).limit(500))]


@app.post("/api/v1/plots", dependencies=[Admin], status_code=201)
def create_plot(payload: PlotIn, db: DB):
    if not db.get(Farm, payload.farm_id):
        raise HTTPException(404, "Farm not found")
    return store(db, Plot, payload.model_dump(mode="json"))


@app.patch("/api/v1/plots/{plot_id}", dependencies=[Admin])
def update_plot(plot_id: str, payload: PlotIn, db: DB):
    row = get_plot(db, plot_id)
    if not db.get(Farm, payload.farm_id):
        raise HTTPException(404, "Farm not found")
    for k, v in payload.model_dump(mode="json").items():
        setattr(row, k, v)
    db.commit()
    return serialize(row)


@app.post("/api/v1/readings", status_code=201, response_model=ReadingOut)
def add_reading(payload: ReadingIn, db: DB, request: Request, x_device_token: str = Header(default="")):
    limiter.check(request.client.host if request.client else "unknown")
    return serialize(ingest(db, payload, x_device_token))


@app.get("/api/v1/plots/{plot_id}/status", response_model=RootSenseOut)
def plot_status(plot_id: str, db: DB):
    return status(db, get_plot(db, plot_id))


def readings_query(plot_id, start, end):
    query = select(Reading).where(Reading.plot_id == plot_id, Reading.source.in_(MODES[settings.data_source_mode]))
    if start:
        query = query.where(Reading.timestamp >= start)
    if end:
        query = query.where(Reading.timestamp <= end)
    return query.order_by(Reading.timestamp.desc())


@app.get("/api/v1/plots/{plot_id}/readings")
def readings(
    plot_id: str,
    db: DB,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int = Query(500, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    get_plot(db, plot_id)
    for value in (start, end):
        if value and value.tzinfo is None:
            raise HTTPException(422, "Date filters require timezone")
    rows = db.scalars(readings_query(plot_id, start, end).limit(limit).offset(offset)).all()
    return {"items": [serialize(x) for x in reversed(rows)], "limit": limit, "offset": offset, "unit": "vwc_m3_m3"}


@app.get("/api/v1/plots/{plot_id}/export")
def export_readings(plot_id: str, db: DB):
    get_plot(db, plot_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "device_id", "moisture_vwc", "unit", "source", "provenance", "quality_flags"])
    for row in db.scalars(readings_query(plot_id, None, None).limit(100000)):
        writer.writerow(
            [
                aware(row.timestamp).isoformat(),
                row.device_id,
                row.moisture_vwc,
                row.moisture_unit,
                row.source,
                row.provenance,
                ";".join(row.quality_flags),
            ]
        )
    return Response(
        output.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="agrosphere-readings.csv"'}
    )


@app.get("/api/v1/plots/{plot_id}/forecast", response_model=ForecastOut)
def plot_forecast(plot_id: str, db: DB):
    return save_forecast(db, get_plot(db, plot_id))


@app.get("/api/v1/plots/{plot_id}/advisories")
def advisories(plot_id: str, db: DB):
    result = save_forecast(db, get_plot(db, plot_id))
    return {
        "advice": result["advice"],
        "reasons": result["reasons"],
        "risk_level": result["risk_level"],
        "validation_status": result["validation_status"],
    }


@app.get("/api/v1/devices")
def devices(db: DB):
    return [serialize(x) for x in db.scalars(select(Device).limit(500))]


@app.post("/api/v1/devices", dependencies=[Admin], status_code=201)
def create_device(payload: DeviceIn, db: DB):
    get_plot(db, payload.plot_id)
    token = new_token()
    result = store(db, Device, {**payload.model_dump(), "token_hash": token_hash(token)})
    return {**result, "device_token": token, "notice": "Copy now; the secret is never returned again"}


@app.get("/api/v1/devices/{device_id}")
def device(device_id: str, db: DB):
    row = db.get(Device, device_id)
    if not row:
        raise HTTPException(404, "Device not found")
    return serialize(row)


@app.get("/api/v1/devices/{device_id}/health")
def device_health(device_id: str, db: DB):
    row = device(device_id, db)
    last = db.scalar(select(Reading).where(Reading.device_id == device_id).order_by(Reading.timestamp.desc()).limit(1))
    age = (utcnow() - aware(last.timestamp)).total_seconds() / 60 if last else None
    return {
        **row,
        "connection": "connected" if age is not None and age <= settings.stale_minutes else "disconnected",
        "age_minutes": age,
        "quality_flags": last.quality_flags if last else ["no_observations"],
        "battery_percent": last.battery_percent if last else None,
    }


@app.get("/api/v1/devices/{device_id}/calibrations")
def calibrations(device_id: str, db: DB):
    device(device_id, db)
    return [serialize(x) for x in db.scalars(select(Calibration).where(Calibration.device_id == device_id))]


@app.post("/api/v1/devices/{device_id}/calibrations", dependencies=[Admin], status_code=201)
def create_calibration(device_id: str, payload: CalibrationIn, db: DB):
    device(device_id, db)
    result = store(db, Calibration, {**payload.model_dump(), "device_id": device_id})
    db.add(AuditLog(action="calibration.created", entity_id=device_id, details={"calibration_id": result["id"]}))
    db.commit()
    return result


@app.get("/api/v1/weather/current")
@app.get("/api/v1/weather/forecast")
def plot_weather(plot_id: str, db: DB):
    return weather(db, get_plot(db, plot_id))


@app.get("/api/v1/weather/historical", dependencies=[Admin])
def historical_weather(plot_id: str, start: str, end: str, db: DB):
    from datetime import date

    try:
        first, last = date.fromisoformat(start), date.fromisoformat(end)
        if last < first or (last - first).days > 366 or last >= utcnow().date():
            raise ValueError()
    except ValueError:
        raise HTTPException(422, "Provide a past date range of at most 366 days") from None
    farm = db.get(Farm, get_plot(db, plot_id).farm_id)
    try:
        return client.historical(farm.latitude, farm.longitude, start, end)
    except Exception:
        raise HTTPException(503, "Historical weather unavailable") from None


@app.get("/api/v1/simulation/status")
def simulation_status(plot_id: str, db: DB):
    get_plot(db, plot_id)
    row = db.scalar(select(SimulationSession).where(SimulationSession.plot_id == plot_id))
    return (
        serialize(row) if row else {"plot_id": plot_id, "running": False, "scenario": "drying", "speed": 1, "step": 0, "last_error": None}
    )


@app.post("/api/v1/simulation/start", dependencies=[Admin])
def simulation_start(payload: SimulationIn, db: DB):
    get_plot(db, payload.plot_id)
    if settings.data_source_mode not in {"simulation", "hybrid"}:
        raise HTTPException(409, "Simulation disabled in this source mode")
    row = db.scalar(select(SimulationSession).where(SimulationSession.plot_id == payload.plot_id))
    if not row:
        row = SimulationSession(plot_id=payload.plot_id)
        db.add(row)
    row.scenario, row.speed, row.running, row.last_error = payload.scenario, payload.speed, True, None
    db.commit()
    return serialize(row)


@app.post("/api/v1/simulation/pause", dependencies=[Admin])
def simulation_pause(payload: SimulationIn, db: DB):
    row = db.scalar(select(SimulationSession).where(SimulationSession.plot_id == payload.plot_id))
    if row:
        row.running = False
        db.commit()
    return simulation_status(payload.plot_id, db)


@app.post("/api/v1/simulation/reset", dependencies=[Admin])
def simulation_reset(payload: SimulationIn, db: DB):
    get_plot(db, payload.plot_id)
    # Reset deletes only synthetic readings and associated forecast runs, never actual observations.
    synthetic_ids = select(Reading.id).where(Reading.plot_id == payload.plot_id, Reading.source == "simulator")
    db.execute(delete(ForecastRun).where(ForecastRun.reading_id.in_(synthetic_ids)))
    db.execute(delete(Reading).where(Reading.plot_id == payload.plot_id, Reading.source == "simulator"))
    row = db.scalar(select(SimulationSession).where(SimulationSession.plot_id == payload.plot_id))
    if row:
        row.step, row.running, row.last_tick, row.last_error = 0, False, None, None
    db.add(AuditLog(action="simulation.reset", entity_id=payload.plot_id, details={"synthetic_only": True}))
    db.commit()
    return simulation_status(payload.plot_id, db)


@app.get("/api/v1/plots/{plot_id}/irrigation")
def irrigation_history(plot_id: str, db: DB):
    get_plot(db, plot_id)
    return [
        serialize(x)
        for x in db.scalars(select(Irrigation).where(Irrigation.plot_id == plot_id).order_by(Irrigation.timestamp.desc()).limit(500))
    ]


@app.post("/api/v1/plots/{plot_id}/irrigation", dependencies=[Admin], status_code=201)
def irrigation_event(plot_id: str, payload: IrrigationIn, db: DB):
    get_plot(db, plot_id)
    if payload.timestamp > utcnow() + timedelta(minutes=5):
        raise HTTPException(422, "Irrigation events cannot be in the future")
    return store(db, Irrigation, {**payload.model_dump(), "plot_id": plot_id})


@app.post("/api/v1/feedback", dependencies=[Admin], status_code=201)
def feedback(payload: FeedbackIn, db: DB):
    get_plot(db, payload.plot_id)
    return store(db, Feedback, payload.model_dump())


@app.get("/api/v1/notifications")
def notifications(db: DB, plot_id: str | None = None):
    query = select(Notification)
    if plot_id:
        query = query.where(Notification.plot_id == plot_id)
    return [serialize(x) for x in db.scalars(query.order_by(Notification.created_at.desc()).limit(200))]


@app.patch("/api/v1/notifications/{notification_id}/read", dependencies=[Admin])
def read_notification(notification_id: str, db: DB):
    row = db.get(Notification, notification_id)
    if not row:
        raise HTTPException(404, "Notification not found")
    row.read = True
    db.commit()
    return serialize(row)


@app.get("/api/v1/models")
def models():
    return {
        "active": "baseline-v1",
        "mode": "baseline",
        "ml_status": "not_validated",
        "reason": "No field-validated measured-data artifact has been approved",
        "methods": ["persistence_baseline", "water_balance_baseline"],
    }


@app.get("/api/v1/models/evaluations")
def evaluations():
    from pathlib import Path

    path = Path("ml/artifacts/evaluation.json")
    return (
        json.loads(path.read_text())
        if path.exists()
        else {
            "status": "no_measured_evaluation",
            "results": [],
            "notice": "Measured test data required; simulation is not validation evidence",
        }
    )


@app.post("/api/v1/models/predict", dependencies=[Admin])
def experimental_prediction(values: dict[str, float]):
    """Explicit experimental inference, never silently promoted into field advice."""
    from pathlib import Path

    if not Path(settings.model_path).is_file():
        raise HTTPException(409, "No trained artifact available. Baseline mode remains active.")
    try:
        from ml.pipeline import load_artifact, predict
    except ImportError:
        raise HTTPException(409, "ML runtime is not installed. Install ml/requirements.txt or build with INSTALL_ML=true.") from None

    try:
        artifact = load_artifact(settings.model_path)
        return predict(artifact, values)
    except (ValueError, KeyError):
        raise HTTPException(422, "Incompatible artifact or incomplete prediction-time feature vector") from None


@app.get("/api/v1/analytics")
def analytics(plot_id: str, db: DB):
    get_plot(db, plot_id)
    grouped = db.execute(
        select(Reading.provenance, func.count(Reading.id)).where(Reading.plot_id == plot_id).group_by(Reading.provenance)
    ).all()
    return {
        "provenance_counts": dict(grouped),
        "evaluation": evaluations(),
        "irrigation": irrigation_history(plot_id, db),
        "field_savings": None,
    }
