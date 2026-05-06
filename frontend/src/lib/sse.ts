import { useEffect, useState } from 'react'

export interface AlertEvent {
  type: 'RISK_FLAG' | 'MODE2_TRIGGER' | 'heartbeat'
  session_id?: string
  score?: number
  action?: string
  drivers?: string[]
}

export function useLiveFeed() {
  const [events, setEvents] = useState<AlertEvent[]>([])
  const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
  const KEY = import.meta.env.VITE_API_KEY ?? 'sentinel_demo'

  useEffect(() => {
    // ── Browser SSE Authentication ──
    // Standard browsers do not support custom headers in EventSource.
    // We append the key to the URL so the backend can validate it via Query param.
    const url = `${BASE}/v1/sentinel/stream?api_key=${KEY}`
    const es = new EventSource(url)

    es.onmessage = (e: MessageEvent) => {
      try {
        const data: AlertEvent = JSON.parse(e.data)

        // Preserve feature: Ignore heartbeats to keep the UI clean
        if (data.type === 'heartbeat') return

        // Preserve feature: Maintain a rolling list of the last 50 events
        setEvents(prev => [data, ...prev].slice(0, 50))
      } catch (err) {
        console.error("Failed to parse SSE event:", err)
      }
    }

    es.onerror = () => {
      console.warn("SSE connection lost. Reconnecting...")
      es.close()
    }

    return () => es.close()
  }, [BASE, KEY])

  //  Added the clear function
  const clearEvents = () => setEvents([])

  //  Returning both the events array and the clear function
  return { events, clearEvents }
}
