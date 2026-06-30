import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CategoryPoint, TrendPoint } from "../api/client";

type TrendProps = {
  data: TrendPoint[];
  loading: boolean;
};

type CategoryProps = {
  data: CategoryPoint[];
  loading: boolean;
};

export function RevenueTrendChart({ data, loading }: TrendProps) {
  return (
    <div className="panel">
      <h2>Revenue Trend</h2>
      {loading ? (
        <p className="loading">Loading trend…</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
            <XAxis dataKey="period" stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                background: "#0f172a",
                border: "1px solid rgba(148,163,184,0.25)",
                borderRadius: 8,
              }}
            />
            <Line type="monotone" dataKey="revenue" stroke="#38bdf8" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export function CategoryBarChart({ data, loading }: CategoryProps) {
  return (
    <div className="panel">
      <h2>Revenue by Category</h2>
      {loading ? (
        <p className="loading">Loading categories…</p>
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
            <XAxis dataKey="category" stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                background: "#0f172a",
                border: "1px solid rgba(148,163,184,0.25)",
                borderRadius: 8,
              }}
            />
            <Bar dataKey="revenue" fill="#a855f7" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
