import type { CubeRow } from "../api/client";

type Props = {
  rows: CubeRow[];
  loading: boolean;
};

export default function CubeTable({ rows, loading }: Props) {
  return (
    <div className="panel">
      <h2>OLAP Cube — Region × Category</h2>
      {loading ? (
        <p className="loading">Loading cube…</p>
      ) : (
        <table className="cube-table">
          <thead>
            <tr>
              <th>Region</th>
              <th>Category</th>
              <th>Revenue</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr key={`${row.region}-${row.category}-${index}`}>
                <td>{row.region}</td>
                <td>{row.category}</td>
                <td>
                  {new Intl.NumberFormat("en-US", {
                    style: "currency",
                    currency: "USD",
                    maximumFractionDigits: 0,
                  }).format(Number(row.value))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
