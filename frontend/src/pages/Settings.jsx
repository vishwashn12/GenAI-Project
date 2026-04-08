import { Label } from '@radix-ui/react-label'
import * as Switch from '@radix-ui/react-switch'
import { useEffect, useRef, useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../lib/ThemeContext'

const STORAGE_KEY = 'supportops_settings'

const defaults = {
  queryRewriting: true,
  multiQueryRetrieval: false,
  contextCompression: false,
}

/** Read saved settings from sessionStorage (per-tab, resets on new session). */
function readSavedSettings() {
  try {
    const cached = sessionStorage.getItem(STORAGE_KEY)
    return cached ? { ...defaults, ...JSON.parse(cached) } : defaults
  } catch {
    return defaults
  }
}

function ToggleRow({ id, label, description, checked, onCheckedChange }) {
  const { isDark } = useTheme()
  return (
    <div className={`flex items-center justify-between gap-4 rounded-xl border p-5 transition-colors ${
      isDark
        ? 'border-surface-700/50 bg-surface-800/50 hover:border-brand-500/30'
        : 'border-surface-200 bg-white hover:border-brand-300 shadow-sm'
    }`}>
      <div>
        <Label htmlFor={id} className={`text-sm font-semibold ${isDark ? 'text-surface-200' : 'text-surface-800'}`}>
          {label}
        </Label>
        <p className={`mt-1 text-[13px] ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>{description}</p>
      </div>
      <Switch.Root
        id={id}
        checked={checked}
        onCheckedChange={onCheckedChange}
        className={`relative h-7 w-12 rounded-full outline-none transition-colors ${
          checked
            ? 'bg-brand-600'
            : isDark ? 'bg-surface-700' : 'bg-surface-200'
        }`}
      >
        <Switch.Thumb className="block h-5 w-5 translate-x-1 rounded-full bg-white shadow-lg transition data-[state=checked]:translate-x-6" />
      </Switch.Root>
    </div>
  )
}

export default function Settings() {
  const { isDark, toggleTheme } = useTheme()
  // Lazy init — reads from sessionStorage immediately, no race condition
  const [settings, setSettings] = useState(readSavedSettings)
  const isFirstRender = useRef(true)

  // Only write to storage AFTER user changes — skip the mount write
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  }, [settings])

  return (
    <section className="mx-auto max-w-3xl space-y-6">
      <header>
        <h1 className={`font-display text-2xl font-bold tracking-tight ${isDark ? 'text-white' : 'text-surface-900'}`}>
          Settings
        </h1>
        <p className={`mt-1 text-sm ${isDark ? 'text-surface-400' : 'text-surface-500'}`}>
          Tune retrieval behavior and appearance.
        </p>
      </header>

      {/* Theme Section */}
      <div>
        <p className={`mb-3 text-[10px] font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
          Appearance
        </p>
        <div className={`flex items-center justify-between gap-4 rounded-xl border p-5 transition-colors ${
          isDark
            ? 'border-surface-700/50 bg-surface-800/50'
            : 'border-surface-200 bg-white shadow-sm'
        }`}>
          <div className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${isDark ? 'bg-surface-700' : 'bg-surface-100'}`}>
              {isDark ? <Moon size={18} className="text-brand-400" /> : <Sun size={18} className="text-amber-500" />}
            </div>
            <div>
              <p className={`text-sm font-semibold ${isDark ? 'text-surface-200' : 'text-surface-800'}`}>
                {isDark ? 'Dark Mode' : 'Light Mode'}
              </p>
              <p className={`text-[13px] ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
                {isDark ? 'Switch to light for a brighter view' : 'Switch to dark to reduce eye strain'}
              </p>
            </div>
          </div>
          <Switch.Root
            checked={isDark}
            onCheckedChange={toggleTheme}
            className={`relative h-7 w-12 rounded-full outline-none transition-colors ${
              isDark ? 'bg-brand-600' : 'bg-surface-200'
            }`}
          >
            <Switch.Thumb className="block h-5 w-5 translate-x-1 rounded-full bg-white shadow-lg transition data-[state=checked]:translate-x-6" />
          </Switch.Root>
        </div>
      </div>

      {/* RAG Settings */}
      <div>
        <p className={`mb-3 text-[10px] font-bold uppercase tracking-widest ${isDark ? 'text-surface-500' : 'text-surface-400'}`}>
          Retrieval Pipeline
        </p>
        <div className="space-y-3">
          <ToggleRow
            id="query-rewriting"
            label="Query Rewriting"
            description="Normalize and enrich customer queries before retrieval to improve recall."
            checked={settings.queryRewriting}
            onCheckedChange={(value) => setSettings(p => ({ ...p, queryRewriting: value }))}
          />
          <ToggleRow
            id="multi-query"
            label="Multi-Query Retrieval"
            description="Generate multiple retrieval intents in parallel for broader evidence coverage."
            checked={settings.multiQueryRetrieval}
            onCheckedChange={(value) => setSettings(p => ({ ...p, multiQueryRetrieval: value }))}
          />
          <ToggleRow
            id="compression"
            label="Context Compression"
            description="Condense retrieved passages before LLM synthesis to reduce token overhead."
            checked={settings.contextCompression}
            onCheckedChange={(value) => setSettings(p => ({ ...p, contextCompression: value }))}
          />
        </div>
      </div>
    </section>
  )
}
