import { useState } from 'react'
import { sentinelCheck, postmortem, type CheckResponse } from '../lib/api'
import { useLiveFeed } from '../lib/sse'
import { RiskGauge } from '../components/RiskGauge'
import { SignalGrid } from '../components/SignalGrid'
import { ModeTimeline } from '../components/ModeTimeline'

const SCENARIOS = {
  clean: {
    phone_number: '+99999991001',
    account_id: 'demo_clean_001',
    transaction_amount: 45000,
    expected_region: 'Lagos',
    name: 'Amara Okonkwo',
    dob: '1990-01-01',
    address: '12 Victoria Island Lagos',
    account_registered_at: '2022-06-01'
  },
  fraud: {
    phone_number: '+99999991000',
    account_id: 'demo_fraud_002',
    transaction_amount: 450000,
    expected_region: 'Lagos',
    name: 'Emeka Adeyemi',
    dob: '1985-03-15',
    address: '5 Broad Street Lagos',
    account_registered_at: '2024-01-10'
  }
}

export default function Demo() {
  const [result, setResult] = useState<CheckResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [pm, setPm] = useState<object | null>(null)

  const [persona, setPersona] = useState<'executive' | 'analyst' | 'developer'>('analyst')
  const { events: feed, clearEvents } = useLiveFeed()


  const handlePersonaSwitch = (newPersona: 'executive' | 'analyst' | 'developer') => {
    if (newPersona === persona) return;
    setPersona(newPersona);
    setResult(null);
    setPm(null);
    setError(null);
    setLoading(false);
    clearEvents();
  };


  const activeMode = pm ? 3 : (result?.mode2 ? 2 : (result ? 1 : 0));

  const getHeaderText = () => {
    if (activeMode === 3) return "Mode 3: Device Visit + Location Evidence Trail";
    if (activeMode === 2) return "Mode 2: Live Enforcement + Consent Gate";
    return "18 CAMARA APIs × Nokia NaC × Gemini MCP";
  };

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

        {/* Header with Persona Switcher */}
        <div className='flex flex-col md:flex-row md:justify-between md:items-center gap-3 mb-6'>
          <div className='flex flex-wrap items-center gap-3'>
            <h1 className='text-xl md:text-2xl font-bold text-blue-400'>SentinelLayer</h1>
            <div className='flex bg-slate-800 rounded-lg p-1 border border-slate-700'>
              {(['executive', 'analyst', 'developer'] as const).map(p => (
                <button
                  key={p}
                  onClick={() => handlePersonaSwitch(p)}
                  className={`px-3 py-1 text-xs rounded-md capitalize transition-colors ${
                    persona === p ? 'bg-blue-600 text-white font-bold' : 'text-slate-400 hover:text-slate-300'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
          <span className='hidden md:inline text-xs font-mono text-blue-500 bg-blue-900/20 px-3 py-1 rounded-full border border-blue-800/50 truncate max-w-xs'>
            {getHeaderText()}
          </span>
        </div>

        {/* Scenario buttons */}
        <div className='flex flex-col md:flex-row gap-3 mb-6'>
          <button onClick={() => runScenario('clean')} disabled={loading}
            className='w-full md:w-auto bg-green-700 hover:bg-green-600 disabled:opacity-50 px-6 py-3 rounded-lg font-semibold transition-all'>
            {loading ? 'Scanning...' : 'Scenario 1 — Clean User'}
          </button>
          <button onClick={() => runScenario('fraud')} disabled={loading}
            className='w-full md:w-auto bg-red-700 hover:bg-red-600 disabled:opacity-50 px-6 py-3 rounded-lg font-semibold transition-all'>
            {loading ? 'Scanning...' : 'Scenario 2 — SIM Swap Attack'}
          </button>
          {result && result.mode2 && (
            <button onClick={runPostmortem}
              className='w-full md:w-auto bg-purple-700 hover:bg-purple-600 px-6 py-3 rounded-lg font-semibold animate-pulse'>
              Scenario 3 — Post-Mortem
            </button>
          )}
        </div>

        {error && <div className='bg-red-900/30 border border-red-700 text-red-300 p-4 rounded-lg mb-4'>{error}</div>}

        {/* Loading Skeleton */}
        {loading && !result && (
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4 animate-pulse opacity-60'>
            <div className='bg-slate-800 rounded-xl h-48 md:h-64 border border-slate-700'></div>
            <div className='md:col-span-2 space-y-4'>
              <div className='bg-slate-800 rounded-xl h-24 border border-slate-700'></div>
              <div className='bg-slate-800 rounded-xl h-48 border border-slate-700'></div>
            </div>
          </div>
        )}

        {result && !loading && (
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6'>

            {/* LEFT COLUMN: Risk Gauge & Executive Summary */}
            <div className='flex flex-col gap-4'>
              <div className='bg-slate-800 rounded-xl p-4 md:p-6 border border-slate-700 flex flex-col items-center'>
                <RiskGauge score={result.risk_score} />

                {/* Developer/Analyst details */}
                {persona !== 'executive' && (
                  <div className='mt-4 text-xs text-slate-500 font-mono text-center'>
                    {result.duration_ms ? `${result.duration_ms}ms` : ''} | Fast path: {String(result.fast_path)}
                    {persona === 'developer' && <div className='mt-1 text-blue-400'>Source: {result.source || 'live_nokia_nac'}</div>}
                  </div>
                )}
              </div>

              {/* Executive persona — plain language summary */}
              {persona === 'executive' && (
                <div className={`p-4 rounded-xl border text-center ${
                  result.recommended_action === 'ALLOW'
                    ? 'bg-green-900/20 border-green-700 text-green-300'
                    : 'bg-red-900/20 border-red-700 text-red-300'
                }`}>
                  <p className='text-sm font-semibold'>
                    {result.recommended_action === 'ALLOW'
                      ? '✓ Transaction approved. No fraud indicators detected at the network layer.'
                      : `✗ Transaction blocked. ${(result.signal_drivers?.[0] || 'High risk anomalies').replace(/_/g, ' ')} detected before authentication.`
                    }
                  </p>
                  <p className='text-xs mt-2 opacity-70'>
                    Decision made in {result.duration_ms}ms — zero user friction.
                  </p>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN: Mode timeline + signals */}
            <div className='md:col-span-2 space-y-4'>
              <div className='bg-slate-800 rounded-xl p-4 border border-slate-700'>
                <ModeTimeline activeMode={activeMode} />
              </div>

              {/* Executive Persona hides the complex signal grid */}
              {persona !== 'executive' && (
                <div className='bg-slate-800 rounded-xl p-4 border border-slate-700'>
                  <h3 className='text-sm font-semibold text-slate-400 mb-3'>14 CAMARA Signal Results</h3>
                  {/* Fixed prop name: drivers instead of fastPath */}
                  <SignalGrid signals={result.signals} drivers={result.signal_drivers} />
                </div>
              )}
            </div>
          </div>
        )}

        {/* Mode 2 result - Developer Persona sees raw JSON, Analyst sees summary */}
        {result?.mode2 && persona !== 'executive' && (
          <div className='mt-4 bg-red-900/20 border border-red-700 rounded-xl p-4'>
            <h3 className='font-bold text-red-300 mb-2'>Mode 2 — Live Enforcement</h3>
            {persona === 'developer' ? (
              <pre className='text-xs text-slate-300 overflow-auto'>
                {JSON.stringify(result.mode2, null, 2)}
              </pre>
            ) : (
              <div className='text-sm text-slate-300'>
                Outcome: <span className='font-mono font-bold'>{result.mode2.outcome}</span><br/>
                Parties Alerted: {result.mode2.alerted_parties?.join(', ')}
              </div>
            )}
          </div>
        )}

        {/* Post-mortem map */}
        {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
        {pm && (pm as any).maps_evidence_url && (
          <div className='mt-4 bg-purple-900/20 border border-purple-700 rounded-xl p-4'>
            <h3 className='font-bold text-purple-300 mb-2'>Mode 3 — Evidence Map</h3>
            {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
            <a href={(pm as any).maps_evidence_url} target='_blank' rel="noreferrer"
              className='text-blue-400 underline text-sm flex items-center gap-2'>
              Open Google Maps Evidence Trail →
            </a>
          </div>
        )}

        {/* Live SSE feed - Hidden from Executives */}
        {persona !== 'executive' && (
          <div className='mt-6 bg-slate-900 border border-slate-700 rounded-xl p-4'>
            <h3 className='text-sm font-semibold text-slate-400 mb-3'>Live Fraud Signal Feed (SSE)</h3>
            <div className='space-y-1 max-h-32 overflow-y-auto font-mono text-xs'>
              {feed.length === 0 && <span className='text-slate-600'>Waiting for events...</span>}
              {feed.map((ev, i) => (
                <div key={i} className={`flex gap-3 ${ev.action === 'HOLD' ? 'text-red-400' : ev.action === 'STEP-UP' ? 'text-amber-400' : 'text-green-400'}`}>
                  <span className='text-slate-600'>{ev.session_id?.slice(0, 8) || 'sys'}</span>
                  <span>score={ev.score || '--'}</span>
                  <span className='font-bold'>{ev.action || ev.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
