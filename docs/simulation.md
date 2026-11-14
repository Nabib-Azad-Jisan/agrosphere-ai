# Simulation

Run python -m backend.app.worker separately from uvicorn. The worker reads persisted simulation_sessions and POSTs canonical readings over HTTP with a per-device token. The web API validates, records audits and commits observations. One worker owns virtual devices and rotates their internal tokens in memory.

Scenarios: drying (decreasing VWC), normal (periodic variation), rainfall and irrigation (increasing VWC), wet (persistent high VWC), disconnected (no readings), stale (two-hour-old observations), invalid (out-of-range payload rejected). Rain/irrigation scenarios are synthetic moisture responses, not real weather or farmer irrigation records. Speed changes generation interval: 15 seconds / speed, minimum one second. Timestamps remain actual wall-clock times, not fabricated future measurements.

Start applies scenario/speed to the selected plot. Pause stops generation. Reset pauses, clears step counters, and deletes only synthetic observations and their associated forecast runs. Historical and hardware observations remain intact. To demonstrate disconnection after live simulation, wait for the configured stale window or set STALE_MINUTES appropriately for a test.

The simulation is for software behavior testing, not physical accuracy. Its moisture changes and trends may be much faster than a real soil profile. UI always retains Simulation/synthetic labels. Original historical timestamps can be imported using scripts/import_history.py with a registered historical device, DEVICE_TOKEN environment variable and explicit --license attribution. DATA_SOURCE_MODE must allow the source.
