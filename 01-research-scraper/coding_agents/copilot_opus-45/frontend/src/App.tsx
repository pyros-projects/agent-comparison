import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import PaperList from './pages/PaperList'
import PaperDetail from './pages/PaperDetail'
import TheoryMode from './pages/TheoryMode'
import ImportTasks from './pages/ImportTasks'
import { WebSocketProvider } from './context/WebSocketContext'
import { StatusProvider } from './context/StatusContext'

function App() {
  console.log('[PaperTrail] App component rendering')
  
  return (
    <BrowserRouter>
      <StatusProvider>
        <WebSocketProvider>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/papers" element={<PaperList />} />
              <Route path="/papers/:id" element={<PaperDetail />} />
              <Route path="/theory" element={<TheoryMode />} />
              <Route path="/imports" element={<ImportTasks />} />
            </Routes>
          </Layout>
        </WebSocketProvider>
      </StatusProvider>
    </BrowserRouter>
  )
}

export default App
