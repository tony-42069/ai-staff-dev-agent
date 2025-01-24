import axios, { AxiosError, AxiosResponse } from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

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
  description?: string;
  status: 'active' | 'completed' | 'archived';
  project_metadata: Record<string, any>;
  agent_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateProjectDto {
  name: string;
  description?: string;
  status?: 'active' | 'completed' | 'archived';
  project_metadata?: Record<string, any>;
  agent_id?: string;
}

export interface UpdateProjectDto {
  name?: string;
  description?: string;
  status?: 'active' | 'completed' | 'archived';
  project_metadata?: Record<string, any>;
  agent_id?: string;
}

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
  (response: AxiosResponse) => response.data,
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
  request: () => Promise<T>,
  retries: number = 3,
  delay: number = 1000
): Promise<T> => {
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
    retryRequest(() => api.get<Agent[]>('/agents')),
  
  getById: (id: string) => 
    retryRequest(() => api.get<Agent>(`/agents/${id}`)),
  
  create: (data: CreateAgentDto) => 
    api.post<Agent>('/agents', data),
  
  update: (id: string, data: UpdateAgentDto) => 
    api.put<Agent>(`/agents/${id}`, data),
  
  delete: (id: string) => 
    api.delete(`/agents/${id}`),
};

// Project API
export const projectApi = {
  getAll: () => 
    retryRequest(() => api.get<Project[]>('/projects')),
  
  getById: (id: string) => 
    retryRequest(() => api.get<Project>(`/projects/${id}`)),
  
  create: (data: CreateProjectDto) => 
    api.post<Project>('/projects', data),
  
  update: (id: string, data: UpdateProjectDto) => 
    api.patch<Project>(`/projects/${id}`, data),
  
  delete: (id: string) => 
    api.delete(`/projects/${id}`),
};

export default api;
