import api from '@/api';
import type { FinancialIndicator } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Get financial indicators by task ID */
export function getFinancialIndicators(taskId: string): Promise<ApiSuccess<FinancialIndicator[]>> {
  return api.get(`/tasks/${taskId}/financial/indicators`).then((res) => res.data);
}

/** Get detailed financial report for a specific year */
export function getFinancialReport(taskId: string, year?: number): Promise<ApiSuccess<FinancialIndicator>> {
  const params = year ? { year } : undefined;
  return api.get(`/tasks/${taskId}/financial/report`, { params }).then((res) => res.data);
}
