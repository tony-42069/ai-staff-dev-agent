import { Box, VStack, Input, IconButton, Flex, Text, useToast, Spinner } from '@chakra-ui/react'
import { ArrowUpIcon } from '@chakra-ui/icons'
import { FC, useState, useRef, useEffect } from 'react'
import { websocketService, WebSocketMessage } from '@/services/websocket'

interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: Date
  status?: 'sending' | 'sent' | 'error'
  type?: 'message' | 'command' | 'status'
}

const Chat: FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
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
      if (wsMessage.type === 'status' && wsMessage.content.includes('typing')) {
        setIsTyping(true)
        return
      }

      setIsTyping(false)
      const newMessage: Message = {
        id: Date.now().toString(),
        content: wsMessage.content,
        sender: wsMessage.sender,
        timestamp: new Date(wsMessage.timestamp),
        type: wsMessage.type,
        status: 'sent'
      }
      
      // Update status of pending messages
      if (wsMessage.type === 'status') {
        setMessages(prev => prev.map(msg => 
          msg.status === 'sending' ? { ...msg, status: 'sent' } : msg
        ))
      } else {
        setMessages(prev => [...prev, newMessage])
      }
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
      setIsTyping(false)
      toast({
        title: 'Disconnected',
        description: 'Lost connection to chat server',
        status: 'warning',
        duration: null,
        isClosable: true,
      })
    })

    const errorUnsubscribe = websocketService.onError(() => {
      setIsTyping(false)
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
      const isCommand = input.startsWith('/')
      const newMessage: Message = {
        id: Date.now().toString(),
        content: input.trim(),
        sender: 'user',
        timestamp: new Date(),
        status: 'sending',
        type: isCommand ? 'command' : 'message'
      }
      setMessages(prev => [...prev, newMessage])

      if (isCommand) {
        websocketService.sendCommand(input.trim().slice(1))
      } else {
        websocketService.sendMessage(input.trim())
      }
      
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
                opacity={message.status === 'sending' ? 0.7 : 1}
              >
                <Text>{message.content}</Text>
                {message.status === 'sending' && (
                  <Box mt={2}>
                    <Spinner size="xs" />
                  </Box>
                )}
              </Box>
              <Flex fontSize="xs" color="gray.500" mt={1} alignItems="center">
                <Text>{message.timestamp.toLocaleTimeString()}</Text>
                {message.type === 'command' && (
                  <Text ml={2} color="blue.500">Command</Text>
                )}
                {message.status === 'error' && (
                  <Text ml={2} color="red.500">Error</Text>
                )}
              </Flex>
            </Box>
          ))}
          {isTyping && (
            <Box alignSelf="flex-start" maxW="70%">
              <Box bg="gray.100" p={3} borderRadius="lg">
                <Spinner size="xs" mr={2} />
                <Text as="span">Agent is typing...</Text>
              </Box>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      <Box p={4} borderTop="1px" borderColor="gray.200">
        <Flex>
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Type your message or /command..." : "Connecting..."}
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