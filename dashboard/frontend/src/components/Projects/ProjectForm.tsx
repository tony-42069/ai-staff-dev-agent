import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Textarea,
  FormErrorMessage,
  useToast,
  Select,
  Checkbox,
  Stack
} from '@chakra-ui/react';
import { FC, useState } from 'react';
import { useProjects } from '../../hooks/useProjects';
import { useAgents } from '../../hooks/useAgents';

interface FormData {
  name: string;
  description: string;
  repository_url: string;
  assigned_agents: string[];
}

const ProjectForm: FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    repository_url: '',
    assigned_agents: []
  });
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const { createProject } = useProjects();
  const { agents } = useAgents();
  const toast = useToast();

  const validateForm = () => {
    const newErrors: Partial<FormData> = {};
    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      await createProject.mutateAsync({
        name: formData.name,
        description: formData.description,
        repository_url: formData.repository_url || undefined,
        assigned_agents: formData.assigned_agents,
        status: 'active'
      });

      setFormData({
        name: '',
        description: '',
        repository_url: '',
        assigned_agents: []
      });

      toast({
        title: 'Project created',
        description: 'The project was successfully created',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create project',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (errors[name as keyof FormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const handleAgentToggle = (agentId: string) => {
    setFormData(prev => ({
      ...prev,
      assigned_agents: prev.assigned_agents.includes(agentId)
        ? prev.assigned_agents.filter(id => id !== agentId)
        : [...prev.assigned_agents, agentId]
    }));
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={!!errors.name}>
          <FormLabel>Name</FormLabel>
          <Input
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter project name"
          />
          <FormErrorMessage>{errors.name}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter project description"
          />
        </FormControl>

        <FormControl>
          <FormLabel>Repository URL</FormLabel>
          <Input
            name="repository_url"
            value={formData.repository_url}
            onChange={handleChange}
            placeholder="Enter repository URL (optional)"
          />
        </FormControl>

        <FormControl>
          <FormLabel>Assign Agents</FormLabel>
          <Stack spacing={2} maxH="200px" overflowY="auto">
            {agents?.map(agent => (
              <Checkbox
                key={agent.id}
                isChecked={formData.assigned_agents.includes(agent.id)}
                onChange={() => handleAgentToggle(agent.id)}
              >
                {agent.name}
              </Checkbox>
            ))}
          </Stack>
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={createProject.isPending}
        >
          Create Project
        </Button>
      </VStack>
    </Box>
  );
};

export default ProjectForm; 