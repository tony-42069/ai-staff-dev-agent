import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface ConnectionConfig {
  maxRetries: number;
  initialRetryDelay: number;
  maxRetryDelay: number;
  heartbeatInterval: number;
}

const DEFAULT_CONFIG: ConnectionConfig = {
  maxRetries: 10,
  initialRetryDelay: 1000,
  maxRetryDelay: 30000,
  heartbeatInterval: 30000,
};

interface WebSocketHook {
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  onMessage: (callback: (data: WebSocketMessage) => void) => void;
  send: (message: any) => void;
  connected: boolean;
}

interface WebSocketClient {
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  onMessage: (callback: (data: WebSocketMessage) => void) => void;
  send: (message: any) => void;
  close: () => void;
}

const createWebSocketClient = (url: string = '/ws', config: Partial<ConnectionConfig> = {}): WebSocketClient => {
  let ws: WebSocket | null = null;
  let messageCallbacks: ((data: WebSocketMessage) => void)[] = [];
  let subscriptions = new Set<string>();
  let reconnectTimeout: NodeJS.Timeout;
  let heartbeatInterval: NodeJS.Timeout;
  let retryCount = 0;
  let messageQueue: any[] = [];
  
  const fullConfig = { ...DEFAULT_CONFIG, ...config };

  const connect = () => {
    if (ws?.readyState === WebSocket.CONNECTING) {
      return; // Prevent multiple connection attempts
    }
    
    clearInterval(heartbeatInterval);
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const wsUrl = `${protocol}//${window.location.hostname}:8000${url}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      retryCount = 0; // Reset retry count on successful connection
      
      // Resubscribe to channels
      subscriptions.forEach(channel => {
        ws?.send(JSON.stringify({
          type: 'subscribe',
          channel
        }));
      });

      // Send any queued messages
      while (messageQueue.length > 0) {
        const message = messageQueue.shift();
        if (message && ws?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify(message));
        }
      }

      // Start heartbeat
      heartbeatInterval = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, fullConfig.heartbeatInterval);
    };

    ws.onclose = () => {
      clearInterval(heartbeatInterval);
      
      if (retryCount < fullConfig.maxRetries) {
        const delay = Math.min(
          fullConfig.initialRetryDelay * Math.pow(2, retryCount),
          fullConfig.maxRetryDelay
        );
        console.log(`WebSocket disconnected, retrying in ${delay/1000}s... (attempt ${retryCount + 1}/${fullConfig.maxRetries})`);
        reconnectTimeout = setTimeout(connect, delay);
        retryCount++;
      } else {
        console.error('WebSocket reconnection failed after maximum attempts');
        messageCallbacks.forEach(callback => 
          callback({
            type: 'error',
            error: 'Connection failed after maximum retry attempts'
          })
        );
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        messageCallbacks.forEach(callback => callback(data));
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
};

  const subscribe = (channel: string) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'subscribe',
        channel
      }));
    }
    subscriptions.add(channel);
  };

  const unsubscribe = (channel: string) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({
        type: 'unsubscribe',
        channel
      }));
    }
    subscriptions.delete(channel);
  };

  const onMessage = (callback: (data: WebSocketMessage) => void) => {
    messageCallbacks.push(callback);
  };

  const send = (message: any) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, queueing message');
      messageQueue.push(message);
      if (ws?.readyState === WebSocket.CLOSED) {
        connect(); // Attempt to reconnect if closed
      }
    }
  };

  const close = () => {
    clearTimeout(reconnectTimeout);
    clearInterval(heartbeatInterval);
    if (ws) {
      ws.close();
      ws = null;
    }
    messageCallbacks = [];
    subscriptions.clear();
    messageQueue = [];
    retryCount = 0;
  };

  connect();

  return {
    subscribe,
    unsubscribe,
    onMessage,
    send,
    close
  };
};

export const websocketService = createWebSocketClient();

export const useWebSocket = (url: string = '/ws'): WebSocketHook => {
  const ws = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const messageCallbacks = useRef<((data: WebSocketMessage) => void)[]>([]);
  const subscriptions = useRef<Set<string>>(new Set());

  useEffect(() => {
    const connect = () => {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.hostname}:8000${url}`;
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        setConnected(true);
        console.log('WebSocket connected');

        // Resubscribe to channels
        subscriptions.current.forEach(channel => {
          ws.current?.send(JSON.stringify({
            type: 'subscribe',
            channel
          }));
        });
      };

      ws.current.onclose = () => {
        setConnected(false);
        console.log('WebSocket disconnected, retrying in 5s...');
        setTimeout(connect, 5000);
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          messageCallbacks.current.forEach(callback => callback(data));
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
};

    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  const subscribe = (channel: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'subscribe',
        channel
      }));
    }
    subscriptions.current.add(channel);
  };

  const unsubscribe = (channel: string) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        type: 'unsubscribe',
        channel
      }));
    }
    subscriptions.current.delete(channel);
  };

  const onMessage = (callback: (data: WebSocketMessage) => void) => {
    messageCallbacks.current.push(callback);
  };

  const send = (message: any) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  };

  return {
    subscribe,
    unsubscribe,
    onMessage,
    send,
    connected
  };
};
