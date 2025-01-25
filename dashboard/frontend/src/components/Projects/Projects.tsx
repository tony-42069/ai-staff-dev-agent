import { FC, useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Button,
  Card,
  CardHeader,
  CardBody,
  Grid,
  GridItem,
  Text,
  IconButton,
  useToast,
  Badge,
  Stack,
  HStack,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  useColorModeValue,
  Heading,
  SimpleGrid,
  Divider,
  Tooltip,
  Code,
  Skeleton
} from '@chakra-ui/react';
import { EditIcon, DeleteIcon, AddIcon, ExternalLinkIcon } from '@chakra-ui/icons';
import {
  Project,
  CreateProjectDto,
  UpdateProjectDto,
  projectApi,
  agentApi,
  ApiResponse,
  Agent
} from '../../services/api';
import {
  VStack,
  Wrap,
  WrapItem,
  Checkbox
} from '@chakra-ui/react';

interface Filters {
  search?: string;
  statuses?: string[];
}

export const Projects: FC = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const metadataBg = useColorModeValue('gray.50', 'gray.800');
  const descriptionColor = useColorModeValue('gray.600', 'gray.400');

  // State
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedCapability, setSelectedCapability] = useState<string | null>(null);
  const [formData, setFormData] = useState<CreateProjectDto>({
    name: '',
    description: '',
    status: 'active',
    project_metadata: {},
  });
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showExecuteModal, setShowExecuteModal] = useState(false);
  const [filters, setFilters] = useState<Filters>({});
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([]);

  // Query agents and projects
  const { data: agents } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await agentApi.getAll();
      return (response as unknown as ApiResponse<Agent[]>).data;
    }
  });

  const { 
    data: projects = [], 
    isLoading,
    error,
    refetch,
    isRefetching
  } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectApi.getAll();
      return (response as unknown as ApiResponse<Project[]>).data;
    }
  });

  // Listen for filter changes from sidebar
  useEffect(() => {
    const handleFilterChange = (event: CustomEvent<Filters>) => {
      setFilters(event.detail);
    };

    window.addEventListener('filterChange', handleFilterChange as EventListener);
    return () => {
      window.removeEventListener('filterChange', handleFilterChange as EventListener);
    };
  }, []);

  // Initialize filteredProjects with projects data
  useEffect(() => {
    setFilteredProjects(projects);
  }, [projects]);

  // Apply filters to projects
  useEffect(() => {
    if (!projects.length) return;

    let result = [...projects];

    if (filters.search) {
      const searchTerm = filters.search.toLowerCase();
      result = result.filter(
        project =>
          project.name.toLowerCase().includes(searchTerm) ||
          project.description?.toLowerCase().includes(searchTerm)
      );
    }

    if (filters.statuses?.length) {
      result = result.filter(project => filters.statuses?.includes(project.status));
    }

    setFilteredProjects(result);
  }, [projects, filters]);

  // Create project mutation
  const createMutation = useMutation({
    mutationFn: (data: CreateProjectDto) => projectApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setIsCreateModalOpen(false);
      resetForm();
      toast({
        title: 'Project created',
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
      });
    },
    onError: () => {
      toast({
        title: 'Error creating project',
        description: 'Please try again later',
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
      });
    }
  });

  // Update project mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateProjectDto }) =>
      projectApi.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setIsEditModalOpen(false);
      setSelectedProject(null);
      toast({
        title: 'Project updated',
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
      });
    },
    onError: () => {
      toast({
        title: 'Error updating project',
        description: 'Please try again later',
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
      });
    }
  });

  // Delete project mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => projectApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      toast({
        title: 'Project deleted',
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
      });
    },
    onError: () => {
      toast({
        title: 'Error deleting project',
        description: 'Please try again later',
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: 'top-right'
      });
    }
  });

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      status: 'active',
      project_metadata: {},
    });
  };

  const handleCreateSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    createMutation.mutate(formData);
  };

  const handleEditSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (selectedProject) {
      updateMutation.mutate({
        id: selectedProject.id,
        data: formData,
      });
    }
  };

  const handleEdit = (project: Project) => {
    setSelectedProject(project);
    setFormData({
      name: project.name,
      description: project.description || '',
      status: project.status,
      project_metadata: project.project_metadata,
    });
    setIsEditModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this project?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleStatusChange = (value: string) => {
    setFormData({
      ...formData,
      status: value as Project['status'],
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'completed':
        return 'blue';
      case 'archived':
        return 'gray';
      default:
        return 'gray';
    }
  };

  if (isLoading || !filteredProjects) {
    return (
      <Box p={5}>
        <Card bg={cardBg} shadow="md" borderRadius="lg">
          <CardHeader>
            <HStack justify="space-between">
              <Heading size="md">Projects</Heading>
              <Skeleton height="32px" width="120px" data-testid="skeleton" />
            </HStack>
          </CardHeader>
          <Divider />
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              <Skeleton height="200px" data-testid="skeleton" />
              <Skeleton height="200px" data-testid="skeleton" />
              <Skeleton height="200px" data-testid="skeleton" />
            </SimpleGrid>
          </CardBody>
        </Card>
      </Box>
    );
  }

  return (
    <Box p={5}>
      <Card bg={cardBg} shadow="md" borderRadius="lg">
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Projects</Heading>
            <HStack spacing={2}>
              <Button
                leftIcon={<EditIcon />}
                onClick={() => setIsCreateModalOpen(true)}
                colorScheme="blue"
                size="sm"
              >
                Create Project
              </Button>
            </HStack>
          </HStack>
        </CardHeader>
        <Divider />
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {filteredProjects.map((project) => (
              <Card key={project.id} variant="outline" size="sm">
                <CardBody>
                  <Stack spacing={3}>
                    <HStack justify="space-between" align="flex-start">
                      <Box>
                        <Heading size="sm" mb={1}>
                          {project.name}
                        </Heading>
                        <Badge colorScheme={getStatusColor(project.status)}>
                          {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                        </Badge>
                      </Box>
                      <HStack>
                        <Tooltip label="Edit project">
                          <IconButton
                            aria-label="Edit project"
                            icon={<EditIcon />}
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(project)}
                          />
                        </Tooltip>
                        <Tooltip label="Delete project">
                          <IconButton
                            aria-label="Delete project"
                            icon={<DeleteIcon />}
                            size="sm"
                            variant="ghost"
                            colorScheme="red"
                            onClick={() => handleDelete(project.id)}
                          />
                        </Tooltip>
                      </HStack>
                    </HStack>
                    
                    {project.description && (
                      <Text fontSize="sm" color={descriptionColor}>
                        {project.description}
                      </Text>
                    )}

                    {/* Agent Operations */}
                    <Box>
                      <HStack spacing={2} mb={2}>
                        <Button
                          size="xs"
                          leftIcon={<AddIcon />}
                          onClick={() => {
                            setSelectedProject(project);
                            setShowAssignModal(true);
                          }}
                        >
                          Assign Agent
                        </Button>
                        <Button
                          size="xs"
                          leftIcon={<ExternalLinkIcon />}
                          onClick={() => {
                            setSelectedProject(project);
                            setShowExecuteModal(true);
                          }}
                          isDisabled={!project.agent_metadata.assigned_agents.length}
                        >
                          Execute Capability
                        </Button>
                      </HStack>

                      {/* Assigned Agents */}
                      {project.agent_metadata.assigned_agents.length > 0 && (
                        <Box mb={2}>
                          <Text fontSize="sm" fontWeight="medium">
                            Assigned Agents
                          </Text>
                          <Wrap spacing={2}>
                            {project.agent_metadata.assigned_agents.map((agentId) => (
                              <WrapItem key={agentId}>
                                <Badge>{agentId}</Badge>
                              </WrapItem>
                            ))}
                          </Wrap>
                        </Box>
                      )}

                      {/* Operation History */}
                      {project.agent_metadata.operation_history.length > 0 && (
                        <Box>
                          <Text fontSize="sm" fontWeight="medium" mb={1}>
                            Recent Operations
                          </Text>
                          <VStack spacing={1} align="stretch">
                            {project.agent_metadata.operation_history.slice(-3).map((op, i) => (
                              <Box
                                key={i}
                                p={1}
                                borderRadius="sm"
                                bg={op.status === 'completed' ? 'green.50' : 'red.50'}
                                fontSize="xs"
                              >
                                <Text>
                                  {op.capability} by {op.agent_id}
                                </Text>
                                <Text color="gray.600">
                                  {new Date(op.timestamp).toLocaleString()}
                                </Text>
                                {op.error && (
                                  <Text color="red.500">Error: {op.error}</Text>
                                )}
                              </Box>
                            ))}
                          </VStack>
                        </Box>
                      )}
                    </Box>

                    {/* Project Metadata */}
                    {project.project_metadata && Object.keys(project.project_metadata).length > 0 && (
                      <Box
                        bg={metadataBg}
                        p={2}
                        borderRadius="md"
                        fontSize="sm"
                      >
                        <Text fontWeight="medium" mb={1}>
                          Metadata
                        </Text>
                        <Code
                          display="block"
                          whiteSpace="pre"
                          children={JSON.stringify(project.project_metadata, null, 2)}
                          p={2}
                          borderRadius="md"
                          fontSize="xs"
                        />
                      </Box>
                    )}
                  </Stack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Create Project Modal */}
      <Modal isOpen={isCreateModalOpen} onClose={() => setIsCreateModalOpen(false)}>
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleCreateSubmit}>
          <ModalHeader>Create Project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Name</FormLabel>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Status</FormLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </Select>
              </FormControl>
            </Stack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setIsCreateModalOpen(false)}>
              Cancel
            </Button>
            <Button colorScheme="blue" type="submit" isLoading={createMutation.isPending}>
              Create
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Assign Agent Modal */}
      <Modal isOpen={showAssignModal} onClose={() => setShowAssignModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Assign Agent to Project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={4}>
              <FormControl>
                <FormLabel>Select Agent</FormLabel>
                <Select
                  value={selectedAgent || ''}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                >
                  <option value="">Select an agent...</option>
                  {agents?.map((agent) => (
                    <option key={agent.id} value={agent.id}>
                      {agent.name}
                    </option>
                  ))}
                </Select>
              </FormControl>

              {selectedAgent && (
                <FormControl>
                  <FormLabel>Select Capabilities</FormLabel>
                  <Stack spacing={2}>
                    {agents?.find(a => a.id === selectedAgent)?.capabilities.map((cap) => (
                      <Checkbox
                        key={cap}
                        isChecked={selectedProject?.agent_metadata.capability_requirements.includes(cap)}
                        onChange={(e) => {
                          if (selectedProject) {
                            const requirements = [...selectedProject.agent_metadata.capability_requirements];
                            if (e.target.checked) {
                              requirements.push(cap);
                            } else {
                              const index = requirements.indexOf(cap);
                              if (index > -1) {
                                requirements.splice(index, 1);
                              }
                            }
                            setSelectedProject({
                              ...selectedProject,
                              agent_metadata: {
                                ...selectedProject.agent_metadata,
                                capability_requirements: requirements
                              }
                            });
                          }
                        }}
                      >
                        {cap}
                      </Checkbox>
                    ))}
                  </Stack>
                </FormControl>
              )}
            </Stack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowAssignModal(false)}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={async () => {
                if (selectedProject && selectedAgent) {
                  try {
                    await agentApi.assignToProject(selectedAgent, {
                      project_id: selectedProject.id,
                      capabilities: selectedProject.agent_metadata.capability_requirements
                    });
                    queryClient.invalidateQueries({ queryKey: ['projects'] });
                    setShowAssignModal(false);
                    toast({
                      title: 'Agent assigned successfully',
                      status: 'success',
                      duration: 3000
                    });
                  } catch (error) {
                    toast({
                      title: 'Failed to assign agent',
                      description: error instanceof Error ? error.message : 'Unknown error',
                      status: 'error',
                      duration: 3000
                    });
                  }
                }
              }}
              isDisabled={!selectedAgent || !selectedProject?.agent_metadata.capability_requirements.length}
            >
              Assign
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Execute Capability Modal */}
      <Modal isOpen={showExecuteModal} onClose={() => setShowExecuteModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Execute Agent Capability</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={4}>
              <FormControl>
                <FormLabel>Select Agent</FormLabel>
                <Select
                  value={selectedAgent || ''}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                >
                  <option value="">Select an agent...</option>
                  {selectedProject?.agent_metadata.assigned_agents.map((agentId) => {
                    const agent = agents?.find(a => a.id === agentId);
                    return agent ? (
                      <option key={agent.id} value={agent.id}>
                        {agent.name}
                      </option>
                    ) : null;
                  })}
                </Select>
              </FormControl>

              {selectedAgent && (
                <FormControl>
                  <FormLabel>Select Capability</FormLabel>
                  <Select
                    value={selectedCapability || ''}
                    onChange={(e) => setSelectedCapability(e.target.value)}
                  >
                    <option value="">Select a capability...</option>
                    {agents?.find(a => a.id === selectedAgent)?.capabilities.map((cap) => (
                      <option key={cap} value={cap}>
                        {cap}
                      </option>
                    ))}
                  </Select>
                </FormControl>
              )}
            </Stack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowExecuteModal(false)}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={async () => {
                if (selectedProject && selectedAgent && selectedCapability) {
                  try {
                    await agentApi.executeCapability(selectedAgent, {
                      project_id: selectedProject.id,
                      capability: selectedCapability
                    });
                    queryClient.invalidateQueries({ queryKey: ['projects'] });
                    setShowExecuteModal(false);
                    toast({
                      title: 'Capability execution started',
                      status: 'success',
                      duration: 3000
                    });
                  } catch (error) {
                    toast({
                      title: 'Failed to execute capability',
                      description: error instanceof Error ? error.message : 'Unknown error',
                      status: 'error',
                      duration: 3000
                    });
                  }
                }
              }}
              isDisabled={!selectedAgent || !selectedCapability}
            >
              Execute
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Edit Project Modal */}
      <Modal isOpen={isEditModalOpen} onClose={() => setIsEditModalOpen(false)}>
        <ModalOverlay />
        <ModalContent as="form" onSubmit={handleEditSubmit}>
          <ModalHeader>Edit Project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Stack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Name</FormLabel>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Description</FormLabel>
                <Textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </FormControl>
              <FormControl>
                <FormLabel>Status</FormLabel>
                <Select
                  value={formData.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                >
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </Select>
              </FormControl>
            </Stack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button colorScheme="blue" type="submit" isLoading={updateMutation.isPending}>
              Save
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};
