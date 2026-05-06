import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const nav = useNavigate()
  return (
    <div className='min-h-screen bg-[#0F172A] text-white'>
      {/* Navigation */}
      <nav className='flex justify-between items-center px-8 py-4 border-b border-slate-800'>
        <div className='text-xl font-bold text-blue-400'>SentinelLayer</div>
        <div className='flex gap-6 text-sm text-slate-400'>
          <a href='#problem' className='hover:text-white'>Problem</a>
          <a href='#solution' className='hover:text-white'>Solution</a>
          <a href='#pricing' className='hover:text-white'>Pricing</a>
        </div>
        <button onClick={() => nav('/demo')}
          className='bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm font-semibold'>
          Live Demo
        </button>
      </nav>

      {/* Hero */}
      <section className='max-w-4xl mx-auto px-8 py-24 text-center'>
        <div className='inline-block bg-blue-900/30 border border-blue-700 text-blue-300 text-xs font-mono px-3 py-1 rounded-full mb-6'>
          GSMA Open Gateway × Nokia Network-as-Code
        </div>
        <h1 className='text-5xl font-bold mb-6 leading-tight'>
          Stop fraud before<br />authentication begins.
        </h1>
        <p className='text-xl text-slate-400 mb-10 max-w-2xl mx-auto'>
          SentinelLayer intercepts the modern fraud chain at the telecom network layer — before deepfakes, SIM swaps, or stolen OTPs ever reach your authentication screen.
        </p>
        <div className='flex gap-4 justify-center'>
          <button onClick={() => nav('/demo')}
            className='bg-blue-600 hover:bg-blue-500 px-8 py-3 rounded-lg font-semibold text-lg'>
            See It Live
          </button>
          <a href={`${import.meta.env.VITE_API_BASE_URL}/docs`} target='_blank' rel="noreferrer"
            className='border border-slate-600 hover:border-slate-400 px-8 py-3 rounded-lg font-semibold text-lg'>
            API Docs
          </a>
        </div>

        {/* 1. Hero API Response Preview */}
        <div className='mt-12 max-w-lg mx-auto bg-slate-900 border border-slate-700 rounded-xl p-4 text-left font-mono text-xs'>
          <div className='flex items-center gap-2 mb-3'>
            <span className='w-2 h-2 rounded-full bg-green-400 animate-pulse'/>
            <span className='text-slate-500'>Live API Response — 847ms</span>
          </div>
          <pre className='text-green-400'>{`{
  "risk_score": 92,
  "recommended_action": "HOLD",
  "fast_path": true,
  "signal_drivers": [
    "sim_swapped_recent",
    "device_swapped",
    "device_roaming_anomaly"
  ]
}`}</pre>
        </div>
      </section>

      {/* Problem stats */}
      <section id='problem' className='bg-slate-900/50 py-16'>
        <div className='max-w-5xl mx-auto px-8'>
          <h2 className='text-3xl font-bold text-center mb-12'>The attack chain is broken</h2>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6'>
            {[
              {
                stat: '₦320B',
                label: 'Lost to digital fraud 2023–2025',
                sub: 'SentinelLayer blocks this at the network layer'
              },
              {
                stat: '704%',
                label: 'Rise in deepfake attacks (2023)',
                sub: 'Biometric liveness is now structurally broken'
              },
              {
                stat: '25%',
                label: 'Of all fraud is SIM swap',
                sub: 'Intercepted in <300ms before authentication begins'
              },
            ].map(({ stat, label, sub }) => (
              <div key={stat} className='bg-slate-800 rounded-xl p-6 text-center border border-slate-700'>
                <div className='text-4xl font-bold text-red-400 mb-2'>{stat}</div>
                <div className='text-slate-400 text-sm'>{label}</div>
                {/* 2. Stats Context Line */}
                <div className='text-xs text-slate-500 mt-2 border-t border-slate-700 pt-2'>
                  {sub}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 3. How It Works Section */}
      <section id='solution' className='py-16 max-w-5xl mx-auto px-8'>
        <h2 className='text-3xl font-bold text-center mb-12'>
          Three modes. One integration.
        </h2>
        <div className='grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6'>
          {[
            {
              mode: 'M1',
              name: 'Pre-emptive',
              borderColor: 'border-blue-800/40',
              textColor: 'text-blue-400',
              desc: '15 Nokia NaC signals checked in parallel in under 300ms. Silent. Zero user friction. Runs on every transaction.',
            },
            {
              mode: 'M2',
              name: 'Live Enforcement',
              borderColor: 'border-amber-800/40',
              textColor: 'text-amber-400',
              desc: 'Consent-gated precise location retrieved. Fraud desk, telecom, and enforcement alerted simultaneously.',
            },
            {
              mode: 'M3',
              name: 'Post-Mortem',
              borderColor: 'border-purple-800/40',
              textColor: 'text-purple-400',
              desc: 'Historical device trail rendered as a court-ready Google Maps evidence map for law enforcement.',
            },
          ].map(({ mode, name, borderColor, textColor, desc }) => (
            <div key={mode}
              className={`bg-slate-800 rounded-xl p-6 border ${borderColor}`}>
              <div className={`${textColor} text-2xl font-bold mb-1`}>{mode}</div>
              <div className='font-semibold mb-3'>{name}</div>
              <p className='text-slate-400 text-sm'>{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id='pricing' className='py-16'>
        <div className='max-w-5xl mx-auto px-8'>

          {/* 4. Integration Line */}
          <div className='text-center py-8 border-y border-slate-800 mb-16'>
            <p className='text-slate-400 text-sm mb-3'>One endpoint. Any fintech. Any SSA network.</p>
            <code className='bg-slate-900 text-green-400 px-4 py-2 rounded-lg text-sm font-mono border border-slate-700'>
              POST /v1/sentinel/check → risk_score, recommended_action, signals
            </code>
          </div>

          <h2 className='text-3xl font-bold text-center mb-12'>Pricing</h2>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6'>
            {[
              { tier: 'Developer', price: 'Free', desc: '10,000 checks/month', cta: 'Start Free', highlight: false },
              { tier: 'Business', price: '$0.002/check', desc: 'Volume tiers, SLA', cta: 'Contact Sales', highlight: true },
              { tier: 'Enterprise', price: 'Custom', desc: 'White-label, compliance', cta: 'Contact Us', highlight: false },
            ].map(({ tier, price, desc, cta, highlight }) => (
              <div key={tier}
                className={`rounded-xl p-6 border ${highlight ? 'border-blue-500 bg-blue-900/20' : 'border-slate-700 bg-slate-800'}`}>
                <div className='text-lg font-bold mb-2'>{tier}</div>
                <div className='text-3xl font-bold text-blue-400 mb-2'>{price}</div>
                <div className='text-slate-400 text-sm mb-6'>{desc}</div>
                <button className={`w-full py-2 rounded-lg text-sm font-semibold
                  ${highlight ? 'bg-blue-600 hover:bg-blue-500' : 'border border-slate-600 hover:border-slate-400'}`}>
                  {cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 5. Footer */}
      <footer className='border-t border-slate-800 mt-16 py-8 text-center text-slate-500 text-xs'>
        <div className='flex justify-center gap-8 mb-4'>
          <span>🏆 Africa Ignite Hackathon 2026</span>
          <span>📡 GSMA Open Gateway</span>
          <span>🔷 Nokia Network-as-Code</span>
          <span>🌍 Theme 1: Financial Inclusion</span>
        </div>
        <p>SentinelLayer — Network-native fraud intelligence for Sub-Saharan Africa</p>
      </footer>
    </div>
  )
}
