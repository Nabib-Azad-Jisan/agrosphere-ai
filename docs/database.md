# Database

Alembic revision 0001 creates normalized farms, plots, devices, device_calibrations, sensor_readings, weather_forecasts, irrigation_events, forecast_runs, notifications, simulation_sessions, feedback and audit_logs. Migration schema is frozen in backend/alembic/schema_v1.py, independent from future model edits. Add a new revision for schema changes.

Foreign keys associate all observations with plots and devices. Device/timestamp pairs are unique. Source and timestamp columns are indexed. Raw measurement JSON is immutable on ingestion; derived VWC and calibration reference are separate columns. Calibration profiles are append-only; old readings are not overwritten by new calibrations. UTC timestamps and explicit VWC units are preserved.

Forecast runs store input reading references and explanation payloads. Weather fetches store the complete provider response plus retrieval time; provider model issuance is not invented. Current schema omits user accounts because this deliverable is a local single-operator app. Crop configuration lives on each plot. ML artifacts/evaluation metadata live in versioned files rather than dedicated registry tables.

Backup PostgreSQL with pg_dump before migrations. Restore into a clean database and apply migrations. Docker compose down preserves postgres_data; do not delete the volume unless discarding all local data is intended.
