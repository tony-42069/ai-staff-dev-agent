import { Box, Container, Heading, VStack } from '@chakra-ui/react';
import { FC } from 'react';
import ProjectList from '../components/Projects/ProjectList';
import ProjectForm from '../components/Projects/ProjectForm';

const ProjectsPage: FC = () => {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        <Box>
          <Heading size="lg" mb={6}>Manage Projects</Heading>
          <ProjectForm />
        </Box>
        
        <Box>
          <Heading size="md" mb={4}>Projects</Heading>
          <ProjectList />
        </Box>
      </VStack>
    </Container>
  );
};

export default ProjectsPage; 