import { 
  Box, 
  Button, 
  FormControl, 
  FormErrorMessage, 
  FormLabel, 
  Input, 
  Textarea, 
  useToast, 
  VStack,
  FormHelperText,
  Tag,
  HStack,
  Text,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Agent, agentApi } from '../../services/api';

const VALID_CAPABILITIES = [
  'code_review',
  'testing',
  'development',
  'documentation',
  'deployment'
];

const AgentForm = () => {
  const toast = useToast();
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [capabilities, setCapabilities] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const createAgentMutation = useMutation({
    mutationFn: async (newAgent: Omit<Agent, 'id' | 'created_at' | 'updated_at' | 'status'>) => {
      const response = await agentApi.create({
        ...newAgent,
        status: 'idle'
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agents'] });
      toast({
        title: 'Success',
        description: 'Agent created successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      // Reset form
      setName('');
      setDescription('');
      setCapabilities('');
      setErrors({});
      setIsSubmitted(false);
    },
    onError: (error: any) => {
      toast({
        title: 'Error creating agent',
        description: error.response?.data?.detail || 'Please try again later',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      if (error.response?.data?.validation_errors) {
        setErrors(error.response.data.validation_errors);
      }
    }
  });

  const validateCapabilities = (caps: string[]): boolean => {
    const invalidCaps = caps.filter(cap => !VALID_CAPABILITIES.includes(cap));
    if (invalidCaps.length > 0) {
      setErrors(prev => ({
        ...prev,
        capabilities: `Invalid capabilities: ${invalidCaps.join(', ')}`
      }));
      return false;
    }
    return true;
  };

  const validateForm = (showErrors: boolean = false) => {
    const newErrors: Record<string, string> = {};
    
    // Name validation
    if (!name) {
      newErrors.name = 'Name is required';
    } else if (name.length < 3) {
      newErrors.name = 'Name must be at least 3 characters';
    } else if (name.length > 50) {
      newErrors.name = 'Name must be less than 50 characters';
    }

    // Capabilities validation
    if (!capabilities) {
      newErrors.capabilities = 'At least one capability is required';
    } else {
      const caps = capabilities.split(',').map(c => c.trim()).filter(Boolean);
      if (caps.length === 0) {
        newErrors.capabilities = 'At least one capability is required';
      } else if (!validateCapabilities(caps)) {
        return false;
      }
    }

    if (showErrors) {
      setErrors(newErrors);
    }
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitted(true);
    if (!validateForm(true)) return;

    const caps = capabilities.split(',').map(c => c.trim()).filter(Boolean);
    
    createAgentMutation.mutate({
      name,
      description,
      capabilities: caps,
    });
  };

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <VStack spacing={4} align="stretch">
        <FormControl isInvalid={isSubmitted && !!errors.name}>
          <FormLabel htmlFor="name">Name</FormLabel>
          <Input
            id="name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              if (isSubmitted) validateForm(true);
            }}
            placeholder="Enter agent name"
          />
          <FormHelperText>Must be between 3 and 50 characters</FormHelperText>
          <FormErrorMessage>{errors.name}</FormErrorMessage>
        </FormControl>

        <FormControl>
          <FormLabel htmlFor="description">Description</FormLabel>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter agent description (optional)"
          />
        </FormControl>

        <FormControl isInvalid={isSubmitted && !!errors.capabilities}>
          <FormLabel htmlFor="capabilities">Capabilities</FormLabel>
          <Input
            id="capabilities"
            value={capabilities}
            onChange={(e) => {
              setCapabilities(e.target.value);
              if (isSubmitted) validateForm(true);
            }}
            placeholder="e.g., code_review,testing,development"
          />
          <FormHelperText>
            Available capabilities:
            <HStack spacing={2} mt={2}>
              {VALID_CAPABILITIES.map(cap => (
                <Tag key={cap} size="sm" colorScheme="blue">
                  {cap}
                </Tag>
              ))}
            </HStack>
          </FormHelperText>
          <FormErrorMessage>{errors.capabilities}</FormErrorMessage>
        </FormControl>

        {createAgentMutation.isError && (
          <Alert status="error">
            <AlertIcon />
            <Text>Failed to create agent. Please try again.</Text>
          </Alert>
        )}

        <Button 
          type="submit" 
          colorScheme="blue"
          isLoading={createAgentMutation.isPending}
          loadingText="Creating..."
        >
          Create Agent
        </Button>
      </VStack>
    </Box>
  );
};

export default AgentForm;
