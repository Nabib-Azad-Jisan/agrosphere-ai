"use client";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  Legend,
} from "recharts";
import { type Reading } from "@/lib/api";
export function MoistureChart({
  readings,
  low = 0.2,
  high = 0.4,
}: {
  readings: Reading[];
  low?: number;
  high?: number;
}) {
  if (!readings.length)
    return (
      <div className="chart-empty">
        <span>◌</span>
        <strong>No observations yet</strong>
        <p>Start a simulation or connect a registered device.</p>
      </div>
    );
  const devices = [...new Set(readings.map((r) => r.device_id))];
  const data = readings.map((r) => ({
    time: new Date(r.timestamp).getTime(),
    [r.device_id]:
      r.moisture_vwc == null ? null : +(r.moisture_vwc * 100).toFixed(2),
    source: r.provenance,
  }));
  const colors = ["#168B5D", "#8d64d8", "#df9a27", "#338ab8"];
  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 12, right: 12, left: -12, bottom: 0 }}
        >
          <defs>
            {devices.map((d, i) => (
              <linearGradient
                id={`fill-${d}`}
                key={d}
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="0%"
                  stopColor={colors[i % 4]}
                  stopOpacity={0.22}
                />
                <stop offset="100%" stopColor={colors[i % 4]} stopOpacity={0} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid
            strokeDasharray="3 6"
            vertical={false}
            stroke="var(--border)"
          />
          <XAxis
            type="number"
            domain={["dataMin", "dataMax"]}
            dataKey="time"
            tickFormatter={(v) =>
              new Date(v).toLocaleTimeString("en-GB", {
                timeZone: "Asia/Dhaka",
                hour: "2-digit",
                minute: "2-digit",
              })
            }
            tick={{ fontSize: 11, fill: "var(--muted)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            domain={[0, 60]}
            unit="%"
            tick={{ fontSize: 11, fill: "var(--muted)" }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            labelFormatter={(v) =>
              new Date(Number(v)).toLocaleString("en-GB", {
                timeZone: "Asia/Dhaka",
              })
            }
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 12,
            }}
          />
          <ReferenceLine y={low * 100} stroke="#d8a347" strokeDasharray="4 4" />
          <ReferenceLine
            y={high * 100}
            stroke="#6e9cb7"
            strokeDasharray="4 4"
          />
          {devices.map((d, i) => (
            <Area
              key={d}
              type="monotone"
              dataKey={d}
              name={`${d} · ${readings.find((r) => r.device_id === d)?.provenance}`}
              connectNulls={false}
              stroke={colors[i % 4]}
              fill={`url(#fill-${d})`}
              strokeWidth={2.5}
              isAnimationActive={false}
            />
          ))}
          <Legend wrapperStyle={{ fontSize: 11 }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
