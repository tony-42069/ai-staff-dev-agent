import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';
import { Card, Grid, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { MetricValue, SystemMetrics } from '../../types/metrics';
import { api } from '../../services/api';

const MonitoringDashboard: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [cpuHistory, setCpuHistory] = useState<MetricValue[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<MetricValue[]>([]);
  const [diskHistory, setDiskHistory] = useState<MetricValue[]>([]);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const [system, cpuHist, memHist, diskHist] = await Promise.all([
          api.get('/metrics/system'),
          api.get('/metrics/history/system/cpu_usage'),
          api.get('/metrics/history/system/memory_usage'),
          api.get('/metrics/history/system/disk_usage'),
        ]);

        setSystemMetrics(system.data);
        setCpuHistory(cpuHist.data.values);
        setMemoryHistory(memHist.data.values);
        setDiskHistory(diskHist.data.values);
        setError(null);
      } catch (err) {
        setError('Failed to fetch metrics');
        console.error('Error fetching metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };

  const formatBytes = (bytes: number) => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(2)} GB`;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Monitoring
      </Typography>

      <Grid container spacing={3}>
        {/* Current Metrics Cards */}
        <Grid item xs={12} md={4}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">CPU Usage</Typography>
            <Typography variant="h3" color="primary">
              {systemMetrics?.cpu?.value?.percent.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {systemMetrics?.cpu?.value?.count} Cores
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">Memory Usage</Typography>
            <Typography variant="h3" color="primary">
              {systemMetrics?.memory?.value?.percent.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatBytes(systemMetrics?.memory?.value?.available)} Available
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">Disk Usage</Typography>
            <Typography variant="h3" color="primary">
              {systemMetrics?.disk?.value?.percent.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatBytes(systemMetrics?.disk?.value?.free)} Free
            </Typography>
          </Card>
        </Grid>

        {/* Historical Charts */}
        <Grid item xs={12}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              CPU Usage History
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={cpuHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTimestamp}
                  interval="preserveStartEnd"
                />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip
                  labelFormatter={formatTimestamp}
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'CPU Usage']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value.percent"
                  name="CPU Usage"
                  stroke={theme.palette.primary.main}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Memory Usage History
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={memoryHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTimestamp}
                  interval="preserveStartEnd"
                />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip
                  labelFormatter={formatTimestamp}
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'Memory Usage']}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="value.percent"
                  name="Memory Usage"
                  stroke={theme.palette.secondary.main}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Disk Usage History
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={diskHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={formatTimestamp}
                  interval="preserveStartEnd"
                />
                <YAxis domain={[0, 100]} unit="%" />
                <Tooltip
                  labelFormatter={formatTimestamp}
                  formatter={(value: number) => [`${value.toFixed(1)}%`, 'Disk Usage']}
                />
                <Legend />
                <Bar
                  dataKey="value.percent"
                  name="Disk Usage"
                  fill={theme.palette.info.main}
                />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MonitoringDashboard;
