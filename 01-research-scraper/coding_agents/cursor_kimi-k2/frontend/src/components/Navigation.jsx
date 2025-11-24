import React from 'react'
import { Link, useLocation } from 'react-router-dom'

export function Navigation() {
  const location = useLocation()
  
  const navItems = [
    { path: '/', label: 'Papers', icon: '📄' },
    { path: '/theory', label: 'Theory Mode', icon: '🔍' },
    { path: '/dashboard', label: 'Dashboard', icon: '📊' }
  ]

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link to="/" className="text-2xl font-bold text-blue-600">
            PaperTrail
          </Link>
          
          <div className="flex space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  location.pathname === item.path
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
