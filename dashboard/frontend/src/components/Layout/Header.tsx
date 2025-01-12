import { Box, Flex, Heading, Spacer, IconButton, useColorMode } from '@chakra-ui/react'
import { SunIcon, MoonIcon } from '@chakra-ui/icons'
import { FC } from 'react'

const Header: FC = () => {
  const { colorMode, toggleColorMode } = useColorMode()

  return (
    <Box px={4} bg="white" borderBottom="1px" borderColor="gray.200">
      <Flex h={14} alignItems="center">
        <Heading size="md">AI Staff Dev Agent</Heading>
        <Spacer />
        <IconButton
          aria-label="Toggle color mode"
          icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
          onClick={toggleColorMode}
          size="sm"
          variant="ghost"
        />
      </Flex>
    </Box>
  )
}

export default Header 