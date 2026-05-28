import api from '@/api';
import type { CompanyInfo } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Get company info by task ID */
export function getCompanyInfo(taskId: string): Promise<ApiSuccess<CompanyInfo>> {
  return api.get(`/tasks/${taskId}/company`).then((res) => res.data);
}
