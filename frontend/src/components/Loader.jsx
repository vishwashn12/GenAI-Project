import { useTheme } from '../lib/ThemeContext'

export default function Loader({ type = 'bubble' }) {
  const { isDark } = useTheme()

  if (type === 'panel') {
    return (
      <div className="panel p-6">
        <div className="shimmer h-5 w-1/3 rounded-lg" />
        <div className="mt-5 space-y-3">
          <div className="shimmer h-4 w-full rounded-lg" />
          <div className="shimmer h-4 w-5/6 rounded-lg" />
          <div className="shimmer h-4 w-4/6 rounded-lg" />
        </div>
      </div>
    )
  }

  return (
    <div className={`inline-flex items-center gap-3 rounded-2xl px-5 py-3.5 animate-rise ${
      isDark
        ? 'bg-surface-800/80 ring-1 ring-surface-700/50 shadow-panel-dark'
        : 'bg-white ring-1 ring-surface-100 shadow-panel'
    }`}>
      <div className="flex gap-1.5">
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
      <span className={`text-xs font-semibold ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
        Analyzing your query…
      </span>
    </div>
  )
}
