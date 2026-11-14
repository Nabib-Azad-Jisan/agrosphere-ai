# MASTER DEVELOPMENT PROMPT — ZYNTRIX AGROSPHERE AI

## 1. Your Role

You are a senior full-stack software engineer, AI/ML engineer, IoT systems architect, agricultural technology specialist, and expert UI/UX designer.

Your mission is to build a complete, production-oriented, modular, and visually impressive agricultural intelligence platform named:

**ZYNTRIX — AgroSphere AI**

Brand tagline: **Intelligence Beyond Boundaries**

This is an AI-powered agricultural monitoring, soil-moisture forecasting, and irrigation decision-support platform initially designed for tomato cultivation in Bangladesh, with a long-term goal of supporting other crops and regions.

I want you to IMPLEMENT THE APPLICATION, not merely describe how to build it.

Create actual working source code, database models, API endpoints, frontend pages, ML pipelines, tests, configuration files, developer documentation, and setup instructions.

Work autonomously through implementation stages. Make reasonable engineering decisions, record them, and continue. Do not stop after creating the UI or a project skeleton.

**CRITICAL REQUIREMENT: HARDWARE WILL BE ADDED LATER. THE ENTIRE SOFTWARE MUST WORK WITHOUT HARDWARE FIRST.**

Build the architecture so that simulated data sources can later be replaced or supplemented by real ESP32-based sensors without rewriting the frontend, application services, machine-learning modules, database architecture, or core API.

A real hardware integration must only require sensor setup, calibration, secure device provisioning, configuration, and connection to the already implemented ingestion interface.

Do not claim that physical calibration or field validation is complete before actual hardware is tested.

---

# 2. Project Vision

AgroSphere AI must solve an important agricultural problem:

Farmers often make irrigation decisions without knowing the actual condition of the soil root zone or how that condition might change over the next 24 hours.

Weather conditions, irrigation records, and soil measurements are usually disconnected.

Our platform should combine these sources into one intelligent system.

The application must:

1. Monitor soil moisture conditions.
2. Display weather forecasts.
3. Track soil-moisture trends.
4. Estimate future soil-moisture conditions.
5. Identify potential moisture-deficit and excessive-moisture risk.
6. Explain why a risk warning is generated.
7. Recommend whether the farmer should inspect soil or consider irrigation.
8. Display all information through a modern dashboard.
9. Support Bengali and English.
10. Support simulation now and real IoT hardware later.

The primary modules are:

**RootSense:** Soil monitoring, sensor ingestion, measurement validation, moisture history, and moisture-risk monitoring.

**AquaMind:** Weather-informed forecasting, agronomic calculations, explainable ML, irrigation decision support, and advisory generation.

A possible future module is PestCast, but it must not distract from completing and validating RootSense and AquaMind.

---

# 3. Mandatory Technology Stack

Use the following technologies unless a clear technical incompatibility requires a small change.

## Frontend

- Next.js with App Router
- React
- TypeScript
- Tailwind CSS
- shadcn/ui
- Framer Motion / Motion for React
- Recharts
- Lucide icons
- TanStack Query
- React Hook Form
- Zod

Use current, stable, mutually compatible versions. Follow modern Next.js conventions and avoid deprecated APIs.

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Async-compatible database access where appropriate
- APScheduler or an equivalent reliable scheduling mechanism
- Structured logging

Keep scheduled jobs separate from web-request handling so the architecture can later support independent workers.

## AI and Data Science

- pandas
- NumPy
- scikit-learn
- XGBoost, if useful
- SHAP, if compatible with the selected models
- joblib
- matplotlib for evaluation outputs when appropriate

## External Data

Use Open-Meteo for weather forecasts and historical weather context.

Potential research sources include NASA POWER and suitable openly licensed datasets containing actual soil-moisture measurements.

Weather data must not be misrepresented as directly measured soil moisture.

## Development and Deployment

- Docker and Docker Compose
- Git
- GitHub-compatible repository
- pytest
- Frontend testing framework
- Playwright for end-to-end testing
- Ruff or equivalent Python linting
- ESLint and TypeScript checking
- `.env.example`
- README documentation
- CI checks through GitHub Actions

Do not require paid cloud services for local development.

---

# 4. Required System Architecture

Design the system using this architecture:

