import api from '@/api';
import type { RatingResult } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Calculate rating for a task */
export function calculateRating(taskId: string): Promise<ApiSuccess<RatingResult>> {
  return api.post(`/tasks/${taskId}/rating/calculate`).then((res) => res.data);
}

/** Get rating result by task ID */
export function getRatingResult(taskId: string): Promise<ApiSuccess<RatingResult>> {
  return api.get(`/tasks/${taskId}/rating`).then((res) => res.data);
}

/** Get rating history for a task */
export function getRatingHistory(taskId: string): Promise<ApiSuccess<RatingResult[]>> {
  return api.get(`/tasks/${taskId}/rating/history`).then((res) => res.data);
}
