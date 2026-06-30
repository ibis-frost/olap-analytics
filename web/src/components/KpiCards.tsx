import type { Summary } from "../api/client";

type Props = {
  summary: Summary | null;
  loading: boolean;
};

function formatCurrency(value: number | undefined) {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatNumber(value: number | undefined) {
  if (value == null) return "—";
  return new Intl.NumberFormat("en-US").format(value);
}

export default function KpiCards({ summary, loading }: Props) {
  const cards = [
    { label: "Total Revenue", value: formatCurrency(summary?.total_revenue) },
    { label: "Orders", value: formatNumber(summary?.total_orders) },
    { label: "Units Sold", value: formatNumber(summary?.total_units) },
    { label: "Avg Order Value", value: formatCurrency(summary?.avg_order_value) },
  ];

  return (
    <div className="kpi-grid">
      {cards.map((card) => (
        <div className="kpi-card" key={card.label}>
          <span>{card.label}</span>
          <strong>{loading ? "…" : card.value}</strong>
        </div>
      ))}
    </div>
  );
}
