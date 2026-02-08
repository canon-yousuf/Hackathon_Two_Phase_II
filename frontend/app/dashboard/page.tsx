"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/hooks/useAuth";
import { api } from "@/lib/api";
import type { Task, TaskCreateData, TaskUpdateData, StatusFilter, SortOption } from "@/types/task";
import Navbar from "@/components/Navbar";
import TaskForm from "@/components/TaskForm";
import TaskFilter from "@/components/TaskFilter";
import TaskList from "@/components/TaskList";

export default function DashboardPage() {
  const { session } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [sortOption, setSortOption] = useState<SortOption>("created");
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  const userId = session?.user?.id;

  const fetchTasks = useCallback(async () => {
    if (!userId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getTasks(userId, statusFilter, sortOption);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setIsLoading(false);
    }
  }, [userId, statusFilter, sortOption]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const handleCreate = async (data: TaskCreateData | TaskUpdateData) => {
    if (!userId) return;
    await api.createTask(userId, data as TaskCreateData);
    await fetchTasks();
  };

  const handleUpdate = async (data: TaskCreateData | TaskUpdateData) => {
    if (!userId || !editingTask) return;
    await api.updateTask(userId, editingTask.id, data as TaskUpdateData);
    setEditingTask(null);
    await fetchTasks();
  };

  const handleDelete = async (id: number) => {
    if (!userId) return;
    await api.deleteTask(userId, id);
    await fetchTasks();
  };

  const handleToggle = async (id: number) => {
    if (!userId) return;
    await api.toggleComplete(userId, id);
    await fetchTasks();
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
  };

  const handleCancelEdit = () => {
    setEditingTask(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="mx-auto max-w-4xl p-6 space-y-6">
        <TaskForm
          mode={editingTask ? "edit" : "create"}
          initialData={editingTask ?? undefined}
          onSubmit={editingTask ? handleUpdate : handleCreate}
          onCancel={editingTask ? handleCancelEdit : undefined}
        />

        <TaskFilter
          statusFilter={statusFilter}
          sortOption={sortOption}
          onStatusChange={setStatusFilter}
          onSortChange={setSortOption}
        />

        <TaskList
          tasks={tasks}
          isLoading={isLoading}
          error={error}
          onRetry={fetchTasks}
          onToggle={handleToggle}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </main>
    </div>
  );
}
