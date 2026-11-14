# Architecture

Next.js App Router → server-only local gateway → FastAPI → SQLAlchemy → PostgreSQL. A separate APScheduler worker owns simulation and notification checks. Do not run more than one simulation worker without adding distributed locking. FastAPI uses synchronous DB sessions in threadpool routes.

SourceAdapter supports SimulatorAdapter, HistoricalAdapter, HardwareAdapter (ESP32/external API). Every source produces schema 1.0 and calls POST /api/v1/readings. Units and provenance persist in the same schema. No React-generated agricultural observations.

RootSense selects eligible sources for DATA_SOURCE_MODE, checks observation age/calibration, and computes same-device trends. AquaMind uses valid VWC with persistence and, when usable weather exists, a simplified root-zone bucket. Data quality limits advisory claims. Weather retrieval time and model issuance are distinguished.

The green design system uses reusable cards, controls, responsive navigation, device/source badges, Recharts, reduced-motion-aware Motion transitions and light/dark palettes. Local browser preferences persist independently from farm records.

Sources used for framework setup: https://nextjs.org/docs/app/getting-started/installation and https://fastapi.tiangolo.com/tutorial/sql-databases/ . User master prompt controls requirements.
