import { 
  Box, 
  Flex, 
  Heading, 
  IconButton, 
  useColorMode,
  HStack,
  Button,
  useColorModeValue,
  Container
} from '@chakra-ui/react'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'
import { FC } from 'react'
import { Link, useLocation } from 'react-router-dom'

const Header: FC = () => {
  const { colorMode, toggleColorMode } = useColorMode()
  const location = useLocation()
  
  // Color mode values
  const bg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const textColor = useColorModeValue('gray.800', 'white')
  const buttonHoverBg = useColorModeValue('gray.100', 'gray.700')

  const isActive = (path: string) => location.pathname === path

  const NavButton: FC<{ to: string; children: React.ReactNode }> = ({ to, children }) => (
    <Button
      as={Link}
      to={to}
      variant="ghost"
      colorScheme={isActive(to) ? 'blue' : 'gray'}
      bg={isActive(to) ? 'blue.50' : 'transparent'}
      color={isActive(to) ? 'blue.600' : textColor}
      _hover={{ bg: isActive(to) ? 'blue.100' : buttonHoverBg }}
      size="sm"
      px={4}
    >
      {children}
    </Button>
  )

  return (
    <Box 
      bg={bg} 
      borderBottom="1px" 
      borderColor={borderColor}
      height="60px"
      position="fixed"
      width="100%"
      zIndex={1000}
    >
      <Container maxW="1200px" height="100%">
        <Flex justify="space-between" align="center" height="100%" px={4}>
          <HStack spacing={8}>
            <Heading size="md" color={textColor}>AI Staff Dev Agent</Heading>
            <HStack spacing={2}>
              <NavButton to="/agents">Agents</NavButton>
              <NavButton to="/projects">Projects</NavButton>
              <NavButton to="/chat">Chat</NavButton>
            </HStack>
          </HStack>
          <IconButton
            aria-label="Toggle color mode"
            icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
            onClick={toggleColorMode}
            variant="ghost"
            color={textColor}
            _hover={{ bg: buttonHoverBg }}
            size="sm"
          />
        </Flex>
      </Container>
    </Box>
  )
}

export default Header
