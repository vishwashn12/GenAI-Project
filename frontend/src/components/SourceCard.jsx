import { useTheme } from '../lib/ThemeContext'

const typeConfig = {
  policy:  { label: 'Policy',   light: 'bg-brand-50 text-brand-700 ring-brand-200', dark: 'bg-brand-500/10 text-brand-400 ring-brand-500/20' },
  review:  { label: 'Review',   light: 'bg-amber-50 text-amber-700 ring-amber-200', dark: 'bg-amber-500/10 text-amber-400 ring-amber-500/20' },
  ticket:  { label: 'Ticket',   light: 'bg-emerald-50 text-emerald-700 ring-emerald-200', dark: 'bg-emerald-500/10 text-emerald-400 ring-emerald-500/20' },
  complaint: { label: 'Complaint', light: 'bg-rose-50 text-rose-700 ring-rose-200', dark: 'bg-rose-500/10 text-rose-400 ring-rose-500/20' },
  unknown: { label: 'Source',   light: 'bg-surface-100 text-surface-700 ring-surface-200', dark: 'bg-surface-700 text-surface-300 ring-surface-600' },
}

function detectType(source) {
  const raw = String(source?.source_type || source?.type || source?.label || '').toLowerCase()
  if (raw.includes('policy')) return 'policy'
  if (raw.includes('review') || raw.includes('olist')) return 'review'
  if (raw.includes('ticket') || raw.includes('support')) return 'ticket'
  if (raw.includes('complaint') || raw.includes('amazon')) return 'complaint'
  return 'unknown'
}

export default function SourceCard({ source, index }) {
  const { isDark } = useTheme()
  const type = detectType(source)
  const cfg = typeConfig[type]
  const score = Number(source?.score || source?.similarity || 0)
  const clamped = Math.max(0, Math.min(1, score))

  return (
    <div className={`group rounded-xl border p-4 transition-all duration-200 hover:-translate-y-0.5 ${
      isDark
        ? 'border-surface-700/60 bg-surface-800/50 hover:border-surface-600 hover:shadow-panel-dark'
        : 'border-surface-200 bg-white hover:border-surface-300 hover:shadow-panel'
    }`}>
      <div className="flex items-center justify-between gap-3">
        <p className={`text-xs font-bold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>
          Source #{index + 1}
        </p>
        <span className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ring-1 ${isDark ? cfg.dark : cfg.light}`}>
          {cfg.label}
        </span>
      </div>

      <p className={`mt-2.5 line-clamp-3 text-[13px] leading-relaxed ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>
        {source?.snippet || source?.text || source?.content || 'No snippet available'}
      </p>

      <div className="mt-3">
        <div className="flex items-center justify-between text-[11px]">
          <span className={isDark ? 'text-surface-500' : 'text-surface-400'}>Relevance</span>
          <span className={`font-mono font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>
            {(clamped * 100).toFixed(1)}%
          </span>
        </div>
        <div className={`mt-1.5 h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-surface-700' : 'bg-surface-100'}`}>
          <div
            className="h-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-400 transition-all duration-700 ease-out"
            style={{ width: `${clamped * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}
