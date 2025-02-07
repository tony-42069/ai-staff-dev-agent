import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

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

const createWebSocketClient = (url: string = '/ws'): WebSocketClient => {
  let ws: WebSocket | null = null;
  let messageCallbacks: ((data: WebSocketMessage) => void)[] = [];
  let subscriptions = new Set<string>();
  let reconnectTimeout: NodeJS.Timeout;

  const connect = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}${url}`;
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
      // Resubscribe to channels
      subscriptions.forEach(channel => {
        ws?.send(JSON.stringify({
          type: 'subscribe',
          channel
        }));
      });
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected, retrying in 5s...');
      reconnectTimeout = setTimeout(connect, 5000);
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
      console.warn('WebSocket not connected');
    }
  };

  const close = () => {
    clearTimeout(reconnectTimeout);
    if (ws) {
      ws.close();
      ws = null;
    }
    messageCallbacks = [];
    subscriptions.clear();
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
      const wsUrl = `${protocol}//${window.location.host}${url}`;
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
