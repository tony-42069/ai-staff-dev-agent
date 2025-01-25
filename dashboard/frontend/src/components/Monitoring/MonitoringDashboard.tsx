import React, { useEffect, useState } from 'react';
import { Box, Grid, Text, Spinner, Card, CardBody, Stack, Stat, StatLabel, StatNumber, StatHelpText } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../../services/api';
import { DashboardMetrics, HistoricalMetrics } from '../../types/metrics';

const MetricCard: React.FC<{ title: string; value: number | string; unit?: string }> = ({
  title,
  value,
  unit
}) => (
  <Card height="100%">
    <CardBody>
      <Stat>
        <StatLabel color="gray.600">{title}</StatLabel>
        <StatNumber fontSize="2xl">
          {typeof value === 'number' ? value.toFixed(1) : value}
          {unit && <StatHelpText as="span" ml={1}>{unit}</StatHelpText>}
        </StatNumber>
      </Stat>
    </CardBody>
  </Card>
);

const MonitoringDashboard: React.FC = () => {
  const [historicalData, setHistoricalData] = useState<HistoricalMetrics[]>([]);

  const { data: currentMetrics, isLoading } = useQuery({
    queryKey: ['metrics', 'current'],
    queryFn: () => api.get<DashboardMetrics>('/metrics/current').then(res => res.data),
    refetchInterval: 5000 // Refresh every 5 seconds
  });

  useEffect(() => {
    // Fetch historical data
    const fetchHistorical = async () => {
      const response = await api.get<HistoricalMetrics[]>('/metrics/historical/hour');
      setHistoricalData(response.data);
    };
    fetchHistorical();
    const interval = setInterval(fetchHistorical, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  if (isLoading || !currentMetrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  const { system, operations, queues } = currentMetrics;

  return (
    <Box p={6}>
      <Text fontSize="2xl" fontWeight="bold" mb={6}>
        System Monitoring
      </Text>

      {/* System Health Metrics */}
      <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6} mb={8}>
        <MetricCard
          title="Worker Utilization"
          value={system.worker_utilization}
          unit="%"
        />
        <MetricCard
          title="Error Rate"
          value={system.error_rate}
          unit="%"
        />
        <MetricCard
          title="Retry Rate"
          value={system.retry_rate}
          unit="%"
        />
      </Grid>

      {/* Operation Statistics */}
      <Text fontSize="xl" fontWeight="bold" mt={8} mb={4}>
        Operation Statistics
      </Text>
      <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={6} mb={8}>
        <MetricCard
          title="Total Operations"
          value={operations.total}
        />
        <MetricCard
          title="Active Operations"
          value={operations.active}
        />
        <MetricCard
          title="Success Rate"
          value={operations.success_rate}
          unit="%"
        />
        <MetricCard
          title="Average Duration"
          value={operations.average_duration}
          unit="s"
        />
      </Grid>

      {/* Queue Status */}
      <Text fontSize="xl" fontWeight="bold" mt={8} mb={4}>
        Queue Status
      </Text>
      <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6} mb={8}>
        {Object.entries(queues).map(([priority, metrics]) => (
          <Card key={priority}>
            <CardBody>
              <Stack spacing={2}>
                <Text fontWeight="bold" fontSize="lg">
                  {priority.toUpperCase()} Priority Queue
                </Text>
                <Text>Size: {metrics.size}</Text>
                <Text>Est. Wait Time: {metrics.wait_time.toFixed(1)}s</Text>
              </Stack>
            </CardBody>
          </Card>
        ))}
      </Grid>

      {/* Historical Charts */}
      <Text fontSize="xl" fontWeight="bold" mt={8} mb={4}>
        Historical Trends
      </Text>
      <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
        <Card>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>
              Operation Status
            </Text>
            <Box height="300px">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="operations.completed" name="Completed" fill="#48BB78" />
                  <Bar dataKey="operations.failed" name="Failed" fill="#F56565" />
                  <Bar dataKey="operations.queued" name="Queued" fill="#4299E1" />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Text fontSize="lg" fontWeight="bold" mb={4}>
              System Performance
            </Text>
            <Box height="300px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="system.worker_utilization"
                    name="Worker Utilization"
                    stroke="#4299E1"
                  />
                  <Line
                    type="monotone"
                    dataKey="system.error_rate"
                    name="Error Rate"
                    stroke="#F56565"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Card>
      </Grid>
    </Box>
  );
};

export default MonitoringDashboard;
