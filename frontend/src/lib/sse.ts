// src/lib/sse.ts
import { useEffect, useState } from 'react'

export interface AlertEvent {
    type: 'RISK_FLAG' | 'MODE2_TRIGGER' | 'heartbeat'
    session_id?: string
    score?: number
    action?: string
    drivers?: string[]
}

export function useLiveFeed(): AlertEvent[] {
    const [events, setEvents] = useState<AlertEvent[]>([])
    const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
    const KEY = import.meta.env.VITE_API_KEY ?? ''

    useEffect(() => {
        // SSE does not support custom headers in browsers
        // Pass API key as query param
        const url = `${BASE}/v1/sentinel/stream?api_key=${KEY}`
        const es = new EventSource(url)

        es.onmessage = (e: MessageEvent) => {
            const data: AlertEvent = JSON.parse(e.data)
            if (data.type === 'heartbeat') return
            setEvents(prev => [data, ...prev].slice(0, 50))
        }
        es.onerror = () => es.close()
        return () => es.close()
    }, [])

    return events
}
