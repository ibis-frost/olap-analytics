const API_URL =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.PROD ? "" : "http://localhost:8000");

export type Filters = {
  start: string;
  end: string;
  region: string;
  category: string;
};

export type Summary = {
  total_revenue: number;
  total_orders: number;
  total_units: number;
  avg_order_value: number;
};

export type TrendPoint = {
  period: string;
  revenue: number;
  orders: number;
};

export type CategoryPoint = {
  category: string;
  revenue: number;
  units: number;
};

export type CubeRow = Record<string, string | number>;

function buildQuery(params: Record<string, string>) {
  const query = new URLSearchParams(params);
  return `${API_URL}${query.toString() ? `?${query.toString()}` : ""}`;
}

async function fetchJson<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const url = `${API_URL}${path}?${new URLSearchParams(params).toString()}`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error ${response.status}: ${await response.text()}`);
  }
  return response.json() as Promise<T>;
}

export function getSummary(filters: Filters) {
  return fetchJson<Summary>("/api/metrics/summary", {
    start: filters.start,
    end: filters.end,
    region: filters.region,
    category: filters.category,
  });
}

export function getRevenueTrend(filters: Filters, grain = "month") {
  return fetchJson<TrendPoint[]>("/api/metrics/revenue-trend", {
    grain,
    start: filters.start,
    end: filters.end,
    region: filters.region,
    category: filters.category,
  });
}

export function getByCategory(filters: Filters) {
  return fetchJson<CategoryPoint[]>("/api/metrics/by-category", {
    start: filters.start,
    end: filters.end,
    region: filters.region,
    category: filters.category,
  });
}

export function getCube(filters: Filters) {
  return fetchJson<CubeRow[]>("/api/cube", {
    dimensions: "region,category",
    measure: "revenue",
    start: filters.start,
    end: filters.end,
    region: filters.region,
    category: filters.category,
  });
}

export function getDrill(filters: Filters, level: string) {
  return fetchJson<TrendPoint[]>("/api/cube/drill", {
    dimension: "date",
    level,
    start: filters.start,
    end: filters.end,
    region: filters.region,
    category: filters.category,
  });
}

export function getFilterOptions() {
  return fetchJson<{ regions: string[]; categories: string[] }>("/api/metrics/filters");
}

export function getHealth() {
  return fetchJson<{ status: string; warehouse_ready: boolean }>("/health");
}

export { API_URL, buildQuery };