```text
                    AGROSPHERE AI

               DATA SOURCE LAYER
                      |
        +-------------+-------------+
        |             |             |
    Simulator     Historical     Future ESP32
    Adapter       Data Adapter   Sensor Adapter
        |             |             |
        +-------------+-------------+
                      |
             UNIFIED INGESTION API
                      |
             Validation & QC Layer
                      |
                PostgreSQL
                      |
           +----------+----------+
           |                     |
       RootSense             AquaMind
       Monitoring            Intelligence
           |                     |
           |              Weather API
           |                     |
           |              ML Forecasting
           |                     |
           |              Advisory Engine
           |                     |
           +----------+----------+
                      |
                 FastAPI
                      |
             Next.js Frontend
                      |
        +-------------+-------------+
        |             |             |
     Dashboard      Alerts       Analytics
```

Very important:

The simulation system and hardware system must use the same canonical ingestion contract and downstream processing pipeline.

There must not be separate, incompatible databases or forecasting logic for simulated versus real data.

Create a source-adapter abstraction supporting:

- `simulator`
- `historical_import`
- `esp32`
- `external_sensor_api`

Store the source of each measurement explicitly.

Implement a configurable data-source mode:

```env
DATA_SOURCE_MODE=simulation
```

Supported modes:

```text
simulation
historical
hardware
hybrid
```

In hardware mode, missing sensor readings must be shown as unavailable. Never secretly substitute simulated readings and display them as real measurements.

Hybrid mode must preserve provenance and make the difference between actual and simulated data visible.

---

# 5. Hardware-Ready Design — Most Important Requirement

I will add physical equipment AFTER the software is finished.

Design for future devices such as:

- ESP32
- Capacitive soil-moisture sensor
- DHT22 or equivalent temperature/humidity sensor
- Optional DS18B20 soil-temperature sensor
- Optional electrical-conductivity sensor

Do not require these devices to run the current project.

Implement the complete sensor-ingestion interface now.

Example JSON payload:

```json
{
  "schema_version": "1.0",
  "device_id": "esp32_station_001",
  "plot_id": "tomato_plot_001",
  "timestamp": "2026-11-13T10:30:00+06:00",
  "source": "esp32",
  "measurements": {
    "soil_moisture_raw": 2180,
    "soil_moisture_vwc": null,
    "soil_temperature_c": 27.8,
    "air_temperature_c": 30.2,
    "air_humidity_percent": 74.5
  },
  "battery_percent": 86,
  "calibration_id": null
}
```

The raw soil-moisture value is an illustrative ADC reading, not a true percentage.

Do not automatically interpret raw ADC values as volumetric soil-water content.

Once the sensors are connected, allow configuration of soil-specific calibration profiles.

Develop:

- Device registration
- Device authentication
- Device-to-plot association
- Measurement validation
- Timestamp validation
- Duplicate-event handling
- Missing-value handling
- Sensor health monitoring
- Calibration profile management
- Ingestion audit logs
- Data-source provenance
- Device last-seen status
- Sensor disconnection warnings

Create:

```text
POST /api/v1/readings
GET  /api/v1/devices
POST /api/v1/devices
GET  /api/v1/devices/{device_id}
GET  /api/v1/devices/{device_id}/health
POST /api/v1/devices/{device_id}/calibrations
```

These routes may be adjusted slightly to follow consistent REST conventions.

Implement authenticated device ingestion and rate limiting. Do not hardcode hardware credentials.

Create a future ESP32 firmware example that sends data through the already implemented API, but do not require compiling or running this firmware for the initial software deliverable.

**Acceptance condition:** Switching from simulated data to real hardware must not require rewriting the dashboard, forecast service, advisory engine, or database schema.

Physical calibration and real-device integration testing will still be required.

---

# 6. RootSense Module

RootSense is the soil intelligence monitoring module.

Build the following features:

### Soil monitoring

- Latest soil-moisture observation
- Historical moisture trend
- Soil temperature
- Air temperature
- Humidity
- Sensor status
- Sensor reading age
- Crop and plot information
- Moisture threshold configuration
- Rainfall and irrigation event history

### Risk detection

Initially support transparent threshold-based monitoring for:

- Low moisture
- Adequate moisture
- Excessive moisture
- Missing or stale sensor data

Thresholds must depend on documented units, calibration, soil context, and crop configuration.

Do not use one arbitrary moisture percentage as a scientifically validated threshold for every farm.

