import { Box, Table, Thead, Tbody, Tr, Th, Td, Badge, IconButton, Menu, MenuButton, MenuList, MenuItem } from '@chakra-ui/react';
import { DeleteIcon, EditIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { FC } from 'react';
import { useProjects } from '../../hooks/useProjects';

const ProjectList: FC = () => {
  const { projects, isLoading, deleteProject, updateProject } = useProjects();

  const handleDelete = async (id: string) => {
    try {
      await deleteProject.mutateAsync(id);
    } catch (error) {
      console.error('Failed to delete project:', error);
    }
  };

  const handleStatusChange = async (id: string, status: 'active' | 'archived' | 'completed') => {
    try {
      await updateProject.mutateAsync({
        id,
        data: { status }
      });
    } catch (error) {
      console.error('Failed to update project status:', error);
    }
  };

  if (isLoading) {
    return <Box>Loading projects...</Box>;
  }

  return (
    <Box overflowX="auto">
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Name</Th>
            <Th>Description</Th>
            <Th>Repository</Th>
            <Th>Status</Th>
            <Th>Assigned Agents</Th>
            <Th>Actions</Th>
          </Tr>
        </Thead>
        <Tbody>
          {projects.map((project) => (
            <Tr key={project.id}>
              <Td>{project.name}</Td>
              <Td>{project.description}</Td>
              <Td>
                {project.repository_url && (
                  <a href={project.repository_url} target="_blank" rel="noopener noreferrer">
                    View Repository
                  </a>
                )}
              </Td>
              <Td>
                <Menu>
                  <MenuButton
                    as={Badge}
                    colorScheme={
                      project.status === 'active'
                        ? 'green'
                        : project.status === 'completed'
                        ? 'blue'
                        : 'gray'
                    }
                    cursor="pointer"
                    display="flex"
                    alignItems="center"
                    px={2}
                    py={1}
                  >
                    {project.status}
                    <ChevronDownIcon ml={1} />
                  </MenuButton>
                  <MenuList>
                    <MenuItem onClick={() => handleStatusChange(project.id, 'active')}>
                      Active
                    </MenuItem>
                    <MenuItem onClick={() => handleStatusChange(project.id, 'completed')}>
                      Completed
                    </MenuItem>
                    <MenuItem onClick={() => handleStatusChange(project.id, 'archived')}>
                      Archived
                    </MenuItem>
                  </MenuList>
                </Menu>
              </Td>
              <Td>{project.assigned_agents.length}</Td>
              <Td>
                <IconButton
                  aria-label="Edit project"
                  icon={<EditIcon />}
                  size="sm"
                  mr={2}
                  onClick={() => {/* TODO: Implement edit */}}
                />
                <IconButton
                  aria-label="Delete project"
                  icon={<DeleteIcon />}
                  size="sm"
                  colorScheme="red"
                  onClick={() => handleDelete(project.id)}
                />
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </Box>
  );
};

export default ProjectList; 