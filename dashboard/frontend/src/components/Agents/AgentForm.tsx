import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Textarea,
  FormErrorMessage,
  useToast
} from '@chakra-ui/react';
import { FC, useState } from 'react';
import { useAgents } from '../../hooks/useAgents';

interface FormData {
  name: string;
  description: string;
  capabilities: string;
}

const AgentForm: FC = () => {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    capabilities: ''
  });
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const { createAgent } = useAgents();
  const toast = useToast();

  const validateForm = () => {
    const newErrors: Partial<FormData> = {};
    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    if (!formData.capabilities) {
      newErrors.capabilities = 'At least one capability is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    try {
      await createAgent.mutateAsync({
        name: formData.name,
        description: formData.description,
        capabilities: formData.capabilities.split(',').map(cap => cap.trim()),
        status: 'idle'
      });

      setFormData({
        name: '',
        description: '',
        capabilities: ''
      });

      toast({
        title: 'Agent created',
        description: 'The agent was successfully created',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create agent',
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
    // Clear error when user starts typing
    if (errors[name as keyof FormData]) {
      setErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
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
            placeholder="Enter agent name"
          />
          <FormErrorMessage>{errors.name}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Enter agent description"
          />
        </FormControl>

        <FormControl isInvalid={!!errors.capabilities}>
          <FormLabel>Capabilities</FormLabel>
          <Input
            name="capabilities"
            value={formData.capabilities}
            onChange={handleChange}
            placeholder="Enter capabilities (comma-separated)"
          />
          <FormErrorMessage>{errors.capabilities}</FormErrorMessage>
        </FormControl>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={createAgent.isPending}
        >
          Create Agent
        </Button>
      </VStack>
    </Box>
  );
};

export default AgentForm; 