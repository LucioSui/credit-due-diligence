import api from '@/api';
import type { ReportMetadata } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Generate report for a task */
export function generateReport(taskId: string): Promise<ApiSuccess<ReportMetadata>> {
  return api.post(`/tasks/${taskId}/reports/generate`).then((res) => res.data);
}

/** Get report preview by task ID */
export function getReportPreview(taskId: string): Promise<ApiSuccess<ReportMetadata>> {
  return api.get(`/tasks/${taskId}/reports/preview`).then((res) => res.data);
}

/** Download report in specified format */
export function downloadReport(taskId: string, format: 'pdf' | 'docx' = 'pdf'): Promise<void> {
  return api.get(`/tasks/${taskId}/reports/download`, {
    params: { format },
    responseType: 'blob',
  }).then((res) => {
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `report-${taskId}.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  });
}
