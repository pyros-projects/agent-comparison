import { useEffect } from 'react';

const DEFAULT_WS_URL = (() => {
  if (typeof window === 'undefined') return '';
  return `${window.location.origin.replace(/^http/, 'ws')}/ws/events`;
})();

export function useEventStream(onEvent: (event: MessageEvent) => void) {
  useEffect(() => {
    let active = true;
    let socket: WebSocket | null = null;
    const wsUrl = import.meta.env.VITE_WS_URL ?? DEFAULT_WS_URL;

    const connect = () => {
      if (!active) return;
      console.info('[ws] connecting', wsUrl);
      socket = new WebSocket(wsUrl);
      socket.addEventListener('message', onEvent);
      socket.addEventListener('open', () => console.info('[ws] open'));
      socket.addEventListener('close', () => {
        console.warn('[ws] closed, retrying…');
        socket?.removeEventListener('message', onEvent);
        if (active) setTimeout(connect, 2000);
      });
      socket.addEventListener('error', (error) => console.error('[ws] error', error));
    };

    connect();

    return () => {
      active = false;
      socket?.close();
      socket?.removeEventListener('message', onEvent);
    };
  }, [onEvent]);
}
