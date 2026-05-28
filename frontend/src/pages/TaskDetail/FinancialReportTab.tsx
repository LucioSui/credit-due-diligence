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
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Alert,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import CompareArrowsIcon from '@mui/icons-material/CompareArrows';
import FileUpload from '@/components/common/FileUpload';
import ReportCompareChart from '@/components/charts/ReportCompareChart';
// API placeholder: financial report management endpoints not yet available
// Using empty functions as stubs — replace once backend API is implemented
import type { ApiSuccess } from '@/types/api';

const listFinancialReports = async (_companyId: string): Promise<ApiSuccess<any[]>> => ({ data: [], code: 0, message: 'ok' });
const uploadFinancialReport = async (_companyId: string, _file: File): Promise<ApiSuccess<null>> => ({ data: null, code: 0, message: 'ok' });
const deleteFinancialReport = async (_id: string): Promise<ApiSuccess<null>> => ({ data: null, code: 0, message: 'ok' });
const getFinancialReportDetail = async (_id: string): Promise<ApiSuccess<any>> => ({ data: null, code: 0, message: 'ok' });

interface ReportItem {
  id: string;
  reportType: string;
  reportPeriod: string;
  fileName: string;
  parseStatus: 'pending' | 'parsed' | 'failed';
  uploadedAt: string;
}

interface FinancialReportTabProps {
  companyId: string;
}

const STATUS_CONFIG: Record<string, { label: string; color: 'default' | 'info' | 'success' | 'error' }> = {
  pending: { label: '解析中', color: 'info' },
  parsed: { label: '解析成功', color: 'success' },
  failed: { label: '解析失败', color: 'error' },
};

const FinancialReportTab: React.FC<FinancialReportTabProps> = ({ companyId }) => {
  const [reports, setReports] = useState<ReportItem[]>([]);
  const [detailOpen, setDetailOpen] = useState(false);
  const [compareOpen, setCompareOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<ReportItem | null>(null);
  const [detailData, setDetailData] = useState<any>(null);
  const [error, setError] = useState('');

  const fetchReports = async () => {
    try {
      const res = await listFinancialReports(companyId);
      setReports(res.data || []);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchReports();
  }, [companyId]);

  const handleUpload = async (file: File) => {
    try {
      await uploadFinancialReport(companyId, file);
      fetchReports();
    } catch {
      setError('上传财报失败');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteFinancialReport(id);
      fetchReports();
    } catch {
      setError('删除失败');
    }
  };

  const handleViewDetail = async (report: ReportItem) => {
    setSelectedReport(report);
    try {
      const res = await getFinancialReportDetail(report.id);
      setDetailData(res.data);
    } catch {
      setDetailData(null);
    }
    setDetailOpen(true);
  };

  return (
    <Box>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>
      )}

      {/* Actions */}
      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <FileUpload onUpload={handleUpload} accept=".pdf,.xlsx,.xls" maxSize={20} />
        <Button
          variant="outlined"
          startIcon={<CompareArrowsIcon />}
          onClick={() => setCompareOpen(true)}
          disabled={reports.filter((r) => r.parseStatus === 'parsed').length < 2}
        >
          多期对比
        </Button>
      </Stack>

      {/* Report list */}
      <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>报告类型</TableCell>
              <TableCell>报告期间</TableCell>
              <TableCell>文件名</TableCell>
              <TableCell>解析状态</TableCell>
              <TableCell>上传时间</TableCell>
              <TableCell align="center">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {reports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
              </TableRow>
            ) : (
              reports.map((r) => {
                const st = STATUS_CONFIG[r.parseStatus] || STATUS_CONFIG.pending;
                return (
                  <TableRow key={r.id}>
                    <TableCell>{r.reportType}</TableCell>
                    <TableCell>{r.reportPeriod}</TableCell>
                    <TableCell>{r.fileName}</TableCell>
                    <TableCell><Chip label={st.label} color={st.color} size="small" /></TableCell>
                    <TableCell>{new Date(r.uploadedAt).toLocaleString('zh-CN')}</TableCell>
                    <TableCell align="center">
                      <IconButton size="small" color="primary" onClick={() => handleViewDetail(r)}>
                        <VisibilityIcon fontSize="small" />
                      </IconButton>
                      <IconButton size="small" color="error" onClick={() => handleDelete(r.id)}>
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Detail dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>财报详情 — {selectedReport?.fileName}</DialogTitle>
        <DialogContent>
          {detailData ? (
            <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#fafafa' }}>
              <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0, fontSize: '0.875rem' }}>
                {JSON.stringify(detailData, null, 2)}
              </pre>
            </Paper>
          ) : (
            <Typography color="text.secondary">暂无解析数据</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>

      {/* Compare dialog */}
      <Dialog open={compareOpen} onClose={() => setCompareOpen(false)} maxWidth="lg" fullWidth>
        <DialogTitle>多期财报对比</DialogTitle>
        <DialogContent>
          <ReportCompareChart data={reports.filter((r) => r.parseStatus === 'parsed').map((r) => r.id)} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompareOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FinancialReportTab;
