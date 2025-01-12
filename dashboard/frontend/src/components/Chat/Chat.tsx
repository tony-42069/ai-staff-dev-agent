import { Box, VStack, Input, IconButton, Flex, Text, useToast } from '@chakra-ui/react'
import { ArrowUpIcon } from '@chakra-ui/icons'
import { FC, useState, useRef, useEffect } from 'react'
import { websocketService, WebSocketMessage } from '@/services/websocket'

interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: Date
}

const Chat: FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const toast = useToast()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    // Connect to WebSocket when component mounts
    websocketService.connect()

    // Set up event listeners
    const messageUnsubscribe = websocketService.onMessage((wsMessage: WebSocketMessage) => {
      const newMessage: Message = {
        id: Date.now().toString(),
        content: wsMessage.content,
        sender: wsMessage.sender,
        timestamp: new Date(wsMessage.timestamp)
      }
      setMessages(prev => [...prev, newMessage])
    })

    const connectedUnsubscribe = websocketService.onConnected(() => {
      setIsConnected(true)
      toast({
        title: 'Connected',
        description: 'Connected to chat server',
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
    })

    const disconnectedUnsubscribe = websocketService.onDisconnected(() => {
      setIsConnected(false)
      toast({
        title: 'Disconnected',
        description: 'Lost connection to chat server',
        status: 'warning',
        duration: null,
        isClosable: true,
      })
    })

    const errorUnsubscribe = websocketService.onError(() => {
      toast({
        title: 'Error',
        description: 'Failed to connect to chat server',
        status: 'error',
        duration: null,
        isClosable: true,
      })
    })

    // Clean up on unmount
    return () => {
      messageUnsubscribe()
      connectedUnsubscribe()
      disconnectedUnsubscribe()
      errorUnsubscribe()
      websocketService.disconnect()
    }
  }, [toast])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = () => {
    if (!input.trim()) return

    try {
      websocketService.sendMessage(input.trim())
      setInput('')
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to send message',
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <Box h="100%" display="flex" flexDirection="column">
      <Box flex="1" overflowY="auto" p={4}>
        <VStack spacing={4} align="stretch">
          {messages.map(message => (
            <Box
              key={message.id}
              alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
              maxW="70%"
            >
              <Box
                bg={message.sender === 'user' ? 'blue.500' : 'gray.100'}
                color={message.sender === 'user' ? 'white' : 'black'}
                p={3}
                borderRadius="lg"
              >
                <Text>{message.content}</Text>
              </Box>
              <Text fontSize="xs" color="gray.500" mt={1}>
                {message.timestamp.toLocaleTimeString()}
              </Text>
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      <Box p={4} borderTop="1px" borderColor="gray.200">
        <Flex>
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            mr={2}
            isDisabled={!isConnected}
          />
          <IconButton
            colorScheme="blue"
            aria-label="Send message"
            icon={<ArrowUpIcon />}
            onClick={handleSend}
            isDisabled={!isConnected}
          />
        </Flex>
      </Box>
    </Box>
  )
}

export default Chat 