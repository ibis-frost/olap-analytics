import { useEffect, useState } from "react";
import {
  getByCategory,
  getCube,
  getFilterOptions,
  getHealth,
  getRevenueTrend,
  getSummary,
  type CategoryPoint,
  type CubeRow,
  type Filters,
  type Summary,
  type TrendPoint,
} from "../api/client";
import { CategoryBarChart, RevenueTrendChart } from "../components/Charts";
import CubeTable from "../components/CubeTable";
import FiltersBar from "../components/FiltersBar";
import KpiCards from "../components/KpiCards";

const DEFAULT_FILTERS: Filters = {
  start: "2023-01-01",
  end: "2025-06-30",
  region: "all",
  category: "all",
};

export default function Dashboard() {
  const [filters, setFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [regions, setRegions] = useState<string[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [byCategory, setByCategory] = useState<CategoryPoint[]>([]);
  const [cubeRows, setCubeRows] = useState<CubeRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getFilterOptions()
      .then((options) => {
        setRegions(options.regions);
        setCategories(options.categories);
      })
      .catch(() => {
        setRegions(["North", "South", "East", "West", "Central"]);
        setCategories(["Electronics", "Apparel", "Home", "Sports", "Grocery"]);
      });
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const health = await getHealth();
        if (!health.warehouse_ready) {
          throw new Error("Analytics warehouse is not built yet. Run the ETL pipeline first.");
        }

        const [summaryData, trendData, categoryData, cubeData] = await Promise.all([
          getSummary(filters),
          getRevenueTrend(filters),
          getByCategory(filters),
          getCube(filters),
        ]);

        if (!cancelled) {
          setSummary(summaryData);
          setTrend(trendData);
          setByCategory(categoryData);
          setCubeRows(cubeData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load dashboard data.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [filters]);

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <h1>Retail OLAP Dashboard</h1>
        <p>Postgres staging → Python ETL → DuckDB star schema → slice &amp; dice analytics</p>
      </header>

      {error ? <div className="status-banner">{error}</div> : null}

      <FiltersBar
        filters={filters}
        regions={regions}
        categories={categories}
        onChange={setFilters}
      />

      <KpiCards summary={summary} loading={loading} />

      <div className="chart-grid">
        <RevenueTrendChart data={trend} loading={loading} />
        <CategoryBarChart data={byCategory} loading={loading} />
      </div>

      <CubeTable rows={cubeRows} loading={loading} />
    </main>
  );
}
