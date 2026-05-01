const BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
const KEY = import.meta.env.VITE_API_KEY ?? ''

const headers = () => ({
  'Content-Type': 'application/json',
  'X-API-Key': KEY,
})

export interface CheckRequest {
  phone_number: string
  account_id: string
  transaction_amount: number
  expected_region: string
  name: string
  dob: string
  address: string
  account_registered_at: string
}

export interface CheckResponse {
  session_id: string
  risk_score: number
  recommended_action: 'ALLOW' | 'STEP-UP' | 'HOLD'
  mode_triggered: number
  signals: Record<string, boolean>
  signal_drivers: string[]
  fast_path: boolean
  duration_ms?: number
  mode2?: {
    outcome: string
    location?: object
    alerted_parties?: string[]
  }
}

export async function sentinelCheck(req: CheckRequest): Promise<CheckResponse> {
  const res = await fetch(`${BASE}/v1/sentinel/check`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify(req),
  })
  if (!res.ok) throw new Error(`API error ${res.status}`)
  return res.json()
}

export async function postmortem(sessionId: string, phone: string, start: string, end: string) {
  const res = await fetch(`${BASE}/v1/sentinel/postmortem`, {
    method: 'POST',
    headers: headers(),
    body: JSON.stringify({
      session_id: sessionId,
      phone_number: phone,
      incident_start: start,
      incident_end: end
    }),
  })
  return res.json()
}
