import { useQuery } from '@tanstack/react-query';
import { agentApi, Agent } from '../services/api';

export const useAgents = () => {
  const { data: response, isLoading, error } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentApi.getAll();
      return response.data.data;
    },
  });

  return {
    agents: response || [],
    isLoading,
    error,
  };
};
