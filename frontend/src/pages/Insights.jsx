import { useEffect, useMemo, useState } from 'react'
import {
  Bar, BarChart, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { useTheme } from '../lib/ThemeContext'
import Loader from '../components/Loader'
import { fetchInsights } from '../lib/api'

const MODE_COLORS = ['#3672ff', '#10b981', '#f59e0b', '#ef4444']

export default function Insights() {
  const { isDark } = useTheme()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ;(async () => {
      setLoading(true)
      try { setData(await fetchInsights()) } finally { setLoading(false) }
    })()
  }, [])

  const latencyBreakdown = useMemo(() => data?.latency_breakdown || [], [data])
  const modeDistribution = useMemo(() => data?.mode_distribution || [], [data])
  const toolUsage = useMemo(() => data?.tool_usage || [], [data])
  const tickFill = isDark ? '#94a3b8' : '#64748b'
  const gridStroke = isDark ? '#334155' : '#e2e8f0'

  if (loading) return <section className="mx-auto max-w-7xl"><Loader type="panel" /></section>

  return (
    <section className="mx-auto max-w-7xl space-y-6">
      <header>
        <h1 className={`font-display text-2xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
          System Insights
        </h1>
        <p className={`mt-1 text-sm ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
          Runtime behavior of the RAG and agent pipeline.
        </p>
      </header>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="panel p-5">
          <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Latency Breakdown</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={latencyBreakdown}>
                <XAxis dataKey="metric" tick={{ fill: tickFill, fontSize: 11 }} axisLine={{ stroke: gridStroke }} tickLine={false} />
                <YAxis tick={{ fill: tickFill, fontSize: 11 }} axisLine={{ stroke: gridStroke }} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 8px 30px rgba(0,0,0,0.12)', background: isDark ? '#1e293b' : '#fff', color: isDark ? '#e2e8f0' : '#1e293b' }} />
                <Bar dataKey="value" fill="#0ea5e9" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel p-5">
          <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Mode Distribution</h2>
          <div className="mt-4 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={modeDistribution} dataKey="value" nameKey="label" innerRadius={65} outerRadius={100} paddingAngle={4} stroke="none">
                  {modeDistribution.map((_, idx) => <Cell key={idx} fill={MODE_COLORS[idx % MODE_COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 8px 30px rgba(0,0,0,0.12)', background: isDark ? '#1e293b' : '#fff', color: isDark ? '#e2e8f0' : '#1e293b' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="panel overflow-hidden">
        <div className={`border-b px-5 py-4 ${isDark ? 'border-surface-700/50' : 'border-surface-200'}`}>
          <h2 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>Tool Usage Stats</h2>
        </div>
        <div className="p-5">
          {toolUsage.length ? (
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {toolUsage.map((tool) => (
                <div key={tool.tool} className={`rounded-xl border p-4 transition-colors ${
                  isDark
                    ? 'border-surface-700/50 bg-surface-800/50'
                    : 'border-surface-200 bg-surface-50'
                }`}>
                  <p className={`text-sm font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>{tool.tool}</p>
                  <p className={`mt-2 font-display text-2xl font-bold ${isDark ? 'text-white' : 'text-surface-900'}`}>{tool.count}</p>
                  <p className={`text-[11px] ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>invocations</p>
                </div>
              ))}
            </div>
          ) : (
            <p className={`text-sm ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>No tool usage telemetry.</p>
          )}
        </div>
      </div>
    </section>
  )
}
