import { 
  Box, 
  Table, 
  Thead, 
  Tbody, 
  Tr, 
  Th, 
  Td, 
  Text, 
  Spinner, 
  Center, 
  Button, 
  HStack, 
  Tag, 
  IconButton,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription
} from '@chakra-ui/react';
import { FC } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Agent, agentApi, ApiResponse } from '../../services/api';
import { RepeatIcon, DeleteIcon, EditIcon } from '@chakra-ui/icons';

const AgentList: FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();

  const { 
    data: response, 
    isLoading, 
    error, 
    refetch,
    isRefetching 
  } = useQuery<ApiResponse<Agent[]>>({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentApi.getAll();
      return response.data;
    }
  });

  const agents = response?.data;

  const deleteMutation = useMutation({
    mutationFn: async (agentId: string) => {
      await agentApi.delete(agentId);
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
        description: 'Please try again later',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  });

  const handleDelete = async (agentId: string) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      deleteMutation.mutate(agentId);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'green';
      case 'busy':
        return 'yellow';
      case 'error':
        return 'red';
      default:
        return 'gray';
    }
  };

  if (isLoading) {
    return (
      <Center p={8}>
        <Spinner size="xl" />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert
        status="error"
        variant="subtle"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        textAlign="center"
        height="200px"
        borderRadius="lg"
      >
        <AlertIcon boxSize="40px" mr={0} />
        <AlertTitle mt={4} mb={1} fontSize="lg">
          Failed to load agents
        </AlertTitle>
        <AlertDescription maxWidth="sm">
          There was an error loading the agents list. Please try again later.
        </AlertDescription>
        <Button
          leftIcon={<RepeatIcon />}
          onClick={() => refetch()}
          mt={4}
          isLoading={isRefetching}
        >
          Retry
        </Button>
      </Alert>
    );
  }

  return (
    <Box borderWidth="1px" borderRadius="lg" p={4}>
      <HStack mb={4} justify="space-between">
        <Text fontSize="lg" fontWeight="semibold">Active Agents</Text>
        <Button
          leftIcon={<RepeatIcon />}
          onClick={() => refetch()}
          isLoading={isRefetching}
          size="sm"
        >
          Refresh
        </Button>
      </HStack>

      {!agents || agents.length === 0 ? (
        <Center p={8}>
          <Text color="gray.500">No agents available</Text>
        </Center>
      ) : (
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Status</Th>
              <Th>Capabilities</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {agents.map((agent: Agent) => (
              <Tr key={agent.id}>
                <Td>
                  <Text fontWeight="medium">{agent.name}</Text>
                  {agent.description && (
                    <Text fontSize="sm" color="gray.600">
                      {agent.description}
                    </Text>
                  )}
                </Td>
                <Td>
                  <Tag colorScheme={getStatusColor(agent.status)}>
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </Tag>
                </Td>
                <Td>
                  <HStack spacing={2} wrap="wrap">
                    {agent.capabilities.map((capability: string, index: number) => (
                      <Tag key={index} size="sm" colorScheme="blue">
                        {capability}
                      </Tag>
                    ))}
                  </HStack>
                </Td>
                <Td>
                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Edit agent"
                      icon={<EditIcon />}
                      size="sm"
                      variant="ghost"
                      onClick={() => {
                        // TODO: Implement edit functionality
                        toast({
                          title: 'Edit functionality coming soon',
                          status: 'info',
                          duration: 2000,
                        });
                      }}
                    />
                    <IconButton
                      aria-label="Delete agent"
                      icon={<DeleteIcon />}
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      onClick={() => handleDelete(agent.id)}
                      isLoading={deleteMutation.isPending}
                    />
                  </HStack>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </Box>
  );
};

export default AgentList;
