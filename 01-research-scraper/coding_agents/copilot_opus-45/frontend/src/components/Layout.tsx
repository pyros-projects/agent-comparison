import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FileText, 
  FlaskConical, 
  Download, 
  Wifi, 
  WifiOff,
  AlertCircle,
  CheckCircle,
} from 'lucide-react'
import { useWebSocket } from '../context/WebSocketContext'
import { useStatus } from '../context/StatusContext'
import { ReactNode } from 'react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/papers', label: 'Papers', icon: FileText },
  { path: '/theory', label: 'Theory Mode', icon: FlaskConical },
  { path: '/imports', label: 'Imports', icon: Download },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const { isConnected } = useWebSocket()
  const { status } = useStatus()

  console.log('[Layout] Rendering, path:', location.pathname)

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <h1 className="text-2xl font-bold text-gray-900">
              📚 PaperTrail
            </h1>
            <nav className="flex gap-1">
              {navItems.map(item => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`
                      flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors
                      ${isActive 
                        ? 'bg-blue-100 text-blue-700' 
                        : 'text-gray-600 hover:bg-gray-100'
                      }
                    `}
                  >
                    <Icon size={18} />
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </div>
          
          {/* Status indicators */}
          <div className="flex items-center gap-4">
            {/* WebSocket status */}
            <div className={`flex items-center gap-1 text-sm ${isConnected ? 'text-green-600' : 'text-red-600'}`}>
              {isConnected ? <Wifi size={16} /> : <WifiOff size={16} />}
              <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
            
            {/* LLM status */}
            {status && (
              <div className={`flex items-center gap-1 text-sm ${status.llm.available ? 'text-green-600' : 'text-yellow-600'}`}>
                {status.llm.available ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                <span>LLM: {status.llm.available ? 'Available' : 'Unavailable'}</span>
              </div>
            )}
            
            {/* Embedding fallback status */}
            {status?.embedding.using_fallback && (
              <div className="flex items-center gap-1 text-sm text-yellow-600">
                <AlertCircle size={16} />
                <span>Using fallback embeddings</span>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="flex-1 p-6">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 px-6 py-3 text-sm text-gray-500">
        <div className="flex items-center justify-between">
          <span>PaperTrail - Research Paper Catalog</span>
          <span>
            {status?.import_tasks.active_count || 0} active import tasks
          </span>
        </div>
      </footer>
    </div>
  )
}
