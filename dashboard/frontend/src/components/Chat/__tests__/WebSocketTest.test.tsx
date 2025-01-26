import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { ChakraProvider } from '@chakra-ui/react'
import WebSocketTest from '../WebSocketTest'
import { websocketService, WebSocketMessage } from '@services/websocket'
import { vi, describe, it, expect, beforeEach } from 'vitest'

// Mock the websocket service
vi.mock('@services/websocket', () => {
  const mockCleanup = vi.fn()
  return {
    websocketService: {
      connect: vi.fn(),
      disconnect: vi.fn(),
      sendMessage: vi.fn(),
      sendCommand: vi.fn(),
      onConnected: vi.fn(() => mockCleanup),
      onDisconnected: vi.fn(() => mockCleanup),
      onError: vi.fn(() => mockCleanup),
      onMessage: vi.fn(() => mockCleanup),
    },
    WebSocketMessage: {
      type: 'message' as const,
      content: '',
      sender: 'user' as const,
      timestamp: '',
    },
  }
})

describe('WebSocketTest', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders WebSocket test component', () => {
    render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    expect(screen.getByText('WebSocket Status:')).toBeInTheDocument()
    expect(screen.getByText('disconnected')).toBeInTheDocument()
    expect(screen.getByText('Send Test Message')).toBeInTheDocument()
    expect(screen.getByText('Send Test Command')).toBeInTheDocument()
    expect(screen.getByText('Reconnect')).toBeInTheDocument()
  })

  it('connects to WebSocket on mount', () => {
    render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    expect(websocketService.connect).toHaveBeenCalled()
  })

  it('disconnects from WebSocket on unmount', () => {
    const { unmount } = render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    unmount()
    expect(websocketService.disconnect).toHaveBeenCalled()
  })

  it('sends test message when button is clicked', async () => {
    render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    // Simulate connected state
    const onConnected = (websocketService.onConnected as ReturnType<typeof vi.fn>).mock.calls[0][0]
    onConnected()

    // Click the send message button
    fireEvent.click(screen.getByText('Send Test Message'))
    expect(websocketService.sendMessage).toHaveBeenCalledWith('Test message')
  })

  it('sends test command when button is clicked', async () => {
    render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    // Simulate connected state
    const onConnected = (websocketService.onConnected as ReturnType<typeof vi.fn>).mock.calls[0][0]
    onConnected()

    // Click the send command button
    fireEvent.click(screen.getByText('Send Test Command'))
    expect(websocketService.sendCommand).toHaveBeenCalledWith('test_command')
  })

  it('handles reconnection when button is clicked', () => {
    render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    // Click the reconnect button
    fireEvent.click(screen.getByText('Reconnect'))
    expect(websocketService.disconnect).toHaveBeenCalled()
    expect(websocketService.connect).toHaveBeenCalled()
  })

  it('displays received messages', async () => {
    render(
      <ChakraProvider>
        <WebSocketTest />
      </ChakraProvider>
    )

    // Simulate message received
    const onMessage = (websocketService.onMessage as ReturnType<typeof vi.fn>).mock.calls[0][0]
    const testMessage: WebSocketMessage = {
      type: 'message',
      content: 'Test response',
      sender: 'agent',
      timestamp: new Date().toISOString(),
    }
    onMessage(testMessage)

    await waitFor(() => {
      expect(screen.getByText('Last Message:')).toBeInTheDocument()
      expect(screen.getByText('Content: Test response')).toBeInTheDocument()
    })
  })
}) 