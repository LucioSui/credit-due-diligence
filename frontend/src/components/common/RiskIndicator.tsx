import React from 'react';
import { Box, Typography } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';

interface RiskIndicatorProps {
  level: 'high' | 'medium' | 'low';
  count?: number;
}

const riskConfig: Record<string, { color: string; icon: React.ReactElement; label: string }> = {
  high: {
    color: '#c62828',
    icon: <ErrorOutlineIcon />,
    label: '高风险',
  },
  medium: {
    color: '#e65100',
    icon: <WarningAmberIcon />,
    label: '中风险',
  },
  low: {
    color: '#2e7d32',
    icon: <CheckCircleIcon />,
    label: '低风险',
  },
};

const RiskIndicator: React.FC<RiskIndicatorProps> = ({ level, count }) => {
  const config = riskConfig[level] ?? riskConfig.medium;

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
      <Box sx={{ color: config.color }}>{config.icon}</Box>
      <Box>
        <Typography variant="body2" sx={{ fontWeight: 600, color: config.color }}>
          {config.label}
        </Typography>
        {count !== undefined && (
          <Typography variant="caption" sx={{ color: '#999' }}>
            {count} 项
          </Typography>
        )}
      </Box>
    </Box>
  );
};

export default RiskIndicator;
