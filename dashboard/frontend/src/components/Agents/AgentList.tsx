import { Box, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton } from '@chakra-ui/react';
import { DeleteIcon, EditIcon } from '@chakra-ui/icons';
import { FC } from 'react';
import { useAgents } from '../../hooks/useAgents';

const AgentList: FC = () => {
  const { agents, isLoading, deleteAgent } = useAgents();

  const handleDelete = async (id: string) => {
    try {
      await deleteAgent.mutateAsync(id);
    } catch (error) {
      console.error('Failed to delete agent:', error);
    }
  };

  if (isLoading) {
    return <Box>Loading agents...</Box>;
  }

  return (
    <Box overflowX="auto">
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Description</Th>
            <Th>Capabilities</Th>
            <Th>Status</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {agents.map((agent) => (
            <Tr key={agent.id}>
              <Td>{agent.name}</Td>
              <Td>{agent.description}</Td>
              <Td>{agent.capabilities.join(', ')}</Td>
              <Td>
                <Badge
                  colorScheme={
                    agent.status === 'idle'
                      ? 'green'
                      : agent.status === 'busy'
                      ? 'yellow'
                      : 'red'
                  }
                >
                  {agent.status}
                </Badge>
              </Td>
              <Td>
                <IconButton
                  aria-label="Edit agent"
                  icon={<EditIcon />}
                  size="sm"
                  mr={2}
                  onClick={() => {/* TODO: Implement edit */}}
                />
                <IconButton
                  aria-label="Delete agent"
                  icon={<DeleteIcon />}
                  size="sm"
                  colorScheme="red"
                  onClick={() => handleDelete(agent.id)}
                />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default AgentList; 