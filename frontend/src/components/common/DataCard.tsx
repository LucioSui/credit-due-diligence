import React from 'react';
import { Card, CardContent, Box, Typography } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

interface DataCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactElement;
  label?: string;
  trend?: 'up' | 'down';
  color?: string;
  level?: 'low' | 'medium' | 'high';
}

const DataCard: React.FC<DataCardProps> = ({ title, label, icon, value, trend, color, level }) => {
  const displayLabel = title || label || '';
  const iconColor = level === 'high' ? '#c62828' : level === 'medium' ? '#e65100' : color ?? '#1565C0';

  return (
    <Card
      sx={{
        height: '100%',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        borderRadius: 2,
      }}
    >
      <CardContent sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 2, height: '100%' }}>
        {icon && (
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 2,
              bgcolor: `${iconColor}15`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            <Box sx={{ color: iconColor, display: 'flex' }}>{React.cloneElement(icon as React.ReactElement, { fontSize: 'large' })}</Box>
          </Box>
        )}
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="caption" sx={{ color: '#999', display: 'block', mb: 0.5 }}>
            {displayLabel}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
            <Typography variant="h5" sx={{ fontWeight: 700, color: '#333' }}>
              {value}
            </Typography>
            {trend && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  color: trend === 'up' ? '#2e7d32' : '#c62828',
                }}
              >
                {trend === 'up' ? (
                  <TrendingUpIcon sx={{ fontSize: 18 }} />
                ) : (
                  <TrendingDownIcon sx={{ fontSize: 18 }} />
                )}
              </Box>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default DataCard;
