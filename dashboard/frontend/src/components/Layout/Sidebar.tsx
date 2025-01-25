import { Box, VStack, Link, Icon } from '@chakra-ui/react'
import { FiHome, FiUsers, FiFolder, FiSettings, FiMessageSquare } from 'react-icons/fi'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { FC, useState } from 'react'
import SidebarFilters from './SidebarFilters'

interface NavItemProps {
  to: string
  icon: any
  children: React.ReactNode
}

const NavItem: FC<NavItemProps> = ({ to, icon, children }) => {
  const location = useLocation()
  const isActive = location.pathname === to

  return (
    <Link
      as={RouterLink}
      to={to}
      w="full"
      p={3}
      borderRadius="md"
      bg={isActive ? 'blue.100' : 'transparent'}
      color={isActive ? 'blue.500' : 'gray.700'}
      _hover={{
        bg: isActive ? 'blue.100' : 'gray.100',
        textDecoration: 'none',
      }}
    >
      <Box display="flex" alignItems="center">
        <Icon as={icon} boxSize={5} mr={3} />
        {children}
      </Box>
    </Link>
  )
}

const Sidebar: FC = () => {
  const [filters, setFilters] = useState({});
  const location = useLocation();
  
  const handleFilterChange = (newFilters: any) => {
    setFilters(newFilters);
    // Emit filter changes to parent components
    const event = new CustomEvent('filterChange', { detail: newFilters });
    window.dispatchEvent(event);
  };

  return (
    <Box
      bg="white"
      w="full"
      h="full"
      py={5}
      borderRight="1px"
      borderColor="gray.200"
      overflowY="auto"
    >
      <VStack spacing={2} align="stretch" px={3} mb={4}>
        <NavItem to="/" icon={FiHome}>
          Dashboard
        </NavItem>
        <NavItem to="/agents" icon={FiUsers}>
          Agents
        </NavItem>
        <NavItem to="/projects" icon={FiFolder}>
          Projects
        </NavItem>
        <NavItem to="/chat" icon={FiMessageSquare}>
          Chat
        </NavItem>
        <NavItem to="/settings" icon={FiSettings}>
          Settings
        </NavItem>
      </VStack>
      
      {(location.pathname === '/agents' || location.pathname === '/projects') && (
        <SidebarFilters onFilterChange={handleFilterChange} />
      )}
    </Box>
  )
}

export default Sidebar
