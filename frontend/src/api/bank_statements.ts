import api from '@/api';
import type { BankStatementItem } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Get bank statements by task ID */
export function getBankStatements(taskId: string): Promise<ApiSuccess<BankStatementItem[]>> {
  return api.get(`/tasks/${taskId}/bank-statements`).then((res) => res.data);
}

/** Upload bank statement file */
export function uploadBankStatement(taskId: string, file: File): Promise<ApiSuccess<null>> {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/tasks/${taskId}/bank-statements/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then((res) => res.data);
}
