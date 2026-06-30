import type { Filters } from "../api/client";

type Props = {
  filters: Filters;
  regions: string[];
  categories: string[];
  onChange: (next: Filters) => void;
};

export default function FiltersBar({ filters, regions, categories, onChange }: Props) {
  return (
    <div className="filters">
      <label>
        Start date
        <input
          type="date"
          value={filters.start}
          onChange={(event) => onChange({ ...filters, start: event.target.value })}
        />
      </label>
      <label>
        End date
        <input
          type="date"
          value={filters.end}
          onChange={(event) => onChange({ ...filters, end: event.target.value })}
        />
      </label>
      <label>
        Region
        <select
          value={filters.region}
          onChange={(event) => onChange({ ...filters, region: event.target.value })}
        >
          <option value="all">All regions</option>
          {regions.map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
      </label>
      <label>
        Category
        <select
          value={filters.category}
          onChange={(event) => onChange({ ...filters, category: event.target.value })}
        >
          <option value="all">All categories</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
