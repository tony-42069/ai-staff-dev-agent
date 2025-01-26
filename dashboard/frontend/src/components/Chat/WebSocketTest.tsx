import { FC, useEffect, useState } from 'react'
import { Box, Button, Text, VStack, Badge, useToast } from '@chakra-ui/react'
import { websocketService, WebSocketMessage } from '@services/websocket'

const WebSocketTest: FC = () => {
  const [status, setStatus] = useState<'disconnected' | 'connected' | 'error'>('disconnected')
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const toast = useToast()

  useEffect(() => {
    const onConnected = () => {
      setStatus('connected')
      toast({
        title: 'WebSocket Connected',
        status: 'success',
        duration: 3000,
      })
    }

    const onDisconnected = () => {
      setStatus('disconnected')
      toast({
        title: 'WebSocket Disconnected',
        status: 'warning',
        duration: 3000,
      })
    }

    const onError = (error: Event) => {
      setStatus('error')
      toast({
        title: 'WebSocket Error',
        description: error.toString(),
        status: 'error',
        duration: 5000,
      })
    }

    const onMessage = (message: WebSocketMessage) => {
      setLastMessage(message)
      toast({
        title: 'Message Received',
        description: `Type: ${message.type}, Content: ${message.content}`,
        status: 'info',
        duration: 3000,
      })
    }

    // Set up listeners
    const cleanupConnected = websocketService.onConnected(onConnected)
    const cleanupDisconnected = websocketService.onDisconnected(onDisconnected)
    const cleanupError = websocketService.onError(onError)
    const cleanupMessage = websocketService.onMessage(onMessage)

    // Connect on mount
    websocketService.connect()

    // Cleanup on unmount
    return () => {
      cleanupConnected()
      cleanupDisconnected()
      cleanupError()
      cleanupMessage()
      websocketService.disconnect()
    }
  }, [toast])

  const handleTestMessage = () => {
    try {
      websocketService.sendMessage('Test message')
    } catch (error) {
      toast({
        title: 'Failed to send message',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const handleTestCommand = () => {
    try {
      websocketService.sendCommand('test_command')
    } catch (error) {
      toast({
        title: 'Failed to send command',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
        duration: 3000,
      })
    }
  }

  const handleReconnect = () => {
    websocketService.disconnect()
    websocketService.connect()
  }

  return (
    <Box p={4} borderWidth={1} borderRadius="lg">
      <VStack spacing={4} align="stretch">
        <Box>
          <Text fontWeight="bold" mb={2}>WebSocket Status:</Text>
          <Badge
            colorScheme={
              status === 'connected' ? 'green' :
              status === 'disconnected' ? 'yellow' :
              'red'
            }
          >
            {status}
          </Badge>
        </Box>

        {lastMessage && (
          <Box>
            <Text fontWeight="bold" mb={2}>Last Message:</Text>
            <Text>Type: {lastMessage.type}</Text>
            <Text>Content: {lastMessage.content}</Text>
            <Text>Sender: {lastMessage.sender}</Text>
            <Text>Timestamp: {new Date(lastMessage.timestamp).toLocaleString()}</Text>
          </Box>
        )}

        <Box>
          <Button
            colorScheme="blue"
            mr={2}
            onClick={handleTestMessage}
            isDisabled={status !== 'connected'}
          >
            Send Test Message
          </Button>
          <Button
            colorScheme="green"
            mr={2}
            onClick={handleTestCommand}
            isDisabled={status !== 'connected'}
          >
            Send Test Command
          </Button>
          <Button
            colorScheme="yellow"
            onClick={handleReconnect}
          >
            Reconnect
          </Button>
        </Box>
      </VStack>
    </Box>
  )
}

export default WebSocketTest 