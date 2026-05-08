class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.listeners = [];
  }

  connect(token) {
    if (this.ws) return;

    // Use ws:// or wss:// based on current protocol, fallback to localhost for dev
    const wsUrl = `ws://localhost:8000/map/ws/live-risk?token=${token}`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('WebSocket Connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.listeners.forEach(listener => listener(data));
      } catch (e) {
        console.error('WebSocket Message Parse Error:', e);
      }
    };

    this.ws.onclose = () => {
      console.log('WebSocket Disconnected');
      this.ws = null;
      this.attemptReconnect(token);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket Error:', error);
      this.ws.close();
    };
  }

  attemptReconnect(token) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
        this.connect(token);
      }, 3000 * this.reconnectAttempts); // Exponential backoff
    }
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
  }
}

export const wsService = new WebSocketService();
