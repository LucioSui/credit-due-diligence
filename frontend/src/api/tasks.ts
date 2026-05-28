import api from '@/api';
import type { DueDiligenceTask, CreateTaskRequest, ScanStep } from '@/types';
import type { PageResult, ApiSuccess, TaskFilters } from '@/types/api';

/** List tasks with filters */
export function listTasks(filters: TaskFilters = {}): Promise<ApiSuccess<PageResult<DueDiligenceTask>>> {
  return api.get('/tasks', { params: filters }).then((res) => res.data);
}

/** Create a new task */
export function createTask(req: CreateTaskRequest): Promise<ApiSuccess<DueDiligenceTask>> {
  return api.post('/tasks', req).then((res) => res.data);
}

/** Get task by ID */
export function getTask(id: string): Promise<ApiSuccess<DueDiligenceTask>> {
  return api.get(`/tasks/${id}`).then((res) => res.data);
}

/** Cancel a task */
export function cancelTask(id: string): Promise<ApiSuccess<null>> {
  return api.post(`/tasks/${id}/cancel`).then((res) => res.data);
}

/** Retry a failed task */
export function retryTask(id: string): Promise<ApiSuccess<null>> {
  return api.post(`/tasks/${id}/retry`).then((res) => res.data);
}

/** Get scan progress for a task */
export function getScanProgress(id: string): Promise<ApiSuccess<Record<ScanStep, 'pending' | 'running' | 'completed' | 'failed'>>> {
  return api.get(`/tasks/${id}/progress`).then((res) => res.data);
}
