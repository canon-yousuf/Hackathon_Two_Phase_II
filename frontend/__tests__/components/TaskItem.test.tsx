import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import TaskItem from "@/components/TaskItem";
import type { Task } from "@/types/task";

const pendingTask: Task = {
  id: 1,
  user_id: "user-1",
  title: "Test Task",
  description: "A description",
  completed: false,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

const completedTask: Task = {
  ...pendingTask,
  id: 2,
  title: "Done Task",
  completed: true,
};

describe("TaskItem", () => {
  const onToggle = vi.fn();
  const onEdit = vi.fn();
  const onDelete = vi.fn();

  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("displays title and completion status (FR-049)", () => {
    render(
      <TaskItem
        task={pendingTask}
        onToggle={onToggle}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    );
    expect(screen.getByText("Test Task")).toBeInTheDocument();
  });

  it("completed task has line-through (FR-050)", () => {
    render(
      <TaskItem
        task={completedTask}
        onToggle={onToggle}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    );
    const titleElement = screen.getByText("Done Task");
    expect(titleElement.className).toContain("line-through");
  });

  it("delete button triggers callback (FR-051)", async () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const user = userEvent.setup();

    render(
      <TaskItem
        task={pendingTask}
        onToggle={onToggle}
        onEdit={onEdit}
        onDelete={onDelete}
      />
    );

    const deleteButton = screen.getByText("Delete");
    await user.click(deleteButton);

    expect(window.confirm).toHaveBeenCalled();
    expect(onDelete).toHaveBeenCalledWith(pendingTask.id);
  });
});
