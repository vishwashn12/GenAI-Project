import { useTheme } from '../lib/ThemeContext'

export default function MetricCard({ title, value, subtitle, icon: Icon, trend = 'low' }) {
  const { isDark } = useTheme()

  const trendColor = {
    high:   isDark ? 'text-red-400 bg-red-500/10 ring-red-500/20' : 'text-red-700 bg-red-50 ring-red-200',
    medium: isDark ? 'text-amber-400 bg-amber-500/10 ring-amber-500/20' : 'text-amber-700 bg-amber-50 ring-amber-200',
    low:    isDark ? 'text-emerald-400 bg-emerald-500/10 ring-emerald-500/20' : 'text-emerald-700 bg-emerald-50 ring-emerald-200',
  }

  return (
    <div className="panel p-5">
      <div className="flex items-center justify-between">
        <p className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
          {title}
        </p>
        {Icon && (
          <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${isDark ? 'bg-surface-700/50' : 'bg-surface-100'}`}>
            <Icon size={14} className={isDark ? 'text-surface-400' : 'text-surface-500'} />
          </div>
        )}
      </div>
      <div className="mt-3 flex items-end justify-between gap-2">
        <p className={`font-display text-3xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
          {value}
        </p>
        <span className={`mb-1 rounded-full px-2 py-0.5 text-[10px] font-bold ring-1 ${trendColor[trend]}`}>
          {trend}
        </span>
      </div>
      <p className={`mt-2 text-[11px] ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
        {subtitle}
      </p>
    </div>
  )
}
