import { useEffect, useMemo, useState } from 'react'
import {
  Activity, AlertTriangle, CheckCircle2, Clock, Package, Star, TrendingDown,
} from 'lucide-react'
import {
  Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend,
} from 'recharts'
import { useTheme } from '../lib/ThemeContext'
import Loader from '../components/Loader'
import { fetchAnalytics } from '../lib/api'

const ISSUE_COLORS  = ['#3b82f6','#f59e0b','#ef4444','#10b981','#8b5cf6','#ec4899','#14b8a6']
const STATUS_COLORS = ['#10b981','#3b82f6','#f59e0b','#ef4444','#94a3b8','#8b5cf6','#ec4899','#14b8a6']
const CHANNEL_COLORS = ['#3b82f6','#10b981','#f59e0b','#8b5cf6']
const PRIORITY_COLORS = { Critical:'#ef4444', High:'#f97316', Medium:'#f59e0b', Low:'#10b981' }

const fmt = (n) => Number(n || 0).toLocaleString()

function KpiCard({ title, value, subtitle, icon: Icon, accent = 'blue', trend }) {
  const { isDark } = useTheme()
  const accentMap = {
    blue:   { bg: isDark ? 'bg-blue-500/10'   : 'bg-blue-50',   text: 'text-blue-500',   icon: 'bg-blue-500/20'   },
    green:  { bg: isDark ? 'bg-emerald-500/10': 'bg-emerald-50', text: 'text-emerald-500', icon: 'bg-emerald-500/20' },
    amber:  { bg: isDark ? 'bg-amber-500/10'  : 'bg-amber-50',  text: 'text-amber-500',  icon: 'bg-amber-500/20'  },
    red:    { bg: isDark ? 'bg-red-500/10'    : 'bg-red-50',    text: 'text-red-500',    icon: 'bg-red-500/20'    },
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
      {trend && (
        <div className={`mt-3 flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold w-fit ${a.bg} ${a.text}`}>
          {trend}
        </div>
      )}
    </div>
  )
}

const CustomTooltip = ({ active, payload, label, isDark }) => {
  if (!active || !payload?.length) return null
  return (
    <div className={`rounded-xl border px-3 py-2 text-xs shadow-xl ${
      isDark ? 'border-surface-700 bg-surface-800 text-surface-200' : 'border-surface-200 bg-white text-surface-800'
    }`}>
      <p className="font-semibold">{label || payload[0]?.name}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color || p.fill }}>{p.name || 'Count'}: <span className="font-bold">{fmt(p.value)}</span></p>
      ))}
    </div>
  )
}

function ChartPanel({ title, subtitle, children }) {
  const { isDark } = useTheme()
  return (
    <div className={`rounded-2xl border p-5 ${isDark ? 'border-surface-700/50 bg-surface-800/60' : 'border-surface-200 bg-white'}`}>
      <p className={`text-xs font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>{title}</p>
      {subtitle && <p className={`mt-0.5 text-xs ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>{subtitle}</p>}
      <div className="mt-4 h-64">{children}</div>
    </div>
  )
}

