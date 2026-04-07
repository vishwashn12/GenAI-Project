import { useEffect, useRef, useState } from 'react'
import { MessageSquareText, SendHorizontal, Trash2 } from 'lucide-react'
import { useTheme } from '../lib/ThemeContext'
import ChatBubble from '../components/ChatBubble'
import Loader from '../components/Loader'
import { chatWithSupport } from '../lib/api'

const STORAGE_KEY = 'supportops_chat_history'
const SESSION_KEY = 'supportops_session_id'

/** Generate a stable session ID per browser tab. New tab = new session. */
function getOrCreateSessionId() {
  let id = sessionStorage.getItem(SESSION_KEY)
  if (!id) {
    id = `session-${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
    sessionStorage.setItem(SESSION_KEY, id)
  }
  return id
}

export default function Chat() {
  const { isDark } = useTheme()
  const [query, setQuery] = useState('')
  const [orderId, setOrderId] = useState('')
  const [messages, setMessages] = useState(() => {
    try {
      const cached = localStorage.getItem(STORAGE_KEY)
      return cached ? JSON.parse(cached) : []
    } catch {
      return []
    }
  })
  const [loading, setLoading] = useState(false)
  const scrollRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
    }
  }, [messages, loading])

  const sessionId = getOrCreateSessionId()

  const clearChat = () => {
    setMessages([])
    localStorage.removeItem(STORAGE_KEY)
    // also reset the backend session so memory starts fresh
    sessionStorage.removeItem(SESSION_KEY)
  }

  const submitQuery = async (event) => {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed || loading) return

    const userMessage = {
      id: `u-${Date.now()}`,
      role: 'user',
      text: trimmed,
      orderId: orderId.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setQuery('')
    setLoading(true)

    try {
      const response = await chatWithSupport({ query: trimmed, order_id: orderId.trim(), session_id: sessionId })
      setMessages((prev) => [...prev, {
        id: `a-${Date.now()}`,
        role: 'assistant',
        response,
      }])
    } catch (error) {
      const fallback = {
        answer: error?.response?.data?.detail || 'The assistant is temporarily unavailable. Please try again.',
        intent: 'error',
        mode: 'error',
        latency: 0,
        sources: [],
        documents_retrieved: 0,
        similarity_scores: [],
        reasoning: {
          intent_classification: 'failed',
          tool_calls: [],
          retrieval_summary: 'Request failed before retrieval could complete.',
        },
      }
      setMessages((prev) => [...prev, { id: `a-${Date.now()}`, role: 'assistant', response: fallback }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <section className="mx-auto max-w-5xl">
      {/* Header */}
      <header className="mb-5 flex items-center justify-between">
        <div>
          <h1 className={`font-display text-2xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
            AI Support Chat
          </h1>
          <p className={`mt-1 text-sm ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
            Ask about orders, returns, policies, or complaints — with full source transparency.
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className={`flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold transition-colors ${
              isDark
                ? 'bg-surface-800 text-surface-400 hover:bg-red-500/10 hover:text-red-400'
                : 'bg-surface-100 text-surface-500 hover:bg-red-50 hover:text-red-600'
            }`}
          >
            <Trash2 size={13} /> Clear
          </button>
        )}
      </header>

      {/* Chat Container */}
      <div className={`overflow-hidden rounded-2xl border transition-colors ${
        isDark
          ? 'border-surface-700/50 bg-surface-900/50 shadow-panel-dark'
          : 'border-surface-200/80 bg-white shadow-panel'
      }`}>
        {/* Messages */}
        <div
          ref={scrollRef}
          className={`h-[calc(100vh-280px)] min-h-[400px] space-y-5 overflow-y-auto p-5 sm:p-6 ${
            isDark ? 'bg-surface-900/30' : 'bg-surface-50/50'
          }`}
        >
          {!messages.length ? (
            <div className="flex h-full items-center justify-center">
              <div className="text-center">
                <div className={`mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl ${
                  isDark ? 'bg-brand-500/10' : 'bg-brand-50'
                }`}>
                  <MessageSquareText size={28} className={isDark ? 'text-brand-400' : 'text-brand-600'} />
                </div>
                <h2 className={`font-display text-xl font-bold ${isDark ? 'text-white' : 'text-surface-800'}`}>
                  How can I help you?
                </h2>
                <p className={`mt-2 max-w-md text-sm ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
                  Ask me about orders, returns, policies, or product complaints. I'll provide answers with source citations and reasoning traces.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {['What is the return policy?', 'My order is delayed', 'Product arrived damaged'].map(q => (
                    <button
                      key={q}
                      onClick={() => setQuery(q)}
                      className={`rounded-xl px-3.5 py-2 text-xs font-medium transition-all hover:-translate-y-0.5 ${
                        isDark
                          ? 'bg-surface-800 text-surface-300 ring-1 ring-surface-700 hover:bg-surface-700 hover:text-white'
                          : 'bg-white text-surface-600 ring-1 ring-surface-200 hover:bg-surface-50 hover:text-surface-900 hover:shadow-sm'
                      }`}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg) => <ChatBubble key={msg.id} message={msg} />)
          )}
          {loading && (
            <div className="flex justify-start">
              <Loader />
            </div>
          )}
        </div>

        {/* Input Bar */}
        <form
          onSubmit={submitQuery}
          className={`border-t px-4 py-4 sm:px-5 transition-colors ${
            isDark
              ? 'border-surface-700/50 bg-surface-800/50'
              : 'border-surface-200/80 bg-white'
          }`}
        >
          <div className="flex gap-2">
            <input
              value={orderId}
              onChange={(e) => setOrderId(e.target.value)}
              placeholder="Order/Seller ID"
              className={`w-28 shrink-0 rounded-xl border px-3 py-2.5 text-sm outline-none transition-colors sm:w-36 ${
                isDark
                  ? 'border-surface-700 bg-surface-800 text-surface-200 placeholder-surface-600 focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/20'
                  : 'border-surface-200 bg-surface-50 text-surface-800 placeholder-surface-400 focus:border-brand-400 focus:ring-1 focus:ring-brand-200'
              }`}
            />
            <input
              ref={inputRef}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Type your question…"
              className={`flex-1 rounded-xl border px-4 py-2.5 text-sm outline-none transition-colors ${
                isDark
                  ? 'border-surface-700 bg-surface-800 text-surface-200 placeholder-surface-600 focus:border-brand-500/50 focus:ring-1 focus:ring-brand-500/20'
                  : 'border-surface-200 bg-surface-50 text-surface-800 placeholder-surface-400 focus:border-brand-400 focus:ring-1 focus:ring-brand-200'
              }`}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-500 to-brand-700 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-500/25 transition-all hover:scale-[1.02] hover:shadow-brand-500/40 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
            >
              <SendHorizontal size={15} />
              <span className="hidden sm:inline">Send</span>
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}
