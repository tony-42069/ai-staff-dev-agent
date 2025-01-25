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
  AlertIcon,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Divider,
  Flex,
  IconButton,
  Tooltip,
  useColorModeValue
} from '@chakra-ui/react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Agent, agentApi } from '../../services/api';
import { AddIcon } from '@chakra-ui/icons';

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

  // Color mode values
  const cardBg = useColorModeValue('white', 'gray.700');
  const tagHoverBg = useColorModeValue('blue.100', 'blue.600');

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
        position: 'top-right'
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
        position: 'top-right'
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

  const addCapability = (cap: string) => {
    const currentCaps = capabilities
      .split(',')
      .map(c => c.trim())
      .filter(Boolean);
    
    if (!currentCaps.includes(cap)) {
      const newCaps = [...currentCaps, cap];
      setCapabilities(newCaps.join(', '));
      if (isSubmitted) validateForm(true);
    }
  };

  return (
    <Card bg={cardBg} shadow="md" borderRadius="lg">
      <CardHeader>
        <Heading size="md">Manage Agents</Heading>
      </CardHeader>
      <Divider />
      <CardBody>
        <Box as="form" onSubmit={handleSubmit}>
          <VStack spacing={6} align="stretch">
            <FormControl isInvalid={isSubmitted && !!errors.name}>
              <FormLabel htmlFor="name" fontWeight="medium">Name</FormLabel>
              <Input
                id="name"
                value={name}
                onChange={(e) => {
                  setName(e.target.value);
                  if (isSubmitted) validateForm(true);
                }}
                placeholder="Enter agent name"
                size="md"
                borderRadius="md"
              />
              <FormHelperText color="gray.500">
                Must be between 3 and 50 characters
              </FormHelperText>
              {errors.name && (
                <FormErrorMessage>
                  {errors.name}
                </FormErrorMessage>
              )}
            </FormControl>

            <FormControl>
              <FormLabel htmlFor="description" fontWeight="medium">Description</FormLabel>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Enter agent description (optional)"
                size="md"
                borderRadius="md"
                rows={3}
              />
            </FormControl>

            <FormControl isInvalid={isSubmitted && !!errors.capabilities}>
              <FormLabel htmlFor="capabilities" fontWeight="medium">Capabilities</FormLabel>
              <Input
                id="capabilities"
                value={capabilities}
                onChange={(e) => {
                  setCapabilities(e.target.value);
                  if (isSubmitted) validateForm(true);
                }}
                placeholder="e.g., code_review, testing, development"
                size="md"
                borderRadius="md"
              />
              <FormHelperText color="gray.500" mb={2}>
                Click to add capabilities or type them manually (comma-separated)
              </FormHelperText>
              
              <Flex wrap="wrap" gap={2}>
                {VALID_CAPABILITIES.map(cap => (
                  <Tooltip 
                    key={cap} 
                    label="Click to add"
                    placement="top"
                  >
                    <Tag
                      size="md"
                      variant="subtle"
                      colorScheme="blue"
                      cursor="pointer"
                      onClick={() => addCapability(cap)}
                      _hover={{ bg: tagHoverBg }}
                      display="flex"
                      alignItems="center"
                    >
                      {cap}
                      <IconButton
                        aria-label={`Add ${cap}`}
                        icon={<AddIcon />}
                        size="xs"
                        ml={1}
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation();
                          addCapability(cap);
                        }}
                      />
                    </Tag>
                  </Tooltip>
                ))}
              </Flex>
              
              {errors.capabilities && (
                <FormErrorMessage>
                  {errors.capabilities}
                </FormErrorMessage>
              )}
            </FormControl>

            {createAgentMutation.isError && (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                <Text>Failed to create agent. Please try again.</Text>
              </Alert>
            )}

            <Button 
              type="submit" 
              colorScheme="blue"
              isLoading={createAgentMutation.isPending}
              loadingText="Creating..."
              size="lg"
              width="full"
              mt={4}
            >
              Create Agent
            </Button>
          </VStack>
        </Box>
      </CardBody>
    </Card>
  );
};

export default AgentForm;
