import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { healthAPI } from './api'
import { useWebSocket } from './websocket'
import PaperListView from './views/PaperListView'
import PaperDetailView from './views/PaperDetailView'
import TheoryModeView from './views/TheoryModeView'
import DashboardView from './views/DashboardView'
import './App.css'

function Navigation() {
  const location = useLocation()
  const [health, setHealth] = useState(null)
  
  useEffect(() => {
    console.log('App: Checking system health...')
    healthAPI.check()
      .then(data => {
        console.log('App: Health check complete:', data)
        setHealth(data)
      })
      .catch(err => console.error('App: Health check failed:', err))
  }, [])
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/papers', label: 'Papers', icon: '📚' },
    { path: '/theory', label: 'Theory Mode', icon: '🔬' },
  ]
  
  return (
    <nav className="navbar">
      <div className="nav-brand">
        <h1>📄 PaperTrail</h1>
      </div>
      <div className="nav-links">
        {navItems.map(item => (
          <Link
            key={item.path}
            to={item.path}
            className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </div>
      {health && (
        <div className="nav-status">
          <div className={`status-indicator ${health.llm_available ? 'online' : 'offline'}`}>
            LLM: {health.llm_available ? '✓' : '✗'}
          </div>
          <div className="status-indicator online">
            Embeddings: ✓
          </div>
        </div>
      )}
    </nav>
  )
}

function App() {
  const { connected, messages } = useWebSocket()
  
  useEffect(() => {
    console.log('App: Component mounted')
    console.log(`App: WebSocket ${connected ? 'connected' : 'disconnected'}`)
  }, [connected])
  
  useEffect(() => {
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1]
      console.log('App: WebSocket message received:', lastMessage.type, lastMessage)
    }
  }, [messages])
  
  return (
    <BrowserRouter>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DashboardView />} />
            <Route path="/papers" element={<PaperListView />} />
            <Route path="/papers/:id" element={<PaperDetailView />} />
            <Route path="/theory" element={<TheoryModeView />} />
          </Routes>
        </main>
        {!connected && (
          <div className="connection-warning">
            ⚠️ WebSocket disconnected - real-time updates unavailable
          </div>
        )}
      </div>
    </BrowserRouter>
  )
}

export default App
