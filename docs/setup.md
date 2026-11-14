# Setup

Use the exact commands in ../README.md. Start Docker Desktop before docker compose. Run scripts/configure_local.py to create .env if missing and generate only empty secrets. Preserve existing .env credentials when reusing a PostgreSQL volume. No paid services or hardware are required.

Native commands run from the monorepo root so .env, migrations and model paths resolve consistently. Frontend commands run from frontend/. Node 24 and Python 3.12 are the development runtimes. package-lock.json pins the frontend dependency graph. backend/requirements-lock.txt records the verified backend environment when generated.

Ports: frontend 3000, API 8000, PostgreSQL 5432. Native development defaults to SQLite only as an optional convenience; Docker uses PostgreSQL. Seed is idempotent and creates only a farm and plot, not fake live observations. Select a scenario and start the worker to receive labeled synthetic data.

If Windows application control rejects a compiled Python extension, use a compatible approved installation or the Docker environment. Do not disable system security policies.
