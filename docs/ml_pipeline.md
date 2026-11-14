# ML pipeline and evidence

Operational mode is baseline-only until credible measured data and review exist. No measured dataset is bundled. Persistence predicts the latest valid VWC. Water balance uses VWC + (rain - Kc × ET0)/(root depth × 1000), bounded to [0, field capacity]. This is a simplified bucket, not an irrigation volume prescription.

CSV columns: timestamp, moisture_vwc (m³/m³), provenance (historical_observed/live_sensor), forecast_available_at, forecast_rain_mm, forecast_et0_mm (next 24h issued by prediction time), temperature_c, humidity_pct, recent_irrigation_mm, kc, rooting_depth_m, field_capacity_vwc. Optional device_id must contain exactly one sensor series. Values are measured/authenticated by dataset supplier; this is not independently certified by software.

Lag 1h/6h/24h values and the +24h target are joined by exact timestamps, not row offsets. Missing hours invalidate dependent rows. Weather available after prediction time is rejected. Synthetic rows are rejected. A 60/20/20 chronological split removes training/validation examples whose targets overlap the following partition. At least 240 aligned rows and 20 rows per purged partition are required; this minimum does not establish scientific sufficiency.

Random Forest depth selection uses validation MAE; the untouched test period compares ML, persistence and water balance by MAE/RMSE. Fixed random seed, SHA256 dataset fingerprint, attribution, time ranges, feature importance and model schema are saved. `python -m ml.pipeline measured.csv --attribution "..."` outputs ml/artifacts/model.joblib, evaluation.json and evaluation.png. `ml.pipeline.load_artifact` and `predict` provide validated experimental inference; only load artifacts you trust because joblib uses pickle.

No automatic field approval or confidence interval is generated. Serving baseline estimates remains deliberate until a reviewed model, compatible features and field calibration are available. Reanalysis is historical context, never silently substituted for historical forecast inputs. Future work: cross-farm evaluation, independent dataset provenance review, quantile calibration, model registry and explicit approval workflow.

Model versions use a training-pipeline version plus dataset fingerprint and are retained under ml/artifacts/{model_version}/. The current artifact alias remains ml/artifacts/model.joblib. Authenticated POST /api/v1/models/predict accepts the exact finite feature vector and returns an explicitly experimental prediction; missing artifacts return 409 and do not change operational baseline mode.
