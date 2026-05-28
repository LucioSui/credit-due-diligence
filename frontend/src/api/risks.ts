import api from '@/api';
import type { RiskItem, RiskCategory } from '@/types';
import type { PageResult, ApiSuccess } from '@/types/api';

/** Get risk summary by task ID */
export function getRiskSummary(taskId: string): Promise<ApiSuccess<{ total: number; high: number; medium: number; low: number }>> {
  return api.get(`/tasks/${taskId}/risks/summary`).then((res) => res.data);
}

/** Get risk items by task ID, optionally filtered by category */
export function getRiskItems(taskId: string, category?: RiskCategory): Promise<ApiSuccess<PageResult<RiskItem>>> {
  const params = category ? { category } : undefined;
  return api.get(`/tasks/${taskId}/risks`, { params }).then((res) => res.data);
}
