import { useEffect, useRef, useState } from 'react';
import type { ResearchEvent, WebSocketMessage } from './types';

export type WsStatus = 'idle' | 'connecting' | 'open' | 'closed' | 'error';

export interface UseWebSocketOptions {
  sessionId: string | null;
  onEvent: (ev: ResearchEvent) => void;
  enabled?: boolean;
}

/** Open a WebSocket to /ws/{sessionId} and dispatch events to the caller. */
export function useWebSocket({ sessionId, onEvent, enabled = true }: UseWebSocketOptions) {
  const [status, setStatus] = useState<WsStatus>('idle');
  const wsRef = useRef<WebSocket | null>(null);
  const onEventRef = useRef(onEvent);

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

  useEffect(() => {
    if (!enabled || !sessionId) {
      setStatus('idle');
      return;
    }

    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${proto}//${window.location.host}/ws/${sessionId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;
    setStatus('connecting');

    ws.onopen = () => setStatus('open');
    ws.onerror = () => setStatus('error');
    ws.onclose = () => setStatus('closed');
    ws.onmessage = (msg) => {
      try {
        const payload = JSON.parse(msg.data) as WebSocketMessage;
        if (payload.type === 'event' && payload.data) {
          onEventRef.current(payload.data as ResearchEvent);
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message', err);
      }
    };

    return () => {
      ws.close();
    };
  }, [sessionId, enabled]);

  return { status };
}
