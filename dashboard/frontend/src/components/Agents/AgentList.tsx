import { Box, Table, Thead, Tbody, Tr, Th, Td, Text } from '@chakra-ui/react';
import { FC } from 'react';

const AgentList: FC = () => {
  // Temporary mock data
  const agents = [
    { id: 1, name: 'Dev Agent', status: 'Online', capabilities: 5 },
    { id: 2, name: 'Test Agent', status: 'Offline', capabilities: 3 }
  ];

  return (
    <Box borderWidth="1px" borderRadius="lg" p={4}>
      {agents.length === 0 ? (
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
                <Td><Text color={agent.status === 'Online' ? 'green.500' : 'red.500'}>{agent.status}</Text></Td>
                <Td>{agent.capabilities}</Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </Box>
  );
};

export default AgentList;
