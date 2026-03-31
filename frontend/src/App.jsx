import { Route, Routes } from 'react-router-dom'
import { useTheme } from './lib/ThemeContext'
import Sidebar from './components/Sidebar'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import Insights from './pages/Insights'
import Settings from './pages/Settings'

export default function App() {
  const { isDark } = useTheme()

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDark ? 'bg-surface-950 bg-grid-dark' : 'bg-surface-50 bg-grid-light'}`}>
      <Sidebar />
      <main className="min-h-screen px-4 pb-10 pt-6 sm:px-8 lg:ml-[280px] lg:px-10">
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/insights" element={<Insights />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}
