import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
  Grid,
  Alert,
} from '@mui/material';
import FileUpload from '@/components/common/FileUpload';
import BankStatementChart from '@/components/charts/BankStatementChart';
import DataCard from '@/components/common/DataCard';
import { getBankStatements, uploadBankStatement } from '@/api/bank_statements';
import type { BankStatementItem } from '@/types';

interface BankStatementTabProps {
  companyId: string;
}

const fmtMoney = (v: number | undefined) => (v != null ? `¥${v.toLocaleString()}` : '-');

const BankStatementTab: React.FC<BankStatementTabProps> = ({ companyId }) => {
  const [statements, setStatements] = useState<BankStatementItem[]>([]);
  const [error, setError] = useState('');

  const fetchStatements = async () => {
    try {
      const res = await getBankStatements(companyId);
      setStatements(res.data || []);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchStatements();
  }, [companyId]);

  const handleUpload = async (file: File) => {
    try {
      await uploadBankStatement(companyId, file);
      fetchStatements();
    } catch {
      setError('上传流水失败');
    }
  };

  const totalIncome = statements.reduce((sum, s) => sum + (s.income || 0), 0);
  const totalExpense = statements.reduce((sum, s) => sum + (s.expense || 0), 0);

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>
      )}

      {/* Actions */}
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <FileUpload onUpload={handleUpload} accept=".xlsx,.xls,.csv" maxSize={20} />
      </Stack>

      {/* Summary cards */}
      {statements.length > 0 && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={4}>
            <DataCard title="流入总额" value={fmtMoney(totalIncome)} />
          </Grid>
          <Grid item xs={4}>
            <DataCard title="流出总额" value={fmtMoney(totalExpense)} />
          </Grid>
          <Grid item xs={4}>
            <DataCard title="交易笔数" value={String(statements.length)} />
          </Grid>
        </Grid>
      )}

      {/* Chart */}
      {statements.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <BankStatementChart data={statements} />
        </Box>
      )}

      {/* Statement detail table */}
      <Typography variant="h6" fontWeight={600} sx={{ mb: 1 }}>
        流水明细
      </Typography>
      <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>日期</TableCell>
              <TableCell>摘要</TableCell>
              <TableCell>收入</TableCell>
              <TableCell>支出</TableCell>
              <TableCell>余额</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {statements.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
              </TableRow>
            ) : (
              statements.map((s, i) => (
                <TableRow key={i}>
                  <TableCell>{s.date}</TableCell>
                  <TableCell>{s.description}</TableCell>
                  <TableCell>{fmtMoney(s.income)}</TableCell>
                  <TableCell>{fmtMoney(s.expense)}</TableCell>
                  <TableCell>{fmtMoney(s.balance)}</TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default BankStatementTab;
