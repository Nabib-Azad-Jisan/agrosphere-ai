// Illustrative HTTPS transport; install ESP32 Arduino core. Not hardware validated.
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <time.h>
#include "secrets.h" // Copy secrets.example.h locally; never commit real credentials.

void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED || time(nullptr) < 1700000000) { delay(5000); return; }
  // Pin selection depends on your ESP32 variant and wiring. ADC is NOT VWC.
  int raw = analogRead(MOISTURE_PIN);
  time_t now = time(nullptr);
  char timestamp[30];
  strftime(timestamp, sizeof(timestamp), "%Y-%m-%dT%H:%M:%SZ", gmtime(&now));
  String payload = "{\"schema_version\":\"1.0\",\"device_id\":\"" + String(DEVICE_ID) +
    "\",\"plot_id\":\"" + String(PLOT_ID) + "\",\"timestamp\":\"" + timestamp +
    "\",\"source\":\"esp32\",\"measurements\":{\"soil_moisture_raw\":" + String(raw) +
    ",\"soil_moisture_vwc\":null},\"calibration_id\":null}";
  WiFiClientSecure tls;
  tls.setCACert(ROOT_CA); // Provision a valid certificate; never use setInsecure().
  HTTPClient http;
  http.begin(tls, INGEST_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Token", DEVICE_TOKEN);
  int status = http.POST(payload);
  Serial.printf("Ingestion HTTP %d\n", status);
  // Production firmware must buffer payloads in persistent flash and retry with the original timestamp.
  // A 409 duplicate response indicates the original event has already been stored.
  http.end();
  delay(15 * 60 * 1000);
}
