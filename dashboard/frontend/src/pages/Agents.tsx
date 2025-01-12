import { Box, Container, Heading, VStack } from '@chakra-ui/react';
import { FC } from 'react';
import AgentList from '../components/Agents/AgentList';
import AgentForm from '../components/Agents/AgentForm';

const AgentsPage: FC = () => {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={6}>Manage Agents</Heading>
          <AgentForm />
        </Box>
        
        <Box>
          <Heading size="md" mb={4}>Active Agents</Heading>
          <AgentList />
        </Box>
      </VStack>
    </Container>
  );
};

export default AgentsPage; 