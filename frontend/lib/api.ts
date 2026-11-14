export async function api<T>(
  path: string,
  body?: unknown,
  method?: string,
): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    method: method || (body ? "POST" : "GET"),
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      error.error?.message || `Request failed (${response.status})`,
    );
  }
  return response.json();
}
export type Plot = {
  id: string;
  farm_id: string;
  name: string;
  crop: string;
  crop_stage: string;
  soil_type: string;
  planting_date: string | null;
  rooting_depth_m: number;
  kc: number;
  low_vwc: number;
  high_vwc: number;
  field_capacity_vwc: number;
  thresholds_verified: boolean;
  threshold_notes: string;
};
export type Farm = {
  id: string;
  name: string;
  location: string;
  latitude: number;
  longitude: number;
};
export type Reading = {
  id: string;
  timestamp: string;
  moisture_vwc: number | null;
  source: string;
  provenance: string;
  device_id: string;
  quality_flags: string[];
  measurements: {
    soil_temperature_c: number | null;
    air_temperature_c: number | null;
    air_humidity_percent: number | null;
  };
};
export type Status = {
  plot: Plot;
  reading: Reading | null;
  status: string;
  age_minutes: number | null;
  trend_per_hour: number | null;
  data_source_mode: string;
  thresholds_verified: boolean;
};
export type Forecast = {
  issued_at: string;
  predicted_vwc: number | null;
  persistence_vwc: number | null;
  water_balance_vwc: number | null;
  risk_level: string;
  method: string;
  model_version: string;
  validation_status: string;
  data_source: string;
  reasons: string[];
  limitations: string[];
  advice: { en: string; bn: string };
};
export type Device = {
  id: string;
  plot_id: string;
  name: string;
  source: string;
  last_seen: string | null;
  active: boolean;
};
export type Simulation = {
  plot_id: string;
  running: boolean;
  scenario: string;
  speed: number;
  step: number;
  last_error: string | null;
  last_tick: string | null;
};
export type Notice = {
  id: string;
  kind: string;
  message: string;
  read: boolean;
  created_at: string;
};
export type Weather = {
  available: boolean;
  usable: boolean;
  age_minutes: number | null;
  request_status: string;
  data: {
    current: {
      temperature_2m: number;
      relative_humidity_2m: number;
      precipitation: number;
      wind_speed_10m: number;
    };
    hourly: {
      time: string[];
      temperature_2m: number[];
      relative_humidity_2m: number[];
      precipitation: number[];
      precipitation_probability: number[];
      wind_speed_10m: number[];
      et0_fao_evapotranspiration: number[];
    };
    daily: {
      time: string[];
      temperature_2m_max: number[];
      temperature_2m_min: number[];
      precipitation_sum: number[];
      et0_fao_evapotranspiration: number[];
    };
  } | null;
};
export function displayDate(value: string | null | undefined) {
  return value
    ? new Date(value).toLocaleString("en-GB", {
        timeZone: "Asia/Dhaka",
        day: "numeric",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";
}
export function moisture(value: number | null | undefined) {
  return value == null ? "—" : `${(value * 100).toFixed(1)}%`;
}
