export interface MetricValue {
  timestamp: string;
  value: {
    percent?: number;
    count?: number;
    available?: number;
    used?: number;
    free?: number;
    total?: number;
    [key: string]: any;
  };
  metadata?: Record<string, any>;
}

export interface SystemMetrics {
  cpu?: {
    value: {
      percent: number;
      count: number;
      frequency?: number;
    };
    metadata?: Record<string, any>;
  };
  memory?: {
    value: {
      percent: number;
      total: number;
      available: number;
      used: number;
    };
    metadata?: Record<string, any>;
  };
  disk?: {
    value: {
      percent: number;
      total: number;
      free: number;
      used: number;
    };
    metadata?: Record<string, any>;
  };
  network?: {
    value: {
      bytes_sent: number;
      bytes_recv: number;
      packets_sent: number;
      packets_recv: number;
      errors_in: number;
      errors_out: number;
    };
    metadata?: Record<string, any>;
  };
  timestamp: string;
}

export interface AgentMetrics {
  operations_completed: number;
  operations_failed: number;
  average_response_time: number;
  error_rate: number;
  resource_utilization: {
    cpu: number;
    memory: number;
    disk: number;
    [key: string]: number;
  };
  capability_metrics: {
    [capability: string]: {
      invocations: number;
      success_rate: number;
      average_duration: number;
      error_rate: number;
      last_used: string;
    };
  };
}

export interface ProjectMetrics {
  total_operations: number;
  completed_operations: number;
  failed_operations: number;
  active_operations: number;
  success_rate: number;
  average_duration: number;
  resource_usage: {
    cpu: number;
    memory: number;
    disk: number;
    [key: string]: number;
  };
  agent_metrics: {
    [agent_id: string]: {
      operations: number;
      success_rate: number;
      error_rate: number;
    };
  };
}

export interface OperationMetrics {
  duration: number;
  resource_usage: {
    cpu: number;
    memory: number;
    disk: number;
    [key: string]: number;
  };
  error_count: number;
  retry_count: number;
  status_history: Array<{
    status: string;
    timestamp: string;
    duration: number;
  }>;
  performance_metrics: {
    [metric: string]: number;
  };
}

export interface MetricsTimeRange {
  start_time: string;
  end_time: string;
  interval: string;
}

export interface MetricsQuery {
  timeRange: MetricsTimeRange;
  filters?: {
    [key: string]: any;
  };
  aggregation?: string;
  groupBy?: string[];
}

export interface MetricsResponse<T> {
  data: T;
  metadata: {
    timeRange: MetricsTimeRange;
    aggregation?: string;
    groupBy?: string[];
    [key: string]: any;
  };
}

export interface HistoricalMetrics {
  timestamps: string[];
  values: number[];
  metadata?: {
    unit?: string;
    description?: string;
    [key: string]: any;
  };
}

export interface ResourceMetrics {
  cpu: {
    usage: number;
    limit: number;
    throttling?: {
      periods: number;
      throttled_periods: number;
      throttled_time: number;
    };
  };
  memory: {
    usage: number;
    limit: number;
    max_usage: number;
    cache?: number;
    rss?: number;
    swap?: number;
  };
  disk: {
    read_bytes: number;
    write_bytes: number;
    read_ops: number;
    write_ops: number;
    io_time?: number;
  };
  network: {
    rx_bytes: number;
    tx_bytes: number;
    rx_packets: number;
    tx_packets: number;
    rx_errors: number;
    tx_errors: number;
  };
}

export interface PerformanceMetrics {
  latency: {
    p50: number;
    p90: number;
    p95: number;
    p99: number;
  };
  throughput: number;
  error_rate: number;
  saturation: number;
}
