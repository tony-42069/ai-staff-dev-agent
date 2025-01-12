import { Box, Flex, Heading, IconButton, useColorMode } from '@chakra-ui/react'
import { MoonIcon, SunIcon } from '@chakra-ui/icons'
import { FC } from 'react'

const Header: FC = () => {
  const { colorMode, toggleColorMode } = useColorMode()

  return (
    <Box bg="blue.500" px={4} py={2}>
      <Flex justify="space-between" align="center">
        <Heading size="md" color="white">AI Staff Dev Agent</Heading>
        <IconButton
          aria-label="Toggle color mode"
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          variant="ghost"
          color="white"
          _hover={{ bg: 'blue.600' }}
        />
      </Flex>
    </Box>
  )
}

export default Header
