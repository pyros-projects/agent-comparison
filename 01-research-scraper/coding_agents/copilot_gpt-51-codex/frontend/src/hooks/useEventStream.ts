import { useEffect } from 'react';

export function useEventStream(onEvent: (event: MessageEvent) => void) {
  useEffect(() => {
    const url = `${location.origin.replace('http', 'ws')}/ws/events`;
    console.info('[ws] connecting', url);
    const socket = new WebSocket(url);
    socket.addEventListener('message', onEvent);
    socket.addEventListener('open', () => console.info('[ws] open'));
    socket.addEventListener('close', () => console.warn('[ws] closed'));
    socket.addEventListener('error', (error) => console.error('[ws] error', error));
    return () => {
      socket.close();
    };
  }, [onEvent]);
}
