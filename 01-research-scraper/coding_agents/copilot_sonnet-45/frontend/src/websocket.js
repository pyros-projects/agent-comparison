import { useState, useEffect } from 'react'

const WS_URL = `ws://${window.location.host}/ws`

export const useWebSocket = () => {
  const [ws, setWs] = useState(null)
  const [connected, setConnected] = useState(false)
  const [messages, setMessages] = useState([])

  useEffect(() => {
    console.log('WebSocket: Connecting to', WS_URL)
    
    const websocket = new WebSocket(WS_URL)
    
    websocket.onopen = () => {
      console.log('✓ WebSocket: Connected')
      setConnected(true)
    }
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('WebSocket: Received message:', data.type)
      setMessages(prev => [...prev, data])
    }
    
    websocket.onerror = (error) => {
      console.error('WebSocket: Error:', error)
    }
    
    websocket.onclose = () => {
      console.log('WebSocket: Disconnected')
      setConnected(false)
    }
    
    setWs(websocket)
    
    return () => {
      console.log('WebSocket: Closing connection')
      websocket.close()
    }
  }, [])

  return { ws, connected, messages }
}
