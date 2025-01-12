import { http, HttpResponse } from 'msw';
import type { Agent } from '../services/api';

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

export const handlers = [
  http.get(`${BASE_URL}/agents`, () => {
    return HttpResponse.json(mockAgents);
  }),

  http.post(`${BASE_URL}/agents`, async ({ request }) => {
    const body = await request.json() as Partial<Agent>;
    const newAgent: Agent = {
      id: Date.now().toString(),
      name: body.name!,
      description: body.description || '',
      capabilities: body.capabilities || [],
      status: 'idle',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    mockAgents.push(newAgent);
    return HttpResponse.json(newAgent);
  }),

  http.get(`${BASE_URL}/agents/:id`, ({ params }) => {
    const agent = mockAgents.find(a => a.id === params.id);
    if (!agent) {
      return new HttpResponse(null, { status: 404 });
    }
    return HttpResponse.json(agent);
  }),

  http.put(`${BASE_URL}/agents/:id`, async ({ params, request }) => {
    const body = await request.json() as Partial<Agent>;
    const index = mockAgents.findIndex(a => a.id === params.id);
    if (index === -1) {
      return new HttpResponse(null, { status: 404 });
    }
    mockAgents[index] = {
      ...mockAgents[index],
      ...body,
      updated_at: new Date().toISOString()
    };
    return HttpResponse.json(mockAgents[index]);
  }),

  http.delete(`${BASE_URL}/agents/:id`, ({ params }) => {
    const index = mockAgents.findIndex(a => a.id === params.id);
    if (index === -1) {
      return new HttpResponse(null, { status: 404 });
    }
    mockAgents.splice(index, 1);
    return HttpResponse.json({ success: true });
  })
]; 