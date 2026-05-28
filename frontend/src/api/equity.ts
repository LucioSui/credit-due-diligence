import api from '@/api';
import type { EquityStructure, EquityNode } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Get equity structure by task ID */
export function getEquityStructure(taskId: string): Promise<ApiSuccess<EquityStructure>> {
  return api.get(`/tasks/${taskId}/equity`).then((res) => res.data);
}

/** Get actual controller by task ID */
export function getActualController(taskId: string): Promise<ApiSuccess<EquityNode | null>> {
  return api.get(`/tasks/${taskId}/equity/controller`).then((res) => res.data);
}
