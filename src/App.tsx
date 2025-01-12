import React from 'react'
import { ChakraProvider } from '@chakra-ui/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter as Router } from 'react-router-dom'
import { Box, Flex, Spacer, Button, Text, Link } from '@chakra-ui/react'

// Initialize React Query client
const queryClient = new QueryClient()

function App() {
  return (
    <ChakraProvider>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Flex direction="row" minH="100vh">
            {/* Sidebar */}
            <Box bg="gray.800" w="250px" p={4} color="white">
              <Text fontSize="xl" fontWeight="bold" mb={6}>AiStaff Dashboard</Text>
              <Flex direction="column" gap={3}>
                <Link href="/">Dashboard</Link>
                <Link href="/agents">Agents</Link>
                <Link href="/chat">Chat Interface</Link>
              </Flex>
            </Box>

            {/* Main Content */}
            <Box flex="1">
              {/* Header */}
              <Box bg="white" p={4} shadow="sm">
                <Flex>
                  <Text fontSize="lg">AiStaff</Text>
                  <Spacer />
                  <Button colorScheme="blue">New Agent</Button>
                </Flex>
              </Box>

              {/* Content Area */}
              <Box p={6}>
                {/* Routes will go here */}
              </Box>
            </Box>
          </Flex>
        </Router>
      </QueryClientProvider>
    </ChakraProvider>
  )
}

export default App