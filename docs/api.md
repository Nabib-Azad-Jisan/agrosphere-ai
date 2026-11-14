# API contract v1

Interactive OpenAPI: http://127.0.0.1:8000/docs . Canonical JSON schema: contracts/schemas/reading-v1.json . Datetimes require explicit timezones; storage normalizes UTC. UI displays Asia/Dhaka.

- GET /api/v1/health
- GET/POST /api/v1/farms; PATCH /api/v1/farms/{id}
- GET/POST /api/v1/plots; PATCH /api/v1/plots/{id}
- GET /api/v1/plots/{id}/status, /readings, /forecast, /advisories, /export
- GET/POST /api/v1/plots/{id}/irrigation
- POST /api/v1/readings; X-Device-Token required
- GET/POST /api/v1/devices; GET /api/v1/devices/{id}, /health, /calibrations
- POST /api/v1/devices/{id}/calibrations
- GET /api/v1/weather/current, /forecast, /historical; plot_id query required
- GET /api/v1/simulation/status?plot_id=...; POST /start, /pause, /reset
- POST /api/v1/feedback
- GET /api/v1/models, /models/evaluations, /analytics?plot_id=...
- GET /api/v1/notifications; PATCH /notifications/{id}/read

Mutations require Bearer ADMIN_TOKEN except explicit loopback native local-demo access. Read-only routes expose demo farm information; public deployment needs full user authorization. Device tokens are shown once and hashed in storage. Reading duplicates use device_id + UTC timestamp and return 409. Invalid measurement ranges or missing timezones return 422. Source/plot spoofing returns 403. Body-size limit is 1 MiB; rate limiting is per-client/IP, 120 ingestion requests/minute by default. In-memory limits apply per API process; use a shared edge limiter for multiple replicas.

Readings pagination: limit 1–5000, offset >= 0, timezone-aware start/end filters. Returned items are ascending within the most recent requested page. CSV exports are capped at 100,000 rows. Errors use {error:{code,message,details?}}. No traceback or secret fields are returned.
