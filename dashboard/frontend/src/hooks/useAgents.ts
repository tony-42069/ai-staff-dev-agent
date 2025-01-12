import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentApi, Agent } from '../services/api';

export const useAgents = () => {
  const queryClient = useQueryClient();

  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentApi.getAll();
      return response.data;
    },
  });

  const createAgent = useMutation({
    mutationFn: async (data: Omit<Agent, 'id' | 'created_at' | 'updated_at'>) => {
      const response = await agentApi.create(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  const updateAgent = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Agent> }) => {
      const response = await agentApi.update(id, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  const deleteAgent = useMutation({
    mutationFn: async (id: string) => {
      await agentApi.delete(id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
    },
  });

  return {
    agents: agents || [],
    isLoading,
    createAgent,
    updateAgent,
    deleteAgent,
  };
}; 