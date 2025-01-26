import { Box, Input, IconButton, Flex, Text, useToast, Spinner, Badge } from '@chakra-ui/react'
import { ArrowUpIcon } from '@chakra-ui/icons'
import { FC, useState, useRef, useEffect, useCallback, useMemo } from 'react'
import { websocketService, WebSocketMessage } from '@/services/websocket'
import { useVirtualizer } from '@tanstack/react-virtual'
import React from 'react'
import { usePerformanceMonitor } from '@/hooks/usePerformanceMonitor'

interface Message {
  id: string
  content: string
  sender: 'user' | 'agent'
  timestamp: Date
  status?: 'sending' | 'sent' | 'error'
  type?: 'message' | 'command' | 'status' | 'metrics'
}

interface MessageItemProps {
  message: Message
}

const MessageItem = React.memo<MessageItemProps>(({ message }) => (
  <Box
    alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
    maxW="70%"
    data-testid="message"
    data-sender={message.sender}
    data-type={message.type}
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
        <Box mt={2} data-testid="message-status">
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
));

const Chat: FC = () => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const parentRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  const { startMeasure, endMeasure, measureMessageLatency, getMetrics } = usePerformanceMonitor('Chat')

  const rowVirtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 100,
    overscan: 5
  })

  const handleMessage = useCallback((wsMessage: WebSocketMessage) => {
    const startTime = performance.now()
    
    if (wsMessage.type === 'status' && wsMessage.content.includes('typing')) {
      setIsTyping(true)
      return
    }

    setIsTyping(false)
    const newMessage: Message = {
      id: Date.now().toString(),
      content: wsMessage.content,
      sender: wsMessage.sender as 'user' | 'agent',
      timestamp: new Date(wsMessage.timestamp),
      type: wsMessage.type === 'metrics' ? undefined : wsMessage.type,
      status: 'sent'
    }
    
    if (wsMessage.type === 'status') {
      setMessages(prev => prev.map(msg => 
        msg.status === 'sending' ? { ...msg, status: 'sent' } : msg
      ))
    } else {
      setMessages(prev => [...prev, newMessage])
    }

    measureMessageLatency(startTime)
  }, [measureMessageLatency])

  useEffect(() => {
    startMeasure()
    websocketService.connect()
    const messageUnsubscribe = websocketService.onMessage(handleMessage)
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

    return () => {
      messageUnsubscribe()
      connectedUnsubscribe()
      disconnectedUnsubscribe()
      errorUnsubscribe()
      websocketService.disconnect()
      endMeasure()
      console.debug('Chat Performance Metrics:', getMetrics())
    }
  }, [toast, handleMessage, startMeasure, endMeasure, getMetrics])

  const handleSend = useCallback(() => {
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
  }, [input, toast])

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }, [handleSend])

  const virtualItems = useMemo(() => rowVirtualizer.getVirtualItems(), [rowVirtualizer])

  return (
    <Box h="100%" display="flex" flexDirection="column">
      <Box 
        ref={parentRef}
        flex="1" 
        overflowY="auto" 
        p={4}
      >
        <Box
          height={`${rowVirtualizer.getTotalSize()}px`}
          width="100%"
          position="relative"
        >
          {virtualItems.map((virtualRow: { index: number; size: number; start: number }) => (
            <Box
              key={messages[virtualRow.index].id}
              position="absolute"
              top={0}
              left={0}
              width="100%"
              height={`${virtualRow.size}px`}
              transform={`translateY(${virtualRow.start}px)`}
            >
              <MessageItem message={messages[virtualRow.index]} />
            </Box>
          ))}
        </Box>
        {isTyping && (
          <Box alignSelf="flex-start" maxW="70%" data-testid="typing-indicator">
            <Box bg="gray.100" p={3} borderRadius="lg">
              <Spinner size="xs" mr={2} />
              <Text as="span">Agent is typing...</Text>
            </Box>
          </Box>
        )}
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
            data-testid="message-input"
          />
          <IconButton
            colorScheme="blue"
            aria-label="Send message"
            icon={<ArrowUpIcon />}
            onClick={handleSend}
            isDisabled={!isConnected}
            data-testid="send-button"
          />
        </Flex>
      </Box>
      <Box 
        position="absolute" 
        top={2} 
        right={2} 
        data-testid="connection-status"
      >
        <Badge colorScheme={isConnected ? 'green' : 'orange'}>
          {isConnected ? 'Connected' : 'Connecting...'}
        </Badge>
      </Box>
    </Box>
  )
}

export default Chat 