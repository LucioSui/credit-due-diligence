import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  CircularProgress,
  Divider,
} from '@mui/material';
import RatingBadge from '@/components/common/RatingBadge';
import RatingRadar from '@/components/charts/RatingRadar';
import { getRatingResult, calculateRating } from '@/api/rating';
import type { RatingResult, RatingDimension } from '@/types/index';

interface RatingCardProps {
  companyId: string;
}

type Grade = 'A' | 'B' | 'C' | 'D';

const GRADE_COLOR: Record<Grade, 'success' | 'info' | 'warning' | 'error'> = {
  A: 'success',
  B: 'info',
  C: 'warning',
  D: 'error',
};

const RatingCard: React.FC<RatingCardProps> = ({ companyId }) => {
  const [rating, setRating] = useState<RatingResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    (async () => {
      try {
        const res = await getRatingResult(companyId);
        setRating(res.data);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    })();
  }, [companyId]);

  const handleRate = async () => {
    try {
      const res = await calculateRating(companyId);
      if (res.data) {
        setRating(res.data);
      }
    } catch {
      // ignore
    }
  };

  if (loading) {
    return (
      <Card sx={{ mt: 3, display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Card>
    );
  }

  if (!rating) {
    return (
      <Card sx={{ mt: 3 }}>
        <CardContent sx={{ textAlign: 'center', py: 3 }}>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            尚未评级
          </Typography>
          <Button variant="contained" color="primary" onClick={handleRate}>
            立即评级
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card sx={{ mt: 3 }}>
      <CardContent>
        <Typography variant="h6" fontWeight={600} sx={{ mb: 2 }}>
          评级结果
        </Typography>

        <Grid container spacing={3}>
          {/* Left — grade + score */}
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 2 }}>
              <RatingBadge grade={rating.grade} size="large" />
              <Typography variant="h4" fontWeight={700} sx={{ mt: 1, color: GRADE_COLOR[rating.grade] }}>
                {rating.overall_score.toFixed(1)}
                <Typography component="span" variant="body2" color="text.secondary">
                  {' / 100'}
                </Typography>
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                建议：{rating.recommendation === 'approve' ? '建议批准' : rating.recommendation === 'review' ? '需进一步审核' : '建议拒绝'}
              </Typography>
            </Box>
          </Grid>

          {/* Right — radar chart */}
          <Grid item xs={12} md={8}>
            <RatingRadar data={rating.dimensions} />
          </Grid>
        </Grid>

        <Divider sx={{ my: 2 }} />

        {/* Dimension breakdown table */}
        <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
          维度得分明细
        </Typography>
        <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0, mb: 2 }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>维度</TableCell>
                <TableCell align="right">权重</TableCell>
                <TableCell align="right">得分</TableCell>
                <TableCell align="right">加权得分</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rating.dimensions.map((d: RatingDimension, i: number) => (
                <TableRow key={i}>
                  <TableCell>{d.name}</TableCell>
                  <TableCell align="right">{(d.weight * 100).toFixed(0)}%</TableCell>
                  <TableCell align="right">{d.score.toFixed(1)}</TableCell>
                  <TableCell align="right">{(d.score * d.weight).toFixed(1)}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Rating summary */}
        {rating.summary && (
          <Box>
            <Typography variant="subtitle2" fontWeight={600} sx={{ mb: 1 }}>
              评级说明
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafafa' }}>
              <Typography variant="body2">{rating.summary}</Typography>
            </Paper>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default RatingCard;