export default function Dashboard() {
  const { isDark } = useTheme()
  const [data, setData]     = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError]   = useState(null)

  useEffect(() => {
    ;(async () => {
      setLoading(true)
      try { setData(await fetchAnalytics()) }
      catch (e) { setError('Failed to load data.') }
      finally { setLoading(false) }
    })()
  }, [])

  const summary       = data?.summary || {}
  const issues        = useMemo(() => data?.issue_distribution || [], [data])
  const orderStatuses = useMemo(() => data?.order_status_distribution || [], [data])
  const channels      = useMemo(() => data?.channel_distribution || [], [data])
  const resolution    = useMemo(() => data?.resolution_status || [], [data])
  const priorities    = useMemo(() => data?.priority_distribution || [], [data])
  const cities        = useMemo(() => data?.top_cities || [], [data])

  const tickStyle  = { fill: isDark ? '#94a3b8' : '#64748b', fontSize: 11 }
  const axisStroke = isDark ? '#334155' : '#e2e8f0'

  if (loading) return (
    <section className="mx-auto max-w-7xl space-y-6 animate-pulse">
      <div className={`h-8 w-48 rounded-lg ${isDark ? 'bg-surface-800' : 'bg-surface-200'}`} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => <div key={i} className={`h-32 rounded-2xl ${isDark ? 'bg-surface-800' : 'bg-surface-200'}`} />)}
      </div>
      <div className="grid gap-6 lg:grid-cols-2">
        {[...Array(4)].map((_, i) => <div key={i} className={`h-72 rounded-2xl ${isDark ? 'bg-surface-800' : 'bg-surface-200'}`} />)}
      </div>
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
          Operations Dashboard
        </h1>
        <p className={`mt-1 text-sm ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
          Live view of support health, order delivery, and customer satisfaction across the platform.
        </p>
      </header>

      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Total Tickets"
          value={fmt(summary.total_tickets)}
          subtitle="Support conversations"
          icon={Activity}
          accent="blue"
          trend="Support volume"
        />
        <KpiCard
          title="SLA Compliance"
          value={`${summary.sla_compliance_pct ?? 0}%`}
          subtitle="Tickets resolved in time"
          icon={CheckCircle2}
          accent={summary.sla_compliance_pct >= 80 ? 'green' : 'amber'}
          trend={summary.sla_compliance_pct >= 80 ? '✓ On target' : '⚠ Below 80% target'}
        />
        <KpiCard
          title="Late Delivery Rate"
          value={`${summary.late_delivery_rate ?? 0}%`}
          subtitle={`${fmt(summary.never_delivered)} never delivered`}
          icon={AlertTriangle}
          accent={summary.late_delivery_rate > 10 ? 'red' : 'amber'}
          trend={summary.late_delivery_rate > 10 ? '⚠ High — investigate' : 'Within range'}
        />
        <KpiCard
          title="Avg Review Score"
          value={`${summary.avg_review_score ?? 0} / 5`}
          subtitle="Customer satisfaction"
          icon={Star}
          accent={summary.avg_review_score >= 4 ? 'green' : 'amber'}
          trend={summary.avg_review_score >= 4 ? '★ Excellent' : '↓ Room to improve'}
        />
      </div>

      {/* Row 2: Issue distribution + Priority */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <ChartPanel title="Issue Category Breakdown" subtitle="What customers are contacting support about">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={issues} layout="vertical" margin={{ left: 40, right: 20 }}>
                <XAxis type="number" tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} />
                <YAxis type="category" dataKey="label" tick={tickStyle} axisLine={false} tickLine={false} width={110} />
                <Tooltip content={<CustomTooltip isDark={isDark} />} cursor={{ fill: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }} />
                <Bar dataKey="count" radius={[0, 6, 6, 0]} maxBarSize={28}>
                  {issues.map((_, idx) => <Cell key={idx} fill={ISSUE_COLORS[idx % ISSUE_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartPanel>
        </div>

        <ChartPanel title="Ticket Priority" subtitle="Severity distribution">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={priorities} dataKey="count" nameKey="label" innerRadius={60} outerRadius={95} paddingAngle={3} stroke="none">
                {priorities.map((p, idx) => <Cell key={idx} fill={PRIORITY_COLORS[p.label] || ISSUE_COLORS[idx]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip isDark={isDark} />} />
              <Legend iconType="circle" iconSize={8} formatter={(v) => <span className={`text-xs ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>
      </div>

      {/* Row 3: Order status + Channel + Resolution */}
      <div className="grid gap-6 lg:grid-cols-3">
        <ChartPanel title="Order Status" subtitle="Across 99K orders">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={orderStatuses} layout="vertical" margin={{ left: 10, right: 20 }}>
              <XAxis type="number" tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} />
              <YAxis type="category" dataKey="label" tick={tickStyle} axisLine={false} tickLine={false} width={80} />
              <Tooltip content={<CustomTooltip isDark={isDark} />} cursor={{ fill: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }} />
              <Bar dataKey="count" radius={[0, 6, 6, 0]} maxBarSize={22}>
                {orderStatuses.map((_, idx) => <Cell key={idx} fill={STATUS_COLORS[idx % STATUS_COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Contact Channel" subtitle="How customers reach support">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={channels} dataKey="count" nameKey="label" innerRadius={58} outerRadius={92} paddingAngle={3} stroke="none">
                {channels.map((_, idx) => <Cell key={idx} fill={CHANNEL_COLORS[idx % CHANNEL_COLORS.length]} />)}
              </Pie>
              <Tooltip content={<CustomTooltip isDark={isDark} />} />
              <Legend iconType="circle" iconSize={8} formatter={(v) => <span className={`text-xs ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Resolution Status" subtitle="Ticket outcomes">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={resolution} dataKey="count" nameKey="label" innerRadius={58} outerRadius={92} paddingAngle={3} stroke="none">
                {resolution.map((r, idx) => (
                  <Cell key={idx} fill={r.label === 'Resolved' ? '#10b981' : r.label === 'Escalated' ? '#ef4444' : '#f59e0b'} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip isDark={isDark} />} />
              <Legend iconType="circle" iconSize={8} formatter={(v) => <span className={`text-xs ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>{v}</span>} />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>
      </div>

      {/* Row 4: Top cities */}
      <ChartPanel title="Top 10 Cities by Ticket Volume" subtitle="Where support requests originate">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cities} margin={{ left: 0, right: 20, bottom: 20 }}>
              <XAxis dataKey="city" tick={{ ...tickStyle, fontSize: 10 }} axisLine={{ stroke: axisStroke }} tickLine={false} angle={-30} textAnchor="end" interval={0} />
              <YAxis tick={tickStyle} axisLine={{ stroke: axisStroke }} tickLine={false} />
              <Tooltip content={<CustomTooltip isDark={isDark} />} cursor={{ fill: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)' }} />
              <Bar dataKey="tickets" radius={[6, 6, 0, 0]} maxBarSize={36}>
                {cities.map((_, idx) => <Cell key={idx} fill={`hsl(${220 + idx * 8}, 75%, ${isDark ? '60%' : '52%'})`} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </ChartPanel>
    </section>
  )
}
