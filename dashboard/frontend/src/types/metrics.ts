export interface MetricValue {
  value: any;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface MetricHistory {
  category: string;
  name: string;
  values: MetricValue[];
  start_time?: string;
  end_time?: string;
}

export interface MetricsSummary {
  categories: string[];
  metrics: Record<string, Record<string, MetricValue>>;
  timestamp: string;
}

export interface MetricStatistics {
  count: number;
  min: number;
  max: number;
  avg: number;
  start_time: string;
  end_time: string;
}

export interface SystemMetrics {
  memory?: {
    value: {
      total: number;
      available: number;
      percent: number;
    };
    timestamp: string;
    metadata: Record<string, any>;
  };
  cpu?: {
    value: {
      percent: number;
      count: number;
    };
    timestamp: string;
    metadata: Record<string, any>;
  };
  disk?: {
    value: {
      total: number;
      used: number;
      free: number;
      percent: number;
    };
    timestamp: string;
    metadata: Record<string, any>;
  };
}

export interface AgentMetrics {
  operations_completed: number;
  operations_failed: number;
  average_response_time: number;
  memory_usage: number;
  uptime: number;
  last_active: string;
  capabilities_used: Record<string, number>;
}

export interface ProjectMetrics {
  total_operations: number;
  active_agents: number;
  completion_rate: number;
  average_operation_time: number;
  error_rate: number;
  last_operation: string;
  resource_usage: {
    cpu: number;
    memory: number;
    disk: number;
  };
}

export interface MetricsFilter {
  startTime?: Date;
  endTime?: Date;
  categories?: string[];
  names?: string[];
  limit?: number;
}
