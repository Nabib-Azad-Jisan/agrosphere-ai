from datetime import timedelta, datetime, timezone
import time
import httpx
from sqlalchemy import select
from .models import WeatherForecast, Farm
from .database import utcnow, aware
from .config import settings

HOURLY = "temperature_2m,relative_humidity_2m,precipitation,precipitation_probability,wind_speed_10m,et0_fao_evapotranspiration"


class OpenMeteoClient:
    def fetch(self, latitude, longitude):
        error = None
        for attempt in range(3):
            try:
                response = httpx.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "hourly": HOURLY,
                        "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code",
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration",
                        "forecast_days": 7,
                        "timezone": "UTC",
                    },
                    timeout=settings.weather_timeout,
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("hourly", {}).get("time"):
                    raise ValueError("Weather response missing hourly time series")
                return data
            except (httpx.HTTPError, ValueError) as exc:
                error = exc
                if attempt < 2:
                    time.sleep(0.2 * (attempt + 1))
        raise ValueError("Weather provider unavailable") from error

    def historical(self, latitude, longitude, start, end):
        response = httpx.get(
            "https://archive-api.open-meteo.com/v1/archive",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start,
                "end_date": end,
                "hourly": "temperature_2m,relative_humidity_2m,precipitation,et0_fao_evapotranspiration",
                "timezone": "UTC",
            },
            timeout=settings.weather_timeout,
        )
        response.raise_for_status()
        return {"source": "open_meteo_reanalysis", "use": "historical_context_only_not_archived_forecast", "data": response.json()}


client = OpenMeteoClient()


def weather(db, plot, refresh=False):
    cached = db.scalar(
        select(WeatherForecast).where(WeatherForecast.plot_id == plot.id).order_by(WeatherForecast.fetched_at.desc()).limit(1)
    )
    age = (utcnow() - aware(cached.fetched_at)).total_seconds() / 60 if cached else None
    request_status = "cached"
    if refresh or cached is None or age > settings.weather_cache_minutes:
        farm = db.get(Farm, plot.farm_id)
        try:
            data = client.fetch(farm.latitude, farm.longitude)
            cached = WeatherForecast(plot_id=plot.id, payload=data)
            db.add(cached)
            db.commit()
            age = 0
            request_status = "fresh"
        except ValueError:
            request_status = "provider_unavailable"
    if cached is None:
        return {
            "available": False,
            "request_status": request_status,
            "data": None,
            "age_minutes": None,
            "usable": False,
            "source": "open_meteo",
        }
    return {
        "available": True,
        "usable": age <= settings.weather_max_age_minutes,
        "age_minutes": round(age, 1),
        "fetched_at": aware(cached.fetched_at).isoformat(),
        "forecast_issued_at": None,
        "issuance_note": "Retrieval time recorded; provider model issuance not supplied by this endpoint",
        "request_status": request_status,
        "source": "open_meteo",
        "data": cached.payload,
    }


def next_24h(weather_result, at=None):
    if not weather_result.get("usable"):
        return None
    now = at or utcnow()
    hourly = weather_result["data"]["hourly"]
    indices = [
        i
        for i, value in enumerate(hourly["time"])
        if now <= datetime.fromisoformat(value).replace(tzinfo=timezone.utc) < now + timedelta(hours=24)
    ]
    if len(indices) < 20:
        return None

    def total(key):
        values = hourly.get(key, [])
        if any(i >= len(values) or values[i] is None for i in indices):
            return None
        return sum(values[i] for i in indices)

    rain, et0 = total("precipitation"), total("et0_fao_evapotranspiration")
    return {"rain_mm": round(rain, 2), "et0_mm": round(et0, 2)} if rain is not None and et0 is not None else None
