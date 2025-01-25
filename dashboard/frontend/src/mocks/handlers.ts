import { http, HttpResponse, delay } from 'msw';
import type { Agent, Project, CreateProjectDto, UpdateProjectDto } from '../services/api';
import type { DashboardMetrics, HistoricalMetrics } from '../types/metrics';


const BASE_URL = 'http://localhost:8000/api/v1';

const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Test Agent',
    description: 'A test agent',
    capabilities: ['test'],
    status: 'idle',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Test Project',
    description: 'A test project',
    status: 'active',
    project_metadata: {
      repository: 'https://github.com/test/project',
      language: 'TypeScript'
    },
    agent_metadata: {
      assigned_agents: ['1'],
      capability_requirements: ['test'],
      operation_history: []
    },
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

// Helper function to simulate network delay
const withDelay = async (data: any) => {
  await delay(100); // Add a small delay to simulate network latency
  return HttpResponse.json(data);
};

export const handlers = [
  // Agent handlers
  http.get(`${BASE_URL}/agents`, async () => {
    return withDelay(mockAgents);
  }),

  http.post(`${BASE_URL}/agents`, async ({ request }) => {
    const body = await request.json() as Partial<Agent>;
    
    if (!body.name) {
      return new HttpResponse(null, { 
        status: 400,
        statusText: 'Bad Request',
      });
    }

    const newAgent: Agent = {
      id: Date.now().toString(),
      name: body.name,
      description: body.description || '',
      capabilities: body.capabilities || [],
      status: 'idle',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    mockAgents.push(newAgent);
    return withDelay(newAgent);
  }),

  http.get(`${BASE_URL}/agents/:id`, async ({ params }) => {
    const agent = mockAgents.find(a => a.id === params.id);
    if (!agent) {
      return new HttpResponse(null, { 
        status: 404,
        statusText: 'Not Found',
      });
    }
    return withDelay(agent);
  }),

  http.put(`${BASE_URL}/agents/:id`, async ({ params, request }) => {
    const body = await request.json() as Partial<Agent>;
    const index = mockAgents.findIndex(a => a.id === params.id);
    if (index === -1) {
      return new HttpResponse(null, { 
        status: 404,
        statusText: 'Not Found',
      });
    }
    mockAgents[index] = {
      ...mockAgents[index],
      ...body,
      updated_at: new Date().toISOString()
    };
    return withDelay(mockAgents[index]);
  }),

  http.delete(`${BASE_URL}/agents/:id`, async ({ params }) => {
    const index = mockAgents.findIndex(a => a.id === params.id);
    if (index === -1) {
      return new HttpResponse(null, { 
        status: 404,
        statusText: 'Not Found',
      });
    }
    mockAgents.splice(index, 1);
    return withDelay({ success: true });
  }),

  // Project handlers
  http.get(`${BASE_URL}/projects`, async () => {
    return withDelay(mockProjects);
  }),

  http.post(`${BASE_URL}/projects`, async ({ request }) => {
    const body = await request.json() as CreateProjectDto;
    
    if (!body.name) {
      return new HttpResponse(null, { 
        status: 400,
        statusText: 'Bad Request',
      });
    }

    const newProject: Project = {
      id: Date.now().toString(),
      name: body.name,
      description: body.description || '',
      status: body.status || 'active',
      project_metadata: body.project_metadata || {},
      agent_metadata: {
        assigned_agents: body.agent_id ? [body.agent_id] : [],
        capability_requirements: [],
        operation_history: []
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    mockProjects.push(newProject);
    return withDelay(newProject);
  }),

  http.get(`${BASE_URL}/projects/:id`, async ({ params }) => {
    const project = mockProjects.find(p => p.id === params.id);
    if (!project) {
      return new HttpResponse(null, { 
        status: 404,
        statusText: 'Not Found',
      });
    }
    return withDelay(project);
  }),

  http.patch(`${BASE_URL}/projects/:id`, async ({ params, request }) => {
    const body = await request.json() as UpdateProjectDto;
    const index = mockProjects.findIndex(p => p.id === params.id);
    if (index === -1) {
      return new HttpResponse(null, { 
        status: 404,
        statusText: 'Not Found',
      });
    }
    mockProjects[index] = {
      ...mockProjects[index],
      ...body,
      updated_at: new Date().toISOString()
    };
    return withDelay(mockProjects[index]);
  }),

  http.delete(`${BASE_URL}/projects/:id`, async ({ params }) => {
    const index = mockProjects.findIndex(p => p.id === params.id);
    if (index === -1) {
      return new HttpResponse(null, { 
        status: 404,
        statusText: 'Not Found',
      });
    }
    mockProjects.splice(index, 1);
    return withDelay({ success: true });
  }),

  // Metrics handlers
  http.get(`${BASE_URL}/metrics/current`, async () => {
    const mockMetrics: DashboardMetrics = {
      system: {
        worker_utilization: Math.random() * 100,
        error_rate: Math.random() * 10,
        retry_rate: Math.random() * 5
      },
      operations: {
        total: Math.floor(Math.random() * 100),
        active: Math.floor(Math.random() * 20),
        completed: Math.floor(Math.random() * 50),
        failed: Math.floor(Math.random() * 10),
        queued: Math.floor(Math.random() * 15),
        cancelled: Math.floor(Math.random() * 5),
        success_rate: 85 + Math.random() * 10,
        average_duration: Math.random() * 30,
        by_priority: {
          high: Math.floor(Math.random() * 5),
          normal: Math.floor(Math.random() * 10),
          low: Math.floor(Math.random() * 5)
        }
      },
      queues: {
        high: { size: Math.floor(Math.random() * 5), wait_time: Math.random() * 10 },
        normal: { size: Math.floor(Math.random() * 10), wait_time: Math.random() * 20 },
        low: { size: Math.floor(Math.random() * 5), wait_time: Math.random() * 30 }
      }
    };
    return withDelay(mockMetrics);
  }),

  http.get(`${BASE_URL}/metrics/historical/:timeframe`, async () => {
    const historicalData: HistoricalMetrics[] = Array.from({ length: 12 }, (_, i) => {
      const timestamp = new Date();
      timestamp.setMinutes(timestamp.getMinutes() - (i * 5));
      
      return {
        timestamp: timestamp.toISOString(),
        system: {
          worker_utilization: 50 + Math.random() * 30,
          error_rate: Math.random() * 10,
          retry_rate: Math.random() * 5
        },
        operations: {
          total: 50 + Math.floor(Math.random() * 50),
          active: Math.floor(Math.random() * 20),
          completed: 30 + Math.floor(Math.random() * 20),
          failed: Math.floor(Math.random() * 10),
          queued: Math.floor(Math.random() * 15),
          cancelled: Math.floor(Math.random() * 5),
          success_rate: 85 + Math.random() * 10,
          average_duration: 15 + Math.random() * 15,
          by_priority: {
            high: Math.floor(Math.random() * 5),
            normal: Math.floor(Math.random() * 10),
            low: Math.floor(Math.random() * 5)
          }
        },
        queues: {
          high: { size: Math.floor(Math.random() * 5), wait_time: Math.random() * 10 },
          normal: { size: Math.floor(Math.random() * 10), wait_time: Math.random() * 20 },
          low: { size: Math.floor(Math.random() * 5), wait_time: Math.random() * 30 }
        }
      };
    });
    return withDelay(historicalData);
  }),

  // Fallback handler for unhandled requests
  http.all('*', ({ request }) => {
    console.warn(`Unhandled ${request.method} request to ${request.url}`);
    return new HttpResponse(null, { 
      status: 404,
      statusText: 'Not Found',
    });
  })
];
