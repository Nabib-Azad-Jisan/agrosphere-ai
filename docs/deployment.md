# Deployment

Docker Compose is local-only and binds ports to 127.0.0.1. Generate non-empty ADMIN_TOKEN and POSTGRES_PASSWORD before startup. The API runs without local-demo bypass in Docker; Next.js passes the administrator token server-side for this local single-operator application. Do not publish this gateway as a multi-user service.

Before public hosting: add user authentication and per-farm authorization to both gateway and API, terminate HTTPS, configure exact CORS origins, centralize rate limiting, define token rotation/revocation, add a backup/restore schedule, limit retention, and review farmer consent/export/deletion needs. Model artifact loading must be restricted to trusted artifacts. Do not expose .env or raw DB ports.

Use one scheduler worker; API can scale only after shared rate limiting and coordinated jobs exist. Restart policies and healthchecks are configured. Temporary provider failure falls back to recent cached weather or persistence-only advice; database failure returns a generic 503 instead of internal tracebacks.

Default Docker images contain the operational API/baseline runtime, excluding training and test packages. The native development requirements include the complete ML toolchain. To enable experimental artifact inference or training in a container, build with `docker compose build --build-arg INSTALL_ML=true api worker migrate`. This downloads the scientific libraries and does not approve a model for field use. Without an artifact/runtime, the inference route returns an explicit 409; operational baselines continue normally.

Back up with pg_dump, test restoring, and run Alembic upgrades as a single release job before starting new API instances. Preserve the postgres_data volume across container replacement. No cloud account is needed for local development.
