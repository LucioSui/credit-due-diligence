import React from 'react';
import { Chip, Typography, Box } from '@mui/material';

interface RatingBadgeProps {
  grade: 'A' | 'B' | 'C' | 'D';
  score?: number;
  size?: 'small' | 'medium' | 'large';
}

const gradeConfig: Record<string, { bg: string; color: string; label: string }> = {
  A: { bg: '#e8f5e9', color: '#2e7d32', label: '优秀' },
  B: { bg: '#e3f2fd', color: '#1565c0', label: '良好' },
  C: { bg: '#fff3e0', color: '#e65100', label: '一般' },
  D: { bg: '#ffebee', color: '#c62828', label: '较差' },
};

const sizeHeight: Record<string, number> = { small: 28, medium: 32, large: 36 };
const sizeCircle: Record<string, number> = { small: 22, medium: 26, large: 28 };

const RatingBadge: React.FC<RatingBadgeProps> = ({ grade, score, size = 'medium' }) => {
  const config = gradeConfig[grade] ?? gradeConfig.B;

  return (
    <Chip
      label={
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: sizeCircle[size],
              height: sizeCircle[size],
              borderRadius: '50%',
              bgcolor: config.color,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant={size === 'small' ? 'caption' : 'body2'} sx={{ color: '#fff', fontWeight: 700 }}>
              {grade}
            </Typography>
          </Box>
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: config.color }}>
              {config.label}
            </Typography>
            {score !== undefined && (
              <Typography variant="caption" sx={{ color: '#999' }}>
                {score}分
              </Typography>
            )}
          </Box>
        </Box>
      }
      sx={{
        bgcolor: config.bg,
        border: `1px solid ${config.color}30`,
        height: sizeHeight[size],
      }}
    />
  );
};

export default RatingBadge;
