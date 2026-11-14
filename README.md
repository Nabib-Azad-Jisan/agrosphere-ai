# ZYNTRIX — AgroSphere AI

**Intelligence Beyond Boundaries**

Software-first tomato monitoring and irrigation decision support for Bangladesh. Next.js App Router, React/TypeScript, FastAPI, SQLAlchemy/Alembic, PostgreSQL, and a separate simulation/monitoring worker. Simulation and future ESP32 devices share the authenticated ingestion API.

**Evidence boundary:** synthetic readings are labeled. Current live forecasting uses transparent persistence/water-balance baselines. No measured training dataset is bundled, no field-validated ML is claimed, and no pump is controlled. See [limitations](docs/limitations.md) and [implementation status](IMPLEMENTATION.md).

## Quick start: Docker

Requires Docker Desktop running, Node 20.9+ for native frontend work, and Python 3.12 for native backend work. Docker contains its own runtimes.

From this directory in PowerShell:

```powershell
python scripts/configure_local.py
docker compose up --build -d
```

The configuration script generates random local database and administrator secrets, preserving existing non-empty values. Docker runs PostgreSQL, the migration/seed job, API, worker, and frontend. Open **http://127.0.0.1:3000**, then Sensor center → Start simulation. API documentation: **http://127.0.0.1:8000/docs**.

The browser uses a server-side local gateway; secrets are not shipped to browser JavaScript. All published ports bind to loopback. This is a local single-operator demo, not a public multi-user deployment.

```powershell
docker compose logs -f api worker
docker compose stop
# Remove containers while retaining the database volume:
docker compose down
```

## Native development

Once dependencies are installed and PostgreSQL is running, a single local launcher runs migrations, seeds, API, worker and Next.js:

```powershell
.\.venv\Scripts\python.exe scripts/run_local.py --postgres
```

Press Ctrl+C to stop its services. Omit `--postgres` to use DATABASE_URL from .env (SQLite by default). The native PostgreSQL launcher uses the portable pg8000 driver for Windows compatibility; Docker uses psycopg.

Run from the monorepo root. SQLite is optional for hardware-free local testing. For PostgreSQL, set DATABASE_URL to a `postgresql+psycopg://` URL in `.env`, and run `docker compose up -d db` before migrations. Native local demo actions are accepted only from loopback.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
.\.venv\Scripts\python.exe scripts/configure_local.py
.\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head
.\.venv\Scripts\python.exe -m backend.app.seed
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

Second terminal (same root):

```powershell
.\.venv\Scripts\python.exe -m backend.app.worker
```

Third terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open **http://127.0.0.1:3000**. Open Sensor center, select a scenario and start the simulation. Use Pause to stop generation. Reset removes only synthetic observations for the selected plot. Use Ctrl+C in each terminal to stop native processes.

## Checks

```powershell
# Root
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend ml scripts
# Frontend
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
# With API, worker, frontend and seeded DB running:
npx playwright install chromium
npm run test:e2e
```

Python API tests mock weather and use an isolated in-memory test database. ML tests use fixtures to check mathematics and leakage protection, not to claim field performance. Browser tests use the complete local API/worker/database journey. Weather internet checks are separate from deterministic tests.

## Measured-data ML

```powershell
.\.venv\Scripts\python.exe -m ml.pipeline path/to/measured.csv --attribution "Dataset name, license and source URL"
```

See [ML pipeline](docs/ml_pipeline.md) for the exact columns and forecast-availability requirement. The script creates metrics, a comparison plot and a trusted local model artifact. It does not automatically approve a model for field use or replace the operational baselines.

## GitHub continuous integration

The complete GitHub Actions definition is preserved at [docs/ci/github-actions.yml](docs/ci/github-actions.yml). It is provided as an inactive template because the GitHub login used for the initial upload does not have the `workflow` scope. After authorizing workflow access, copy it to `.github/workflows/ci.yml` and commit that change to activate the backend, frontend and end-to-end checks. The application runs normally without activating GitHub Actions.

## Documentation links

[Architecture](docs/architecture.md) · [Setup](docs/setup.md) · [API](docs/api.md) · [Database](docs/database.md) · [ML](docs/ml_pipeline.md) · [Simulation](docs/simulation.md) · [Hardware](docs/hardware_integration.md) · [Calibration](docs/calibration.md) · [Testing](docs/testing.md) · [Deployment](docs/deployment.md) · [Limitations](docs/limitations.md)
