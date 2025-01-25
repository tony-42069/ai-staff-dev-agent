export interface SystemMetrics {
  worker_utilization: number;
  error_rate: number;
  retry_rate: number;
}

export interface QueueMetrics {
  size: number;
  wait_time: number;
}

export interface OperationMetrics {
  total: number;
  active: number;
  completed: number;
  failed: number;
  queued: number;
  cancelled: number;
  success_rate: number;
  average_duration: number;
  by_priority: {
    high: number;
    normal: number;
    low: number;
  };
}

export interface DashboardMetrics {
  system: SystemMetrics;
  queues: {
    high: QueueMetrics;
    normal: QueueMetrics;
    low: QueueMetrics;
  };
  operations: OperationMetrics;
  timestamp?: string;
}

export interface HistoricalMetrics extends DashboardMetrics {
  timestamp: string;
}
