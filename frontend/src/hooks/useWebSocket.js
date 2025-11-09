/**
 * React hook for managing WebSocket connections.
 *
 * Provides a declarative way to connect to WebSocket and subscribe to events.
 */

import { useEffect, useRef, useState } from 'react';
import { createWebSocketClient, closeWebSocketClient } from '../services/websocket';

/**
 * Hook for WebSocket connection and event handling.
 *
 * @param {string} projectId - Project ID to connect to
 * @param {object} handlers - Event handlers for WebSocket messages
 * @param {boolean} enabled - Whether to establish connection (default: true)
 * @returns {object} WebSocket state and utilities
 */
export function useWebSocket(projectId, handlers = {}, enabled = true) {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('CLOSED');
  const [error, setError] = useState(null);
  const wsClientRef = useRef(null);
  const unsubscribersRef = useRef([]);

  useEffect(() => {
    // Don't connect if not enabled or no project ID
    if (!enabled || !projectId) {
      return;
    }

    // Create WebSocket client
    const wsClient = createWebSocketClient(projectId);
    wsClientRef.current = wsClient;

    // Connection state handlers
    const handleConnected = () => {
      setIsConnected(true);
      setConnectionState('OPEN');
      setError(null);
    };

    const handleDisconnected = () => {
      setIsConnected(false);
      setConnectionState('CLOSED');
    };

    const handleError = (data) => {
      setError(data.error);
    };

    // Register internal handlers
    const unsubConnect = wsClient.on('connected', handleConnected);
    const unsubDisconnect = wsClient.on('disconnected', handleDisconnected);
    const unsubError = wsClient.on('error', handleError);

    unsubscribersRef.current.push(unsubConnect, unsubDisconnect, unsubError);

    // Register user-provided handlers
    Object.entries(handlers).forEach(([event, handler]) => {
      const unsub = wsClient.on(event, handler);
      unsubscribersRef.current.push(unsub);
    });

    // Connect
    wsClient.connect();

    // Update connection state periodically
    const stateInterval = setInterval(() => {
      if (wsClient) {
        setConnectionState(wsClient.getState());
      }
    }, 1000);

    // Cleanup on unmount
    return () => {
      clearInterval(stateInterval);

      // Unsubscribe all listeners
      unsubscribersRef.current.forEach(unsub => unsub());
      unsubscribersRef.current = [];

      // Close WebSocket
      closeWebSocketClient();
      wsClientRef.current = null;
    };
  }, [projectId, enabled]);

  // Send message function
  const sendMessage = (message) => {
    if (wsClientRef.current) {
      wsClientRef.current.send(message);
    } else {
      console.warn('Cannot send message: WebSocket not connected');
    }
  };

  // Ping function
  const ping = () => {
    if (wsClientRef.current) {
      wsClientRef.current.ping();
    }
  };

  return {
    isConnected,
    connectionState,
    error,
    sendMessage,
    ping,
    wsClient: wsClientRef.current,
  };
}

/**
 * Hook for subscribing to specific WebSocket events.
 *
 * @param {string} event - Event name to subscribe to
 * @param {function} handler - Handler function
 * @param {object} wsClient - WebSocket client instance
 */
export function useWebSocketEvent(event, handler, wsClient) {
  useEffect(() => {
    if (!wsClient || !event || !handler) return;

    const unsubscribe = wsClient.on(event, handler);

    return () => {
      unsubscribe();
    };
  }, [event, handler, wsClient]);
}

/**
 * Hook for accumulating streaming content.
 *
 * @param {object} wsClient - WebSocket client instance
 * @returns {object} Streaming state
 */
export function useStreamingContent(wsClient) {
  const [content, setContent] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    if (!wsClient) return;

    const handleStreamChunk = (data) => {
      setIsStreaming(true);

      if (data.is_reasoning) {
        setReasoning(prev => prev + data.content);
      } else {
        setContent(prev => prev + data.content);
      }
    };

    const handlePhaseChange = () => {
      // Reset streaming state on phase change
      setIsStreaming(false);
      setContent('');
      setReasoning('');
    };

    const unsubChunk = wsClient.on('stream_chunk', handleStreamChunk);
    const unsubPhase = wsClient.on('phase_change', handlePhaseChange);

    return () => {
      unsubChunk();
      unsubPhase();
    };
  }, [wsClient]);

  const clearContent = () => {
    setContent('');
    setReasoning('');
    setIsStreaming(false);
  };

  return {
    content,
    reasoning,
    isStreaming,
    clearContent,
  };
}

/**
 * Hook for tracking tool calls and results.
 *
 * @param {object} wsClient - WebSocket client instance
 * @returns {object} Tool call state
 */
export function useToolCalls(wsClient) {
  const [toolCalls, setToolCalls] = useState([]);

  useEffect(() => {
    if (!wsClient) return;

    const handleToolCall = (data) => {
      setToolCalls(prev => [
        ...prev,
        {
          id: Date.now(),
          name: data.tool_name,
          arguments: data.arguments,
          timestamp: new Date().toISOString(),
          status: 'executing',
        },
      ]);
    };

    const handleToolResult = (data) => {
      setToolCalls(prev =>
        prev.map(call =>
          call.name === data.tool_name && call.status === 'executing'
            ? { ...call, result: data.result, status: 'completed' }
            : call
        )
      );
    };

    const handlePhaseChange = () => {
      // Clear tool calls on phase change
      setToolCalls([]);
    };

    const unsubCall = wsClient.on('tool_call', handleToolCall);
    const unsubResult = wsClient.on('tool_result', handleToolResult);
    const unsubPhase = wsClient.on('phase_change', handlePhaseChange);

    return () => {
      unsubCall();
      unsubResult();
      unsubPhase();
    };
  }, [wsClient]);

  const clearToolCalls = () => {
    setToolCalls([]);
  };

  return {
    toolCalls,
    clearToolCalls,
  };
}
