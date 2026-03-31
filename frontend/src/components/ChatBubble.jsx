import { ChevronDown, Cpu, Database, Gauge, User, Wrench, Zap } from 'lucide-react'
import { useState } from 'react'
import { useTheme } from '../lib/ThemeContext'
import SourceCard from './SourceCard'

function Badge({ label, value, variant = 'default' }) {
  const { isDark } = useTheme()
  const styles = {
    default: isDark ? 'bg-surface-700/60 text-surface-300 ring-surface-600/50' : 'bg-surface-100 text-surface-700 ring-surface-200',
    success: isDark ? 'bg-emerald-500/10 text-emerald-400 ring-emerald-500/20' : 'bg-emerald-50 text-emerald-700 ring-emerald-200',
    warning: isDark ? 'bg-amber-500/10 text-amber-400 ring-amber-500/20' : 'bg-amber-50 text-amber-700 ring-amber-200',
    danger: isDark ? 'bg-red-500/10 text-red-400 ring-red-500/20' : 'bg-red-50 text-red-700 ring-red-200',
    brand: isDark ? 'bg-brand-500/10 text-brand-400 ring-brand-500/20' : 'bg-brand-50 text-brand-700 ring-brand-200',
  }
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-[11px] font-semibold ring-1 ${styles[variant]}`}>
      <span className={`text-[9px] uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>{label}</span>
      {value}
    </span>
  )
}

function inferLatencyVariant(latency = 0) {
  if (latency > 3.5) return 'danger'
  if (latency > 1.5) return 'warning'
  return 'success'
}

