import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Navigation } from './components/Navigation'
import { PaperListView } from './views/PaperListView'
import { PaperDetailView } from './views/PaperDetailView'
import { TheoryModeView } from './views/TheoryModeView'
import { DashboardView } from './views/DashboardView'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="container mx-auto px-4 py-6">
        <Routes>
          <Route path="/" element={<PaperListView />} />
          <Route path="/papers" element={<PaperListView />} />
          <Route path="/paper/:id" element={<PaperDetailView />} />
          <Route path="/theory" element={<TheoryModeView />} />
          <Route path="/dashboard" element={<DashboardView />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
