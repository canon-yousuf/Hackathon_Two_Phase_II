import { authClient } from "./auth-client";
import type { Task, TaskCreateData, TaskUpdateData } from "@/types/task";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchWithAuth(
  path: string,
  options: RequestInit = {}
): Promise<Task | Task[] | null> {
  const { data } = await authClient.token();
  const token = data?.token;

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Authentication expired");
  }

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(
      error.detail || `API error: ${response.status}`
    );
  }

  return response.json();
}

export const api = {
  getTasks: (
    userId: string,
    status: string = "all",
    sort: string = "created"
  ): Promise<Task[]> =>
    fetchWithAuth(
      `/api/${userId}/tasks?status=${status}&sort=${sort}`
    ) as Promise<Task[]>,

  getTask: (userId: string, taskId: number): Promise<Task> =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`) as Promise<Task>,

  createTask: (userId: string, data: TaskCreateData): Promise<Task> =>
    fetchWithAuth(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }) as Promise<Task>,

  updateTask: (
    userId: string,
    taskId: number,
    data: TaskUpdateData
  ): Promise<Task> =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }) as Promise<Task>,

  deleteTask: (userId: string, taskId: number): Promise<null> =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    }) as Promise<null>,

  toggleComplete: (userId: string, taskId: number): Promise<Task> =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    }) as Promise<Task>,
};