### Data visualization

Create interactive charts for:

- Previous 24 hours
- Previous 7 days
- Previous 30 days
- Custom time ranges

Display the data-source label on charts.

If the readings are simulated, show a visible **Simulation** indicator.

Support empty states, loading states, and sensor errors.

---

# 7. AquaMind AI Module

AquaMind is the core forecasting and irrigation decision-support system.

It must combine:

1. RootSense soil measurements
2. Historical moisture trends
3. Weather observations
4. Weather forecasts
5. Recorded irrigation events
6. Soil and crop information
7. Agronomic calculations

## Forecasting

Primary target:

**Predict soil-moisture conditions approximately 24 hours ahead.**

Use appropriately aligned timestamps and consistent measurement units.

Start with three prediction approaches:

**Baseline A:** Persistence forecast.

**Baseline B:** Simplified soil-water-balance estimation.

**Model C:** Random Forest Regressor or XGBoost Regressor trained using suitable actual historical measurements.

Implement time-aware feature engineering using:

- Lagged soil moisture
- Moisture trend
- Recent rainfall
- Forecast rainfall
- Temperature
- Humidity
- Evapotranspiration
- Irrigation history
- Crop stage, where available

The model must never accidentally use future observed measurements as prediction-time features.

When evaluating historical forecasts, use weather forecasts available at the original forecast-issue time, rather than leaking later weather observations into the model.

### Training and validation

Implement:

- Training pipeline
- Data validation
- Time-based train/validation/test split
- MAE and RMSE calculation
- Comparison against both baselines
- Model versioning
- Model metadata
- Feature importance or SHAP explanations
- Reproducible experiment scripts

Do not fabricate training data and report it as actual field evidence.

If sufficient credible measured soil-moisture data is unavailable, run the baseline system and mark the ML model as **Not validated**.

Allow the application to operate in an honest baseline-only mode.

## Irrigation advisory engine

Use agronomic principles, including:

```text
ETc ≈ Kc × ET0
```

Treat this as one component of a simplified water-balance estimate, not a complete irrigation prescription.

Consider:

- Soil type
- Crop stage
- Rooting depth
- Current moisture
- Expected rainfall
- Evaporative demand
- Model uncertainty
- Sensor reliability

Generate understandable advisories.

Example:

```text
Moisture-deficit risk: HIGH

Reason:
Soil moisture is declining,
little rainfall is forecast,
and evaporative demand is elevated.

Recommendation:
Inspect the root-zone soil and verify sensor
readings before deciding whether irrigation
is needed.
```

Do not automatically control irrigation pumps.

Do not claim guaranteed water savings or yield improvements without field evidence.

---

# 8. Weather Intelligence

Build a complete weather module integrated with Open-Meteo.

Display:

- Current weather
- Hourly temperature
- Humidity
- Rainfall forecast
- Rain probability, where available
- Wind
- Reference evapotranspiration
- 24-hour agricultural weather outlook
- Multi-day forecast

Support plot coordinates and location labels.

For the initial demonstration, use a configurable example farm in the Dhaka/Gazipur region of Bangladesh.

Do not hardcode one location throughout the application.

Weather integration must include:

- API client abstraction
- Caching
- Request timeouts
- Retry logic
- API failure handling
- Forecast issuance timestamps
- Time-zone-aware processing
- Historical weather support

If weather data is outdated, show its last-updated time and reduce advisory confidence where appropriate.

---

# 9. Frontend UI/UX — Premium Green Agricultural Technology Design

This requirement is extremely important.

I want the website to look like a premium, modern, original agricultural intelligence SaaS platform.

It must NOT look like a basic university assignment, generic Bootstrap dashboard, or plain Streamlit prototype.

Develop a visually coherent design system.

## Color palette

Use:

- Deep forest green: `#103D2E`
- Primary green: `#168B5D`
- Emerald accent: `#10B981`
- Fresh lime accent: `#B8E66A`
- Warm off-white: `#F7FAF6`
- Very light mint: `#ECF7F0`
- Dark charcoal: `#172A22`
- Muted text green-gray: `#64776B`

Use restrained amber for warnings and red for serious risk conditions.

Maintain attractive contrast, clear typography, and accessibility.

Use soft gradients, subtle glass effects, refined borders, and carefully controlled shadows.

Do not cover every element with gradients.

