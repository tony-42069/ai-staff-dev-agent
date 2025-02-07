import axios from 'axios';

export interface Agent {
  agent_id: string;
  status: string;
  capabilities: string[];
  metadata?: Record<string, any>;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  status: 'active' | 'completed' | 'archived';
  created_at: string;
  updated_at: string;
  project_metadata: Record<string, any>;
  agent_metadata: {
    assigned_agents: string[];
    capability_requirements: string[];
    operation_history: Array<{
      agent_id: string;
      capability: string;
      timestamp: string;
      status: 'completed' | 'failed';
      error?: string;
    }>;
  };
}

export interface CreateProjectDto {
  name: string;
  description?: string;
  status: Project['status'];
  project_metadata: Record<string, any>;
}

export interface UpdateProjectDto {
  name?: string;
  description?: string;
  status?: Project['status'];
  project_metadata?: Record<string, any>;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

const api = axios.create({
  baseURL: '',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Basic error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Project API methods
const projectApi = {
  getAll: () => api.get<ApiResponse<Project[]>>('/api/v1/projects'),
  get: (id: string) => api.get<ApiResponse<Project>>(`/api/v1/projects/${id}`),
  create: (data: CreateProjectDto) => api.post<ApiResponse<Project>>('/api/v1/projects', data),
  update: (id: string, data: UpdateProjectDto) => api.patch<ApiResponse<Project>>(`/api/v1/projects/${id}`, data),
  delete: (id: string) => api.delete<ApiResponse<void>>(`/api/v1/projects/${id}`),
};

// Agent API methods
const agentApi = {
  getAll: () => api.get<ApiResponse<Agent[]>>('/api/v1/agents'),
  get: (id: string) => api.get<ApiResponse<Agent>>(`/api/v1/agents/${id}`),
  assignToProject: (agentId: string, data: { project_id: string; capabilities: string[] }) =>
    api.post<ApiResponse<void>>(`/api/v1/agents/${agentId}/assign`, data),
  executeCapability: (agentId: string, data: { project_id: string; capability: string }) =>
    api.post<ApiResponse<void>>(`/api/v1/agents/${agentId}/execute`, data),
};

export { api, projectApi, agentApi };
