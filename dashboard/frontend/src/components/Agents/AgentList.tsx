import { 
  Box, 
  Table, 
  Thead, 
  Tbody, 
  Tr, 
  Th, 
  Td, 
  Text, 
  Center, 
  Button, 
  HStack, 
  Tag, 
  IconButton,
  useToast,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Divider,
  useColorModeValue,
  Skeleton,
  Stack,
  Tooltip,
  Badge
} from '@chakra-ui/react';
import { FC } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Agent, agentApi } from '../../services/api';
import { RepeatIcon, DeleteIcon, EditIcon } from '@chakra-ui/icons';

interface ApiResponse<T> {
  data: T;
}

const AgentList: FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const tableBg = useColorModeValue('white', 'gray.800');
  const hoverBg = useColorModeValue('gray.50', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const descriptionColor = useColorModeValue('gray.600', 'gray.400');

  const { 
    data: agents = [], 
    isLoading, 
    error, 
    refetch,
    isRefetching 
  } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentApi.getAll();
      return (response as unknown as ApiResponse<Agent[]>).data;
    }
  });

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
        position: 'top-right'
      });
    },
    onError: () => {
      toast({
        title: 'Error deleting agent',
        description: 'Please try again later',
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
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
      <Card bg={cardBg} shadow="md" borderRadius="lg">
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Active Agents</Heading>
            <Skeleton height="32px" width="100px" />
          </HStack>
        </CardHeader>
        <Divider />
        <CardBody>
          <Stack spacing={4}>
            <Skeleton height="50px" />
            <Skeleton height="50px" />
            <Skeleton height="50px" />
          </Stack>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card bg={cardBg} shadow="md" borderRadius="lg">
        <CardHeader>
          <Heading size="md">Active Agents</Heading>
        </CardHeader>
        <Divider />
        <CardBody>
          <Alert
            status="error"
            variant="subtle"
            flexDirection="column"
            alignItems="center"
            justifyContent="center"
            textAlign="center"
            borderRadius="lg"
            py={6}
          >
            <AlertIcon boxSize="40px" mr={0} />
            <AlertTitle mt={4} mb={1} fontSize="lg">
              Failed to load agents
            </AlertTitle>
            <AlertDescription maxWidth="sm" mb={4}>
              There was an error loading the agents list. Please try again later.
            </AlertDescription>
            <Button
              leftIcon={<RepeatIcon />}
              onClick={() => refetch()}
              isLoading={isRefetching}
              colorScheme="blue"
            >
              Retry
            </Button>
          </Alert>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card bg={cardBg} shadow="md" borderRadius="lg">
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">Active Agents</Heading>
          <Button
            leftIcon={<RepeatIcon />}
            onClick={() => refetch()}
            isLoading={isRefetching}
            size="sm"
            colorScheme="blue"
            variant="outline"
          >
            Refresh
          </Button>
        </HStack>
      </CardHeader>
      <Divider />
      <CardBody p={0}>
        {agents.length === 0 ? (
          <Center p={8}>
            <Text color={descriptionColor}>No agents available</Text>
          </Center>
        ) : (
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead bg={tableBg}>
                <Tr>
                  <Th borderColor={borderColor}>Name</Th>
                  <Th borderColor={borderColor}>Status</Th>
                  <Th borderColor={borderColor}>Capabilities</Th>
                  <Th borderColor={borderColor} width="100px">Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {agents.map((agent: Agent) => (
                  <Tr 
                    key={agent.id}
                    _hover={{ bg: hoverBg }}
                    transition="background-color 0.2s"
                  >
                    <Td borderColor={borderColor}>
                      <Text fontWeight="medium">{agent.name}</Text>
                      {agent.description && (
                        <Text fontSize="sm" color={descriptionColor} mt={1}>
                          {agent.description}
                        </Text>
                      )}
                    </Td>
                    <Td borderColor={borderColor}>
                      <Badge
                        colorScheme={getStatusColor(agent.status)}
                        px={2}
                        py={1}
                        borderRadius="full"
                      >
                        {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                      </Badge>
                    </Td>
                    <Td borderColor={borderColor}>
                      <HStack spacing={2} wrap="wrap">
                        {agent.capabilities.map((capability: string, index: number) => (
                          <Tag 
                            key={index} 
                            size="sm" 
                            colorScheme="blue"
                            borderRadius="full"
                          >
                            {capability}
                          </Tag>
                        ))}
                      </HStack>
                    </Td>
                    <Td borderColor={borderColor}>
                      <HStack spacing={2}>
                        <Tooltip label="Edit agent" placement="top">
                          <IconButton
                            aria-label="Edit agent"
                            icon={<EditIcon />}
                            size="sm"
                            variant="ghost"
                            onClick={() => {
                              toast({
                                title: 'Edit functionality coming soon',
                                status: 'info',
                                duration: 2000,
                                position: 'top-right'
                              });
                            }}
                          />
                        </Tooltip>
                        <Tooltip label="Delete agent" placement="top">
                          <IconButton
                            aria-label="Delete agent"
                            icon={<DeleteIcon />}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => handleDelete(agent.id)}
                            isLoading={deleteMutation.isPending}
                          />
                        </Tooltip>
                      </HStack>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Box>
        )}
      </CardBody>
    </Card>
  );
};

export default AgentList;
