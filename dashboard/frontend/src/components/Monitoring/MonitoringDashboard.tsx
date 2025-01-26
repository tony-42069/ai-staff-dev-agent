import React, { useEffect, useState, useCallback } from 'react';
import { Box, Grid, Text, Spinner, Card, CardBody, Stack, Stat, StatLabel, StatNumber, StatHelpText, useToast } from '@chakra-ui/react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { api } from '../../services/api';
import { DashboardMetrics, HistoricalMetrics } from '../../types/metrics';
import { websocketService, WebSocketMessage } from '@/services/websocket';
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor'

interface MetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  isUpdating?: boolean;
}

const MetricCard = React.memo<MetricCardProps>(({
  title,
  value,
  unit,
  isUpdating
}) => (
  <Card height="100%" data-testid="metric-card">
    <CardBody>
      <Stat>
        <StatLabel color="gray.600">{title}</StatLabel>
        <StatNumber fontSize="2xl" data-testid="metric-value">
          {typeof value === 'number' ? value.toFixed(1) : value}
          {unit && <StatHelpText as="span" ml={1}>{unit}</StatHelpText>}
          {isUpdating && <Spinner size="xs" ml={2} />}
        </StatNumber>
      </Stat>
    </CardBody>
  </Card>
), (prevProps: MetricCardProps, nextProps: MetricCardProps) => 
  prevProps.value === nextProps.value && 
  prevProps.isUpdating === nextProps.isUpdating
);

const MonitoringDashboard: React.FC = () => {
  const [historicalData, setHistoricalData] = useState<HistoricalMetrics[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [updatingMetrics, setUpdatingMetrics] = useState<Set<string>>(new Set());
  const toast = useToast();
  const { startMeasure, endMeasure, measureMessageLatency, getMetrics } = usePerformanceMonitor('MonitoringDashboard')

  const { data: currentMetrics, isLoading } = useQuery({
    queryKey: ['metrics', 'current'],
    queryFn: () => api.get<DashboardMetrics>('/metrics/current').then(res => res.data),
    refetchInterval: isConnected ? false : 5000 // Only poll if WebSocket is not connected
  });

  // Measure WebSocket message handling
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    const startTime = performance.now()

    if (message.type === 'status' && message.content === 'updating') {
      setUpdatingMetrics(prev => new Set([...prev, message.sender]))
    } else if (message.type === 'metrics') {
      try {
        const metrics = JSON.parse(message.content)
        if (metrics.historical) {
          setHistoricalData(prev => [...prev.slice(-11), metrics.historical])
        }
        setUpdatingMetrics(prev => {
          const next = new Set(prev)
          next.delete(message.sender)
          return next
        })
      } catch (error) {
        console.error('Failed to parse metrics:', error)
      }
    }

    measureMessageLatency(startTime)
  }, [measureMessageLatency])

  useEffect(() => {
    startMeasure()
    websocketService.connect()

    const messageUnsubscribe = websocketService.onMessage(handleWebSocketMessage)
    const connectedUnsubscribe = websocketService.onConnected(() => {
      setIsConnected(true)
      toast({
        title: 'Connected to monitoring',
        description: 'Receiving real-time updates',
        status: 'success',
        duration: 3000,
      })
    })

    const disconnectedUnsubscribe = websocketService.onDisconnected(() => {
      setIsConnected(false)
      toast({
        title: 'Disconnected from monitoring',
        description: 'Falling back to polling updates',
        status: 'warning',
        duration: null,
      })
    })

    // Initial historical data fetch
    const fetchHistorical = async () => {
      try {
        const response = await api.get<HistoricalMetrics[]>('/metrics/historical/hour')
        setHistoricalData(response.data)
      } catch (error) {
        console.error('Failed to fetch historical data:', error)
      }
    }
    fetchHistorical()

    return () => {
      messageUnsubscribe()
      connectedUnsubscribe()
      disconnectedUnsubscribe()
      websocketService.disconnect()
      endMeasure()
      // Log performance metrics on unmount
      console.debug('MonitoringDashboard Performance Metrics:', getMetrics())
    }
  }, [toast, handleWebSocketMessage, startMeasure, endMeasure, getMetrics])

  if (isLoading || !currentMetrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px" data-testid="loading-indicator">
        <Spinner size="xl" />
      </Box>
    );
  }

  const { system, operations, queues } = currentMetrics;

  return (
    <Box p={6}>
      <Text fontSize="2xl" fontWeight="bold" mb={6}>
        System Monitoring
        {isConnected ? (
          <Text as="span" color="green.500" fontSize="md" ml={2} data-testid="connection-status">
            (Live)
          </Text>
        ) : (
          <Text as="span" color="orange.500" fontSize="md" ml={2} data-testid="connection-status">
            (Polling)
          </Text>
        )}
      </Text>

      {/* System Health Metrics */}
      <Box data-testid="system-status">
        <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={6} mb={8}>
          <MetricCard
            title="Worker Utilization"
            value={system.worker_utilization}
            unit="%"
            isUpdating={updatingMetrics.has('system.worker_utilization')}
          />
          <MetricCard
            title="Error Rate"
            value={system.error_rate}
            unit="%"
            isUpdating={updatingMetrics.has('system.error_rate')}
          />
          <MetricCard
            title="Retry Rate"
            value={system.retry_rate}
            unit="%"
            isUpdating={updatingMetrics.has('system.retry_rate')}
          />
        </Grid>
      </Box>

      {/* Operation Statistics */}
      <Box data-testid="performance-metrics">
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
      </Box>

      {/* Queue Status */}
      <Box data-testid="queue-status">
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
                  <Text data-testid="queue-size">Size: {metrics.size}</Text>
                  <Text>Est. Wait Time: {metrics.wait_time.toFixed(1)}s</Text>
                </Stack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      </Box>

      {/* Historical Charts */}
      <Box data-testid="historical-chart">
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
    </Box>
  );
};

export default MonitoringDashboard;
