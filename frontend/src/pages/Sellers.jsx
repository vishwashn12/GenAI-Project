import { useEffect, useMemo, useState } from 'react'
import {
  AlertOctagon, Award, ShoppingBag, TrendingDown,
} from 'lucide-react'
import {
  Bar, BarChart, Cell, Legend, ResponsiveContainer,
  Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis, ReferenceLine,
} from 'recharts'
import { useTheme } from '../lib/ThemeContext'
import { fetchInsights } from '../lib/api'

const fmt    = (n) => Number(n || 0).toLocaleString()
const fmtPct = (n) => `${Number(n || 0).toFixed(1)}%`
const fmtR   = (n) => `R$ ${Number(n || 0).toLocaleString('en', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`

/* ── KPI Card ─────────────────────────────────────────────── */
function KpiCard({ title, value, subtitle, icon: Icon, accent = 'blue' }) {
  const { isDark } = useTheme()
  const accentMap = {
    blue:  { icon: 'bg-blue-500/20',    text: 'text-blue-400'   },
    green: { icon: 'bg-emerald-500/20', text: 'text-emerald-400' },
    amber: { icon: 'bg-amber-500/20',   text: 'text-amber-400'  },
    red:   { icon: 'bg-red-500/20',     text: 'text-red-400'    },
  }
  const a = accentMap[accent]
  return (
    <div className={`rounded-2xl border p-5 transition-all hover:shadow-md ${
      isDark ? 'border-surface-700/50 bg-surface-800/60' : 'border-surface-200 bg-white'
    }`}>
      <div className="flex items-start justify-between">
        <div>
          <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>{title}</p>
          <p className={`mt-2 font-display text-3xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>{value}</p>
          <p className={`mt-1 text-xs ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>{subtitle}</p>
        </div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${a.icon}`}>
          <Icon size={20} className={a.text} />
        </div>
      </div>
    </div>
  )
}

/* ── Tooltip ──────────────────────────────────────────────── */
const ScatterTooltip = ({ active, payload, isDark }) => {
  if (!active || !payload?.length) return null
  const d = payload[0]?.payload
  if (!d) return null
  return (
    <div className={`rounded-xl border px-3 py-2.5 text-xs shadow-xl ${
      isDark ? 'border-surface-700 bg-surface-800 text-surface-200' : 'border-surface-200 bg-white text-surface-800'
    }`}>
      <p className="font-bold font-mono">{d.seller_id}</p>
      <p className="mt-1">Complaint rate: <span className="font-semibold text-red-400">{d.complaint_rate}%</span></p>
      <p>Avg rating: <span className="font-semibold text-amber-400">{d.avg_rating} ★</span></p>
      <p>Orders: <span className="font-semibold">{fmt(d.total_orders)}</span></p>
      {d.is_flagged && <p className="mt-1 font-bold text-red-500">⚑ Flagged</p>}
    </div>
  )
}

const BarTooltip = ({ active, payload, label, isDark }) => {
  if (!active || !payload?.length) return null
  return (
    <div className={`rounded-xl border px-3 py-2 text-xs shadow-xl ${
      isDark ? 'border-surface-700 bg-surface-800 text-surface-200' : 'border-surface-200 bg-white text-surface-800'
    }`}>
      <p className="font-semibold">{label || payload[0]?.name}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.fill || p.color }}>
          {p.name || 'Value'}: <span className="font-bold">{fmt(p.value)}</span>
        </p>
      ))}
    </div>
  )
}

/* ── Seller Table ─────────────────────────────────────────── */
function SellerTable({ title, subtitle, rows, columns, badgeKey }) {
  const { isDark } = useTheme()
  return (
    <div className={`rounded-2xl border overflow-hidden ${isDark ? 'border-surface-700/50 bg-surface-800/60' : 'border-surface-200 bg-white'}`}>
      <div className={`px-5 py-4 border-b ${isDark ? 'border-surface-700/50' : 'border-surface-100'}`}>
        <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>{title}</p>
        {subtitle && <p className={`mt-0.5 text-xs ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>{subtitle}</p>}
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className={isDark ? 'bg-surface-900/50 text-surface-400' : 'bg-surface-50 text-surface-500'}>
              {columns.map(col => (
                <th key={col.key} className="px-4 py-3 text-left text-[10px] font-bold uppercase tracking-wider">{col.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i} className={`border-t ${isDark ? 'border-surface-700/40' : 'border-surface-100'}`}>
                {columns.map(col => (
                  <td key={col.key} className={`px-4 py-3 ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>
                    {col.key === 'seller_id' ? (
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs">{row[col.key]}</span>
                        {badgeKey && row[badgeKey] && (
                          <span className="inline-flex items-center gap-0.5 rounded-full bg-red-500/15 px-2 py-0.5 text-[10px] font-bold text-red-400">
                            ⚑ Flagged
                          </span>
                        )}
                      </div>
                    ) : col.render ? col.render(row[col.key]) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

/* ── Main Page ────────────────────────────────────────────── */
export default function Insights() {
  const { isDark } = useTheme()
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  useEffect(() => {
    ;(async () => {
      setLoading(true)
      try { setData(await fetchInsights()) }
      catch (e) { setError('Failed to load data.') }
      finally { setLoading(false) }
    })()
  }, [])

  const summary        = data?.summary || {}
  const riskScatter    = useMemo(() => data?.seller_risk || [], [data])
  const worstSellers   = useMemo(() => data?.worst_sellers || [], [data])
  const bestSellers    = useMemo(() => data?.best_sellers || [], [data])
  const ratingDist     = useMemo(() => data?.rating_distribution || [], [data])
  const revenueTop     = useMemo(() => data?.revenue_concentration || [], [data])

  const flaggedDot  = riskScatter.filter(s =>  s.is_flagged)
  const healthyDot  = riskScatter.filter(s => !s.is_flagged)
  const tickStyle   = { fill: isDark ? '#94a3b8' : '#64748b', fontSize: 11 }
  const axisStroke  = isDark ? '#334155' : '#e2e8f0'

  const worstCols = [
    { key: 'seller_id', label: 'Seller ID' },
    { key: 'complaint_rate', label: 'Complaint Rate', render: fmtPct },
    { key: 'avg_rating', label: 'Rating', render: v => `${v} ★` },
    { key: 'late_rate', label: 'Late Rate', render: fmtPct },
    { key: 'total_orders', label: 'Orders', render: fmt },
    { key: 'total_revenue', label: 'Revenue', render: fmtR },
  ]
  const bestCols = [
    { key: 'seller_id', label: 'Seller ID' },
    { key: 'avg_rating', label: 'Rating', render: v => `${v} ★` },
    { key: 'complaint_rate', label: 'Complaint Rate', render: fmtPct },
    { key: 'late_rate', label: 'Late Rate', render: fmtPct },
    { key: 'total_orders', label: 'Orders', render: fmt },
    { key: 'total_revenue', label: 'Revenue', render: fmtR },
  ]

  if (loading) return (
    <section className="mx-auto max-w-7xl space-y-6 animate-pulse">
      <div className={`h-8 w-48 rounded-lg ${isDark ? 'bg-surface-800' : 'bg-surface-200'}`} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => <div key={i} className={`h-32 rounded-2xl ${isDark ? 'bg-surface-800' : 'bg-surface-200'}`} />)}
      </div>
      <div className={`h-96 rounded-2xl ${isDark ? 'bg-surface-800' : 'bg-surface-200'}`} />
    </section>
  )

  if (error) return (
    <section className="mx-auto max-w-7xl flex items-center justify-center h-64">
      <p className="text-red-500 font-medium">{error}</p>
    </section>
  )

  return (
    <section className="mx-auto max-w-7xl space-y-6">
      {/* Header */}
      <header>
        <h1 className={`font-display text-2xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
          Seller Intelligence
        </h1>
        <p className={`mt-1 text-sm ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
          Identify at-risk sellers, monitor performance, and protect platform quality.
        </p>
      </header>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard title="Total Sellers" value={fmt(summary.total_sellers)} subtitle="Active on platform" icon={ShoppingBag} accent="blue" />
        <KpiCard title="Flagged Sellers" value={fmt(summary.flagged_sellers)} subtitle="Require review" icon={AlertOctagon} accent="red" />
        <KpiCard title="Avg Complaint Rate" value={fmtPct(summary.avg_complaint_rate)} subtitle="Platform average" icon={TrendingDown} accent={summary.avg_complaint_rate > 20 ? 'red' : 'amber'} />
        <KpiCard title="Avg Late Rate" value={fmtPct(summary.avg_late_rate)} subtitle="Platform average" icon={Award} accent={summary.avg_late_rate > 10 ? 'amber' : 'green'} />
      </div>

      {/* Seller Risk Scatter Plot */}
      <div className={`rounded-2xl border p-5 ${isDark ? 'border-surface-700/50 bg-surface-800/60' : 'border-surface-200 bg-white'}`}>
        <div className="flex items-start justify-between">
          <div>
            <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
              Seller Risk Quadrant
            </p>
            <p className={`mt-0.5 text-xs ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>
              Complaint rate vs average rating — every dot is a seller. Red = flagged.
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1.5"><span className="inline-block h-2.5 w-2.5 rounded-full bg-red-500" />Flagged</span>
            <span className="flex items-center gap-1.5"><span className="inline-block h-2.5 w-2.5 rounded-full bg-blue-400" />Healthy</span>
          </div>
        </div>

        {/* Quadrant labels */}
        <div className="relative mt-4">
          <div className="absolute left-[52%] top-1 z-10 text-[10px] font-semibold text-emerald-500 opacity-60">★ Star Sellers</div>
          <div className="absolute left-2 top-1 z-10 text-[10px] font-semibold text-amber-500 opacity-60">⚑ Low volume risk</div>
          <div className="absolute bottom-12 left-[52%] z-10 text-[10px] font-semibold text-red-500 opacity-60">✕ At-Risk Sellers</div>
          <div className="absolute bottom-12 left-2 z-10 text-[10px] font-semibold text-surface-500 opacity-60">⟳ Underperformers</div>

          <div style={{ height: 340 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, bottom: 30, left: 10 }}>
                <XAxis
                  type="number" dataKey="complaint_rate" name="Complaint Rate"
                  label={{ value: 'Complaint Rate (%)', position: 'insideBottom', offset: -15, fill: isDark ? '#64748b' : '#94a3b8', fontSize: 11 }}
                  tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} domain={[0, 100]}
                />
                <YAxis
                  type="number" dataKey="avg_rating" name="Avg Rating"
                  label={{ value: 'Avg Rating', angle: -90, position: 'insideLeft', fill: isDark ? '#64748b' : '#94a3b8', fontSize: 11 }}
                  tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} domain={[1, 5]}
                />
                <ZAxis type="number" dataKey="total_orders" range={[30, 200]} />
                <Tooltip content={<ScatterTooltip isDark={isDark} />} />
                {/* Reference lines for quadrants */}
                <ReferenceLine x={30} stroke={isDark ? '#334155' : '#e2e8f0'} strokeDasharray="4 4" />
                <ReferenceLine y={3} stroke={isDark ? '#334155' : '#e2e8f0'} strokeDasharray="4 4" />
                <Scatter name="Healthy" data={healthyDot} fill="#60a5fa" fillOpacity={0.7} />
                <Scatter name="Flagged" data={flaggedDot} fill="#f87171" fillOpacity={0.85} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Worst + Best Sellers Tables */}
      <div className="grid gap-6 xl:grid-cols-2">
        <SellerTable
          title="⚑ At-Risk Sellers"
          subtitle="Highest complaint rates (min 5 orders)"
          rows={worstSellers}
          columns={worstCols}
          badgeKey="is_flagged"
        />
        <SellerTable
          title="★ Top Performers"
          subtitle="Highest rated sellers (min 10 orders)"
          rows={bestSellers}
          columns={bestCols}
          badgeKey={null}
        />
      </div>

      {/* Rating Distribution + Revenue */}
      <div className="grid gap-6 lg:grid-cols-2">
        <div className={`rounded-2xl border p-5 ${isDark ? 'border-surface-700/50 bg-surface-800/60' : 'border-surface-200 bg-white'}`}>
          <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Rating Distribution</p>
          <p className={`mt-0.5 text-xs ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>How seller ratings are spread across 3,095 sellers</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ratingDist} margin={{ right: 10 }}>
                <XAxis dataKey="label" tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} />
                <YAxis tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} />
                <Tooltip content={<BarTooltip isDark={isDark} />} cursor={{ fill: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={50}>
                  {ratingDist.map((r, idx) => {
                    const colors = ['#ef4444','#f97316','#f59e0b','#84cc16','#10b981']
                    return <Cell key={idx} fill={colors[idx] || '#3b82f6'} />
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className={`rounded-2xl border p-5 ${isDark ? 'border-surface-700/50 bg-surface-800/60' : 'border-surface-200 bg-white'}`}>
          <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Revenue Concentration</p>
          <p className={`mt-0.5 text-xs ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>Top 10 sellers by total revenue (R$)</p>
          <div className="mt-4 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenueTop} layout="vertical" margin={{ left: 10, right: 30 }}>
                <XAxis type="number" tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} tickFormatter={v => `R$ ${(v/1000).toFixed(0)}k`} />
                <YAxis type="category" dataKey="seller_id" tick={{ ...tickStyle, fontFamily: 'monospace', fontSize: 10 }} axisLine={false} tickLine={false} width={80} />
                <Tooltip content={<BarTooltip isDark={isDark} />} cursor={{ fill: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }} />
                <Bar dataKey="revenue" name="Revenue (R$)" radius={[0, 6, 6, 0]} maxBarSize={22}>
                  {revenueTop.map((_, idx) => (
                    <Cell key={idx} fill={`hsl(${260 - idx * 10}, 65%, ${isDark ? '62%' : '55%'})`} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  )
}
