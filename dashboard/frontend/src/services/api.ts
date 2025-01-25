import axios, { AxiosError, AxiosResponse } from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

// Error response type
export interface ApiError {
  detail: string;
  validation_errors?: Record<string, string>;
}

// API response type
export interface ApiResponse<T> {
  data: T;
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
export interface AgentOperation {
  agent_id: string;
  capability: string;
  timestamp: string;
  status: 'completed' | 'failed';
  result?: Record<string, any>;
  error?: string;
}

export interface ProjectAgentMetadata {
  assigned_agents: string[];
  capability_requirements: string[];
  operation_history: AgentOperation[];
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'completed' | 'archived';
  project_metadata: Record<string, any>;
  agent_metadata: ProjectAgentMetadata;
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
export interface AssignToProjectRequest {
  project_id: string;
  capabilities: string[];
}

export interface ExecuteCapabilityRequest {
  project_id: string;
  capability: string;
  parameters?: Record<string, any>;
}

export interface OperationResponse {
  status: string;
  message: string;
  data?: Record<string, any>;
}

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
    api.delete(`/agents/${id}`),

  assignToProject: (agentId: string, data: AssignToProjectRequest) =>
    api.post<ApiResponse<OperationResponse>>(`/agents/${agentId}/assign`, data),

  executeCapability: (agentId: string, data: ExecuteCapabilityRequest) =>
    api.post<ApiResponse<OperationResponse>>(`/agents/${agentId}/execute`, data),

  getProjectOperations: (agentId: string, projectId: string) =>
    retryRequest(() => api.get<ApiResponse<AgentOperation[]>>(`/agents/${agentId}/operations/${projectId}`)),
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
    api.patch<ApiResponse<Project>>(`/projects/${id}`, data),
  
  delete: (id: string) => 
    api.delete(`/projects/${id}`),
};

export default api;
