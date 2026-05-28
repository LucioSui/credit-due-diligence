import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Paper,
  CircularProgress,
  Alert,
  Stack,
} from '@mui/material';
import DownloadIcon from '@mui/icons-material/Download';
import { getReportPreview, downloadReport } from '@/api/reports';
import type { ReportMetadata } from '@/types';

const ReportPreview: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();
  const [report, setReport] = useState<ReportMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!reportId) return;
    setLoading(true);
    (async () => {
      try {
        const res = await getReportPreview(reportId);
        setReport(res.data);
      } catch {
        setError('获取报告失败');
      } finally {
        setLoading(false);
      }
    })();
  }, [reportId]);

  const handleDownload = async (format: 'pdf' | 'docx') => {
    if (!report) return;
    try {
      await downloadReport(report.task_id, format);
    } catch {
      setError('下载报告失败');
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !report) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error || '报告不存在'}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            {report.company_name} — 尽调报告
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            任务ID：{report.task_id.slice(0, 8)} {' | '}版本号：v{report.version} {' | '}
            状态：{report.status === 'final' ? '正式版' : '草稿'} {' | '}
            生成时间：{new Date(report.generated_at).toLocaleString('zh-CN')}
          </Typography>
        </Box>
        <Stack direction="row" spacing={1}>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('pdf')}
          >
            下载PDF
          </Button>
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('docx')}
          >
            下载DOCX
          </Button>
        </Stack>
      </Stack>

      {/* Report metadata summary */}
      <Paper sx={{ p: 3, minHeight: 400 }}>
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
          报告概要
        </Typography>
        <Stack spacing={1}>
          <Typography><strong>报告ID：</strong>{report.id}</Typography>
          <Typography><strong>任务ID：</strong>{report.task_id}</Typography>
          <Typography><strong>企业名称：</strong>{report.company_name}</Typography>
          <Typography><strong>版本：</strong>v{report.version}</Typography>
          <Typography><strong>状态：</strong>{report.status === 'final' ? '正式版' : '草稿'}</Typography>
          <Typography><strong>生成时间：</strong>{new Date(report.generated_at).toLocaleString('zh-CN')}</Typography>
        </Stack>
      </Paper>
    </Box>
  );
};

export default ReportPreview;
