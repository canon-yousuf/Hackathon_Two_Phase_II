"use client";

import type { StatusFilter, SortOption } from "@/types/task";

interface TaskFilterProps {
  statusFilter: StatusFilter;
  sortOption: SortOption;
  onStatusChange: (status: StatusFilter) => void;
  onSortChange: (sort: SortOption) => void;
}

const statusOptions: { value: StatusFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
];

const sortOptions: { value: SortOption; label: string }[] = [
  { value: "created", label: "Newest First" },
  { value: "title", label: "Alphabetical" },
];

export default function TaskFilter({
  statusFilter,
  sortOption,
  onStatusChange,
  onSortChange,
}: TaskFilterProps) {
  return (
    <div className="flex flex-wrap items-center gap-4">
      <div className="flex overflow-hidden rounded-lg border border-gray-300">
        {statusOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onStatusChange(opt.value)}
            className={`px-3 py-1.5 text-sm font-medium transition-colors ${
              statusFilter === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="flex overflow-hidden rounded-lg border border-gray-300">
        {sortOptions.map((opt) => (
          <button
            key={opt.value}
            onClick={() => onSortChange(opt.value)}
            className={`px-3 py-1.5 text-sm font-medium transition-colors ${
              sortOption === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
}
