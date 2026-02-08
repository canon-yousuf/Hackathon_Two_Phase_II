"use client";

import { useState } from "react";
import type { Task } from "@/types/task";

interface TaskItemProps {
  task: Task;
  onToggle: (id: number) => void;
  onEdit: (task: Task) => void;
  onDelete: (id: number) => void;
}

export default function TaskItem({
  task,
  onToggle,
  onEdit,
  onDelete,
}: TaskItemProps) {
  const [isToggling, setIsToggling] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleToggle = async () => {
    setIsToggling(true);
    try {
      await onToggle(task.id);
    } finally {
      setIsToggling(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Delete this task?")) return;
    setIsDeleting(true);
    try {
      await onDelete(task.id);
    } finally {
      setIsDeleting(false);
    }
  };

  const truncatedDescription =
    task.description && task.description.length > 150
      ? task.description.slice(0, 150) + "..."
      : task.description;

  const formattedDate = new Date(task.created_at).toLocaleDateString();

  return (
    <div
      className={`rounded-lg border p-4 ${
        task.completed
          ? "border-gray-200 bg-gray-50"
          : "border-gray-300 bg-white"
      }`}
    >
      <div className="flex items-start gap-3">
        <button
          onClick={handleToggle}
          disabled={isToggling}
          className="mt-0.5 flex-shrink-0"
          aria-label={task.completed ? "Mark incomplete" : "Mark complete"}
        >
          {isToggling ? (
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
          ) : (
            <div
              className={`flex h-5 w-5 items-center justify-center rounded border-2 ${
                task.completed
                  ? "border-green-500 bg-green-500 text-white"
                  : "border-gray-300"
              }`}
            >
              {task.completed && (
                <svg
                  className="h-3 w-3"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={3}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              )}
            </div>
          )}
        </button>

        <div className="flex-1 min-w-0">
          <h3
            className={`font-medium ${
              task.completed
                ? "text-gray-400 line-through"
                : "text-gray-900"
            }`}
          >
            {task.title}
          </h3>
          {truncatedDescription && (
            <p
              className={`mt-1 text-sm ${
                task.completed ? "text-gray-400" : "text-gray-600"
              }`}
            >
              {truncatedDescription}
            </p>
          )}
          <p className="mt-1 text-xs text-gray-400">{formattedDate}</p>
        </div>

        <div className="flex gap-2 flex-shrink-0">
          <button
            onClick={() => onEdit(task)}
            className="rounded px-2 py-1 text-sm text-blue-600 hover:bg-blue-50 transition-colors"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="rounded px-2 py-1 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50 transition-colors"
          >
            {isDeleting ? "..." : "Delete"}
          </button>
        </div>
      </div>
    </div>
  );
}
