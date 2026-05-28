import React from 'react';
import { Stepper, Step, StepLabel, StepConnector, stepConnectorClasses, Box } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import { styled } from '@mui/material/styles';

interface StepItem {
  step: string;
  label: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
}

interface ProgressStepperProps {
  steps: StepItem[];
}

const QontoStepConnector = styled(StepConnector)(({ theme: _theme }) => ({
  [`&.${stepConnectorClasses.alternativeLabel}`]: {
    top: 16,
  },
  [`&.${stepConnectorClasses.active}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: '#2e7d32',
    },
  },
  [`&.${stepConnectorClasses.completed}`]: {
    [`& .${stepConnectorClasses.line}`]: {
      borderColor: '#2e7d32',
    },
  },
  [`& .${stepConnectorClasses.line}`]: {
    borderColor: _theme.palette.mode === 'dark' ? '#333' : '#e0e0e0',
    borderTopWidth: 2,
    borderRadius: 1,
  },
}));

const QontoStepLabel = styled(StepLabel)(() => ({
  '& .MuiStepLabel-label': {
    marginTop: 2,
    fontSize: '0.75rem',
  },
  [`& .${stepConnectorClasses.active}`]: {
    '& .MuiStepLabel-label': {
      color: '#2e7d32',
      fontWeight: 600,
    },
  },
  [`& .${stepConnectorClasses.completed}`]: {
    '& .MuiStepLabel-label': {
      color: '#2e7d32',
      fontWeight: 600,
    },
  },
}));

const ProgressStepper: React.FC<ProgressStepperProps> = ({ steps }) => {
  const activeStep = steps.findIndex((s) => s.status === 'running') >= 0
    ? steps.findIndex((s) => s.status === 'running')
    : 0;

  return (
    <Box sx={{ width: '100%' }}>
      <Stepper
        activeStep={activeStep}
        connector={<QontoStepConnector />}
        alternativeLabel
      >
        {steps.map((stepItem) => {
          const iconContent = stepItem.status === 'running' ? (
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                border: '2px solid #1565C0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: '#1565C0' }} />
            </Box>
          ) : stepItem.status === 'failed' ? (
            <ErrorIcon sx={{ fontSize: 22, color: '#c62828' }} />
          ) : stepItem.status === 'completed' ? (
            <CheckCircleIcon sx={{ fontSize: 22, color: '#2e7d32' }} />
          ) : undefined;

          return (
            <Step key={stepItem.step} active={stepItem.status === 'running'} completed={stepItem.status === 'completed'}>
              {(<QontoStepLabel
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                {...({ StepIconProps: { completed: stepItem.status === 'completed', active: stepItem.status === 'running', icon: iconContent }, label: stepItem.label } as any)}
              />)}
            </Step>
          );
        })}
      </Stepper>
    </Box>
  );
};

export default ProgressStepper;
