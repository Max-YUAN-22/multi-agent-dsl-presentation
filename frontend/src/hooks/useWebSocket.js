import { useEffect, useRef, useState } from 'react';

const useWebSocket = (url, onMessage) => {
  const socket = useRef(null);
  const [readyState, setReadyState] = useState(WebSocket.CONNECTING);

  useEffect(() => {
    if (!socket.current) {
      socket.current = new WebSocket(url);
      setReadyState(WebSocket.CONNECTING);

      socket.current.onopen = () => {
        setReadyState(WebSocket.OPEN);
      };

      socket.current.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'ping') {
            if (socket.current && socket.current.readyState === WebSocket.OPEN) {
              socket.current.send(JSON.stringify({ type: 'pong' }));
            }
          } else {
            onMessage(message);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      socket.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event);
        setReadyState(WebSocket.CLOSED);
      };

      socket.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setReadyState(WebSocket.CLOSED);
      };
    }

    return () => {
      if (socket.current) {
        socket.current.close();
        socket.current = null;
      }
    };
  }, [url, onMessage]);

  const sendMessage = (message) => {
    if (socket.current && socket.current.readyState === WebSocket.OPEN) {
      socket.current.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected.');
    }
  };

  return { sendMessage, readyState };
};

export default useWebSocket;