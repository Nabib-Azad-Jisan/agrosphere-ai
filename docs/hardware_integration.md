# Future ESP32 integration

1. Create a farm and plot with actual coordinates and soil context.
2. Register an esp32 device in Sensor center. Copy its token once into a secure device configuration; hashes are stored server-side.
3. Collect soil-specific calibration measurements; append a calibration profile through the UI/API. Document soil, probe depth, procedure and physical reference evidence. An unverified profile does not establish sensor accuracy.
4. Configure DATA_SOURCE_MODE=hardware (or hybrid during a labeled transition), restart API/worker. Hardware mode shows missing data as unavailable and excludes simulator observations from monitoring/forecast history.
5. Send schema 1.0 to POST /api/v1/readings over HTTPS with X-Device-Token. Use registered device_id/plot_id/source, timezone-aware timestamps, nullable missing measurements and calibration_id where appropriate.
6. Confirm status, device health and forecast behavior using the same dashboard. No frontend or DB rewrite is needed. Verify independently in the field.

firmware/esp32_example contains illustrative Arduino transport. Copy secrets.example.h to ignored secrets.h; set Wi-Fi, HTTPS endpoint, CA, provisioned token and board-specific ADC pin. Do not use insecure TLS. The example sends raw ADC only until calibration exists. Temperature/humidity sensor wiring and libraries depend on the chosen board; DHT22/DS18B20 integration remains physical work.

Production firmware still needs persistent offline buffering, bounded retries with backoff, reconnect handling and token rotation. Preserve original timestamps on retry; 409 indicates a duplicate, not a new observation. This example has not been compiled or tested on physical hardware and is not production firmware.
