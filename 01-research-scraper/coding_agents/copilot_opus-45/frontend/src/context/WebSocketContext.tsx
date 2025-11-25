import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react'
import { WSMessage } from '../types'

interface WebSocketContextType {
  isConnected: boolean
  lastMessage: WSMessage | null
  sendMessage: (message: object) => void
  subscribe: (handler: (message: WSMessage) => void) => () => void
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const [socket, setSocket] = useState<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WSMessage | null>(null)
  const [handlers, setHandlers] = useState<Set<(message: WSMessage) => void>>(new Set())

  useEffect(() => {
    console.log('[WebSocket] Initializing connection...')
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    
    const ws = new WebSocket(wsUrl)

    ws.onopen = () => {
      console.log('[WebSocket] Connected')
      setIsConnected(true)
    }

    ws.onclose = () => {
      console.log('[WebSocket] Disconnected')
      setIsConnected(false)
    }

    ws.onerror = (error) => {
      console.error('[WebSocket] Error:', error)
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WSMessage
        console.log('[WebSocket] Received message:', message)
        setLastMessage(message)
        
        // Notify all handlers
        handlers.forEach(handler => handler(message))
      } catch (e) {
        console.error('[WebSocket] Failed to parse message:', e)
      }
    }

    setSocket(ws)

    // Ping every 30 seconds to keep connection alive
    const pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, 30000)

    return () => {
      console.log('[WebSocket] Cleaning up...')
      clearInterval(pingInterval)
      ws.close()
    }
  }, [])

  const sendMessage = useCallback((message: object) => {
    if (socket && socket.readyState === WebSocket.OPEN) {
      console.log('[WebSocket] Sending message:', message)
      socket.send(JSON.stringify(message))
    } else {
      console.warn('[WebSocket] Cannot send message, not connected')
    }
  }, [socket])

  const subscribe = useCallback((handler: (message: WSMessage) => void) => {
    console.log('[WebSocket] Adding subscription handler')
    setHandlers(prev => new Set(prev).add(handler))
    
    return () => {
      console.log('[WebSocket] Removing subscription handler')
      setHandlers(prev => {
        const next = new Set(prev)
        next.delete(handler)
        return next
      })
    }
  }, [])

  return (
    <WebSocketContext.Provider value={{ isConnected, lastMessage, sendMessage, subscribe }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider')
  }
  return context
}
