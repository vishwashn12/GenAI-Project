import { useEffect, useMemo, useState } from 'react'
import { Activity, Clock, TrendingUp } from 'lucide-react'
import {
  Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { useTheme } from '../lib/ThemeContext'
import Loader from '../components/Loader'
import MetricCard from '../components/MetricCard'
import { fetchAnalytics } from '../lib/api'

const COLORS = ['#3672ff', '#10b981', '#f59e0b', '#ef4444', '#0ea5e9', '#8b5cf6', '#ec4899', '#14b8a6']

export default function Dashboard() {
  const { isDark } = useTheme()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      setLoading(true)
      try { setData(await fetchAnalytics()) } finally { setLoading(false) }
    })()
  }, [])

  const summary = data?.summary || {}
  const issueDistribution = useMemo(() => data?.issue_distribution || [], [data])
  const slaCompliance = useMemo(() => data?.sla_compliance || [], [data])
  const sellerKpi = useMemo(() => data?.seller_kpi || [], [data])
  const sentiment = useMemo(() => data?.sentiment_stats || [], [data])
  const tickFill = isDark ? '#94a3b8' : '#64748b'
  const gridStroke = isDark ? '#334155' : '#e2e8f0'

  if (loading) {
    return (
      <section className="mx-auto max-w-7xl space-y-4">
        <Loader type="panel" /><Loader type="panel" />
      </section>
    )
  }

  return (
    <section className="mx-auto max-w-7xl space-y-6">
      <header>
        <h1 className={`font-display text-2xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
          Analytics Dashboard
        </h1>
        <p className={`mt-1 text-sm ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
          Operational visibility across support requests, SLA health, seller quality, and sentiment.
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard title="Total Queries" value={summary.total_queries ?? 0} subtitle="Support conversations" icon={Activity} trend="low" />
        <MetricCard title="Avg Latency" value={`${Number(summary.avg_latency || 0).toFixed(2)}s`} subtitle="Mean response time" icon={Clock} trend={Number(summary.avg_latency || 0) > 2 ? 'medium' : 'low'} />
        <MetricCard title="Success Rate" value={`${Number(summary.success_rate || 0).toFixed(1)}%`} subtitle="Resolved outcomes" icon={TrendingUp} trend={Number(summary.success_rate || 0) < 85 ? 'high' : 'low'} />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Issue Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={issueDistribution}>
                <XAxis dataKey="label" tick={{ fill: tickFill, fontSize: 11 }} axisLine={{ stroke: gridStroke }} tickLine={false} />
                <YAxis tick={{ fill: tickFill, fontSize: 11 }} axisLine={{ stroke: gridStroke }} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 8px 30px rgba(0,0,0,0.12)', background: isDark ? '#1e293b' : '#fff', color: isDark ? '#e2e8f0' : '#1e293b' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {issueDistribution.map((_, idx) => <Cell key={idx} fill={COLORS[idx % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel p-5">
          <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>SLA Compliance</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={slaCompliance} dataKey="value" nameKey="label" innerRadius={65} outerRadius={100} paddingAngle={4} stroke="none">
                  {slaCompliance.map((_, idx) => <Cell key={idx} fill={idx === 0 ? '#10b981' : '#ef4444'} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 8px 30px rgba(0,0,0,0.12)', background: isDark ? '#1e293b' : '#fff', color: isDark ? '#e2e8f0' : '#1e293b' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel overflow-hidden">
          <div className={`border-b px-5 py-4 ${isDark ? 'border-surface-700/50' : 'border-surface-200'}`}>
            <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Top Sellers</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr className={isDark ? 'bg-surface-800/50 text-surface-400' : 'bg-surface-50 text-surface-500'}>
                  <th className="px-5 py-3 text-[11px] font-bold uppercase tracking-wider">Seller</th>
                  <th className="px-5 py-3 text-[11px] font-bold uppercase tracking-wider">Rating</th>
                  <th className="px-5 py-3 text-[11px] font-bold uppercase tracking-wider">Response</th>
                  <th className="px-5 py-3 text-[11px] font-bold uppercase tracking-wider">Fulfillment</th>
                </tr>
              </thead>
              <tbody>
                {sellerKpi.length ? sellerKpi.map((row) => (
                  <tr key={row.seller_id} className={`border-t ${isDark ? 'border-surface-700/50' : 'border-surface-100'}`}>
                    <td className={`px-5 py-3 font-mono text-xs ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>{String(row.seller_id).slice(0, 12)}…</td>
                    <td className={`px-5 py-3 ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>{Number(row.rating).toFixed(2)}</td>
                    <td className={`px-5 py-3 ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>{Number(row.response_time).toFixed(1)}h</td>
                    <td className={`px-5 py-3 ${isDark ? 'text-surface-400' : 'text-surface-600'}`}>{Number(row.fulfillment_rate).toFixed(1)}%</td>
                  </tr>
                )) : (
                  <tr><td className={`px-5 py-4 ${isDark ? 'text-surface-600' : 'text-surface-400'}`} colSpan={4}>No data available.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="panel p-5">
          <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Sentiment Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sentiment}>
                <XAxis dataKey="label" tick={{ fill: tickFill, fontSize: 11 }} axisLine={{ stroke: gridStroke }} tickLine={false} />
                <YAxis tick={{ fill: tickFill, fontSize: 11 }} axisLine={{ stroke: gridStroke }} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 8px 30px rgba(0,0,0,0.12)', background: isDark ? '#1e293b' : '#fff', color: isDark ? '#e2e8f0' : '#1e293b' }} />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {sentiment.map((_, idx) => <Cell key={idx} fill={COLORS[idx % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  )
}
