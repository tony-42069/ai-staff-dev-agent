import { Box, VStack, Link, Text } from '@chakra-ui/react'
import { Link as RouterLink } from 'react-router-dom'

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Agents', path: '/agents' },
    { name: 'Projects', path: '/projects' },
    { name: 'Settings', path: '/settings' },
  ]

  return (
    <Box bg="white" h="full" borderRight="1px" borderColor="gray.200">
      <VStack spacing={2} align="stretch" p={4}>
        {navItems.map((item) => (
          <Link
            key={item.path}
            as={RouterLink}
            to={item.path}
            p={2}
            borderRadius="md"
            _hover={{ bg: 'gray.100', textDecoration: 'none' }}
          >
            <Text>{item.name}</Text>
          </Link>
        ))}
      </VStack>
    </Box>
  )
}

export default Sidebar 