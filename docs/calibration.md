# Calibration

Raw ADC is not a percentage. Without a calibration profile, raw-only readings produce moisture_unavailable, and AquaMind does not invent VWC. VWC measurements without verified calibration are flagged and require review for actual sensors.

The current two-point linear mapping is vwc_dry + (raw - raw_dry)/(raw_wet - raw_dry) × (vwc_wet - vwc_dry). Endpoints must be distinct and measured VWC must increase. ADC direction can be reversed. Preserve soil type, procedure/evidence notes and immutable profile ID. Out-of-endpoint-range inputs are flagged as extrapolation; VWC outside [0,1] is rejected. Reported VWC inconsistent with derived VWC is rejected.

The UI saves profiles as unverified. Verification through an authenticated API requires human evidence review; software does not perform a physical calibration. Configure plot thresholds, rooting depth, field capacity and Kc for the actual crop stage/soil. Defaults are illustrative simulation parameters. Revisit parameters and calibration after sensor replacement or soil changes.
