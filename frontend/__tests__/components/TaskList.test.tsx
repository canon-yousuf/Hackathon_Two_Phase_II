import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import TaskList from "@/components/TaskList";
import type { Task } from "@/types/task";

const mockTasks: Task[] = [
  {
    id: 1,
    user_id: "user-1",
    title: "First Task",
    description: null,
    completed: false,
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  },
  {
    id: 2,
    user_id: "user-1",
    title: "Second Task",
    description: "Some details",
    completed: true,
    created_at: "2026-01-02T00:00:00Z",
    updated_at: "2026-01-02T00:00:00Z",
  },
  {
    id: 3,
    user_id: "user-1",
    title: "Third Task",
    description: null,
    completed: false,
    created_at: "2026-01-03T00:00:00Z",
    updated_at: "2026-01-03T00:00:00Z",
  },
];

const noop = vi.fn();

describe("TaskList", () => {
  it("renders task items when given tasks (FR-046)", () => {
    render(
      <TaskList
        tasks={mockTasks}
        isLoading={false}
        error={null}
        onRetry={noop}
        onToggle={noop}
        onEdit={noop}
        onDelete={noop}
      />
    );
    expect(screen.getByText("First Task")).toBeInTheDocument();
    expect(screen.getByText("Second Task")).toBeInTheDocument();
    expect(screen.getByText("Third Task")).toBeInTheDocument();
  });

  it("renders empty state when no tasks (FR-047)", () => {
    render(
      <TaskList
        tasks={[]}
        isLoading={false}
        error={null}
        onRetry={noop}
        onToggle={noop}
        onEdit={noop}
        onDelete={noop}
      />
    );
    expect(screen.getByText(/no tasks yet/i)).toBeInTheDocument();
  });

  it("renders loading skeletons when loading (FR-048)", () => {
    const { container } = render(
      <TaskList
        tasks={[]}
        isLoading={true}
        error={null}
        onRetry={noop}
        onToggle={noop}
        onEdit={noop}
        onDelete={noop}
      />
    );
    const pulseElements = container.querySelectorAll(".animate-pulse");
    expect(pulseElements.length).toBe(3);
  });
});
