import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';

interface ApiError {
  code: string;
  message: string;
  details?: any;
}

interface ApiErrorResponse {
  code: string;
  message: string;
  details?: any;
}

class ApiService {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || '/api/v1';
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiErrorResponse>) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
        }
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError<ApiErrorResponse>): ApiError {
    if (error.response?.data) {
      // Server responded with error
      const errorData = error.response.data;
      return {
        code: errorData.code || 'SERVER_ERROR',
        message: errorData.message || 'Server error occurred',
        details: errorData.details,
      };
    } else if (error.request) {
      // Request made but no response
      return {
        code: 'NETWORK_ERROR',
        message: 'Network error occurred',
      };
    } else {
      // Error setting up request
      return {
        code: 'REQUEST_ERROR',
        message: error.message,
      };
    }
  }

  async get<T = any>(url: string, params?: any): Promise<AxiosResponse<T>> {
    try {
      return await this.client.get<T>(url, { params });
    } catch (error) {
      throw error;
    }
  }

  async post<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    try {
      return await this.client.post<T>(url, data);
    } catch (error) {
      throw error;
    }
  }

  async put<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    try {
      return await this.client.put<T>(url, data);
    } catch (error) {
      throw error;
    }
  }

  async delete<T = any>(url: string): Promise<AxiosResponse<T>> {
    try {
      return await this.client.delete<T>(url);
    } catch (error) {
      throw error;
    }
  }

  async patch<T = any>(url: string, data?: any): Promise<AxiosResponse<T>> {
    try {
      return await this.client.patch<T>(url, data);
    } catch (error) {
      throw error;
    }
  }

  // Specialized API methods for agents
  async getAgents() {
    return this.get('/agents');
  }

  async getAgentMetrics(agentId: string) {
    return this.get(`/agents/${agentId}/metrics`);
  }

  async getAgentOperations(agentId: string) {
    return this.get(`/agents/${agentId}/operations`);
  }

  async scheduleAgentMaintenance(agentId: string, window: {
    type: string;
    start_time: string;
    end_time: string;
  }) {
    return this.post(`/agents/${agentId}/maintenance`, window);
  }

  // Specialized API methods for operations
  async getOperations(params?: {
    status?: string;
    agent_id?: string;
    project_id?: string;
  }) {
    return this.get('/operations', params);
  }

  async cancelOperation(operationId: string) {
    return this.post(`/operations/${operationId}/cancel`);
  }

  async retryOperation(operationId: string) {
    return this.post(`/operations/${operationId}/retry`);
  }

  // Specialized API methods for metrics
  async getSystemMetrics() {
    return this.get('/metrics/system');
  }

  async getMetricsHistory(
    metricType: string,
    params?: {
      start_time?: string;
      end_time?: string;
      interval?: string;
    }
  ) {
    return this.get(`/metrics/history/${metricType}`, params);
  }

  // Specialized API methods for projects
  async getProjects() {
    return this.get('/projects');
  }

  async getProjectMetrics(projectId: string) {
    return this.get(`/projects/${projectId}/metrics`);
  }

  async getProjectOperations(projectId: string) {
    return this.get(`/projects/${projectId}/operations`);
  }
}

export const api = new ApiService();
