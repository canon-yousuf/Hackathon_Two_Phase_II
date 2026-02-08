export interface Task {
  id: number;
  user_id: string;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreateData {
  title: string;
  description?: string;
}

export interface TaskUpdateData {
  title?: string;
  description?: string;
}

export type StatusFilter = "all" | "pending" | "completed";
export type SortOption = "created" | "title";
