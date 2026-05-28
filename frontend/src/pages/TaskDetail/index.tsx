import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Breadcrumbs,
  Link,
  Button,
  Chip,
  Stack,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { getTask, getScanProgress } from '@/api/tasks';
import { getCompanyInfo } from '@/api/companies';
import ProgressStepper from '@/components/common/ProgressStepper';
import OverviewTab from './OverviewTab';
import ShareholdingTab from './ShareholdingTab';
import RiskTab from './RiskTab';
import FinancialTab from './FinancialTab';
import FinancialReportTab from './FinancialReportTab';
import BankStatementTab from './BankStatementTab';
import LegalPersonCreditTab from './LegalPersonCreditTab';
import EnterpriseCreditTab from './EnterpriseCreditTab';
import EquityTab from './EquityTab';
import RatingCard from './RatingCard';
import type { DueDiligenceTask, CompanyInfo } from '@/types/index';

const STATUS_LABEL: Record<string, string> = {
  pending: '待扫描',
  running: '扫描中',
  completed: '已完成',
  failed: '失败',
};

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, index, value }) => (
  <Box role="tabpanel" hidden={value !== index} sx={{ pt: 2 }}>
    {value === index && <Box sx={{ pb: 3 }}>{children}</Box>}
  </Box>
);

const TABS = [
  '概览', '工商数据', '司法风险', '工商财报',
  '上传财报', '银行流水', '法人征信', '企业征信', '股权穿透',
];

const TaskDetail: React.FC = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<DueDiligenceTask | null>(null);
  const [company, setCompany] = useState<CompanyInfo | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [scanLoading, setScanLoading] = useState(false);

  const fetchDetail = useCallback(async () => {
    if (!taskId) return;
    setLoading(true);
    try {
      const res = await getTask(taskId);
      setTask(res.data);
      try {
        const compRes = await getCompanyInfo(taskId);
        setCompany(compRes.data);
      } catch {
        // company info not yet available
      }
    } catch {
      setError('获取任务详情失败');
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    fetchDetail();
  }, [fetchDetail]);

  const handleStartScan = async () => {
    if (!taskId) return;
    setScanLoading(true);
    try {
      await getScanProgress(taskId);
      fetchDetail();
    } catch {
      setError('启动扫描失败');
    } finally {
      setScanLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '40vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error && !task) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  const scanning = task?.status === 'running';
  const pending = task?.status === 'pending';

  return (
    <Box sx={{ p: 3 }}>
      {/* Breadcrumb */}
      <Breadcrumbs sx={{ mb: 2 }}>
        <Link underline="hover" onClick={() => navigate('/dashboard')} sx={{ cursor: 'pointer' }}>
          工作台
        </Link>
        <Typography color="text.secondary">{task?.company_name}</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Stack direction="row" alignItems="center" spacing={2} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/dashboard')} size="small">
          返回
        </Button>
        <Typography variant="h5" fontWeight={600} sx={{ flex: 1 }}>
          {task?.company_name}
        </Typography>
        <Chip label={STATUS_LABEL[task?.status || ''] || task?.status} size="small" />
        {pending && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<PlayArrowIcon />}
            onClick={handleStartScan}
            disabled={scanLoading}
          >
            {scanLoading ? <CircularProgress size={20} /> : '开始扫描'}
          </Button>
        )}
      </Stack>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Progress stepper for scanning */}
      {scanning && (
        <Box sx={{ mb: 3 }}>
          <ProgressStepper
            steps={[
              { step: '1', label: '工商数据', status: 'completed', progress: 100 },
              { step: '2', label: '司法风险', status: 'completed', progress: 100 },
              { step: '3', label: '股权穿透', status: 'running', progress: 50 },
              { step: '4', label: '工商财报', status: 'pending', progress: 0 },
              { step: '5', label: '企业评级', status: 'pending', progress: 0 },
            ]}
          />
        </Box>
      )}

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
          {TABS.map((label) => (
            <Tab label={label} key={label} />
          ))}
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        {company && task && <OverviewTab company={company} task={task} />}
      </TabPanel>
      <TabPanel value={tabValue} index={1}>
        {taskId && <ShareholdingTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={2}>
        {taskId && <RiskTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={3}>
        {taskId && <FinancialTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={4}>
        {taskId && <FinancialReportTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={5}>
        {taskId && <BankStatementTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={6}>
        {taskId && <LegalPersonCreditTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={7}>
        {taskId && <EnterpriseCreditTab companyId={taskId} />}
      </TabPanel>
      <TabPanel value={tabValue} index={8}>
        {taskId && <EquityTab companyId={taskId} />}
      </TabPanel>

      {/* Rating Card */}
      {taskId && <RatingCard companyId={taskId} />}
    </Box>
  );
};

export default TaskDetail;
