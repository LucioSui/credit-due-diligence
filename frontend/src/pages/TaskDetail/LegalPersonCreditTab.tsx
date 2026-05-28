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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  TextField,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FileUpload from '@/components/common/FileUpload';
// API placeholder: legal person credit management endpoints not yet available
// Using empty functions as stubs — replace once backend API is implemented
import type { ApiSuccess } from '@/types/api';

const listLegalCredit = async (_companyId: string): Promise<ApiSuccess<any[]>> => ({ data: [], code: 0, message: 'ok' });
const uploadLegalCredit = async (_companyId: string, _file: File): Promise<ApiSuccess<null>> => ({ data: null, code: 0, message: 'ok' });
const addLegalCredit = async (_companyId: string, _form: any): Promise<ApiSuccess<null>> => ({ data: null, code: 0, message: 'ok' });
const deleteLegalCredit = async (_id: string): Promise<ApiSuccess<null>> => ({ data: null, code: 0, message: 'ok' });
const getLegalCreditDetail = async (_id: string): Promise<ApiSuccess<any>> => ({ data: null, code: 0, message: 'ok' });

interface CreditRecord {
  id: string;
  name: string;
  idType: string;
  creditSource: string;
  creditAssessment: string;
  createdAt: string;
}

interface ManualCreditForm {
  name: string;
  idNumber: string;
  loanAccounts: string;
  creditCards: string;
  guaranteeInfo: string;
  overdueRecords: string;
  defaultRecords: string;
}

interface LegalPersonCreditTabProps {
  companyId: string;
}

