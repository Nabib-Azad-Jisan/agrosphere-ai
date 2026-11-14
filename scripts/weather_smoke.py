"""Optional network-dependent provider smoke check; not part of deterministic tests."""

import argparse
import os
from dotenv import dotenv_values

parser = argparse.ArgumentParser()
parser.add_argument("--cache-demo", action="store_true")
parser.add_argument("--postgres", action="store_true")
args = parser.parse_args()
if args.postgres:
    values = dotenv_values(".env")
    os.environ["DATABASE_URL"] = (
        f"postgresql+pg8000://{values.get('POSTGRES_USER', 'agrosphere')}:"
        f"{values['POSTGRES_PASSWORD']}@127.0.0.1:5432/{values.get('POSTGRES_DB', 'agrosphere')}"
    )
from backend.app.weather import client, weather  # noqa: E402

if args.cache_demo:
    from backend.app.database import SessionLocal
    from backend.app.models import Plot

    with SessionLocal() as db:
        result = weather(db, db.get(Plot, "tomato_plot_001"), refresh=True)
        if not result["available"]:
            raise RuntimeError("Live forecast unavailable")
        data = result["data"]
else:
    data = client.fetch(24.0023, 90.4264)
print(f"PASS: Open-Meteo returned {len(data['hourly']['time'])} hourly forecasts and {len(data['daily']['time'])} daily forecasts.")
