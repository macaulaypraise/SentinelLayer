import { useState } from 'react'
import { sentinelCheck, postmortem, type CheckResponse } from '../lib/api'
import { useLiveFeed } from '../lib/sse'
import { RiskGauge } from '../components/RiskGauge'
import { SignalGrid } from '../components/SignalGrid'
import { ModeTimeline } from '../components/ModeTimeline'

const SCENARIOS = {
  clean: {
    phone_number: '+2348011111111', account_id: 'acc_clean_001',
    transaction_amount: 45000, expected_region: 'Lagos',
    name: 'John Doe', dob: '1990-01-01',
    address: '12 Victoria Island', account_registered_at: '2023-06-01',
  },
  fraud: {
    phone_number: '+2348022222222', account_id: 'acc_fraud_002',
    transaction_amount: 450000, expected_region: 'Lagos',
    name: 'Jane Smith', dob: '1985-03-15',
    address: '5 Broad Street', account_registered_at: '2024-01-10',
  },
}

export default function Demo() {
  const [result, setResult] = useState<CheckResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pm, setPm] = useState<object | null>(null)
  const feed = useLiveFeed()

  async function runScenario(scenario: 'clean' | 'fraud') {
    setLoading(true)
    setError(null)
    setPm(null)
    try {
      const res = await sentinelCheck(SCENARIOS[scenario])
      setResult(res)
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  async function runPostmortem() {
    if (!result) return
    const now = new Date().toISOString()
    const past = new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
    const data = await postmortem(result.session_id, SCENARIOS.fraud.phone_number, past, now)
    setPm(data)
  }

  return (
    <div className='min-h-screen bg-[#0F172A] text-white p-6'>
      <div className='max-w-7xl mx-auto'>

        {/* Header */}
        <div className='flex justify-between items-center mb-6'>
          <h1 className='text-2xl font-bold text-blue-400'>SentinelLayer — Live Demo</h1>
          <span className='text-xs font-mono text-slate-500'>18 CAMARA APIs × Nokia NaC × Gemini MCP</span>
        </div>

        {/* Scenario buttons */}
        <div className='flex gap-4 mb-6'>
          <button onClick={() => runScenario('clean')} disabled={loading}
            className='bg-green-700 hover:bg-green-600 disabled:opacity-50 px-6 py-3 rounded-lg font-semibold'>
            {loading ? 'Running...' : 'Scenario 1 — Clean User'}
          </button>
          <button onClick={() => runScenario('fraud')} disabled={loading}
            className='bg-red-700 hover:bg-red-600 disabled:opacity-50 px-6 py-3 rounded-lg font-semibold'>
            {loading ? 'Running...' : 'Scenario 2 — SIM Swap Attack'}
          </button>
          {result && result.mode_triggered >= 2 && (
            <button onClick={runPostmortem}
              className='bg-purple-700 hover:bg-purple-600 px-6 py-3 rounded-lg font-semibold'>
              Scenario 3 — Post-Mortem
            </button>
          )}
        </div>

        {/* Error */}
        {error && <div className='bg-red-900/30 border border-red-700 text-red-300 p-4 rounded-lg mb-4'>{error}</div>}

        {result && (
          <div className='grid grid-cols-3 gap-6'>
            {/* Risk gauge */}
            <div className='bg-slate-800 rounded-xl p-6 border border-slate-700 flex flex-col items-center'>
              <RiskGauge score={result.risk_score} />
              <div className='mt-4 text-xs text-slate-500 font-mono'>
                {result.duration_ms ? `${result.duration_ms}ms` : ''} | Fast path: {String(result.fast_path)}
              </div>
            </div>

            {/* Mode timeline + signals */}
            <div className='col-span-2 space-y-4'>
              <div className='bg-slate-800 rounded-xl p-4 border border-slate-700'>
                <ModeTimeline activeMode={result.mode_triggered} />
              </div>
              <div className='bg-slate-800 rounded-xl p-4 border border-slate-700'>
                <h3 className='text-sm font-semibold text-slate-400 mb-3'>14 CAMARA Signal Results</h3>
                <SignalGrid signals={result.signals} />
              </div>
            </div>
          </div>
        )}

        {/* Mode 2 result */}
        {result?.mode2 && (
          <div className='mt-4 bg-red-900/20 border border-red-700 rounded-xl p-4'>
            <h3 className='font-bold text-red-300 mb-2'>Mode 2 — Live Enforcement</h3>
            <pre className='text-xs text-slate-300 overflow-auto'>
              {JSON.stringify(result.mode2, null, 2)}
            </pre>
          </div>
        )}

        {/* Post-mortem map */}
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        {pm && (pm as any).maps_evidence_url && (
          <div className='mt-4 bg-purple-900/20 border border-purple-700 rounded-xl p-4'>
            <h3 className='font-bold text-purple-300 mb-2'>Mode 3 — Evidence Map</h3>
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            <a href={(pm as any).maps_evidence_url} target='_blank' rel="noreferrer"
              className='text-blue-400 underline text-sm'>
              Open Google Maps Evidence Trail →
            </a>
          </div>
        )}

        {/* Live SSE feed */}
        <div className='mt-6 bg-slate-900 border border-slate-700 rounded-xl p-4'>
          <h3 className='text-sm font-semibold text-slate-400 mb-3'>Live Fraud Signal Feed (SSE)</h3>
          <div className='space-y-1 max-h-32 overflow-y-auto font-mono text-xs'>
            {feed.length === 0 && <span className='text-slate-600'>Waiting for events...</span>}
            {feed.map((ev, i) => (
              <div key={i} className={`flex gap-3 ${ev.action === 'HOLD' ? 'text-red-400' : ev.action === 'STEP-UP' ? 'text-amber-400' : 'text-green-400'}`}>
                <span className='text-slate-600'>{ev.session_id?.slice(0, 8)}</span>
                <span>score={ev.score}</span>
                <span className='font-bold'>{ev.action}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