## Typography

Use a modern font pairing such as:

- Plus Jakarta Sans or Inter for English
- An appropriate readable Bengali font for Bangla content

Use a consistent typographic scale.

## Visual design direction

The application should feel:

- Fresh
- Intelligent
- Trustworthy
- Futuristic but practical
- Agricultural
- Premium
- Minimal yet feature-rich

Use beautiful charts, status indicators, cards, modern icons, and distinctive data visualizations.

## Animations and transitions

Use Motion for React to implement:

- Smooth route transitions
- Subtle page entrance animations
- Staggered card reveals
- Refined sidebar interactions
- Animated chart entrances
- Hover feedback
- Animated data updates
- Loading skeletons
- Elegant modal transitions
- Smooth notifications

Route transitions should combine subtle fade, vertical movement, and carefully controlled scale when appropriate.

Avoid excessive animations, slow navigation, or distracting effects.

Respect reduced-motion accessibility preferences.

Keep animations performant on average laptops and mobile devices.

## Responsiveness

Implement excellent layouts for:

- Desktop
- Laptop
- Tablet
- Mobile

Use a collapsible sidebar and responsive navigation.

The mobile experience must be genuinely usable, not simply a compressed desktop interface.

## Theme

Build light mode and dark mode.

The default theme should be a beautiful light interface using green, mint, and off-white.

Dark mode should use deep green and charcoal surfaces, not generic pure black everywhere.

---

# 10. Required Pages

Create these fully integrated pages:

### 1. Landing Page

A polished public product landing page.

Include:

- Hero section
- AgroSphere AI identity
- Product value proposition
- Animated visual preview
- RootSense and AquaMind features
- How it works
- Hardware-ready architecture explanation
- Call to action to open the demo dashboard

The landing page must be visually distinctive.

### 2. Main Dashboard

Include:

- Farm overview
- Latest moisture status
- Weather summary
- 24-hour risk outlook
- Recent alerts
- Interactive trend charts
- Source status: Simulation / Historical / Hardware
- Model mode: Baseline / Validated ML
- Last updated timestamp

### 3. RootSense

Detailed monitoring page with historical readings, sensor quality, chart controls, moisture-risk warnings, and measurement provenance.

### 4. AquaMind

AI forecasting dashboard with:

- Forecast chart
- Prediction explanation
- Baseline comparison
- Advisory cards
- Prediction uncertainty or model limitations
- Model version
- Validation status

### 5. Weather Center

Beautiful weather dashboard featuring hourly and multi-day forecasts, agricultural weather variables, and rainfall visualization.

### 6. Farm & Plot Management

Allow creating and editing:

- Farms
- Plots
- Crop information
- Soil characteristics
- Planting dates
- Irrigation records
- Device associations

### 7. Sensor & Device Center

This must work before physical hardware exists.

Display:

- Virtual devices
- Future hardware devices
- Device health
- Connection state
- Calibration profiles
- Data-source switching
- Device provisioning information

Provide a clearly labeled simulation control panel.

### 8. Analytics & Reports

Include:

- Moisture trends
- Historical alerts
- Irrigation records
- Prediction evaluation
- Baseline comparison
- CSV export
- Clearly labeled experimental or simulated metrics

### 9. Notifications

Include risk warnings, weather warnings, missing-data warnings, and notification preferences.

### 10. Settings

Include:

- Language switching
- Theme settings
- Farm settings
- Unit preferences
- Simulation settings
- Account settings, if authentication is implemented

All pages must have functional navigation and meaningful interactions.

Do not create decorative buttons that do nothing.

---

# 11. Simulation Engine

Since real hardware will be added later, build an excellent simulation system.

It should simulate a moisture sensor operating in a tomato plot.

The simulation must be realistic enough to test software behavior but must never be presented as field-validated agricultural evidence.

Implement configurable scenarios:

1. Gradually drying soil
2. Normal moisture variation
3. Rainfall event
4. Irrigation event
5. Persistently wet soil
6. Sensor disconnection
7. Stale sensor readings
8. Invalid sensor readings

Create simulation controls for:

- Start
- Pause
- Reset
- Select scenario
- Set simulation speed
- Select plot

Generate timestamped readings and send them through the same backend ingestion pipeline used for future ESP32 data.

Do not bypass the backend and generate fake charts exclusively inside React components.

