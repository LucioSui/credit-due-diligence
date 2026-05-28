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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Skeleton,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
// API placeholder: shareholder/executive/investment endpoints not yet available
// Using empty functions as stubs — replace once backend API is implemented
import type { ApiSuccess } from '@/types/api';

const getShareholders = async (_companyId: string): Promise<ApiSuccess<any[]>> => ({ data: [], code: 0, message: 'ok' });
const getExecutives = async (_companyId: string): Promise<ApiSuccess<any[]>> => ({ data: [], code: 0, message: 'ok' });
const getInvestments = async (_companyId: string): Promise<ApiSuccess<any[]>> => ({ data: [], code: 0, message: 'ok' });

interface Shareholder {
  name: string;
  ratio: string;
  amount: string;
  type: string;
}

interface Executive {
  name: string;
  position: string;
  status: string;
}

interface Investment {
  name: string;
  ratio: string;
  status: string;
}

interface ShareholdingTabProps {
  companyId: string;
}

const ShareholdingTab: React.FC<ShareholdingTabProps> = ({ companyId }) => {
  const [shareholders, setShareholders] = useState<Shareholder[]>([]);
  const [executives, setExecutives] = useState<Executive[]>([]);
  const [investments, setInvestments] = useState<Investment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    (async () => {
      try {
        const [shRes, exRes, invRes] = await Promise.all([
          getShareholders(companyId),
          getExecutives(companyId),
          getInvestments(companyId),
        ]);
        setShareholders(shRes.data || []);
        setExecutives(exRes.data || []);
        setInvestments(invRes.data || []);
      } catch {
        // ignore errors, show empty
      } finally {
        setLoading(false);
      }
    })();
  }, [companyId]);

  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        <Skeleton height={60} />
        <Skeleton height={120} />
      </Box>
    );
  }

  return (
    <Box>
      {/* 股东信息 */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={600}>股东信息</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>股东名称</TableCell>
                  <TableCell>持股比例</TableCell>
                  <TableCell>认缴出资额</TableCell>
                  <TableCell>股东类型</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {shareholders.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={4} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
                  </TableRow>
                ) : (
                  shareholders.map((s, i) => (
                    <TableRow key={i}>
                      <TableCell>{s.name}</TableCell>
                      <TableCell>{s.ratio}</TableCell>
                      <TableCell>{s.amount}</TableCell>
                      <TableCell>{s.type}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* 高管信息 */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={600}>高管信息</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>姓名</TableCell>
                  <TableCell>职务</TableCell>
                  <TableCell>任职状态</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {executives.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
                  </TableRow>
                ) : (
                  executives.map((e, i) => (
                    <TableRow key={i}>
                      <TableCell>{e.name}</TableCell>
                      <TableCell>{e.position}</TableCell>
                      <TableCell>{e.status}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* 对外投资 */}
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography fontWeight={600}>对外投资</Typography>
        </AccordionSummary>
        <AccordionDetails sx={{ p: 0 }}>
          <TableContainer component={Paper} variant="outlined" sx={{ boxShadow: 0 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>被投企业</TableCell>
                  <TableCell>持股比例</TableCell>
                  <TableCell>投资状态</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {investments.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} align="center" sx={{ py: 3, color: '#999' }}>暂无数据</TableCell>
                  </TableRow>
                ) : (
                  investments.map((inv, i) => (
                    <TableRow key={i}>
                      <TableCell>{inv.name}</TableCell>
                      <TableCell>{inv.ratio}</TableCell>
                      <TableCell>{inv.status}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default ShareholdingTab;
