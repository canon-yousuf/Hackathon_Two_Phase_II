"use client";

import { useState, useEffect } from "react";
import type { Task, TaskCreateData, TaskUpdateData } from "@/types/task";

interface TaskFormProps {
  mode: "create" | "edit";
  initialData?: Task;
  onSubmit: (data: TaskCreateData | TaskUpdateData) => Promise<void>;
  onCancel?: () => void;
}

export default function TaskForm({
  mode,
  initialData,
  onSubmit,
  onCancel,
}: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState("");
  const [titleError, setTitleError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (mode === "edit" && initialData) {
      setTitle(initialData.title);
      setDescription(initialData.description || "");
    } else if (mode === "create") {
      setTitle("");
      setDescription("");
    }
    setError("");
    setTitleError("");
  }, [mode, initialData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setTitleError("");

    const trimmedTitle = title.trim();

    if (!trimmedTitle) {
      setTitleError("Title is required");
      return;
    }

    if (trimmedTitle.length > 200) {
      setTitleError("Title must be 200 characters or less");
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit({
        title: trimmedTitle,
        description: description.trim() || undefined,
      });

      if (mode === "create") {
        setTitle("");
        setDescription("");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save task");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
      <div>
        <div className="flex items-center justify-between mb-1">
          <label
            htmlFor="task-title"
            className="block text-sm font-medium text-gray-700"
          >
            Title
          </label>
          <span className="text-xs text-gray-400">
            {title.length}/200
          </span>
        </div>
        <input
          id="task-title"
          type="text"
          required
          maxLength={200}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          placeholder="What needs to be done?"
        />
        {titleError && (
          <p className="mt-1 text-sm text-red-600">{titleError}</p>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between mb-1">
          <label
            htmlFor="task-description"
            className="block text-sm font-medium text-gray-700"
          >
            Description (optional)
          </label>
          <span className="text-xs text-gray-400">
            {description.length}/1000
          </span>
        </div>
        <textarea
          id="task-description"
          maxLength={1000}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
          placeholder="Add details..."
        />
      </div>

      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}

      <div className="flex gap-2">
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting
            ? mode === "create"
              ? "Adding..."
              : "Updating..."
            : mode === "create"
              ? "Add Task"
              : "Update Task"}
        </button>
        {mode === "edit" && onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
}