For example:

```text
Simulation starts
      ↓
Synthetic moisture data generated
      ↓
POST /api/v1/readings
      ↓
Backend validates reading
      ↓
PostgreSQL stores observation
      ↓
RootSense updates
      ↓
AquaMind evaluates risk
      ↓
Dashboard displays new information
```

Clearly label all synthetic observations and outputs.

If historical real measurements are available, implement a separate replay mechanism with proper attribution and original timestamps.

---

# 12. Example User Journey

Build a complete demonstration around this example.

A tomato farmer has a plot near Gazipur, Bangladesh.

The farmer opens AgroSphere AI.

The dashboard displays:

```text
Farm: Demo Tomato Farm
Location: Gazipur, Bangladesh
Crop: Tomato
Data source: Simulation

Current moisture condition:
Declining

Weather:
Warm conditions and low forecast rainfall

RootSense:
Moisture trend indicates increasing dryness

AquaMind:
Potential moisture deficit in the next 24 hours

Recommendation:
Inspect the root zone and check irrigation needs.
```

Then simulate an irrigation event.

Show how the moisture observations change, how the baseline or forecast is recalculated, and how the dashboard updates.

The farmer should understand the situation without reading technical ML terminology.

Provide both English and Bengali versions of the key advisory messages.

This should become the main end-to-end competition demonstration.

---

# 13. Database Design

Create normalized database models and migrations.

Suggested tables:

```text
users
farms
plots
crops
devices
device_calibrations
sensor_readings
weather_observations
weather_forecasts
irrigation_events
forecast_runs
predictions
risk_assessments
advisories
notifications
simulation_sessions
model_versions
evaluation_results
audit_logs
```

Use proper foreign keys, indexes, timestamps, and constraints.

Sensor readings should preserve:

- Original measurement
- Measurement units
- Calibrated value, if available
- Calibration reference
- Device ID
- Plot ID
- Timestamp
- Data source
- Quality flags

Never overwrite an original raw measurement when applying a new calibration.

Support database migrations from the beginning.

Provide useful seed data for demo mode.

---

# 14. Backend API

Implement a versioned REST API.

Suggested endpoints:

```text
GET  /api/v1/health

GET  /api/v1/farms
POST /api/v1/farms

GET  /api/v1/plots
POST /api/v1/plots

GET  /api/v1/plots/{id}/status
GET  /api/v1/plots/{id}/readings
GET  /api/v1/plots/{id}/forecast
GET  /api/v1/plots/{id}/advisories

POST /api/v1/readings

GET  /api/v1/weather/current
GET  /api/v1/weather/forecast

GET  /api/v1/devices
POST /api/v1/devices

POST /api/v1/simulation/start
POST /api/v1/simulation/pause
POST /api/v1/simulation/reset
GET  /api/v1/simulation/status

GET  /api/v1/models
GET  /api/v1/models/evaluations

GET  /api/v1/notifications
```

Add other endpoints as required.

Use:

- Pydantic request/response validation
- Consistent error formats
- OpenAPI documentation
- Pagination where appropriate
- Authentication and authorization for protected actions
- CORS configuration
- Device authentication
- Database transactions
- Structured logs

Avoid exposing internal secrets or tracebacks to the frontend.

---

# 15. Recommended Repository Structure

Use a monorepo:

```text
agrosphere-ai/
|
|-- frontend/
|   |-- app/
|   |-- components/
|   |-- features/
|   |-- hooks/
|   |-- lib/
|   |-- styles/
|   |-- public/
|   |-- tests/
|
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- models/
|   |   |-- schemas/
|   |   |-- services/
|   |   |-- repositories/
|   |   |-- adapters/
|   |   |   |-- simulator/
|   |   |   |-- historical/
|   |   |   |-- hardware/
|   |   |-- rootsense/
|   |   |-- aquamind/
|   |   |-- weather/
|   |   |-- notifications/
|   |-- alembic/
|   |-- tests/
|
|-- ml/
|   |-- datasets/
|   |-- features/
|   |-- training/
|   |-- evaluation/
|   |-- inference/
|   |-- artifacts/
|   |-- tests/
|
|-- firmware/
|   |-- esp32_example/
|
|-- contracts/
|   |-- schemas/
|
|-- scripts/
|-- docs/
|-- docker-compose.yml
|-- .env.example
|-- README.md
```

