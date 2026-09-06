type Listener = (data: any) => void;

class WebSocketService {
  private url: string;
  private socket: WebSocket | null = null;
  private listeners: Map<string, Listener[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private isConnecting = false;

  constructor(channel: string) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = import.meta.env.VITE_WS_HOST || window.location.host;
    this.url = `${protocol}//${host}/ws/${channel}`;
  }

  connect() {
    if (this.socket?.readyState === WebSocket.OPEN || this.isConnecting) return;
    
    this.isConnecting = true;
    this.socket = new WebSocket(this.url);

    this.socket.onopen = () => {
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connection', { status: 'connected' });
    };

    this.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit('message', data);
      } catch (e) {
        console.error('Failed to parse WS message', e);
      }
    };

    this.socket.onclose = () => {
      this.isConnecting = false;
      this.emit('connection', { status: 'disconnected' });
      this.attemptReconnect();
    };

    this.socket.onerror = (error) => {
      this.isConnecting = false;
      console.error('WS Error:', error);
    };
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const timeout = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);
      setTimeout(() => this.connect(), timeout);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  on(event: string, callback: Listener) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event)?.push(callback);
  }

  off(event: string, callback: Listener) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      this.listeners.set(event, eventListeners.filter(cb => cb !== callback));
    }
  }

  private emit(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(cb => cb(data));
    }
  }

  send(data: any) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
    }
  }
}

// Singleton instances for common channels
export const wsLive = new WebSocketService('live');
export const wsAlerts = new WebSocketService('alerts');
export const wsDigitalTwin = new WebSocketService('digital-twin');
