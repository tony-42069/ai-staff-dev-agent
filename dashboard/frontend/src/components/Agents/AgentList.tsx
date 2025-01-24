import { Box, Table, Thead, Tbody, Tr, Th, Td, Text, Spinner, Center } from '@chakra-ui/react';
import { FC } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Agent, agentApi } from '../../services/api';

const AgentList: FC = () => {
  const { data: agents, isLoading, error } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentApi.getAll();
      return response.data;
    }
  });

  if (isLoading) {
    return (
      <Center p={8}>
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error) {
    return (
      <Center p={8}>
        <Text color="red.500">Error loading agents. Please try again later.</Text>
      </Center>
    );
  }

  return (
    <Box borderWidth="1px" borderRadius="lg" p={4}>
      {!agents || agents.length === 0 ? (
        <Text>No agents available</Text>
      ) : (
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Status</Th>
              <Th>Capabilities</Th>
            </Tr>
          </Thead>
          <Tbody>
            {agents.map(agent => (
              <Tr key={agent.id}>
                <Td>{agent.name}</Td>
                <Td>
                  <Text color={agent.status === 'idle' ? 'green.500' : agent.status === 'busy' ? 'yellow.500' : 'red.500'}>
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </Text>
                </Td>
                <Td>{agent.capabilities.length}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </Box>
  );
};

export default AgentList;
