import { BarChart3, MessageSquareText, Moon, Settings, ShoppingBag, Sun, Zap } from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useTheme } from '../lib/ThemeContext'

const navItems = [
  { to: '/', label: 'Chat', icon: MessageSquareText, desc: 'AI Assistant' },
  { to: '/dashboard', label: 'Operations', icon: BarChart3, desc: 'Platform Health' },
  { to: '/insights', label: 'Sellers', icon: ShoppingBag, desc: 'Seller Intelligence' },
  { to: '/settings', label: 'Settings', icon: Settings, desc: 'Configure' },
]

export default function Sidebar() {
  const { isDark, toggleTheme } = useTheme()

  return (
    <aside className={`fixed left-0 top-0 z-30 hidden h-screen w-[280px] flex-col border-r px-5 py-6 backdrop-blur-xl lg:flex transition-colors duration-300 ${
      isDark
        ? 'border-surface-700/50 bg-surface-900/90'
        : 'border-surface-200/70 bg-white/90'
    }`}>
      {/* Logo */}
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="relative flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-sm font-bold text-white shadow-lg shadow-brand-500/25">
          <Zap size={18} />
          <div className="absolute -right-0.5 -top-0.5 h-3 w-3 rounded-full border-2 border-white dark:border-surface-900 bg-emerald-400 animate-pulse" />
        </div>
        <div>
          <p className={`font-display text-[15px] font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
            SupportOps
          </p>
          <p className={`text-[11px] font-medium ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
            AI-Powered Support
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        <p className={`mb-3 px-3 text-[10px] font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
          Navigation
        </p>
        {navItems.map(({ to, label, icon: Icon, desc }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? isDark
                    ? 'bg-brand-500/15 text-brand-400 shadow-sm shadow-brand-500/10'
                    : 'bg-brand-50 text-brand-700 shadow-sm shadow-brand-100'
                  : isDark
                    ? 'text-surface-400 hover:bg-surface-800 hover:text-surface-200'
                    : 'text-surface-600 hover:bg-surface-100 hover:text-surface-900'
              }`
            }
          >
            <div className={`flex h-8 w-8 items-center justify-center rounded-lg transition-colors ${
              isDark ? 'bg-surface-800 group-hover:bg-surface-700' : 'bg-surface-100 group-hover:bg-surface-200'
            }`}>
              <Icon size={16} />
            </div>
            <div>
              <p className="leading-none">{label}</p>
              <p className={`mt-0.5 text-[10px] ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>{desc}</p>
            </div>
          </NavLink>
        ))}
      </nav>

      {/* Theme Toggle */}
      <div className="space-y-3">
        <button
          onClick={toggleTheme}
          className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
            isDark
              ? 'bg-surface-800 text-surface-300 hover:bg-surface-700 hover:text-white'
              : 'bg-surface-100 text-surface-600 hover:bg-surface-200 hover:text-surface-900'
          }`}
        >
          <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${isDark ? 'bg-surface-700' : 'bg-surface-200'}`}>
            {isDark ? <Sun size={15} /> : <Moon size={15} />}
          </div>
          {isDark ? 'Light Mode' : 'Dark Mode'}
        </button>

      </div>
    </aside>
  )
}
