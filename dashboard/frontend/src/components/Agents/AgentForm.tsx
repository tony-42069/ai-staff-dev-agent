import { Box, Button, FormControl, FormErrorMessage, FormLabel, Input, Textarea, useToast, VStack } from '@chakra-ui/react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { useState } from 'react';
import type { Agent } from '../../services/api';

const BASE_URL = 'http://localhost:8000/api/v1';

const AgentForm = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [capabilities, setCapabilities] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createAgentMutation = useMutation({
    mutationFn: async (newAgent: Partial<Agent>) => {
      const response = await axios.post(`${BASE_URL}/agents`, newAgent);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      toast({
        title: 'Agent created',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      // Reset form
      setName('');
      setDescription('');
      setCapabilities('');
      setErrors({});
    },
    onError: () => {
      toast({
        title: 'Error creating agent',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  });

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!name) newErrors.name = 'Name is required';
    if (!capabilities) newErrors.capabilities = 'Capabilities are required';
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    createAgentMutation.mutate({
      name,
      description,
      capabilities: capabilities.split(',').map(c => c.trim()),
    });
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={!!errors.name}>
          <FormLabel htmlFor="name">Name</FormLabel>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <FormErrorMessage>{errors.name}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel htmlFor="description">Description</FormLabel>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </FormControl>

        <FormControl isInvalid={!!errors.capabilities}>
          <FormLabel htmlFor="capabilities">Capabilities (comma-separated)</FormLabel>
          <Input
            id="capabilities"
            value={capabilities}
            onChange={(e) => setCapabilities(e.target.value)}
            placeholder="e.g., test,debug,deploy"
          />
          <FormErrorMessage>{errors.capabilities}</FormErrorMessage>
        </FormControl>

        <Button type="submit" colorScheme="blue">
          Create Agent
        </Button>
      </VStack>
    </Box>
  );
};

export default AgentForm; 