You may refine the structure, but maintain clean separation between the data-source adapters, business logic, and presentation layer.

---

# 16. Security and Reliability

Implement responsible software practices.

Requirements:

- No hardcoded API keys or passwords
- Environment-based configuration
- Secure demo authentication or documented local-only demo mode
- Protected ingestion endpoints
- Input validation
- Request-size limits
- Rate limiting
- Safe error handling
- Database backup guidance
- Health checks
- Container restart policies
- Configurable API timeouts
- Retry and failure recovery
- Source and timestamp verification
- Basic audit logging

The application should handle temporary database or weather API outages without crashing the entire frontend.

Do not expose an unauthenticated sensor-ingestion endpoint to the public internet.

---

# 17. Testing Requirements

Create actual automated tests.

## Backend

Use pytest for:

- Sensor ingestion
- Validation failures
- Duplicate readings
- Missing observations
- Calibration handling
- Weather API failures
- Device authentication
- Forecast API responses
- Advisory rules

## Frontend

Test:

- Dashboard rendering
- Page navigation
- Simulation controls
- Form validation
- Language switching
- Error states
- Loading states
- Responsive layouts

## Machine Learning

Test:

- Feature engineering
- Time-series splitting
- Prediction input schemas
- Model artifact loading
- Baseline comparisons
- No future-data leakage
- Insufficient-data behavior

## End-to-end

Use Playwright to test the full journey:

```text
Launch application
    ↓
Create demo farm
    ↓
Start simulation
    ↓
Observe readings
    ↓
Display RootSense status
    ↓
Run AquaMind estimation
    ↓
Display advisory
    ↓
Open analytics
    ↓
Review results
```

Mock external APIs for deterministic automated tests.

Document tests requiring internet access separately.

---

# 18. Development Order

Implement in this sequence.

## Milestone 1 — Foundation

- Create monorepo
- Configure frontend
- Configure backend
- Configure PostgreSQL
- Configure Docker Compose
- Add environment configuration
- Create database migrations
- Create shared API contracts
- Confirm frontend/backend communication

## Milestone 2 — Backend and Simulation

- Build farms and plots
- Build sensor-ingestion API
- Build sensor-adapter interfaces
- Build simulator
- Store and retrieve measurements
- Implement device health monitoring
- Confirm simulation-to-database flow

## Milestone 3 — Weather and RootSense

- Integrate Open-Meteo
- Implement RootSense monitoring
- Add quality checks
- Add threshold alerts
- Add historical chart APIs
- Handle missing and stale data

## Milestone 4 — AquaMind

- Implement persistence baseline
- Implement water-balance baseline
- Build ML training pipeline
- Add validated ML inference when appropriate
- Implement forecast explanations
- Implement advisory rules
- Add model evaluation reports

## Milestone 5 — Premium Frontend

- Create design system
- Build landing page
- Build sidebar and navigation
- Implement all application pages
- Connect pages to actual backend endpoints
- Add charts and interactions
- Add polished animations and transitions
- Implement Bengali and English support
- Implement responsive design

## Milestone 6 — Full Integration

- Connect simulation with dashboard
- Connect RootSense and AquaMind
- Add notifications
- Add analytics
- Fix integration bugs
- Test edge cases

## Milestone 7 — Hardware Readiness

- Finalize ingestion payload
- Finalize device provisioning
- Implement calibration storage
- Add hardware-mode configuration
- Create ESP32 integration example
- Document wiring and configuration assumptions
- Add mock ESP32 integration tests

Do not claim actual hardware validation has passed.

## Milestone 8 — Final Quality Assurance

- Run backend tests
- Run frontend tests
- Run ML tests
- Run end-to-end tests
- Check build output
- Check type errors
- Check linting
- Fix discovered issues
- Prepare deployment documentation

---

# 19. Required Documentation

Create:

```text
README.md
docs/architecture.md
docs/setup.md
docs/api.md
docs/database.md
docs/ml_pipeline.md
docs/simulation.md
docs/hardware_integration.md
docs/calibration.md
docs/testing.md
docs/deployment.md
docs/limitations.md
```

The README must include exact commands to:

1. Install dependencies.
2. Configure environment variables.
3. Start PostgreSQL.
4. Run migrations.
5. Start FastAPI.
6. Start Next.js.
7. Start the simulator.
8. Open the dashboard.
9. Run tests.
10. Stop the application.

