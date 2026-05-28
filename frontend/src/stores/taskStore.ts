import { create } from 'zustand';
import type { DueDiligenceTask, CreateTaskRequest } from '@/types';
import { listTasks, getTask, createTask } from '@/api/tasks';
import type { TaskFilters } from '@/types/api';

interface TaskState {
  tasks: DueDiligenceTask[];
  currentTask: DueDiligenceTask | null;
  loading: boolean;
  total: number;
  fetchTasks: (filters?: TaskFilters) => Promise<void>;
  fetchTask: (id: string) => Promise<void>;
  createNewTask: (req: CreateTaskRequest) => Promise<DueDiligenceTask>;
  setCurrentTask: (task: DueDiligenceTask | null) => void;
}

export const useTaskStore = create<TaskState>((set) => ({
  tasks: [],
  currentTask: null,
  loading: false,
  total: 0,

  fetchTasks: async (filters?: TaskFilters) => {
    set({ loading: true });
    try {
      const res = await listTasks(filters);
      set({ tasks: res.data.items, total: res.data.total, loading: false });
    } catch (err) {
      set({ loading: false });
      throw err;
    }
  },

  fetchTask: async (id: string) => {
    set({ loading: true });
    try {
      const res = await getTask(id);
      set({ currentTask: res.data, loading: false });
    } catch (err) {
      set({ loading: false });
      throw err;
    }
  },

  createNewTask: async (req: CreateTaskRequest) => {
    const res = await createTask(req);
    const task = res.data;
    set((state) => ({ tasks: [task, ...state.tasks] }));
    return task;
  },

  setCurrentTask: (task: DueDiligenceTask | null) => {
    set({ currentTask: task });
  },
}));
