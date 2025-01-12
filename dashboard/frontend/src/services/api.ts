import axios from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: BASE_URL,
});

export interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  status: 'idle' | 'busy' | 'error';
  created_at: string;
  updated_at: string;
}

export type Project = {
  id: string;
  name: string;
  description: string;
  repository_url?: string;
  status: 'active' | 'completed' | 'archived';
  assigned_agents: string[];
  created_at: string;
  updated_at: string;
};

// Agent API
export const agentApi = {
  getAll: () => api.get<Agent[]>('/agents'),
  getById: (id: string) => api.get<Agent>(`/agents/${id}`),
  create: (data: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) => 
    api.post<Agent>('/agents', data),
  update: (id: string, data: Partial<Agent>) => 
    api.put<Agent>(`/agents/${id}`, data),
  delete: (id: string) => api.delete(`/agents/${id}`),
};

// Project API
export const projectApi = {
  getAll: () => api.get<Project[]>('/projects'),
  getById: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: Omit<Project, 'id' | 'created_at' | 'updated_at'>) => 
    api.post<Project>('/projects', data),
  update: (id: string, data: Partial<Project>) => 
    api.put<Project>(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
};

export default api; 