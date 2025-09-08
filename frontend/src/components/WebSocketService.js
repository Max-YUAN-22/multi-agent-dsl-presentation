// src/components/WebSocketService.js
import { io } from 'socket.io-client';

let socket;

const WebSocketService = (() => {
  const connect = (url) => {
    socket = io(url);

    socket.on('connect', () => {
      console.log('Connected to WebSocket');
    });

    socket.on('trafficData', (data) => {
      console.log('Received traffic data:', data);
    });
  };

  const onMessage = (callback) => {
    socket.on('trafficData', callback);
  };

  return {
    connect,
    onMessage,
  };
})();

export default WebSocketService;
