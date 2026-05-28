import type { PageResult } from './index';

export interface ApiSuccess<T = any> { code: 0; message: string; data: T }
export interface ApiError { code: number; message: string; data?: never }
export type ApiResponse<T = any> = ApiSuccess<T> | ApiError;

// Pagination params
export interface PaginationParams { page?: number; page_size?: number }

// Task filters
export interface TaskFilters extends PaginationParams {
  status?: 'pending' | 'running' | 'completed' | 'failed';
  company_name?: string; start_date?: string; end_date?: string;
}

// Rating request
export interface RatingRequest {
  risk_score?: number; financial_score?: number; credit_score?: number;
  operation_score?: number; equity_score?: number; compliance_score?: number;
}

export type { PageResult };
