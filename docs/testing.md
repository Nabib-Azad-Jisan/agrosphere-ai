# Testing and verification

Root: python -m pytest -q; python -m ruff check backend ml scripts. Frontend: npm run lint; npm run typecheck; npm test; npm run build. See README for venv commands.

Backend tests use isolated memory databases and mocked weather. Coverage includes authenticated ingestion, replay rejection, ranges/NaN/empty data, timezone/future timestamps, source spoofing, calibration ownership/derivation/raw retention, unavailable/stale data, hardware-mode exclusion, weather failure, persistence forecasts, source labels, simulation control/reset, CSV export and rate limiting.

ML fixtures test exact horizon alignment, missing hours, provenance gates, future-weather leakage, purged partitions, insufficient data, inference schemas and baseline consistency. Fixture results are software verification only.

Vitest checks language/theme persistence, missing-value formatting and error propagation. Playwright uses running API + worker + seeded DB + Next.js and tests desktop/mobile landing → simulation → persisted reading → RootSense → AquaMind → preferences. Install Chromium with npx playwright install chromium. Run npm run test:e2e. External weather is not required for valid persistence fallback; network-dependent provider smoke tests must be reported separately.

See IMPLEMENTATION.md for actual commands run and remaining verification limitations. A test existing in source does not mean it passed. Docker/PostgreSQL verification requires a running engine. Physical ESP32 validation is outside software tests.

Optional live provider check: `python -m scripts.weather_smoke`. To persist the actual provider response in the local PostgreSQL demo, use `python -m scripts.weather_smoke --cache-demo --postgres`. These commands require internet access; their results are separate from mocked weather unit tests. On Windows with Edge already installed, set `$env:PLAYWRIGHT_CHANNEL='msedge'` before `npm run test:e2e` to use Edge instead of downloading Chromium.
