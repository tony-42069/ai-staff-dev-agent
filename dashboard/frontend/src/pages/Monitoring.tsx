import React, { useState } from 'react';
import { Box, Tab, Tabs, Typography, Paper } from '@mui/material';
import MonitoringDashboard from '../components/Monitoring/MonitoringDashboard';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`monitoring-tabpanel-${index}`}
      aria-labelledby={`monitoring-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `monitoring-tab-${index}`,
    'aria-controls': `monitoring-tabpanel-${index}`,
  };
}

const MonitoringPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ width: '100%', height: '100%', overflow: 'auto' }}>
      <Paper sx={{ borderRadius: 0 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            aria-label="monitoring tabs"
            variant="scrollable"
            scrollButtons="auto"
          >
            <Tab label="System" {...a11yProps(0)} />
            <Tab label="Agents" {...a11yProps(1)} />
            <Tab label="Projects" {...a11yProps(2)} />
            <Tab label="Operations" {...a11yProps(3)} />
            <Tab label="Resources" {...a11yProps(4)} />
          </Tabs>
        </Box>
      </Paper>

      <TabPanel value={tabValue} index={0}>
        <MonitoringDashboard />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Agent Monitoring
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Agent-specific metrics and performance monitoring will be implemented here.
            This will include:
            - Active agents and their status
            - Agent performance metrics
            - Resource usage per agent
            - Operation history
            - Capability usage statistics
          </Typography>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Project Monitoring
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Project-specific metrics and monitoring will be implemented here.
            This will include:
            - Active projects and their status
            - Project completion metrics
            - Resource allocation
            - Agent assignments
            - Operation progress
          </Typography>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Operation Monitoring
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Operation-specific monitoring will be implemented here.
            This will include:
            - Active operations
            - Operation queue status
            - Success/failure rates
            - Performance metrics
            - Resource usage
          </Typography>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Box sx={{ p: 3 }}>
          <Typography variant="h4" gutterBottom>
            Resource Monitoring
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Resource usage monitoring will be implemented here.
            This will include:
            - Overall system resources
            - Resource allocation per agent/project
            - Resource bottlenecks
            - Optimization suggestions
          </Typography>
        </Box>
      </TabPanel>
    </Box>
  );
};

export default MonitoringPage;
