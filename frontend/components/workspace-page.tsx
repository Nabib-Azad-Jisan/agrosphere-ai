"use client";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Link from "next/link";
import { motion } from "motion/react";
import {
  Sprout,
  Droplets,
  CloudSun,
  ArrowUpRight,
  BrainCircuit,
  Radio,
  RefreshCw,
  Download,
  Play,
  Pause,
  RotateCcw,
  Plus,
  Check,
  AlertTriangle,
  Wind,
  Thermometer,
  Waves,
  Activity,
  Leaf,
  SlidersHorizontal,
} from "lucide-react";
import {
  api,
  type Plot,
  type Farm,
  type Status,
  type Forecast,
  type Reading,
  type Device,
  type Simulation,
  type Notice,
  type Weather,
  moisture,
  displayDate,
} from "@/lib/api";
import { useApp } from "./providers";
import { Button } from "./ui/button";
import { MoistureChart } from "./chart";

const titles: Record<string, [string, string, string, string]> = {
  dashboard: [
    "Your farm, in focus.",
    "আপনার খামারের সারসংক্ষেপ।",
    "A clearer picture of your soil. A more thoughtful way to grow.",
    "মাটির তথ্য বুঝুন। যত্ন নিয়ে চাষ করুন।",
  ],
  rootsense: [
    "Listen to your soil.",
    "মাটির অবস্থা জানুন।",
    "Root-zone observations, quality checks, and every change that matters.",
    "মাটির পাঠ, গুণমান ও গুরুত্বপূর্ণ পরিবর্তন।",
  ],
  aquamind: [
    "A little foresight. Better decisions.",
    "আগাম তথ্য, ভালো সিদ্ধান্ত।",
    "A transparent 24-hour outlook, with the evidence behind every advisory.",
    "প্রতিটি পরামর্শের কারণসহ ২৪ ঘণ্টার পূর্বাভাস।",
  ],
  weather: [
    "Weather, with growing in mind.",
    "চাষের জন্য আবহাওয়ার তথ্য।",
    "Your agricultural outlook, from the next hour to the week ahead.",
    "আগামী ঘণ্টা থেকে পুরো সপ্তাহের কৃষি আবহাওয়া।",
  ],
  farms: [
    "Room to grow.",
    "চাষের জায়গা।",
    "Manage farms, plots, soil context, and recorded irrigation.",
    "খামার, জমি, মাটি ও সেচের তথ্য পরিচালনা করুন।",
  ],
  devices: [
    "Connected from the ground up.",
    "মাটি থেকে সংযুক্ত।",
    "Virtual stations today. Calibrated field sensors when you are ready.",
    "আজ ভার্চুয়াল সেন্সর। পরে ক্যালিব্রেট করা মাঠের সেন্সর।",
  ],
  analytics: [
    "Turn observations into understanding.",
    "পর্যবেক্ষণ থেকে বোঝাপড়া।",
    "Explore your records. Keep experimental results in perspective.",
    "তথ্য দেখুন। পরীক্ষামূলক ফলাফলের সীমাবদ্ধতা বুঝুন।",
  ],
  notifications: [
    "Stay a step ahead.",
    "আগেই সতর্ক থাকুন।",
    "Soil, sensor, and weather updates that deserve your attention.",
    "মাটি, সেন্সর ও আবহাওয়ার গুরুত্বপূর্ণ খবর।",
  ],
  settings: [
    "Make it your own.",
    "নিজের মতো সাজান।",
    "A workspace that works the way you do.",
    "আপনার পছন্দের কর্মক্ষেত্র।",
  ],
};
function Badge({
  children,
  tone = "green",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return (
    <span className={`badge ${tone}`}>
      <i />
      {children}
    </span>
  );
}
function ErrorBox({ message }: { message: string }) {
  return (
    <div role="alert" className="error-box">
      <AlertTriangle size={18} />
      <div>
        <strong>Unable to load this information</strong>
        <p>{message}. Check that the API and database are running.</p>
      </div>
    </div>
  );
}
function Panel({
  title,
  eyebrow,
  children,
  action,
  className = "",
}: {
  title: string;
  eyebrow?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <section className={`panel ${className}`}>
      <div className="panel-heading">
        <div>
          {eyebrow && <span className="eyebrow">{eyebrow}</span>}
          <h2>{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
function Stat({
  label,
  value,
  detail,
  icon: Icon,
  tone = "green",
}: {
  label: string;
  value: string;
  detail: string;
  icon: typeof Droplets;
  tone?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`stat-card ${tone}`}
    >
      <div className="stat-top">
        <span>{label}</span>
        <span className="stat-icon">
          <Icon size={19} />
        </span>
      </div>
      <strong className="stat-value">{value}</strong>
      <span className="stat-detail">{detail}</span>
    </motion.div>
  );
}

export function WorkspacePage({ section }: { section: string }) {
  const { t, plotId, language, theme, update, notifications } = useApp();
  const client = useQueryClient();
  const [message, setMessage] = useState("");
  const [days, setDays] = useState("1");
  const [now] = useState(() => new Date().getTime());
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const plots = useQuery({
    queryKey: ["plots"],
    queryFn: () => api<Plot[]>("/plots"),
  });
  const farms = useQuery({
    queryKey: ["farms"],
    queryFn: () => api<Farm[]>("/farms"),
  });
  const status = useQuery({
    queryKey: ["status", plotId],
    queryFn: () => api<Status>(`/plots/${plotId}/status`),
    enabled: !!plotId,
  });
  const forecast = useQuery({
    queryKey: ["forecast", plotId],
    queryFn: () => api<Forecast>(`/plots/${plotId}/forecast`),
    enabled: !!plotId && ["dashboard", "aquamind"].includes(section),
    refetchInterval: 30000,
  });
  const start =
    days === "custom"
      ? customStart
        ? new Date(customStart).toISOString()
        : ""
      : new Date(now - Number(days) * 86400000).toISOString();
  const end =
    days === "custom" && customEnd ? new Date(customEnd).toISOString() : "";
  const history = useQuery({
    queryKey: ["readings", plotId, days, customStart, customEnd],
    queryFn: () =>
      api<{ items: Reading[] }>(
        `/plots/${plotId}/readings?limit=5000${start ? `&start=${encodeURIComponent(start)}` : ""}${end ? `&end=${encodeURIComponent(end)}` : ""}`,
      ),
    enabled:
      !!plotId && ["dashboard", "rootsense", "analytics"].includes(section),
  });
  const weather = useQuery({
    queryKey: ["weather", plotId],
    queryFn: () => api<Weather>(`/weather/forecast?plot_id=${plotId}`),
    enabled: !!plotId && ["dashboard", "weather"].includes(section),
    refetchInterval: 300000,
  });
  const notices = useQuery({
    queryKey: ["notifications", plotId],
    queryFn: () => api<Notice[]>(`/notifications?plot_id=${plotId}`),
    enabled: ["dashboard", "notifications"].includes(section),
  });
  const devices = useQuery({
    queryKey: ["devices"],
    queryFn: () => api<Device[]>("/devices"),
    enabled: section === "devices",
  });
  const plot = plots.data?.find((p) => p.id === plotId);
  const farm = farms.data?.find((f) => f.id === plot?.farm_id);
  const reading = status.data?.reading;
  const f = forecast.data;
  const refresh = () => client.invalidateQueries();
  const action = useMutation({
    mutationFn: ({
      path,
      body,
      method,
    }: {
      path: string;
      body?: unknown;
      method?: string;
    }) => api(path, body, method),
    onSuccess: () => {
      setMessage(t("Saved successfully.", "সফলভাবে সংরক্ষিত।"));
      refresh();
    },
    onError: (e) => setMessage(e.message),
  });
  const [en, bn, sub, subbn] = titles[section];
  const chart = (
    <>
      <div className="chart-caption">
        <Badge tone={reading?.provenance === "synthetic" ? "amber" : "green"}>
          {reading?.provenance === "synthetic"
            ? "Simulation"
            : reading?.provenance || "No data"}
        </Badge>
        <span>VWC · m³/m³ displayed as % · Asia/Dhaka</span>
      </div>
      <MoistureChart
        readings={history.data?.items || []}
        low={plot?.low_vwc}
        high={plot?.high_vwc}
      />
      <div className="chart-foot">
        <span>
          <i className="legend-dot amber" />
          {t("Low threshold", "নিম্ন সীমা")}
        </span>
        <span>
          <i className="legend-dot blue" />
          {t("High threshold", "উচ্চ সীমা")}
        </span>
        <span>
          {plot?.thresholds_verified
            ? t("Field thresholds documented", "মাঠের সীমা নথিভুক্ত")
            : t(
                "Illustrative thresholds · verify for your soil",
                "উদাহরণ সীমা · মাটির জন্য যাচাই করুন",
              )}
        </span>
      </div>
    </>
  );
  const rangeControls = (
    <select
      aria-label="Chart time range"
      className="compact-select"
      value={days}
      onChange={(e) => setDays(e.target.value)}
    >
      <option value="1">24 hours</option>
      <option value="7">7 days</option>
      <option value="30">30 days</option>
      <option value="custom">Custom range</option>
    </select>
  );
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            {t("GROW WITH INTELLIGENCE", "বুদ্ধিমত্তার সাথে চাষ")}
          </span>
          <h1>{t(en, bn)}</h1>
          <p>{t(sub, subbn)}</p>
        </div>
        <Button variant="outline" onClick={() => refresh()}>
          <RefreshCw size={15} />
          {t("Refresh", "রিফ্রেশ")}
        </Button>
      </div>
      {message && (
        <div className="toast" role="status">
          {message}
          <button
            onClick={() => setMessage("")}
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      )}
      {status.isError && <ErrorBox message={status.error.message} />}
      {["dashboard", "rootsense", "aquamind"].includes(section) && (
        <div className="source-strip">
          <span className="live-dot" />
          <strong>{farm?.name || t("Your farm", "আপনার খামার")}</strong>
          <span>{farm?.location || "—"}</span>
          <span className="strip-divider" />
          <Badge tone={reading?.provenance === "synthetic" ? "amber" : "green"}>
            {reading?.provenance === "synthetic"
              ? t("Simulation", "সিমুলেশন")
              : status.data?.data_source_mode || "Connecting"}
          </Badge>
          <span className="strip-end">
            {t("Updated", "আপডেট")} {displayDate(reading?.timestamp)}
          </span>
        </div>
      )}
      {status.isPending &&
        ["dashboard", "rootsense", "aquamind"].includes(section) && (
          <div className="stats-grid" aria-label="Loading observations">
            {[1, 2, 3, 4].map((n) => (
              <div className="skeleton" key={n} />
            ))}
          </div>
        )}
      {["dashboard", "rootsense"].includes(section) && (
        <div className="stats-grid">
          <Stat
            label={t("Soil moisture", "মাটির আর্দ্রতা")}
            value={moisture(reading?.moisture_vwc)}
            detail={
              reading
                ? "VWC · " +
                  (status.data?.status || "unknown").replaceAll("_", " ")
                : t("Awaiting observations", "তথ্যের অপেক্ষায়")
            }
            icon={Droplets}
          />
          <Stat
            label={t("Soil temperature", "মাটির তাপমাত্রা")}
            value={
              reading?.measurements.soil_temperature_c == null
                ? "—"
                : `${reading.measurements.soil_temperature_c.toFixed(1)}°C`
            }
            detail={t("Root-zone observation", "শিকড়ের এলাকার পাঠ")}
            icon={Thermometer}
          />
          <Stat
            label={t("Air humidity", "বাতাসের আর্দ্রতা")}
            value={
              reading?.measurements.air_humidity_percent == null
                ? "—"
                : `${reading.measurements.air_humidity_percent.toFixed(0)}%`
            }
            detail={t("Recorded at your station", "আপনার স্টেশনের পাঠ")}
            icon={Wind}
            tone="mint"
          />
          <Stat
            label={t("24-hour outlook", "২৪ ঘণ্টার পূর্বাভাস")}
            value={f?.risk_level || status.data?.status || "—"}
            detail={t(
              "Baseline · not field validated",
              "বেসলাইন · মাঠে যাচাইকৃত নয়",
            )}
            icon={BrainCircuit}
            tone="lime"
          />
        </div>
      )}
      {section === "dashboard" && (
        <>
          <div className="overview-grid">
            <Panel
              title={t("A closer look at your soil", "মাটির অবস্থার বিস্তারিত")}
              eyebrow="ROOTSENSE"
              action={rangeControls}
            >
              {history.isError ? (
                <ErrorBox message={history.error.message} />
              ) : (
                chart
              )}
            </Panel>
            <section className="insight-panel">
              <div className="insight-icon">
                <BrainCircuit size={26} />
                <span>AQUAMIND</span>
              </div>
              <span className="eyebrow">
                {t("YOUR NEXT 24 HOURS", "আগামী ২৪ ঘণ্টা")}
              </span>
              <h2>
                {f?.risk_level === "high"
                  ? t("Time to check the root zone.", "শিকড়ের মাটি দেখার সময়।")
                  : t(
                      "A thoughtful outlook for your next move.",
                      "পরের সিদ্ধান্তের জন্য আগাম তথ্য।",
                    )}
              </h2>
              <p>
                {f?.advice[language] ||
                  t(
                    "Start collecting observations to generate your first outlook.",
                    "পূর্বাভাস পেতে তথ্য সংগ্রহ শুরু করুন।",
                  )}
              </p>
              <div className="insight-divider" />
              <span className="insight-footnote">
                {t(
                  "Transparent baselines. No validated ML claim.",
                  "স্বচ্ছ বেসলাইন। যাচাইকৃত ML দাবি নেই।",
                )}
              </span>
              <Link href="/aquamind">
                {t("Explore your outlook", "পূর্বাভাস দেখুন")}
                <ArrowUpRight size={18} />
              </Link>
            </section>
          </div>
          <div className="three-grid">
            <Panel
              title={t("Weather at your farm", "খামারের আবহাওয়া")}
              action={<CloudSun size={22} />}
            >
              <div className="weather-mini">
                <strong>
                  {weather.data?.data?.current?.temperature_2m != null
                    ? `${weather.data.data.current.temperature_2m}°`
                    : "—"}
                </strong>
                <span>
                  {farm?.location}
                  <small>
                    {weather.data?.available
                      ? t("Open-Meteo forecast", "Open-Meteo পূর্বাভাস")
                      : t("Weather unavailable", "আবহাওয়ার তথ্য নেই")}
                  </small>
                </span>
              </div>
              <Link href="/weather" className="text-link">
                {t("View weather center", "আবহাওয়া দেখুন")}
                <ArrowUpRight size={15} />
              </Link>
            </Panel>
            <Panel
              title={t("Field notes", "মাঠের তথ্য")}
              action={<Leaf size={21} />}
            >
              <div className="detail-row">
                <span>{t("Crop & stage", "ফসল ও পর্যায়")}</span>
                <strong>
                  {plot?.crop || "—"} · {plot?.crop_stage || "—"}
                </strong>
              </div>
              <div className="detail-row">
                <span>{t("Soil type", "মাটির ধরন")}</span>
                <strong>{plot?.soil_type || "—"}</strong>
              </div>
              <Link href="/farms" className="text-link">
                {t("Manage your plot", "জমি পরিচালনা")}
                <ArrowUpRight size={15} />
              </Link>
            </Panel>
            <Panel
              title={t("Recent updates", "সাম্প্রতিক তথ্য")}
              action={<Activity size={21} />}
            >
              {notifications ? (
                <NoticeList notices={notices.data?.slice(0, 2) || []} compact />
              ) : (
                <p className="muted">
                  Notification summaries are disabled in Settings.
                </p>
              )}
              <Link href="/notifications" className="text-link">
                {t("All notifications", "সব বিজ্ঞপ্তি")}
                <ArrowUpRight size={15} />
              </Link>
            </Panel>
          </div>
          <div className="getting-started">
            <span className="round-icon">
              <Radio size={22} />
            </span>
            <div>
              <strong>
                {t(
                  "Your software is ready to listen.",
                  "সফটওয়্যার তথ্য গ্রহণের জন্য প্রস্তুত।",
                )}
              </strong>
              <p>
                {t(
                  "Try a labeled simulation now, connect calibrated hardware later.",
                  "এখন সিমুলেশন চালান, পরে ক্যালিব্রেট করা হার্ডওয়্যার যুক্ত করুন।",
                )}
              </p>
            </div>
            <Button asChild variant="outline">
              <Link href="/devices">
                {t("Open sensor center", "সেন্সর কেন্দ্র খুলুন")}
                <ArrowUpRight size={15} />
              </Link>
            </Button>
          </div>
        </>
      )}
      {section === "rootsense" && (
        <>
          <Panel
            title={t("Moisture history", "আর্দ্রতার ইতিহাস")}
            action={rangeControls}
          >
            {days === "custom" && (
              <div className="form-row">
                <label>
                  From
                  <input
                    type="datetime-local"
                    value={customStart}
                    onChange={(e) => setCustomStart(e.target.value)}
                  />
                </label>
                <label>
                  To
                  <input
                    type="datetime-local"
                    value={customEnd}
                    onChange={(e) => setCustomEnd(e.target.value)}
                  />
                </label>
              </div>
            )}
            {chart}
          </Panel>
          <div className="two-grid">
            <Panel title={t("Observation quality", "পাঠের গুণমান")}>
              <div className="detail-row">
                <span>Status</span>
                <Badge
                  tone={status.data?.status === "adequate" ? "green" : "amber"}
                >
                  {status.data?.status || "unavailable"}
                </Badge>
              </div>
              <div className="detail-row">
                <span>Reading age</span>
                <strong>
                  {status.data?.age_minutes == null
                    ? "—"
                    : `${status.data.age_minutes} minutes`}
                </strong>
              </div>
              <div className="detail-row">
                <span>Quality flags</span>
                <strong>
                  {reading?.quality_flags.join(", ") || "No observations"}
                </strong>
              </div>
              <p className="muted">{plot?.threshold_notes}</p>
            </Panel>
            <FeedbackForm plotId={plotId} />
          </div>
          <Panel title={t("Recent observations", "সাম্প্রতিক পাঠ")}>
            <div className="table-scroll">
              <table>
                <thead>
                  <tr>
                    <th>Time (Dhaka)</th>
                    <th>VWC</th>
                    <th>Source</th>
                    <th>Quality</th>
                  </tr>
                </thead>
                <tbody>
                  {history.data?.items
                    .slice(-15)
                    .reverse()
                    .map((r) => (
                      <tr key={r.id}>
                        <td>{displayDate(r.timestamp)}</td>
                        <td>{moisture(r.moisture_vwc)}</td>
                        <td>{r.provenance}</td>
                        <td>{r.quality_flags.join(", ") || "—"}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </>
      )}
      {section === "aquamind" && (
        <>
          {forecast.isError && <ErrorBox message={forecast.error.message} />}
          <div className="stats-grid">
            <Stat
              label="Current VWC"
              value={moisture(reading?.moisture_vwc)}
              detail="Latest observation"
              icon={Droplets}
            />
            <Stat
              label="Persistence · +24h"
              value={moisture(f?.persistence_vwc)}
              detail="Assumes no change"
              icon={Activity}
            />
            <Stat
              label="Water balance · +24h"
              value={moisture(f?.water_balance_vwc)}
              detail="Weather + simplified soil bucket"
              icon={Waves}
            />
            <Stat
              label="Risk outlook"
              value={f?.risk_level || "unknown"}
              detail={f?.data_source || "No data"}
              icon={BrainCircuit}
              tone="lime"
            />
          </div>
          <div className="two-grid">
            <Panel
              title={t("What to consider next", "পরের সিদ্ধান্ত")}
              eyebrow="IRRIGATION DECISION SUPPORT"
            >
              <div className="advisory">
                <BrainCircuit />
                <h3>
                  {f?.advice[language] ||
                    (forecast.isPending &&
                      t(
                        "Preparing your outlook from the latest observations…",
                        "সাম্প্রতিক তথ্য থেকে পূর্বাভাস তৈরি হচ্ছে…",
                      )) ||
                    "Collect valid observations to receive guidance."}
                </h3>
              </div>
              <p className="muted">
                {t(
                  "Always inspect soil and verify sensors. No automatic pump control.",
                  "মাটি পরীক্ষা ও সেন্সর যাচাই করুন। স্বয়ংক্রিয় পাম্প নিয়ন্ত্রণ নেই।",
                )}
              </p>
              <h3>{t("Why this outlook?", "এই পূর্বাভাসের কারণ")}</h3>
              <ul className="reason-list">
                {f?.reasons.map((r) => (
                  <li key={r}>
                    <Check size={16} />
                    {r}
                  </li>
                ))}
              </ul>
            </Panel>
            <Panel title={t("The method, made clear", "পদ্ধতি ও সীমাবদ্ধতা")}>
              <div className="detail-row">
                <span>Active method</span>
                <strong>{f?.method.replaceAll("_", " ") || "—"}</strong>
              </div>
              <div className="detail-row">
                <span>Model version</span>
                <strong>{f?.model_version || "baseline-v1"}</strong>
              </div>
              <div className="detail-row">
                <span>Validation</span>
                <Badge tone="amber">Not field validated</Badge>
              </div>
              <p className="formula">ETc ≈ Kc × ET0</p>
              <p className="muted">
                Simplified storage change = (rain − crop demand) / rooting
                depth. Runoff, deep soil transport and irrigation delivery are
                not fully modeled.
              </p>
              {f?.limitations.map((l) => (
                <p className="muted" key={l}>
                  • {l}
                </p>
              ))}
            </Panel>
          </div>
          <Panel title="Baseline comparison">
            <div className="comparison">
              {[
                ["Current", reading?.moisture_vwc],
                ["Persistence", f?.persistence_vwc],
                ["Water balance", f?.water_balance_vwc],
              ].map(([label, v]) => (
                <div key={String(label)}>
                  <span>{label}</span>
                  <div className="comparison-track">
                    <i
                      style={{
                        width: `${typeof v === "number" ? v * 100 : 0}%`,
                      }}
                    />
                  </div>
                  <strong>{moisture(typeof v === "number" ? v : null)}</strong>
                </div>
              ))}
            </div>
            <p className="muted">
              These are estimates, not measured future outcomes or accuracy
              scores. ML remains unvalidated until evaluated on an untouched
              measured test period.
            </p>
          </Panel>
        </>
      )}
      {section === "weather" && (
        <WeatherPage
          weather={weather.data}
          error={weather.isError ? weather.error.message : undefined}
          location={farm?.location}
        />
      )}
      {section === "devices" && (
        <>
          <SimulationPanel plotId={plotId} />
          <Panel
            title={t("Your stations", "আপনার স্টেশন")}
            eyebrow="SOURCE-AWARE BY DESIGN"
          >
            <p className="muted">
              Source mode: {status.data?.data_source_mode || "—"}. Change
              DATA_SOURCE_MODE in the server environment and restart. Hardware
              mode never substitutes simulated observations.
            </p>
            <div className="device-grid">
              {devices.data?.map((d) => (
                <DeviceCard device={d} key={d.id} />
              ))}
              {devices.data?.length === 0 && (
                <div className="empty-state">
                  No devices yet. Start simulation or register a device below.
                </div>
              )}
            </div>
          </Panel>
          <DeviceForm plots={plots.data || []} />
        </>
      )}
      {section === "farms" && (
        <FarmManager
          farms={farms.data || []}
          plots={plots.data || []}
          selectedPlot={plotId}
          onMessage={setMessage}
        />
      )}
      {section === "analytics" && (
        <>
          <Panel
            title="Moisture trends"
            action={
              <Button variant="outline" asChild>
                <a href={`/api/v1/plots/${plotId}/export`} download>
                  <Download size={15} />
                  Export CSV
                </a>
              </Button>
            }
          >
            {chart}
          </Panel>
          <Analytics plotId={plotId} />
        </>
      )}
      {section === "notifications" && (
        <Panel
          title={t("Your notifications", "আপনার বিজ্ঞপ্তি")}
          action={
            <Badge>
              {notices.data?.filter((n) => !n.read).length || 0} unread
            </Badge>
          }
        >
          {notices.isError ? (
            <ErrorBox message={notices.error.message} />
          ) : (
            <NoticeList
              notices={notices.data || []}
              onRead={(id) =>
                action.mutate({
                  path: `/notifications/${id}/read`,
                  method: "PATCH",
                })
              }
            />
          )}
        </Panel>
      )}
      {section === "settings" && (
        <div className="two-grid">
          <Panel title={t("Workspace preferences", "কর্মক্ষেত্রের পছন্দ")}>
            <label className="field-label">
              {t("Language", "ভাষা")}
              <select
                value={language}
                onChange={(e) =>
                  update({ language: e.target.value as "en" | "bn" })
                }
              >
                <option value="en">English</option>
                <option value="bn">বাংলা</option>
              </select>
            </label>
            <label className="field-label">
              {t("Appearance", "থিম")}
              <select
                value={theme}
                onChange={(e) =>
                  update({ theme: e.target.value as "light" | "dark" })
                }
              >
                <option value="light">Light · mint & forest</option>
                <option value="dark">Dark · deep green</option>
              </select>
            </label>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={notifications}
                onChange={(e) => update({ notifications: e.target.checked })}
              />
              Show notification summaries
            </label>
            <p className="muted">
              Preferences are saved in this browser. Measurements use explicit
              VWC m³/m³ units; charts display equivalent percentages.
            </p>
          </Panel>
          <Panel title="Application configuration">
            <div className="detail-row">
              <span>Data source mode</span>
              <strong>{status.data?.data_source_mode || "—"}</strong>
            </div>
            <div className="detail-row">
              <span>Model mode</span>
              <Badge>Baseline</Badge>
            </div>
            <p className="muted">
              Server-wide source mode, authentication and database settings are
              managed with environment variables. This avoids accidental source
              changes during a demo.
            </p>
            <Button asChild variant="outline">
              <Link href="/devices">
                <SlidersHorizontal size={16} />
                Simulation settings
              </Link>
            </Button>
            <p className="muted">
              Local demo access only. No personal account is required.
            </p>
          </Panel>
        </div>
      )}
    </>
  );
}

function NoticeList({
  notices,
  onRead,
  compact = false,
}: {
  notices: Notice[];
  onRead?: (id: string) => void;
  compact?: boolean;
}) {
  const { t } = useApp();
  if (!notices.length)
    return (
      <p className="muted empty-notices">
        {t(
          "All quiet here. New updates will appear as monitoring runs.",
          "নতুন তথ্য পর্যবেক্ষণের সময় দেখা যাবে।",
        )}
      </p>
    );
  return (
    <div className="notice-list">
      {notices.map((n) => (
        <div className={`notice ${n.read ? "read" : ""}`} key={n.id}>
          <span className="notice-icon">
            <AlertTriangle size={16} />
          </span>
          <div>
            <strong>{n.kind.replaceAll("_", " ")}</strong>
            <p>{n.message}</p>
            {!compact && <small>{displayDate(n.created_at)}</small>}
          </div>
          {!compact && !n.read && (
            <Button variant="ghost" onClick={() => onRead?.(n.id)}>
              <Check size={15} />
              Read
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}

function SimulationPanel({ plotId }: { plotId: string }) {
  const { t } = useApp();
  const client = useQueryClient();
  const [scenario, setScenario] = useState("drying");
  const [speed, setSpeed] = useState(1);
  const [error, setError] = useState("");
  const state = useQuery({
    queryKey: ["simulation", plotId],
    queryFn: () => api<Simulation>(`/simulation/status?plot_id=${plotId}`),
    refetchInterval: 3000,
  });
  const mutation = useMutation({
    mutationFn: (command: string) =>
      api(`/simulation/${command}`, { plot_id: plotId, scenario, speed }),
    onSuccess: () => {
      setError("");
      client.invalidateQueries();
    },
    onError: (e) => setError(e.message),
  });
  return (
    <Panel
      title={t("A living demo, clearly labeled.", "স্পষ্টভাবে চিহ্নিত সিমুলেশন।")}
      eyebrow="SIMULATION CONTROL"
      action={<Badge tone="amber">Synthetic data</Badge>}
    >
      <div className="simulation-content">
        <div>
          <p className="muted">
            {t(
              "Test the complete pipeline without physical sensors. Readings are generated by the worker and stored through the official ingestion API.",
              "সেন্সর ছাড়াই পুরো সিস্টেম পরীক্ষা করুন। ওয়ার্কার API দিয়ে তথ্য পাঠায়।",
            )}
          </p>
          <div className="form-row">
            <label>
              Scenario
              <select
                aria-label="Simulation scenario"
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
              >
                {[
                  ["drying", "Gradually drying soil"],
                  ["normal", "Normal variation"],
                  ["rainfall", "Rainfall event"],
                  ["irrigation", "Irrigation event"],
                  ["wet", "Persistently wet soil"],
                  ["disconnected", "Sensor disconnection"],
                  ["stale", "Stale sensor readings"],
                  ["invalid", "Invalid readings (rejected)"],
                ].map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Speed
              <select
                aria-label="Simulation speed"
                value={speed}
                onChange={(e) => setSpeed(Number(e.target.value))}
              >
                {[1, 5, 15, 30, 60].map((s) => (
                  <option key={s} value={s}>
                    {s}×
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="button-row">
            <Button
              disabled={mutation.isPending}
              onClick={() => mutation.mutate("start")}
            >
              <Play size={15} />
              {t("Start simulation", "সিমুলেশন শুরু")}
            </Button>
            <Button
              variant="outline"
              disabled={mutation.isPending || !state.data?.running}
              onClick={() => mutation.mutate("pause")}
            >
              <Pause size={15} />
              Pause
            </Button>
            <Button
              variant="ghost"
              disabled={mutation.isPending}
              onClick={() => mutation.mutate("reset")}
            >
              <RotateCcw size={15} />
              Reset synthetic data
            </Button>
          </div>
          {(error || state.data?.last_error) && (
            <p className="form-error" role="alert">
              {error || state.data?.last_error}
            </p>
          )}
        </div>
        <div className="simulation-state">
          <span className={`pulse-orb ${state.data?.running ? "running" : ""}`}>
            <Radio size={35} />
          </span>
          <strong>{state.data?.running ? "Running" : "Paused"}</strong>
          <span>{state.data?.step || 0} generated events</span>
          <small>Worker required · {state.data?.scenario || scenario}</small>
          <small>Last tick: {displayDate(state.data?.last_tick)}</small>
        </div>
      </div>
    </Panel>
  );
}

const deviceSchema = z.object({
  id: z
    .string()
    .regex(
      /^[a-zA-Z0-9_-]{1,64}$/,
      "Use letters, numbers, underscores or hyphens",
    ),
  name: z.string().min(1),
  plot_id: z.string().min(1),
  source: z.enum(["esp32", "external_sensor_api", "historical_import"]),
});
function DeviceForm({ plots }: { plots: Plot[] }) {
  const client = useQueryClient();
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const form = useForm<z.infer<typeof deviceSchema>>({
    resolver: zodResolver(deviceSchema),
    defaultValues: { source: "esp32" },
  });
  const submit = form.handleSubmit(async (data) => {
    try {
      const result = await api<{ device_token: string }>("/devices", data);
      setToken(result.device_token);
      setError("");
      client.invalidateQueries({ queryKey: ["devices"] });
    } catch (e) {
      setError((e as Error).message);
    }
  });
  return (
    <Panel title="Register a future device">
      <form onSubmit={submit} className="form-grid">
        <label>
          Device ID
          <input {...form.register("id")} placeholder="esp32_station_001" />
        </label>
        <label>
          Display name
          <input {...form.register("name")} placeholder="East field station" />
        </label>
        <label>
          Assigned plot
          <select {...form.register("plot_id")}>
            <option value="">Choose plot</option>
            {plots.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Source
          <select {...form.register("source")}>
            <option value="esp32">ESP32</option>
            <option value="external_sensor_api">External sensor API</option>
            <option value="historical_import">Historical measured data</option>
          </select>
        </label>
        <div className="full-width">
          <Button disabled={form.formState.isSubmitting}>
            <Plus size={15} />
            Provision device
          </Button>
          {Object.entries(form.formState.errors).map(([k, v]) => (
            <p role="alert" className="form-error" key={k}>
              {k}: {v.message}
            </p>
          ))}
          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}
          {token && (
            <div className="secret-box">
              <strong>
                Copy this device token now. It will not be shown again.
              </strong>
              <code>{token}</code>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigator.clipboard.writeText(token)}
              >
                Copy token
              </Button>
            </div>
          )}
        </div>
      </form>
    </Panel>
  );
}

function DeviceCard({ device }: { device: Device }) {
  const [show, setShow] = useState(false);
  const client = useQueryClient();
  const [error, setError] = useState("");
  const health = useQuery({
    queryKey: ["health", device.id],
    queryFn: () =>
      api<{
        connection: string;
        age_minutes: number | null;
        quality_flags: string[];
      }>(`/devices/${device.id}/health`),
  });
  const calibrations = useQuery({
    queryKey: ["calibrations", device.id],
    queryFn: () =>
      api<{ id: string; notes: string; verified: boolean }[]>(
        `/devices/${device.id}/calibrations`,
      ),
  });
  async function calibrate(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const data = new FormData(e.currentTarget);
    try {
      await api(`/devices/${device.id}/calibrations`, {
        raw_dry: Number(data.get("raw_dry")),
        raw_wet: Number(data.get("raw_wet")),
        vwc_dry: Number(data.get("vwc_dry")),
        vwc_wet: Number(data.get("vwc_wet")),
        soil_type: String(data.get("soil_type")),
        notes: String(data.get("notes")),
        verified: false,
      });
      setError("");
      setShow(false);
      client.invalidateQueries({ queryKey: ["calibrations", device.id] });
    } catch (e) {
      setError((e as Error).message);
    }
  }
  return (
    <div className="device-card">
      <div className="device-card-top">
        <span className="round-icon">
          <Radio size={22} />
        </span>
        <Badge tone={device.source === "simulator" ? "amber" : "green"}>
          {device.source === "simulator" ? "Simulation" : device.source}
        </Badge>
      </div>
      <h3>{device.name}</h3>
      <code>{device.id}</code>
      <div className="detail-row">
        <span>Connection</span>
        <strong>{health.data?.connection || "Checking"}</strong>
      </div>
      <div className="detail-row">
        <span>Last observation</span>
        <span>
          {health.data?.age_minutes == null
            ? "None"
            : `${Math.round(health.data.age_minutes)} min ago`}
        </span>
      </div>
      <p className="muted">
        {calibrations.data?.length || 0} calibration profiles
      </p>
      {calibrations.data?.map((c) => (
        <p className="muted" key={c.id}>
          {c.id.slice(0, 8)} · {c.verified ? "Reviewed" : "Unverified"} ·{" "}
          {c.notes}
        </p>
      ))}
      <Button variant="outline" onClick={() => setShow(!show)}>
        Add calibration
      </Button>
      {show && (
        <form onSubmit={calibrate} className="calibration-form">
          <p className="muted">
            Two-point linear calibration. Requires soil-specific physical
            measurements; saving does not validate the sensor.
          </p>
          {[
            ["raw_dry", "Dry-point ADC"],
            ["raw_wet", "Wet-point ADC"],
            ["vwc_dry", "Measured dry VWC (0–1)"],
            ["vwc_wet", "Measured wet VWC (0–1)"],
          ].map(([key, label]) => (
            <label key={key}>
              {label}
              <input
                name={key}
                type="number"
                step="any"
                required
                min="0"
                max={key.startsWith("vwc") ? "1" : "65535"}
              />
            </label>
          ))}
          <label>
            Soil type
            <input name="soil_type" required defaultValue="Loam" />
          </label>
          <label>
            Procedure & evidence
            <textarea name="notes" required minLength={15} />
          </label>
          <Button>Save unverified profile</Button>
          {error && (
            <p role="alert" className="form-error">
              {error}
            </p>
          )}
        </form>
      )}
    </div>
  );
}

function FeedbackForm({ plotId }: { plotId: string }) {
  const [message, setMessage] = useState("");
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    try {
      await api("/feedback", {
        plot_id: plotId,
        condition: form.get("condition"),
        notes: form.get("notes"),
      });
      setMessage("Observation saved. Thank you.");
    } catch (e) {
      setMessage((e as Error).message);
    }
  }
  return (
    <Panel title="What did you observe?">
      <form onSubmit={submit}>
        <label>
          Root-zone condition
          <select name="condition">
            <option value="adequate">Adequate moisture</option>
            <option value="dry">Dry soil</option>
            <option value="wet">Wet soil</option>
            <option value="sensor_issue">Sensor issue</option>
          </select>
        </label>
        <label>
          Field notes
          <textarea
            name="notes"
            maxLength={1000}
            placeholder="Record an inspection…"
          />
        </label>
        <Button>Save field observation</Button>
        {message && <p role="status">{message}</p>}
      </form>
    </Panel>
  );
}

function WeatherPage({
  weather,
  error,
  location,
}: {
  weather: Weather | undefined;
  error?: string;
  location?: string;
}) {
  const { t } = useApp();
  const [now] = useState(() => new Date().getTime());
  if (error) return <ErrorBox message={error} />;
  if (!weather) return <div className="skeleton" />;
  if (!weather.available || !weather.data)
    return (
      <Panel
        title={t(
          "Weather is currently unavailable",
          "আবহাওয়ার তথ্য বর্তমানে নেই",
        )}
      >
        <p className="muted">
          No usable forecast is cached. The app will continue in
          persistence-baseline mode and retry the weather provider. No weather
          readings are fabricated.
        </p>
      </Panel>
    );
  const data = weather.data;
  const hourly = data.hourly.time
    .map((v, i) => ({ time: v, index: i }))
    .filter((v) => new Date(v.time + "Z").getTime() >= now)
    .slice(0, 24);
  return (
    <>
      <div className="weather-hero">
        <div>
          <Badge tone={weather.usable ? "green" : "amber"}>
            {weather.usable ? "Forecast available" : "Outdated forecast"}
          </Badge>
          <h2>{location}</h2>
          <strong>
            {data.current?.temperature_2m ?? "—"}°<small>C</small>
          </strong>
          <p>Open-Meteo · updated {weather.age_minutes} minutes ago</p>
        </div>
        <CloudSun size={130} strokeWidth={1} />
        <div className="weather-details">
          <span>
            <Wind />
            Wind<strong>{data.current?.wind_speed_10m ?? "—"} km/h</strong>
          </span>
          <span>
            <Droplets />
            Humidity
            <strong>{data.current?.relative_humidity_2m ?? "—"}%</strong>
          </span>
          <span>
            <Waves />
            Precipitation
            <strong>{data.current?.precipitation ?? "—"} mm</strong>
          </span>
        </div>
      </div>
      <Panel title="The next 24 hours">
        <div className="hourly-scroll">
          {hourly.map(({ time, index: i }) => (
            <div className="hour-card" key={time}>
              <small>
                {new Date(time + "Z").toLocaleTimeString("en-GB", {
                  timeZone: "Asia/Dhaka",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </small>
              <CloudSun size={25} />
              <strong>{data.hourly.temperature_2m[i]}°</strong>
              <span>{data.hourly.precipitation[i]} mm</span>
              <small>
                {data.hourly.precipitation_probability?.[i] ?? "—"}% rain
              </small>
              <small>ET0 {data.hourly.et0_fao_evapotranspiration[i]} mm</small>
            </div>
          ))}
        </div>
      </Panel>
      <Panel title="Your week ahead">
        <div className="daily-grid">
          {data.daily.time.map((day, i) => (
            <div className="day-card" key={day}>
              <strong>
                {new Date(day).toLocaleDateString("en-GB", {
                  weekday: "short",
                  day: "numeric",
                })}
              </strong>
              <CloudSun size={30} />
              <span>
                {data.daily.temperature_2m_max[i]}° /{" "}
                {data.daily.temperature_2m_min[i]}°
              </span>
              <small>{data.daily.precipitation_sum[i]} mm rain</small>
              <small>ET0 {data.daily.et0_fao_evapotranspiration[i]} mm</small>
            </div>
          ))}
        </div>
      </Panel>
      <p className="muted">
        Weather is a forecast, not a soil-moisture measurement. Retrieval time
        is recorded; the forecast endpoint does not provide the model issuance
        time.
      </p>
    </>
  );
}

function FarmManager({
  farms,
  plots,
  selectedPlot,
  onMessage,
}: {
  farms: Farm[];
  plots: Plot[];
  selectedPlot: string;
  onMessage: (s: string) => void;
}) {
  const client = useQueryClient();
  const [editFarm, setEditFarm] = useState<Farm | null>(null);
  const [editPlot, setEditPlot] = useState<Plot | null>(null);
  const [formVersion, setFormVersion] = useState(0);
  async function submitFarm(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    try {
      await api(
        editFarm ? `/farms/${editFarm.id}` : "/farms",
        {
          name: f.get("name"),
          location: f.get("location"),
          latitude: Number(f.get("latitude")),
          longitude: Number(f.get("longitude")),
        },
        editFarm ? "PATCH" : "POST",
      );
      setEditFarm(null);
      setFormVersion((v) => v + 1);
      client.invalidateQueries();
      onMessage("Farm saved.");
    } catch (e) {
      onMessage((e as Error).message);
    }
  }
  async function submitPlot(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const f = new FormData(e.currentTarget);
    const payload = {
      farm_id: f.get("farm_id"),
      name: f.get("name"),
      crop: f.get("crop"),
      soil_type: f.get("soil_type"),
      crop_stage: f.get("crop_stage"),
      planting_date: f.get("planting_date") || null,
      rooting_depth_m: Number(f.get("rooting_depth_m")),
      kc: Number(f.get("kc")),
      low_vwc: Number(f.get("low_vwc")),
      high_vwc: Number(f.get("high_vwc")),
      field_capacity_vwc: Number(f.get("field_capacity_vwc")),
      thresholds_verified: f.get("thresholds_verified") === "on",
      threshold_notes: f.get("threshold_notes"),
    };
    try {
      await api(
        editPlot ? `/plots/${editPlot.id}` : "/plots",
        payload,
        editPlot ? "PATCH" : "POST",
      );
      setEditPlot(null);
      setFormVersion((v) => v + 1);
      client.invalidateQueries();
      onMessage("Plot saved.");
    } catch (e) {
      onMessage((e as Error).message);
    }
  }
  return (
    <>
      <Panel title="Your farms & plots">
        <div className="farm-grid">
          {farms.map((f) => (
            <div className="farm-card" key={f.id}>
              <span className="round-icon">
                <Sprout />
              </span>
              <h3>{f.name}</h3>
              <p>{f.location}</p>
              <small>
                {f.latitude}, {f.longitude}
              </small>
              <Button variant="ghost" onClick={() => setEditFarm(f)}>
                Edit farm
              </Button>
              {plots
                .filter((p) => p.farm_id === f.id)
                .map((p) => (
                  <div className="plot-row" key={p.id}>
                    <Leaf size={17} />
                    <span>
                      {p.name}
                      <small>
                        {p.crop} · {p.soil_type}
                      </small>
                    </span>
                    <Button variant="ghost" onClick={() => setEditPlot(p)}>
                      Edit
                    </Button>
                  </div>
                ))}
            </div>
          ))}
        </div>
      </Panel>
      <div className="two-grid">
        <Panel title={editFarm ? "Edit farm" : "Create a farm"}>
          <form
            key={`farm-${editFarm?.id}-${formVersion}`}
            onSubmit={submitFarm}
          >
            {[
              ["name", "Farm name", editFarm?.name || ""],
              [
                "location",
                "Location",
                editFarm?.location || "Gazipur, Bangladesh",
              ],
            ].map(([name, label, value]) => (
              <label key={name}>
                {label}
                <input
                  name={name}
                  defaultValue={value}
                  required
                  maxLength={120}
                />
              </label>
            ))}
            <div className="form-row">
              <label>
                Latitude
                <input
                  name="latitude"
                  type="number"
                  step="any"
                  min={-90}
                  max={90}
                  defaultValue={editFarm?.latitude ?? 24.0023}
                  required
                />
              </label>
              <label>
                Longitude
                <input
                  name="longitude"
                  type="number"
                  step="any"
                  min={-180}
                  max={180}
                  defaultValue={editFarm?.longitude ?? 90.4264}
                  required
                />
              </label>
            </div>
            <Button>Save farm</Button>
            {editFarm && (
              <Button
                type="button"
                variant="ghost"
                onClick={() => setEditFarm(null)}
              >
                Cancel
              </Button>
            )}
          </form>
        </Panel>
        <Panel title={editPlot ? "Edit plot" : "Create a plot"}>
          <form
            key={`plot-${editPlot?.id}-${formVersion}`}
            onSubmit={submitPlot}
          >
            <label>
              Farm
              <select
                name="farm_id"
                required
                defaultValue={editPlot?.farm_id || farms[0]?.id}
              >
                {farms.map((f) => (
                  <option key={f.id} value={f.id}>
                    {f.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Plot name
              <input name="name" required defaultValue={editPlot?.name || ""} />
            </label>
            <div className="form-row">
              <label>
                Crop
                <input
                  name="crop"
                  defaultValue={editPlot?.crop || "Tomato"}
                  required
                />
              </label>
              <label>
                Stage
                <select
                  name="crop_stage"
                  defaultValue={editPlot?.crop_stage || "Vegetative"}
                >
                  {[
                    "Seedling",
                    "Vegetative",
                    "Flowering",
                    "Fruiting",
                    "Harvest",
                  ].map((s) => (
                    <option key={s}>{s}</option>
                  ))}
                </select>
              </label>
            </div>
            <div className="form-row">
              <label>
                Soil type
                <input
                  name="soil_type"
                  defaultValue={editPlot?.soil_type || "Loam"}
                  required
                />
              </label>
              <label>
                Planting date
                <input
                  name="planting_date"
                  type="date"
                  defaultValue={editPlot?.planting_date || ""}
                />
              </label>
            </div>
            <div className="form-row">
              <label>
                Rooting depth (m)
                <input
                  name="rooting_depth_m"
                  type="number"
                  step="0.01"
                  min="0.05"
                  max="3"
                  defaultValue={editPlot?.rooting_depth_m ?? 0.3}
                />
              </label>
              <label>
                Kc (assumed)
                <input
                  name="kc"
                  type="number"
                  step="0.01"
                  min="0.1"
                  max="2"
                  defaultValue={editPlot?.kc ?? 0.85}
                />
              </label>
            </div>
            <div className="form-row">
              {[
                ["low_vwc", "Low VWC", editPlot?.low_vwc ?? 0.2],
                ["high_vwc", "High VWC", editPlot?.high_vwc ?? 0.4],
                [
                  "field_capacity_vwc",
                  "Field capacity",
                  editPlot?.field_capacity_vwc ?? 0.35,
                ],
              ].map(([name, label, value]) => (
                <label key={String(name)}>
                  {label}
                  <input
                    name={String(name)}
                    type="number"
                    step="0.01"
                    min="0"
                    max="1"
                    defaultValue={value}
                    required
                  />
                </label>
              ))}
            </div>
            <label>
              Threshold context
              <textarea
                name="threshold_notes"
                defaultValue={
                  editPlot?.threshold_notes ||
                  "Illustrative simulation settings; not field calibrated"
                }
                required
                minLength={15}
              />
            </label>
            <label className="checkbox-label">
              <input
                name="thresholds_verified"
                type="checkbox"
                defaultChecked={editPlot?.thresholds_verified || false}
              />
              Thresholds reviewed against measured soil/crop evidence
            </label>
            <Button>Save plot</Button>
            {editPlot && (
              <Button
                variant="ghost"
                type="button"
                onClick={() => setEditPlot(null)}
              >
                Cancel
              </Button>
            )}
          </form>
        </Panel>
      </div>
      <IrrigationForm plotId={selectedPlot} />
    </>
  );
}

function IrrigationForm({ plotId }: { plotId: string }) {
  const [message, setMessage] = useState("");
  const client = useQueryClient();
  const events = useQuery({
    queryKey: ["irrigation", plotId],
    queryFn: () =>
      api<
        { id: string; timestamp: string; amount_mm: number; source: string }[]
      >(`/plots/${plotId}/irrigation`),
  });
  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    try {
      await api(`/plots/${plotId}/irrigation`, {
        timestamp: new Date(String(form.get("timestamp"))).toISOString(),
        amount_mm: Number(form.get("amount_mm")),
        notes: form.get("notes"),
      });
      setMessage(
        "Irrigation recorded. This records an observed event; it does not control a pump.",
      );
      client.invalidateQueries({ queryKey: ["irrigation", plotId] });
    } catch (e) {
      setMessage((e as Error).message);
    }
  }
  return (
    <Panel title="Irrigation records · selected plot">
      <form className="form-grid" onSubmit={submit}>
        <label>
          When
          <input name="timestamp" type="datetime-local" required />
        </label>
        <label>
          Applied amount (mm)
          <input
            name="amount_mm"
            type="number"
            min="0.1"
            max="500"
            step="0.1"
            required
          />
        </label>
        <label>
          Notes
          <input name="notes" maxLength={500} />
        </label>
        <div className="align-end">
          <Button>Record irrigation</Button>
        </div>
      </form>
      {message && <p role="status">{message}</p>}
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Amount</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {events.data?.map((e) => (
              <tr key={e.id}>
                <td>{displayDate(e.timestamp)}</td>
                <td>{e.amount_mm} mm</td>
                <td>{e.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function Analytics({ plotId }: { plotId: string }) {
  const query = useQuery({
    queryKey: ["analytics", plotId],
    queryFn: () =>
      api<{
        provenance_counts: Record<string, number>;
        evaluation: {
          status: string;
          notice?: string;
          results?: Record<string, { mae: number; rmse: number }>;
        };
        irrigation: {
          id: string;
          timestamp: string;
          amount_mm: number;
          source: string;
        }[];
      }>(`/analytics?plot_id=${plotId}`),
  });
  return (
    <div className="two-grid">
      <Panel title="Data provenance">
        {Object.entries(query.data?.provenance_counts || {}).map(
          ([source, count]) => (
            <div className="detail-row" key={source}>
              <Badge tone={source === "synthetic" ? "amber" : "green"}>
                {source}
              </Badge>
              <strong>{count} observations</strong>
            </div>
          ),
        )}
        <p className="muted">
          Synthetic observations are suitable for testing software behavior.
          They do not establish field accuracy or water savings.
        </p>
      </Panel>
      <Panel title="Model evaluation">
        <Badge tone="amber">
          {query.data?.evaluation.status || "No evaluation"}
        </Badge>
        <p className="muted">
          {query.data?.evaluation.notice ||
            "Review the reproducible evaluation report generated by the measured-data training pipeline."}
        </p>
        <p className="muted">
          MAE / RMSE and baseline comparisons appear only after a measured-data
          evaluation has been run. No invented performance metrics.
        </p>
        {Object.keys(query.data?.evaluation.results || {}).length > 0 && (
          <div className="table-scroll">
            <table>
              <thead>
                <tr>
                  <th>Method</th>
                  <th>MAE (VWC)</th>
                  <th>RMSE (VWC)</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(query.data?.evaluation.results || {}).map(
                  ([method, metrics]) => (
                    <tr key={method}>
                      <td>{method.replaceAll("_", " ")}</td>
                      <td>{metrics.mae.toFixed(4)}</td>
                      <td>{metrics.rmse.toFixed(4)}</td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        )}
      </Panel>
      <Panel title="Recorded irrigation">
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Amount</th>
                <th>Source</th>
              </tr>
            </thead>
            <tbody>
              {query.data?.irrigation.map((event) => (
                <tr key={event.id}>
                  <td>{displayDate(event.timestamp)}</td>
                  <td>{event.amount_mm} mm</td>
                  <td>{event.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {!query.data?.irrigation.length && (
          <p className="muted">No irrigation events recorded for this plot.</p>
        )}
      </Panel>
    </div>
  );
}
