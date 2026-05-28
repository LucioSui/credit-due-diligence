import { useCallback } from 'react';
import { useTaskStore } from '@/stores/taskStore';
import type { CreateTaskRequest } from '@/types';
import type { TaskFilters } from '@/types/api';

/** Hook for task list and current task state */
export function useTask() {
  const tasks = useTaskStore((s) => s.tasks);
  const currentTask = useTaskStore((s) => s.currentTask);
  const loading = useTaskStore((s) => s.loading);
  const total = useTaskStore((s) => s.total);
  const fetchTasks = useTaskStore((s) => s.fetchTasks);
  const createNewTask = useTaskStore((s) => s.createNewTask);
  const setCurrentTask = useTaskStore((s) => s.setCurrentTask);

  const fetchTasksWithFilters = useCallback(
    (filters?: TaskFilters) => fetchTasks(filters),
    [fetchTasks]
  );

  const createTask = useCallback(
    async (req: CreateTaskRequest) => {
      return createNewTask(req);
    },
    [createNewTask]
  );

  return {
    tasks,
    currentTask,
    loading,
    total,
    fetchTasks: fetchTasksWithFilters,
    createTask,
    setCurrentTask,
  };
}
