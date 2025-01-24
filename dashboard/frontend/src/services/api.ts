import axios, { AxiosError, AxiosResponse } from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

// API Response type
export interface ApiResponse<T> {
  data: T;
  message?: string;
}

// Error response type
export interface ApiError {
  detail: string;
  validation_errors?: Record<string, string>;
}

// Agent types
export interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  status: 'idle' | 'busy' | 'error';
  created_at: string;
  updated_at: string;
}

export type CreateAgentDto = Omit<Agent, 'id' | 'created_at' | 'updated_at'>;
export type UpdateAgentDto = Partial<CreateAgentDto>;

// Project types
export interface Project {
  id: string;
  name: string;
  description: string;
  repository_url?: string;
  status: 'active' | 'completed' | 'archived';
  assigned_agents: string[];
  created_at: string;
  updated_at: string;
}

export type CreateProjectDto = Omit<Project, 'id' | 'created_at' | 'updated_at'>;
export type UpdateProjectDto = Partial<CreateProjectDto>;

// Create axios instance with configuration
export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000, // 10 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for consistent error handling
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ApiError>) => {
    // Handle network errors
    if (!error.response) {
      return Promise.reject({
        detail: 'Network error. Please check your connection.',
      });
    }

    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
      return Promise.reject({
        detail: 'Request timed out. Please try again.',
      });
    }

    // Handle API errors
    const errorResponse = error.response.data;
    return Promise.reject(errorResponse);
  }
);

// Retry configuration
const retryRequest = async <T>(
  request: () => Promise<AxiosResponse<T>>,
  retries: number = 3,
  delay: number = 1000
): Promise<AxiosResponse<T>> => {
  try {
    return await request();
  } catch (error) {
    if (retries === 0 || (error as AxiosError).response?.status === 422) {
      throw error;
    }
    await new Promise(resolve => setTimeout(resolve, delay));
    return retryRequest(request, retries - 1, delay * 2);
  }
};

// Agent API
export const agentApi = {
  getAll: () => 
    retryRequest(() => api.get<ApiResponse<Agent[]>>('/agents')),
  
  getById: (id: string) => 
    retryRequest(() => api.get<ApiResponse<Agent>>(`/agents/${id}`)),
  
  create: (data: CreateAgentDto) => 
    api.post<ApiResponse<Agent>>('/agents', data),
  
  update: (id: string, data: UpdateAgentDto) => 
    api.put<ApiResponse<Agent>>(`/agents/${id}`, data),
  
  delete: (id: string) => 
    api.delete<ApiResponse<void>>(`/agents/${id}`),
};

// Project API
export const projectApi = {
  getAll: () => 
    retryRequest(() => api.get<ApiResponse<Project[]>>('/projects')),
  
  getById: (id: string) => 
    retryRequest(() => api.get<ApiResponse<Project>>(`/projects/${id}`)),
  
  create: (data: CreateProjectDto) => 
    api.post<ApiResponse<Project>>('/projects', data),
  
  update: (id: string, data: UpdateProjectDto) => 
    api.put<ApiResponse<Project>>(`/projects/${id}`, data),
  
  delete: (id: string) => 
    api.delete<ApiResponse<void>>(`/projects/${id}`),
};

export default api;
