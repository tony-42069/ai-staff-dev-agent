import { http, HttpResponse } from 'msw';
import { Agent } from '../services/api';

const BASE_URL = 'http://localhost:8000/api/v1';

// Mock data
const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Test Agent 1',
    description: 'A test agent',
    capabilities: ['test', 'debug'],
    status: 'idle',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
];

export const handlers = [
  // Agents endpoints
  http.get(`${BASE_URL}/agents`, () => {
    return HttpResponse.json(mockAgents, { status: 200 });
  }),

  http.post(`${BASE_URL}/agents`, async ({ request }) => {
    const newAgent = await request.json() as Partial<Agent>;
    return HttpResponse.json({
      ...newAgent,
      id: Date.now().toString(),
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    } as Agent, { status: 201 });
  }),

  http.get(`${BASE_URL}/agents/:id`, ({ params }) => {
    const { id } = params;
    const agent = mockAgents.find(a => a.id === id);
    if (!agent) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json(agent, { status: 200 });
  }),

  http.put(`${BASE_URL}/agents/:id`, async ({ params, request }) => {
    const { id } = params;
    const updates = await request.json() as Partial<Agent>;
    const agent = mockAgents.find(a => a.id === id);
    if (!agent) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json({
      ...agent,
      ...updates,
      updated_at: new Date().toISOString(),
    } as Agent, { status: 200 });
  }),

  http.delete(`${BASE_URL}/agents/:id`, ({ params }) => {
    const { id } = params;
    const agent = mockAgents.find(a => a.id === id);
    if (!agent) {
      return new HttpResponse(null, { status: 404 });
    }
    return new HttpResponse(null, { status: 204 });
  }),
]; 