# Limitations and evidence boundaries

- No physical hardware, sensor accuracy, water savings, yield improvement or field predictive performance has been validated.
- No authentic measured dataset is supplied. Operational forecasts are baselines; experimental model training/inference is available as reproducible scripts, not an approved live ML model.
- Simplified water balance omits runoff, effective-rainfall modeling, drainage dynamics, capillary rise and irrigation efficiency. Farmer irrigation history is stored, but future unplanned irrigation is not assumed.
- Plot agronomic defaults and synthetic VWC are illustrative. Calibration and threshold review require physical soil measurements.
- Weather endpoint retrieval time is saved; provider model issue time is not supplied. Historical reanalysis cannot serve as archived forecast evidence.
- Simulation changes are accelerated software scenarios, not a validated physical soil model. Firmware is a transport example, not tested device software.
- Single-operator local access; public user accounts and per-farm authorization are not implemented.
- English/Bengali navigation, headings and key advisories work; administrative/technical forms retain English terms. Full editorial translation is remaining work.
- Current operational ML selection, cross-farm validation, calibrated uncertainty and full model registry remain gated on data and review.
- Original weather payloads and forecast/advisory payloads use JSON records; not every suggested conceptual entity has a dedicated normalized table.
- No automatic irrigation control or volume prescription.
- Default Docker images run the baseline/API runtime. Optional ML-enabled container builds are documented but were not exercised; training, evaluation and experimental artifact inference were tested in the native development environment.
