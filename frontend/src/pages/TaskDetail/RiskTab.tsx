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
  Tabs,
  Tab,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  Chip,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DataCard from '@/components/common/DataCard';
import { getRiskItems } from '@/api/risks';
import type { RiskItem, RiskCategory } from '@/types/index';

interface RiskTabProps {
  companyId: string;
}

const CATEGORY_LABELS: Record<RiskCategory, string> = {
  judicial: '诉讼',
  executive: '失信',
  administrative: '处罚',
  financial: '财务',
  other: '其他',
};

const RISK_LEVEL_LABEL: Record<RiskItem['risk_level'], string> = {
  high: '高',
  medium: '中',
  low: '低',
};

type RiskFilter = '' | RiskCategory;

const RiskTab: React.FC<RiskTabProps> = ({ companyId }) => {
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [filter, setFilter] = useState<RiskFilter>('');
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedRisk, setSelectedRisk] = useState<RiskItem | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await getRiskItems(companyId);
        setRisks((res.data?.items ?? []) as RiskItem[]);
      } catch {
        // ignore
      }
    })();
  }, [companyId]);

  const counts = {
    judicial: risks.filter((r) => r.category === 'judicial').length,
    executive: risks.filter((r) => r.category === 'executive').length,
    administrative: risks.filter((r) => r.category === 'administrative').length,
    financial: risks.filter((r) => r.category === 'financial').length,
  };

  const filtered = filter ? risks.filter((r) => r.category === filter) : risks;

  const handleExpand = (risk: RiskItem) => {
    setSelectedRisk(risk);
    setDetailOpen(true);
  };

  return (
    <Box>
      {/* Stats */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={3}>
          <DataCard title="司法诉讼" value={String(counts.judicial)} level="medium" />
        </Grid>
        <Grid item xs={3}>
          <DataCard title="失信" value={String(counts.executive)} level="high" />
        </Grid>
        <Grid item xs={3}>
          <DataCard title="行政处罚" value={String(counts.administrative)} level="medium" />
        </Grid>
        <Grid item xs={3}>
          <DataCard title="财务风险" value={String(counts.financial)} level="medium" />
        </Grid>
      </Grid>

      {/* Filter tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
        <Tabs value={filter} onChange={(_, v) => setFilter(v as RiskFilter)} textColor="primary">
          <Tab label="全部" value="" />
          <Tab label="司法诉讼" value="judicial" />
          <Tab label="失信" value="executive" />
          <Tab label="行政处罚" value="administrative" />
          <Tab label="财务风险" value="financial" />
        </Tabs>
      </Box>

      {/* Risk list */}
      <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>风险类型</TableCell>
              <TableCell>风险等级</TableCell>
              <TableCell>详情</TableCell>
              <TableCell>发现时间</TableCell>
              <TableCell align="center">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
              </TableRow>
            ) : (
              filtered.map((risk) => (
                <React.Fragment key={risk.id}>
                  <TableRow hover>
                    <TableCell>{CATEGORY_LABELS[risk.category] || risk.category}</TableCell>
                    <TableCell>
                      <Chip
                        label={RISK_LEVEL_LABEL[risk.risk_level]}
                        color={risk.risk_level === 'high' ? 'error' : risk.risk_level === 'medium' ? 'warning' : 'default'}
                        size="small"
                      />
                    </TableCell>
                    <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {risk.detail.slice(0, 80)}{risk.detail.length > 80 ? '...' : ''}
                    </TableCell>
                    <TableCell>{new Date(risk.found_date).toLocaleString('zh-CN')}</TableCell>
                    <TableCell align="center">
                      <IconButton size="small" onClick={() => handleExpand(risk)}>
                        <ExpandMoreIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                </React.Fragment>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Detail dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>风险详情</DialogTitle>
        <DialogContent>
          {selectedRisk && (
            <Box>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                类型：{CATEGORY_LABELS[selectedRisk.category] || selectedRisk.category}
                {' | '}等级：{RISK_LEVEL_LABEL[selectedRisk.risk_level]}
                {' | '}发现时间：{new Date(selectedRisk.found_date).toLocaleString('zh-CN')}
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: '#fafafa' }}>
                <Typography variant="body2">{selectedRisk.detail}</Typography>
              </Paper>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default RiskTab;
