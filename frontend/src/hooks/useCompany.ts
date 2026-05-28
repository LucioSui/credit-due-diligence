import { useState, useCallback } from 'react';
import { getCompanyInfo } from '@/api/companies';
import type { CompanyInfo } from '@/types';

/** Hook for fetching company info by task ID */
export function useCompany() {
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCompanyInfo = useCallback(async (taskId: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await getCompanyInfo(taskId);
      setCompanyInfo(res.data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取公司信息失败');
    } finally {
      setLoading(false);
    }
  }, []);

  return { companyInfo, loading, error, fetchCompanyInfo };
}
