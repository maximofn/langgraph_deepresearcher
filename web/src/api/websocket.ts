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

    const clientId = window.localStorage.getItem('deepresearch.client_id') ?? '';
    const apiUrl = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');
    let url: string;
    if (apiUrl) {
      url = `${apiUrl.replace(/^http/, 'ws')}/ws/${sessionId}?client_id=${clientId}`;
    } else {
      const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      url = `${proto}//${window.location.host}/ws/${sessionId}?client_id=${clientId}`;
    }
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
