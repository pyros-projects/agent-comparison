import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

console.log('PaperTrail Frontend Initializing...')

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

console.log('✓ PaperTrail Frontend Mounted')
