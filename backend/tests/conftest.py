import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.config import settings
from backend.app.models import Farm, Plot, Device
from backend.app.security import token_hash, limiter


@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory() as db:
        db.add(Farm(id="farm", name="Test Farm", location="Gazipur", latitude=24, longitude=90))
        db.flush()
        db.add(Plot(id="plot", farm_id="farm", name="Tomato"))
        db.flush()
        db.add(Device(id="device", plot_id="plot", name="Virtual station", source="simulator", token_hash=token_hash("test-secret")))
        db.commit()

    def override():
        with factory() as db:
            yield db

    app.dependency_overrides[get_db] = override
    monkeypatch.setattr(settings, "data_source_mode", "simulation")
    monkeypatch.setattr(settings, "local_demo", True)
    limiter.events.clear()
    with TestClient(app) as test:
        yield test
    app.dependency_overrides.clear()
    engine.dispose()
