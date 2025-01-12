import { Box, Flex, Spacer, Button } from '@chakra-ui/react'

export const Header = () => {
  return (
    <Box bg="white" p={4} shadow="sm">
      <Flex>
        <Box>AiStaff</Box>
        <Spacer />
        <Button colorScheme="blue">New Agent</Button>
      </Flex>
    </Box>
  )
}