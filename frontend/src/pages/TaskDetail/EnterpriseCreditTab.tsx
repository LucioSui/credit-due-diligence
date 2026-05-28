import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Stack,
  Alert,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import FileUpload from '@/components/common/FileUpload';
import { uploadCreditReport } from '@/api/credit';

interface EnterpriseCreditTabProps {
  companyId: string;
}

const EnterpriseCreditTab: React.FC<EnterpriseCreditTabProps> = ({ companyId }) => {
  const [uploadOpen, setUploadOpen] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    // Future: call getCreditSummary(companyId, 'enterprise') to get overview data
  }, [companyId]);

  const handleUpload = async (file: File) => {
    try {
      await uploadCreditReport(companyId, file);
      setUploadOpen(false);
      setError('');
    } catch {
      setError('上传征信报告失败');
    }
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
        <Button variant="outlined" startIcon={<EditIcon />} disabled>
          手动录入
        </Button>
        <Dialog open={uploadOpen} onClose={() => setUploadOpen(false)}>
          <DialogTitle>上传企业征信报告</DialogTitle>
          <DialogContent sx={{ pt: 1 }}>
            <FileUpload onUpload={handleUpload} accept=".pdf,.doc,.docx" maxSize={20} />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setUploadOpen(false)}>关闭</Button>
          </DialogActions>
        </Dialog>
      </Stack>

      {/* Placeholder — detailed credit data API not yet available */}
      <Box sx={{ textAlign: 'center', py: 6, color: '#999' }}>
        <Typography>暂无详细企业授信数据</Typography>
        <Typography variant="body2" sx={{ mt: 1 }}>请上传征信报告以获取企业授信明细</Typography>
      </Box>
    </Box>
  );
};

export default EnterpriseCreditTab;
