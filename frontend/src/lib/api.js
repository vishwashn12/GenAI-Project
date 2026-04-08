import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
})

/** Read settings fresh from sessionStorage on every call — never stale. */
function getSettings() {
  try {
    return JSON.parse(sessionStorage.getItem('supportops_settings') || '{}')
  } catch {
    return {}
  }
}

export const chatWithSupport = async ({ query, order_id, session_id }) => {
  // Read FRESH on every send — toggles always take effect immediately
  const s = getSettings()
  const payload = {
    query,
    order_id,
    session_id: session_id || 'default',
    // Fallbacks match backend defaults exactly
    use_rewrite: typeof s.queryRewriting      === 'boolean' ? s.queryRewriting      : true,
    use_mq:      typeof s.multiQueryRetrieval === 'boolean' ? s.multiQueryRetrieval : false,
    use_comp:    typeof s.contextCompression  === 'boolean' ? s.contextCompression  : false,
  }
  const { data } = await api.post('/chat', payload)
  return data
}

export const fetchAnalytics = async () => {
  const { data } = await api.get('/analytics')
  return data
}

export const fetchInsights = async () => {
  const { data } = await api.get('/insights')
  return data
}

export default api
