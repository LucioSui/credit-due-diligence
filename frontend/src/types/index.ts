// ==================== 通用 ====================
export type PageResult<T> = { items: T[]; total: number; page: number; page_size: number };
export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed';
export type ScanStep = 'company_info' | 'risk_scan' | 'equity_scan' | 'financial_scan' | 'bank_scan' | 'credit_scan' | 'rating_calc' | 'report_gen';

// ==================== 用户/认证 ====================
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'approver' | 'supervisor' | 'viewer';
  real_name?: string;
  is_active: boolean;
  created_at: string;
}
export interface LoginRequest { username: string; password: string }
export interface TokenPayload { access_token: string; token_type: 'bearer'; user: User }

// ==================== 尽调任务 ====================
export interface DueDiligenceTask {
  id: string; company_name: string; unified_social_credit_code?: string;
  status: ScanStatus; created_by: string; created_at: string; updated_at: string;
  scan_progress?: Record<ScanStep, 'pending' | 'running' | 'completed' | 'failed'>;
  rating_result?: RatingResult;
}
export interface CreateTaskRequest { company_name: string; unified_social_credit_code?: string; remark?: string }

// ==================== 公司信息 ====================
export interface CompanyInfo {
  company_name: string; unified_social_credit_code: string;
  legal_person: string; registered_capital: string; established_date: string;
  business_scope: string; address: string; status: string;
}

// ==================== 司法风险 ====================
export type RiskCategory = 'judicial' | 'executive' | 'administrative' | 'financial' | 'other';
export interface RiskItem {
  id: string; category: RiskCategory; risk_level: 'high' | 'medium' | 'low';
  title: string; detail: string; source: string; found_date: string;
}

// ==================== 股权穿透 ====================
export interface EquityNode {
  id: string; name: string; entity_type: 'company' | 'person';
  share_ratio?: number; role?: string; children?: EquityNode[];
}
export interface EquityStructure { company_name: string; shareholders: EquityNode[]; actual_controller?: EquityNode; }

// ==================== 财务数据 ====================
export interface FinancialIndicator {
  year: number; revenue?: number; net_profit?: number; total_assets?: number;
  total_liabilities?: number; roe?: number; roa?: number; asset_liability_ratio?: number;
  current_ratio?: number; quick_ratio?: number;
}

// ==================== 银行流水 ====================
export interface BankStatementItem {
  date: string; description: string; income?: number; expense?: number; balance: number;
}

// ==================== 征信报告 ====================
export interface CreditReportSummary {
  report_type: 'legal_person' | 'enterprise'; total_loans: number;
  overdue_count: number; credit_score?: number; level: 'excellent' | 'good' | 'fair' | 'poor';
}

// ==================== 评级结果 ====================
export interface RatingDimension {
  name: string; score: number; weight: number; factors: string[];
}
export interface RatingResult {
  overall_score: number; grade: 'A' | 'B' | 'C' | 'D';
  dimensions: RatingDimension[]; recommendation: 'approve' | 'review' | 'reject';
  summary: string;
}

// ==================== 报告 ====================
export interface ReportMetadata {
  id: string; task_id: string; company_name: string;
  generated_at: string; version: string; status: 'draft' | 'final';
}
