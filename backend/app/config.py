from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./agrosphere.db"
    data_source_mode: Literal["simulation", "historical", "hardware", "hybrid"] = "simulation"
    local_demo: bool = True
    admin_token: str = ""
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    api_base_url: str = "http://127.0.0.1:8000/api/v1"
    stale_minutes: int = 60
    weather_cache_minutes: int = 30
    weather_max_age_minutes: int = 180
    weather_timeout: float = 10
    ingestion_limit_per_minute: int = 120
    max_body_bytes: int = 1048576
    model_path: str = "ml/artifacts/model.joblib"


settings = Settings()
