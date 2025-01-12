import { Box, Button, List, ListItem, Text, VStack, useToast } from '@chakra-ui/react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import type { Agent } from '../../services/api';

const BASE_URL = 'http://localhost:8000/api/v1';

const AgentList = () => {
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data: agents, isLoading } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await axios.get(`${BASE_URL}/agents`);
      return response.data;
    }
  });

  const deleteAgentMutation = useMutation({
    mutationFn: async (agentId: string) => {
      await axios.delete(`${BASE_URL}/agents/${agentId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      toast({
        title: 'Agent deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    },
    onError: () => {
      toast({
        title: 'Error deleting agent',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  });

  if (isLoading) {
    return <Text>Loading agents...</Text>;
  }

  return (
    <Box>
      <List spacing={3}>
        {agents?.map((agent) => (
          <ListItem key={agent.id} p={4} borderWidth={1} borderRadius="md">
            <VStack align="start">
              <Text fontWeight="bold">{agent.name}</Text>
              <Text>{agent.description}</Text>
              <Text>Capabilities: {agent.capabilities.join(', ')}</Text>
              <Text>Status: {agent.status}</Text>
              <Button
                colorScheme="red"
                size="sm"
                onClick={() => deleteAgentMutation.mutate(agent.id)}
                aria-label="Delete agent"
              >
                Delete
              </Button>
            </VStack>
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default AgentList; 