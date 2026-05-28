import React, { useState, useCallback, useRef } from 'react';
import { Box, Typography, IconButton, CircularProgress, Stack } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import DescriptionIcon from '@mui/icons-material/Description';

interface FileUploadProps {
  accept?: string;
  onUpload: (file: File) => Promise<void>;
  helperText?: string;
  maxSize?: number;
}

const FileUpload: React.FC<FileUploadProps> = ({ accept = '*/*', onUpload, helperText, maxSize }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(
    async (selectedFile: File) => {
      setFile(selectedFile);
      setError(null);
      setUploading(true);
      setProgress(0);
      try {
        await onUpload(selectedFile);
        setProgress(100);
      } catch (err) {
        setError(err instanceof Error ? err.message : '上传失败');
      } finally {
        setUploading(false);
      }
    },
    [onUpload],
  );

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (maxSize !== undefined && selectedFile.size > maxSize * 1024 * 1024) {
        setError(`文件大小不能超过 ${maxSize}MB`);
        return;
      }
      handleFileSelect(selectedFile);
    }
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const selectedFile = event.dataTransfer.files[0];
    if (selectedFile) {
      if (maxSize !== undefined && selectedFile.size > maxSize * 1024 * 1024) {
        setError(`文件大小不能超过 ${maxSize}MB`);
        return;
      }
      handleFileSelect(selectedFile);
    }
  };

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
  };

  const handleRemove = () => {
    setFile(null);
    setUploading(false);
    setProgress(0);
    setError(null);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <Box>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        onChange={handleInputChange}
        style={{ display: 'none' }}
      />
      {!file && (
        <Box
          onClick={() => inputRef.current?.click()}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          sx={{
            border: '2px dashed #bdbdbd',
            borderRadius: 2,
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            cursor: 'pointer',
            transition: 'border-color 0.2s',
            '&:hover': {
              borderColor: '#1565C0',
              bgcolor: '#f5f9ff',
            },
          }}
        >
          <CloudUploadIcon sx={{ fontSize: 48, color: '#bdbdbd', mb: 1 }} />
          <Typography variant="body2" sx={{ color: '#666', mb: 0.5 }}>
            拖拽文件到此处，或点击选择文件
          </Typography>
          {helperText && (
            <Typography variant="caption" sx={{ color: '#999' }}>
              {helperText}
            </Typography>
          )}
        </Box>
      )}
      {file && (
        <Box
          sx={{
            border: '1px solid #e0e0e0',
            borderRadius: 2,
            p: 2,
            bgcolor: '#fafafa',
          }}
        >
          <Stack direction="row" alignItems="center" spacing={2}>
            <DescriptionIcon sx={{ color: '#1565C0' }} />
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="body2" sx={{ fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {file.name}
              </Typography>
              <Typography variant="caption" sx={{ color: '#999' }}>
                {formatFileSize(file.size)}
              </Typography>
            </Box>
            {uploading && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={20} />
                <Typography variant="caption">{progress}%</Typography>
              </Box>
            )}
            {!uploading && progress === 100 && (
              <Typography variant="caption" sx={{ color: '#2e7d32' }}>
                上传完成
              </Typography>
            )}
            <IconButton size="small" onClick={handleRemove} disabled={uploading}>
              <DeleteIcon sx={{ fontSize: 18 }} />
            </IconButton>
          </Stack>
          {error && (
            <Typography variant="caption" sx={{ color: '#c62828', mt: 1, display: 'block' }}>
              {error}
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default FileUpload;
