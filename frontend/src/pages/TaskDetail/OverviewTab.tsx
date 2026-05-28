import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Typography,
} from '@mui/material';
import DataCard from '@/components/common/DataCard';
import RatingBadge from '@/components/common/RatingBadge';
import { getRiskSummary } from '@/api/risks';
import { getRatingResult } from '@/api/rating';
import type { CompanyInfo, DueDiligenceTask } from '@/types/index';

interface OverviewTabProps {
  company: CompanyInfo;
  task: DueDiligenceTask;
}

const OverviewTab: React.FC<OverviewTabProps> = ({ company, task }) => {
  const [riskTotal, setRiskTotal] = useState(0);
  const [overallScore, setOverallScore] = useState<number | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const riskRes = await getRiskSummary(task.id);
        setRiskTotal(riskRes.data.total);
      } catch { /* ignore */ }
      try {
        const ratingRes = await getRatingResult(task.id);
        setOverallScore(ratingRes.data.overall_score);
      } catch { /* ignore */ }
    })();
  }, [task.id]);

  return (
    <Box>
      <Grid container spacing={3}>
        {/* Left — Company info */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
            企业信息
          </Typography>
          <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
            <Table size="small">
              <TableBody>
                {[
                  ['企业名称', company.company_name],
                  ['统一信用代码', company.unified_social_credit_code],
                  ['法定代表人', company.legal_person || '—'],
                  ['注册资本', company.registered_capital || '—'],
                  ['成立日期', company.established_date || '—'],
                  ['经营状态', company.status || '—'],
                  ['经营范围', company.business_scope || '—'],
                  ['注册地址', company.address || '—'],
                ].map(([label, value]) => (
                  <TableRow key={label as string}>
                    <TableCell sx={{ fontWeight: 500, width: 120, color: '#666' }}>{label}</TableCell>
                    <TableCell>{value as React.ReactNode}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>

        {/* Right — Task info */}
        <Grid item xs={12} md={6}>
          <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
            任务信息
          </Typography>
          <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
            <Table size="small">
              <TableBody>
                {[
                  ['任务ID', task.id],
                  ['创建时间', new Date(task.created_at).toLocaleString('zh-CN')],
                  ['状态', task.status],
                  ['创建人', task.created_by],
                ].map(([label, value]) => (
                  <TableRow key={label as string}>
                    <TableCell sx={{ fontWeight: 500, width: 120, color: '#666' }}>{label}</TableCell>
                    <TableCell>{value as React.ReactNode}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {/* Quick stats */}
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5 }}>
              快速概览
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <DataCard title="司法风险数" value={riskTotal.toString()} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <DataCard title="评分" value={overallScore !== null ? overallScore.toFixed(1) : '—'} />
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box sx={{ p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Typography variant="caption" color="text.secondary">评级</Typography>
                  <Box sx={{ mt: 1 }}>
                    {task.rating_result ? (
                      <RatingBadge grade={task.rating_result.grade} size="large" />
                    ) : (
                      <Typography variant="body2" color="text.secondary">尚未评级</Typography>
                    )}
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <DataCard title="扫描进度" value={task.scan_progress ? `${Object.values(task.scan_progress).filter((s) => s === 'completed').length}/${Object.keys(task.scan_progress).length}` : '—'} />
              </Grid>
            </Grid>
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OverviewTab;
