/**
 * WebSocket client for real-time updates from the backend.
 *
 * Manages WebSocket connection, reconnection, and message handling.
 */

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

export class WebSocketClient {
  constructor(projectId) {
    this.projectId = projectId;
    this.ws = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;
    this.isIntentionallyClosed = false;
    this.messageQueue = [];
  }

  /**
   * Connect to WebSocket server.
   */
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    const url = `${WS_BASE_URL}/${this.projectId}`;
    console.log(`Connecting to WebSocket: ${url}`);

    this.ws = new WebSocket(url);

    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
  }

  /**
   * Handle WebSocket connection opened.
   */
  handleOpen(event) {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;

    // Emit connection event
    this.emit('connected', { projectId: this.projectId });

    // Send any queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  /**
   * Handle incoming WebSocket message.
   */
  handleMessage(event) {
    try {
      const data = JSON.parse(event.data);
      const messageType = data.type;

      // Emit to specific type listeners
      this.emit(messageType, data);

      // Also emit to 'message' listeners for all messages
      this.emit('message', data);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error, event.data);
    }
  }

  /**
   * Handle WebSocket error.
   */
  handleError(event) {
    console.error('WebSocket error:', event);
    this.emit('error', { error: 'WebSocket error occurred' });
  }

  /**
   * Handle WebSocket connection closed.
   */
  handleClose(event) {
    console.log('WebSocket closed:', event.code, event.reason);

    this.emit('disconnected', {
      code: event.code,
      reason: event.reason,
    });

    // Attempt reconnection if not intentionally closed
    if (!this.isIntentionallyClosed && this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;

      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect();
      }, delay);
    }
  }

  /**
   * Send a message to the server.
   */
  send(message) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      const data = typeof message === 'string' ? message : JSON.stringify(message);
      this.ws.send(data);
    } else {
      console.warn('WebSocket not open, queueing message');
      this.messageQueue.push(message);
    }
  }

  /**
   * Send a ping to keep connection alive.
   */
  ping() {
    this.send('ping');
  }

  /**
   * Register an event listener.
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);

    // Return unsubscribe function
    return () => {
      this.off(event, callback);
    };
  }

  /**
   * Unregister an event listener.
   */
  off(event, callback) {
    if (!this.listeners.has(event)) return;

    const callbacks = this.listeners.get(event);
    const index = callbacks.indexOf(callback);

    if (index > -1) {
      callbacks.splice(index, 1);
    }

    if (callbacks.length === 0) {
      this.listeners.delete(event);
    }
  }

  /**
   * Emit an event to all registered listeners.
   */
  emit(event, data) {
    if (!this.listeners.has(event)) return;

    const callbacks = this.listeners.get(event);
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in ${event} listener:`, error);
      }
    });
  }

  /**
   * Close the WebSocket connection.
   */
  close() {
    this.isIntentionallyClosed = true;

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.listeners.clear();
    this.messageQueue = [];
  }

  /**
   * Check if WebSocket is connected.
   */
  isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state.
   */
  getState() {
    if (!this.ws) return 'CLOSED';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'OPEN';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'CLOSED';
      default:
        return 'UNKNOWN';
    }
  }
}

/**
 * Create and manage WebSocket client instance.
 */
let wsClient = null;

export function createWebSocketClient(projectId) {
  // Close existing connection if any
  if (wsClient) {
    wsClient.close();
  }

  wsClient = new WebSocketClient(projectId);
  return wsClient;
}

export function getWebSocketClient() {
  return wsClient;
}

export function closeWebSocketClient() {
  if (wsClient) {
    wsClient.close();
    wsClient = null;
  }
}
