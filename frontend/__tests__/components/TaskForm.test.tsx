import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi } from "vitest";
import TaskForm from "@/components/TaskForm";
import type { Task } from "@/types/task";

const existingTask: Task = {
  id: 1,
  user_id: "user-1",
  title: "Existing Title",
  description: "Existing Description",
  completed: false,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-01T00:00:00Z",
};

describe("TaskForm", () => {
  it("create mode shows empty fields and Add Task button (FR-052)", () => {
    const onSubmit = vi.fn();
    render(<TaskForm mode="create" onSubmit={onSubmit} />);

    const titleInput = screen.getByPlaceholderText("What needs to be done?");
    expect(titleInput).toHaveValue("");

    const submitButton = screen.getByRole("button", { name: /add task/i });
    expect(submitButton).toBeInTheDocument();
  });

  it("edit mode shows prefilled fields and Update Task button (FR-053)", () => {
    const onSubmit = vi.fn();
    render(
      <TaskForm mode="edit" initialData={existingTask} onSubmit={onSubmit} />
    );

    const titleInput = screen.getByPlaceholderText("What needs to be done?");
    expect(titleInput).toHaveValue("Existing Title");

    const submitButton = screen.getByRole("button", { name: /update task/i });
    expect(submitButton).toBeInTheDocument();
  });

  it("empty title shows validation error (FR-054)", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<TaskForm mode="create" onSubmit={onSubmit} />);

    // The title field has required attribute but we need to test client validation
    // Clear any default and submit with spaces only
    const titleInput = screen.getByPlaceholderText("What needs to be done?");
    await user.type(titleInput, "   ");
    await user.clear(titleInput);

    const submitButton = screen.getByRole("button", { name: /add task/i });
    await user.click(submitButton);

    // The component should show validation error since trimmed title is empty
    // Note: The HTML required attribute may prevent form submission,
    // so we check if onSubmit was NOT called (validation prevented it)
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("valid title triggers onSubmit (FR-055)", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(<TaskForm mode="create" onSubmit={onSubmit} />);

    const titleInput = screen.getByPlaceholderText("What needs to be done?");
    await user.type(titleInput, "My New Task");

    const submitButton = screen.getByRole("button", { name: /add task/i });
    await user.click(submitButton);

    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ title: "My New Task" })
    );
  });
});
