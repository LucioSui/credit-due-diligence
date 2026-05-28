import api from '@/api';
import type { CreditReportSummary } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Get credit report summary by task ID */
export function getCreditSummary(
  taskId: string,
  reportType?: 'legal_person' | 'enterprise'
): Promise<ApiSuccess<CreditReportSummary>> {
  const params = reportType ? { report_type: reportType } : undefined;
  return api.get(`/tasks/${taskId}/credit/summary`, { params }).then((res) => res.data);
}

/** Upload credit report file */
export function uploadCreditReport(taskId: string, file: File): Promise<ApiSuccess<null>> {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/tasks/${taskId}/credit/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((res) => res.data);
}
