from sqlalchemy import select
from .database import SessionLocal
from .models import Farm, Plot


def seed():
    with SessionLocal() as db:
        if db.scalar(select(Farm.id).limit(1)):
            return
        db.add(Farm(id="demo_farm", name="Demo Tomato Farm", location="Gazipur, Bangladesh", latitude=24.0023, longitude=90.4264))
        db.flush()
        db.add(Plot(id="tomato_plot_001", farm_id="demo_farm", name="North Tomato Plot", crop="Tomato", planting_date="2026-10-15"))
        db.commit()


if __name__ == "__main__":
    seed()
