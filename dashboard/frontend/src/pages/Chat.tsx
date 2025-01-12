import { Box, Container, Heading } from '@chakra-ui/react'
import { FC } from 'react'
import Chat from '@/components/Chat/Chat'

const ChatPage: FC = () => {
  return (
    <Container maxW="container.xl" py={8}>
      <Heading size="lg" mb={6}>Chat with Agent</Heading>
      <Box
        bg="white"
        borderRadius="lg"
        boxShadow="sm"
        height="calc(100vh - 200px)"
      >
        <Chat />
      </Box>
    </Container>
  )
}

export default ChatPage 