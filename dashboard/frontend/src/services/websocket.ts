type EventCallback = (...args: any[]) => void

class EventEmitter {
  private events: Record<string, EventCallback[]> = {}

  on(event: string, callback: EventCallback) {
    if (!this.events[event]) {
      this.events[event] = []
    }
    this.events[event].push(callback)
  }

  off(event: string, callback: EventCallback) {
    if (this.events[event]) {
      this.events[event] = this.events[event].filter(cb => cb !== callback)
    }
  }

  emit(event: string, ...args: any[]) {
    if (this.events[event]) {
      this.events[event].forEach(callback => callback(...args))
    }
  }
}

interface WebSocketMessage {
  type: 'message' | 'command' | 'status' | 'metrics'
  content: string
  sender: 'user' | 'agent' | string
  timestamp: string
}

class WebSocketService {
  private ws: WebSocket | null = null
  private events = new EventEmitter()
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimeout = 3000
  private clientId: string
  private url: string

  constructor() {
    this.clientId = crypto.randomUUID()
    this.url = `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000'}/ws/chat/${this.clientId}`
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.events.emit('connected')
      }

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          this.events.emit('message', message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.events.emit('disconnected')
        this.attemptReconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.events.emit('error', error)
      }
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error)
      this.attemptReconnect()
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => this.connect(), this.reconnectTimeout)
    } else {
      console.error('Max reconnection attempts reached')
      this.events.emit('maxReconnectAttemptsReached')
    }
  }

  sendMessage(content: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'message',
        content,
        sender: 'user',
        timestamp: new Date().toISOString()
      }
      this.ws.send(JSON.stringify(message))
    } else {
      console.error('WebSocket is not connected')
      throw new Error('WebSocket is not connected')
    }
  }

  sendCommand(command: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const message: WebSocketMessage = {
        type: 'command',
        content: command,
        sender: 'user',
        timestamp: new Date().toISOString()
      }
      this.ws.send(JSON.stringify(message))
    } else {
      console.error('WebSocket is not connected')
      throw new Error('WebSocket is not connected')
    }
  }

  onMessage(callback: (message: WebSocketMessage) => void) {
    this.events.on('message', callback)
    return () => this.events.off('message', callback)
  }

  onConnected(callback: () => void) {
    this.events.on('connected', callback)
    return () => this.events.off('connected', callback)
  }

  onDisconnected(callback: () => void) {
    this.events.on('disconnected', callback)
    return () => this.events.off('disconnected', callback)
  }

  onError(callback: (error: Event) => void) {
    this.events.on('error', callback)
    return () => this.events.off('error', callback)
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export const websocketService = new WebSocketService()
export type { WebSocketMessage }
