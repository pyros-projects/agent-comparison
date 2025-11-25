import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { fetchSystemStatus } from '../api'
import { SystemStatus } from '../types'

interface StatusContextType {
  status: SystemStatus | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

const StatusContext = createContext<StatusContextType | null>(null)

export function StatusProvider({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<SystemStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = async () => {
    console.log('[Status] Refreshing system status...')
    try {
      setLoading(true)
      const data = await fetchSystemStatus()
      setStatus(data)
      setError(null)
      console.log('[Status] System status updated:', data)
    } catch (e) {
      console.error('[Status] Failed to fetch system status:', e)
      setError('Failed to fetch system status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    
    // Refresh every 30 seconds
    const interval = setInterval(refresh, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <StatusContext.Provider value={{ status, loading, error, refresh }}>
      {children}
    </StatusContext.Provider>
  )
}

export function useStatus() {
  const context = useContext(StatusContext)
  if (!context) {
    throw new Error('useStatus must be used within a StatusProvider')
  }
  return context
}
