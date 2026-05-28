import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Skeleton,
} from '@mui/material';
import DataCard from '@/components/common/DataCard';
import FinancialChart from '@/components/charts/FinancialChart';
import { getFinancialIndicators } from '@/api/financial_reports';
import type { FinancialIndicator } from '@/types';

interface FinancialTabProps {
  companyId: string;
}

const fmt = (v: number | undefined) => (v != null ? v.toLocaleString() : '-');
const fmtCurrency = (v: number | undefined) => (v != null ? `¥${v.toLocaleString()}` : '-');
const fmtPercent = (v: number | undefined) => (v != null ? `${v.toFixed(2)}%` : '-');

const FinancialTab: React.FC<FinancialTabProps> = ({ companyId }) => {
  const [financials, setFinancials] = useState<FinancialIndicator[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | ''>('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    (async () => {
      try {
        const res = await getFinancialIndicators(companyId);
        const data = (res.data || []) as FinancialIndicator[];
        setFinancials(data);
        if (data.length > 0) {
          setSelectedYear(data[0].year);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    })();
  }, [companyId]);

  const current = financials.find((f) => f.year === selectedYear);

  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        <Skeleton height={80} />
        <Skeleton height={200} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Year selector */}
      <Box sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>年份</InputLabel>
          <Select
            value={selectedYear}
            label="年份"
            onChange={(e) => setSelectedYear(e.target.value as number)}
          >
            {financials.map((f) => (
              <MenuItem key={f.year} value={f.year}>{f.year}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {/* Key indicators */}
      {current && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={3}>
            <DataCard title="资产总额" value={fmtCurrency(current.total_assets)} />
          </Grid>
          <Grid item xs={3}>
            <DataCard title="负债总额" value={fmtCurrency(current.total_liabilities)} />
          </Grid>
          <Grid item xs={3}>
            <DataCard title="营业收入" value={fmtCurrency(current.revenue)} />
          </Grid>
          <Grid item xs={3}>
            <DataCard title="净利润" value={fmtCurrency(current.net_profit)} />
          </Grid>
        </Grid>
      )}

      {/* Additional ratio indicators */}
      {current && (current.roe != null || current.roa != null || current.current_ratio != null) && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          {current.roe != null && (
            <Grid item xs={4}>
              <DataCard title="净资产收益率 (ROE)" value={fmtPercent(current.roe)} />
            </Grid>
          )}
          {current.roa != null && (
            <Grid item xs={4}>
              <DataCard title="总资产收益率 (ROA)" value={fmtPercent(current.roa)} />
            </Grid>
          )}
          {current.current_ratio != null && (
            <Grid item xs={4}>
              <DataCard title="流动比率" value={current.current_ratio.toFixed(2)} />
            </Grid>
          )}
        </Grid>
      )}

      {/* Chart */}
      {financials.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <FinancialChart data={financials} />
        </Box>
      )}

      {/* Detail table */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
        财务数据明细
      </Typography>
      <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>年份</TableCell>
              <TableCell>资产总额</TableCell>
              <TableCell>负债总额</TableCell>
              <TableCell>营业收入</TableCell>
              <TableCell>净利润</TableCell>
              <TableCell>ROE</TableCell>
              <TableCell>资产负债率</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {financials.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
              </TableRow>
            ) : (
              financials.map((f) => (
                <TableRow key={f.year}>
                  <TableCell>{f.year}</TableCell>
                  <TableCell>{fmt(f.total_assets)}</TableCell>
                  <TableCell>{fmt(f.total_liabilities)}</TableCell>
                  <TableCell>{fmt(f.revenue)}</TableCell>
                  <TableCell>{fmt(f.net_profit)}</TableCell>
                  <TableCell>{fmtPercent(f.roe)}</TableCell>
                  <TableCell>{fmtPercent(f.asset_liability_ratio)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default FinancialTab;
