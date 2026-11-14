# Implementation checklist

Primary specification: user-provided master development prompt. The six-week PDF schedule does not apply.

- [x] Foundation: Next.js / FastAPI monorepo, PostgreSQL, migrations, contracts, Docker definitions
- [x] Unified authenticated ingestion, devices, calibration and separate simulation worker
- [x] Weather client, cache, retry/fallback, RootSense quality and monitoring
- [x] AquaMind persistence/water-balance baselines, bilingual advisories, measured-data training/evaluation and experimental artifact inference
- [x] Landing and all nine workspace pages, responsive green interface, bilingual navigation/headings/advisories, light/dark themes
- [x] Integration, persisted notifications, analytics, irrigation/feedback records, CSV export
- [x] ESP32 transport example, provisioning/calibration contract and hardware documentation
- [x] API/ML/unit/browser test suites, CI and reproducible native setup

## Verification performed

- Python API + ML suite: 25 passed. Test artifacts use generated fixtures only and do not establish field accuracy.
- Frontend unit tests: 4 passed; ESLint and strict TypeScript checks passed.
- Production Next.js build passed for landing, all workspace routes and API gateway.
- Four desktop/mobile browser tests passed on both native PostgreSQL and the full Docker stack: all workspace pages, invalid device-form input, simulation → authenticated ingestion → a newly generated persisted reading → RootSense → AquaMind → language/theme switching, with no horizontal mobile overflow.
- PostgreSQL migrations, seed and a fresh-session persistence check passed against PostgreSQL 17 in Docker.
- Simulation drying/irrigation smoke check passed through the actual running HTTP API.
- Live Open-Meteo check returned 168 hourly and seven daily forecasts; source-labeled provider response cached in the PostgreSQL demo.
- Docker API/frontend images built; Compose migrations completed, API/database health passed, and the frontend returned HTTP 200. Direct unauthenticated mutation returned 401 with local-demo bypass disabled. Default containers run baseline services; INSTALL_ML=true enables optional scientific dependencies.
- Final unique automated test count: 33 (25 Python, four frontend unit tests, four browser tests). The optional scientific-library Docker build was not run; the complete ML pipeline was verified in the native development environment.

## Remaining evidence and deployment work

- GitHub upload: the account's existing credential cannot create active Actions workflows. The CI definition is retained as docs/ci/github-actions.yml; activation requires workflow permission and copying it to .github/workflows/ci.yml.

- No credible measured field dataset has been supplied. Operational ML remains unvalidated and baseline-only by design. Model approval requires independent evaluation and field review.
- No ESP32 was attached. Physical sensor calibration, wiring, secure firmware buffering/retries and actual device validation remain future hardware work.
- Full editorial translation of administrative forms remains; navigation, page headings, key guidance and preferences support English/Bengali.
- Public multi-user accounts/authorization are outside the implemented local single-operator access mode.
- Non-failing dependency deprecation warnings remain in the Python tests (pandas/NumPy timedelta compatibility and Starlette's httpx test transport).

## Local handoff

The full Docker stack has been built and verified. Test services are stopped after verification; containers and PostgreSQL data are retained. From this directory, `docker compose up -d` restarts the app at http://127.0.0.1:3000. Sensor center starts/pauses the labeled simulation. Use `docker compose stop` to stop it again. See README.md for fresh setup, native development and the one-command launcher.

## Decisions

- Local-first application; no external hosting registration or deployment.
- PostgreSQL is the Docker default; SQLite is supported for isolated development/tests.
- Synchronous SQLAlchemy sessions in FastAPI threadpool routes; separate APScheduler worker.
- All canonical moisture values use VWC m³/m³. Raw ADC is retained separately. Synthetic VWC is always labeled synthetic and cannot validate a model or physical calibration.
- No credible measured dataset has been supplied. Baselines work immediately; measured-data ML training is gated, with no bundled fabricated model.
