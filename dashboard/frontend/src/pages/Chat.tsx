import { Box, Container, Heading, VStack } from '@chakra-ui/react'
import { FC } from 'react'
import Chat from '@/components/Chat/Chat'
import WebSocketTest from '@/components/Chat/WebSocketTest'

const ChatPage: FC = () => {
  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={6} align="stretch">
        <Heading size="lg">Chat with Agent</Heading>
        
        {/* WebSocket Test Panel */}
        <Box>
          <Heading size="md" mb={4}>WebSocket Connection Test</Heading>
          <WebSocketTest />
        </Box>

        {/* Chat Interface */}
        <Box
          bg="white"
          borderRadius="lg"
          boxShadow="sm"
          height="calc(100vh - 400px)"
        >
          <Chat />
        </Box>
      </VStack>
    </Container>
  )
}

export default ChatPage 