Provide a one-command Docker Compose development option if feasible.

Hardware documentation must explain how a future ESP32 device can be registered, authenticated, calibrated, and connected without changing existing application logic.

---

# 20. Definition of Done

The project is complete for the software-first phase only when:

- The complete application runs locally.
- The frontend communicates with FastAPI.
- PostgreSQL stores persistent application data.
- The simulator generates readings through the official ingestion API.
- RootSense displays and analyzes measurements.
- Weather forecasts are available with appropriate fallback behavior.
- AquaMind provides working baseline forecasting.
- ML inference is implemented and clearly labeled according to validation status.
- The advisory engine generates understandable explanations.
- All required frontend pages exist and are functional.
- Page transitions and animations work smoothly.
- English/Bengali switching works.
- Light/dark themes work.
- Charts are connected to backend data.
- Device configuration and calibration interfaces exist.
- A future ESP32 device can use the documented ingestion contract.
- Automated tests cover the important workflows.
- The application builds without unresolved type or import errors.
- The README includes reproducible setup instructions.

Do not fabricate test results.

If a requirement cannot be completed in the current environment, identify exactly what is blocked, what has been implemented, and the remaining work.

---

# 21. Important Design and Engineering Rules

1. Do not create only a visual mockup.
2. Do not create frontend pages with permanently hardcoded agricultural metrics.
3. All monitoring data must have a known source.
4. Simulation must be clearly distinguished from actual readings.
5. Never describe an unvalidated ML model as accurate.
6. Never invent field performance or water savings.
7. Use reusable React components.
8. Keep backend modules loosely coupled.
9. Use TypeScript strictly.
10. Avoid unnecessary dependencies.
11. Handle errors gracefully.
12. Follow accessibility best practices.
13. Prioritize performance.
14. Do not implement automatic pump control.
15. Make future hardware integration straightforward.
16. Maintain clean and readable code.
17. Use meaningful names and comments.
18. Avoid unnecessary complexity and overengineering.
19. Keep the application usable without external hardware.
20. Prioritize a genuinely working end-to-end system over decorative features.

---

# 22. How You Should Work in Codex

First inspect the existing repository.

If it is empty, initialize the project.

If existing code is present, preserve working functionality and integrate new components carefully.

Create an implementation checklist and maintain progress as you work.

Before coding, briefly state:

- Your chosen architecture
- The initial implementation sequence
- Any important assumptions

Then start implementing immediately.

Do not stop after the plan.

After completing each milestone:

- Run available checks.
- Fix errors.
- Update documentation.
- Record completed work.
- Proceed to the next milestone.

Avoid asking unnecessary questions. Use the requirements in this prompt as your primary specification.

Do not create fake implementations or placeholder integrations and describe them as finished.

Use mock adapters only where they are explicitly intended for simulation or testing.

If tool limits prevent completing everything in one session, leave the repository in a working state and provide a precise continuation checklist so the next session can resume.

---

# 23. Final User Experience

The finished experience should look like this:

A user visits the AgroSphere AI website and sees an attractive, professional green-themed landing page with elegant animation.

They open the dashboard.

The dashboard shows a modern farm overview with interactive cards and live simulation data.

They navigate to RootSense using a smooth animated transition and inspect soil-moisture trends.

They navigate to AquaMind and review a weather-informed forecast, its source, supporting evidence, and an irrigation advisory.

They navigate to Weather Center and see the forecast for their selected farm.

They visit Sensor Center, where they can inspect simulated devices and see the future ESP32 integration interface.

They can switch between Bengali and English.

They can switch between light and dark themes.

Everything is responsive, coherent, functional, and visually polished.

Later, when real ESP32 sensors are physically connected, calibrated, and provisioned, the application receives actual field measurements through the existing ingestion API.

The frontend, monitoring system, forecasting services, and core business logic remain unchanged.

---

# FINAL INSTRUCTION

Build **ZYNTRIX AgroSphere AI** as a complete, modern, elegant, software-first, hardware-ready agricultural intelligence platform.

Focus on:

**Functional software + clean architecture + validated intelligence + premium green UI + smooth transitions + future ESP32 compatibility.**

Start with the working foundation, implement the full system incrementally, verify each major milestone, and continue until the software-first definition of done is satisfied.

**Begin implementation now.**