const LegalPersonCreditTab: React.FC<LegalPersonCreditTabProps> = ({ companyId }) => {
  const [records, setRecords] = useState<CreditRecord[]>([]);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [manualOpen, setManualOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<CreditRecord | null>(null);
  const [detailData, setDetailData] = useState<any>(null);
  const [error, setError] = useState('');
  const [form, setForm] = useState<ManualCreditForm>({
    name: '',
    idNumber: '',
    loanAccounts: '',
    creditCards: '',
    guaranteeInfo: '',
    overdueRecords: '',
    defaultRecords: '',
  });

  const fetchRecords = async () => {
    try {
      const res = await listLegalCredit(companyId);
      setRecords(res.data || []);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchRecords();
  }, [companyId]);

  const handleUpload = async (file: File) => {
    try {
      await uploadLegalCredit(companyId, file);
      setUploadOpen(false);
      fetchRecords();
    } catch {
      setError('上传征信报告失败');
    }
  };

  const handleManualSubmit = async () => {
    if (!form.name || !form.idNumber) {
      setError('姓名和证件号码为必填项');
      return;
    }
    try {
      await addLegalCredit(companyId, {
        name: form.name,
        idNumber: form.idNumber,
        loanAccounts: form.loanAccounts ? JSON.parse(form.loanAccounts) : [],
        creditCards: form.creditCards ? JSON.parse(form.creditCards) : [],
        guaranteeInfo: form.guaranteeInfo ? JSON.parse(form.guaranteeInfo) : [],
        overdueRecords: form.overdueRecords ? JSON.parse(form.overdueRecords) : [],
        defaultRecords: form.defaultRecords ? JSON.parse(form.defaultRecords) : [],
      });
      setManualOpen(false);
      setForm({ name: '', idNumber: '', loanAccounts: '', creditCards: '', guaranteeInfo: '', overdueRecords: '', defaultRecords: '' });
      fetchRecords();
    } catch {
      setError('录入失败，请检查JSON格式');
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteLegalCredit(id);
      fetchRecords();
    } catch {
      setError('删除失败');
    }
  };

  const handleViewDetail = async (record: CreditRecord) => {
    setSelectedRecord(record);
    try {
      const res = await getLegalCreditDetail(record.id);
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
        <Button variant="outlined" onClick={() => setUploadOpen(true)}>
          上传征信报告
        </Button>
        <Button variant="outlined" startIcon={<EditIcon />} onClick={() => setManualOpen(true)}>
          手动录入
        </Button>
        {/* Hidden file upload trigger */}
        <Dialog open={uploadOpen} onClose={() => setUploadOpen(false)}>
          <DialogTitle>上传法人征信报告</DialogTitle>
          <DialogContent sx={{ pt: 1 }}>
            <FileUpload onUpload={handleUpload} accept=".pdf,.doc,.docx" maxSize={20} />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setUploadOpen(false)}>关闭</Button>
          </DialogActions>
        </Dialog>
      </Stack>

      {/* Credit list */}
      <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>姓名</TableCell>
              <TableCell>证件类型</TableCell>
              <TableCell>信用来源</TableCell>
              <TableCell>信用评估</TableCell>
              <TableCell>录入时间</TableCell>
              <TableCell align="center">操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {records.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
              </TableRow>
            ) : (
              records.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{r.name}</TableCell>
                  <TableCell>{r.idType}</TableCell>
                  <TableCell>{r.creditSource}</TableCell>
                  <TableCell>{r.creditAssessment}</TableCell>
                  <TableCell>{new Date(r.createdAt).toLocaleString('zh-CN')}</TableCell>
                  <TableCell align="center">
                    <IconButton size="small" color="primary" onClick={() => handleViewDetail(r)}>
                      <VisibilityIcon fontSize="small" />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(r.id)}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Manual entry dialog */}
      <Dialog open={manualOpen} onClose={() => setManualOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>手动录入法人征信</DialogTitle>
        <DialogContent sx={{ pt: 1 }}>
          <Stack spacing={2} sx={{ mt: 1 }}>
            <Stack direction="row" spacing={2}>
              <TextField
                label="姓名"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                fullWidth
                required
              />
              <TextField
                label="证件号码"
                value={form.idNumber}
                onChange={(e) => setForm({ ...form, idNumber: e.target.value })}
                fullWidth
                required
              />
            </Stack>
            <TextField
              label="信贷账户 (JSON)"
              multiline
              rows={3}
              value={form.loanAccounts}
              onChange={(e) => setForm({ ...form, loanAccounts: e.target.value })}
              fullWidth
              placeholder='[{"bankName":"XX银行","loanType":"流动资金贷款","amount":1000000}]'
            />
            <TextField
              label="信用卡账户 (JSON)"
              multiline
              rows={2}
              value={form.creditCards}
              onChange={(e) => setForm({ ...form, creditCards: e.target.value })}
              fullWidth
            />
            <TextField
              label="担保信息 (JSON)"
              multiline
              rows={2}
              value={form.guaranteeInfo}
              onChange={(e) => setForm({ ...form, guaranteeInfo: e.target.value })}
              fullWidth
            />
            <TextField
              label="逾期记录 (JSON)"
              multiline
              rows={2}
              value={form.overdueRecords}
              onChange={(e) => setForm({ ...form, overdueRecords: e.target.value })}
              fullWidth
            />
            <TextField
              label="违约记录 (JSON)"
              multiline
              rows={2}
              value={form.defaultRecords}
              onChange={(e) => setForm({ ...form, defaultRecords: e.target.value })}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setManualOpen(false)}>取消</Button>
          <Button variant="contained" onClick={handleManualSubmit}>提交</Button>
        </DialogActions>
      </Dialog>

      {/* Detail dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>法人征信详情 — {selectedRecord?.name}</DialogTitle>
        <DialogContent>
          {detailData ? (
            <Box>
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>信贷账户</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafafa' }}>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0, fontSize: '0.875rem' }}>
                      {JSON.stringify(detailData.loanAccounts || [], null, 2)}
                    </pre>
                  </Paper>
                </AccordionDetails>
              </Accordion>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>信用卡账户</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafafa' }}>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0, fontSize: '0.875rem' }}>
                      {JSON.stringify(detailData.creditCards || [], null, 2)}
                    </pre>
                  </Paper>
                </AccordionDetails>
              </Accordion>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>逾期记录</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafafa' }}>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0, fontSize: '0.875rem' }}>
                      {JSON.stringify(detailData.overdueRecords || [], null, 2)}
                    </pre>
                  </Paper>
                </AccordionDetails>
              </Accordion>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography fontWeight={600}>违约记录</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafafa' }}>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all', margin: 0, fontSize: '0.875rem' }}>
                      {JSON.stringify(detailData.defaultRecords || [], null, 2)}
                    </pre>
                  </Paper>
                </AccordionDetails>
              </Accordion>
            </Box>
          ) : (
            <Typography color="text.secondary">暂无数据</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailOpen(false)}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LegalPersonCreditTab;