export default function ChatBubble({ message }) {
  const { isDark } = useTheme()
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const [reasoningOpen, setReasoningOpen] = useState(false)

  if (message.role === 'user') {
    return (
      <div className="flex justify-end animate-rise">
        <div className="max-w-2xl">
          <div className="rounded-2xl rounded-br-md bg-gradient-to-br from-brand-500 to-brand-700 px-5 py-4 text-white shadow-lg shadow-brand-500/20">
            <p className="text-[14px] leading-relaxed">{message.text}</p>
            {message.orderId ? (
              <p className="mt-2 flex items-center gap-1.5 text-[11px] text-brand-100/80">
                <Database size={11} /> Order: {message.orderId}
              </p>
            ) : null}
          </div>
          <p className={`mt-1.5 text-right text-[10px] ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>You</p>
        </div>
      </div>
    )
  }

  const data = message.response || {}
  const sources = Array.isArray(data.sources) ? data.sources : []
  const similarity = Array.isArray(data.similarity_scores) ? data.similarity_scores : []
  const reasoning = data.reasoning || {}

  return (
    <div className="flex animate-rise gap-3">
      {/* Avatar */}
      <div className="hidden pt-1 sm:block">
        <div className={`flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg ${
          isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-50 text-brand-600'
        }`}>
          <Zap size={14} />
        </div>
      </div>

      <div className={`max-w-3xl flex-1 rounded-2xl rounded-tl-md px-5 py-4 transition-colors ${
        isDark
          ? 'bg-surface-800/70 ring-1 ring-surface-700/50'
          : 'bg-white ring-1 ring-surface-100 shadow-panel'
      }`}>
        {/* Answer */}
        <p className={`whitespace-pre-wrap text-[14px] leading-7 ${isDark ? 'text-surface-200' : 'text-surface-800'}`}>
          {data.answer || 'No answer returned.'}
        </p>

        {/* Meta badges */}
        <div className="mt-4 flex flex-wrap items-center gap-2">
          <Badge label="Intent" value={data.intent || 'unknown'} variant="brand" />
          <Badge label="Mode" value={(data.mode || 'rag').toUpperCase()} variant={data.mode === 'agent' ? 'warning' : 'success'} />
          <Badge
            label="Latency"
            value={`${Number(data.latency || 0).toFixed(2)}s`}
            variant={inferLatencyVariant(Number(data.latency || 0))}
          />
          <Badge label="Docs" value={data.documents_retrieved || 0} variant="default" />
        </div>

        {/* Confidence scores */}
        {similarity.length > 0 && (
          <div className="mt-4">
            <p className={`mb-2 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
              <Gauge size={12} /> Confidence Scores
            </p>
            <div className="grid gap-2 sm:grid-cols-3">
              {similarity.slice(0, 3).map((score, idx) => {
                const val = Math.max(0, Math.min(1, Number(score || 0)))
                return (
                  <div key={`${idx}-${val}`} className={`rounded-lg p-2.5 ${isDark ? 'bg-surface-900/50' : 'bg-surface-50'}`}>
                    <div className="flex justify-between text-[11px]">
                      <span className={isDark ? 'text-surface-500' : 'text-surface-400'}>Doc {idx + 1}</span>
                      <span className={`font-mono font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>
                        {(val * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className={`mt-1.5 h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-surface-700' : 'bg-surface-200'}`}>
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-brand-500 to-emerald-400 transition-all duration-700"
                        style={{ width: `${val * 100}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {/* Sources accordion */}
        {sources.length > 0 && (
          <div className="mt-4">
            <button
              onClick={() => setSourcesOpen(!sourcesOpen)}
              className={`flex w-full items-center justify-between rounded-xl px-4 py-3 text-[13px] font-semibold transition-colors ${
                isDark
                  ? 'bg-surface-900/50 text-surface-300 hover:bg-surface-900'
                  : 'bg-surface-50 text-surface-700 hover:bg-surface-100'
              }`}
            >
              <span className="flex items-center gap-2">
                <Database size={14} className={isDark ? 'text-brand-400' : 'text-brand-600'} />
                Sources ({sources.length})
              </span>
              <ChevronDown size={14} className={`transition-transform duration-200 ${sourcesOpen ? 'rotate-180' : ''}`} />
            </button>
            {sourcesOpen && (
              <div className="mt-3 grid gap-2 animate-fadeIn">
                {sources.map((source, index) => (
                  <SourceCard key={index} source={source} index={index} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Reasoning accordion */}
        <div className="mt-3">
          <button
            onClick={() => setReasoningOpen(!reasoningOpen)}
            className={`flex w-full items-center justify-between rounded-xl px-4 py-3 text-[13px] font-semibold transition-colors ${
              isDark
                ? 'bg-surface-900/50 text-surface-300 hover:bg-surface-900'
                : 'bg-surface-50 text-surface-700 hover:bg-surface-100'
            }`}
          >
            <span className="flex items-center gap-2">
              <Cpu size={14} className={isDark ? 'text-brand-400' : 'text-brand-600'} />
              Reasoning Trace
            </span>
            <ChevronDown size={14} className={`transition-transform duration-200 ${reasoningOpen ? 'rotate-180' : ''}`} />
          </button>
          {reasoningOpen && (
            <div className={`mt-3 space-y-3 rounded-xl p-4 text-[13px] animate-fadeIn ${
              isDark ? 'bg-surface-900/40 text-surface-400' : 'bg-surface-50 text-surface-600'
            }`}>
              <div className="flex items-center gap-2">
                <Cpu size={13} className={isDark ? 'text-brand-400' : 'text-brand-600'} />
                <span className={`font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>Intent:</span>
                <span className="font-mono text-[12px]">{reasoning.intent_classification || 'N/A'}</span>
              </div>
              <div className="flex items-start gap-2">
                <Wrench size={13} className={`mt-0.5 ${isDark ? 'text-brand-400' : 'text-brand-600'}`} />
                <span>
                  <span className={`font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>Tools:</span>{' '}
                  {Array.isArray(reasoning.tool_calls) && reasoning.tool_calls.length
                    ? reasoning.tool_calls.join(', ')
                    : 'None'}
                </span>
              </div>
              <div>
                <span className={`font-semibold ${isDark ? 'text-surface-300' : 'text-surface-700'}`}>Summary:</span>{' '}
                {reasoning.retrieval_summary || 'No retrieval summary.'}
              </div>
            </div>
          )}
        </div>

        <p className={`mt-3 text-[10px] ${isDark ? 'text-surface-600' : 'text-surface-400'}`}>SupportOps AI</p>
      </div>
    </div>
  )
}
