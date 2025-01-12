import { Box, VStack, Text, Link } from '@chakra-ui/react'

export const Sidebar = () => {
  return (
    <Box bg="gray.800" w="250px" h="100vh" color="white" p={4}>
      <VStack align="stretch" spacing={4}>
        <Text fontSize="xl" fontWeight="bold">AiStaff Dashboard</Text>
        <Link href="/">Dashboard</Link>
        <Link href="/agents">Agents</Link>
        <Link href="/chat">Chat Interface</Link>
      </VStack>
    </Box>
  )
}