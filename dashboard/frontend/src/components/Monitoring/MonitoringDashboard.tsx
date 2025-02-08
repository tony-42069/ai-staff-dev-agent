import React, { useEffect, useState, useCallback } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Card, Grid, Typography, Box, CircularProgress, Alert } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { MetricValue, SystemMetrics } from '../../types/metrics';
import { api } from '../../services/api';
import { useWebSocket } from '../../services/websocket';

const MonitoringDashboard: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [cpuHistory, setCpuHistory] = useState<MetricValue[]>([]);
  const [memoryHistory, setMemoryHistory] = useState<MetricValue[]>([]);
  const [diskHistory, setDiskHistory] = useState<MetricValue[]>([]);

  const clientId = 'monitoring-dashboard';
  const ws = useWebSocket(`/ws/metrics?client_id=${clientId}&subscriptions=system`);

  const handleMetricUpdate = useCallback((data: any) => {
    if (data.type === 'system_metrics') {
      setSystemMetrics(data.metrics);
    } else if (data.type === 'metric_update') {
      const { category, name, value } = data.metric;
      if (category === 'system') {
        if (name === 'cpu_usage') {
          setCpuHistory(prev => [...prev.slice(-29), { timestamp: data.timestamp, value }]);
        } else if (name === 'memory_usage') {
          setMemoryHistory(prev => [...prev.slice(-29), { timestamp: data.timestamp, value }]);
        } else if (name === 'disk_usage') {
          setDiskHistory(prev => [...prev.slice(-29), { timestamp: data.timestamp, value }]);
        }
      }
    }
  }, []);

  useEffect(() => {
    const fetchInitialData = async () => {
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

    fetchInitialData();

    if (ws) {
      ws.onMessage(handleMetricUpdate);
    }
  }, [ws, handleMetricUpdate]);

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

  const getMetricValue = (value: number | undefined, defaultValue = 0) => {
    return typeof value === 'number' ? value : defaultValue;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Monitoring
      </Typography>

      <Grid container spacing={3}>
        {/* WebSocket Health Cards */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>
            WebSocket Health
          </Typography>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">Active Connections</Typography>
            <Typography variant="h3" color="primary">
              {getMetricValue(systemMetrics?.websocket?.value?.total_connections, 0)}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Operations: {getMetricValue(systemMetrics?.websocket?.value?.operations_connections, 0)}
              {' | '}
              Metrics: {getMetricValue(systemMetrics?.websocket?.value?.metrics_connections, 0)}
            </Typography>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">Connection Health</Typography>
            <Typography variant="h3" 
              color={
                getMetricValue(systemMetrics?.websocket?.value?.heartbeat_health_percent, 100) >= 90 
                  ? 'success.main' 
                  : getMetricValue(systemMetrics?.websocket?.value?.heartbeat_health_percent, 100) >= 75 
                    ? 'warning.main' 
                    : 'error.main'
              }
            >
              {getMetricValue(systemMetrics?.websocket?.value?.heartbeat_health_percent, 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Heartbeat Health
            </Typography>
          </Card>
        </Grid>

        {/* System Resource Cards */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>
            System Resources
          </Typography>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">CPU Usage</Typography>
            <Typography variant="h3" color="primary">
              {getMetricValue(systemMetrics?.cpu?.value?.percent).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {systemMetrics?.cpu?.value?.count || 0} Cores
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">Memory Usage</Typography>
            <Typography variant="h3" color="primary">
              {getMetricValue(systemMetrics?.memory?.value?.percent).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatBytes(getMetricValue(systemMetrics?.memory?.value?.available))} Available
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">Disk Usage</Typography>
            <Typography variant="h3" color="primary">
              {getMetricValue(systemMetrics?.disk?.value?.percent).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {formatBytes(getMetricValue(systemMetrics?.disk?.value?.free))} Free
            </Typography>
          </Card>
        </Grid>

        {/* Historical Charts */}
        <Grid item xs={12}>
          <Typography variant="h5" gutterBottom sx={{ mt: 2 }}>
            Historical Metrics
          </Typography>
        </Grid>
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
                  dot={true}
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
                  dot={true}
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
              <LineChart data={diskHistory}>
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
                <Line
                  type="monotone"
                  dataKey="value.percent"
                  name="Disk Usage"
                  stroke={theme.palette.info.main}
                  dot={true}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default MonitoringDashboard;
