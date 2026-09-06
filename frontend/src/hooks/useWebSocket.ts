import { useEffect, useState, useCallback } from 'react';
import { wsLive, wsAlerts, wsDigitalTwin } from '../services/websocket';

const services: Record<string, typeof wsLive> = {
  'live': wsLive,
  'alerts': wsAlerts,
  'digital-twin': wsDigitalTwin,
};

export function useWebSocket(channel: string) {
  const [connected, setConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);

  const ws = services[channel];

  useEffect(() => {
    if (!ws) {
      console.warn(`WebSocket channel ${channel} not found.`);
      return;
    }

    const handleConnection = (status: { status: string }) => {
      setConnected(status.status === 'connected');
    };

    const handleMessage = (data: any) => {
      setLastMessage(data);
    };

    ws.on('connection', handleConnection);
    ws.on('message', handleMessage);
    
    ws.connect();

    return () => {
      ws.off('connection', handleConnection);
      ws.off('message', handleMessage);
      // We don't automatically disconnect here if reusing singletons, but depending on architecture we might.
      // For shared feeds, we let the singleton manage it.
    };
  }, [ws, channel]);

  const sendMessage = useCallback((data: any) => {
    if (ws) {
      ws.send(data);
    }
  }, [ws]);

  return { connected, lastMessage, sendMessage };
}
