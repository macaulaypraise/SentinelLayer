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
          <a href='http://localhost:8000/docs' target='_blank' rel="noreferrer"
            className='border border-slate-600 hover:border-slate-400 px-8 py-3 rounded-lg font-semibold text-lg'>
            API Docs
          </a>
        </div>
      </section>

      {/* Problem stats */}
      <section id='problem' className='bg-slate-900/50 py-16'>
        <div className='max-w-5xl mx-auto px-8'>
          <h2 className='text-3xl font-bold text-center mb-12'>The attack chain is broken</h2>
          <div className='grid grid-cols-3 gap-6'>
            {[
              { stat: '₦320B', label: 'Lost to digital fraud 2023–2025' },
              { stat: '704%', label: 'Rise in deepfake attacks (2023)' },
              { stat: '25%', label: 'Of all fraud is SIM swap' },
            ].map(({ stat, label }) => (
              <div key={stat} className='bg-slate-800 rounded-xl p-6 text-center border border-slate-700'>
                <div className='text-4xl font-bold text-red-400 mb-2'>{stat}</div>
                <div className='text-slate-400 text-sm'>{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id='pricing' className='py-16'>
        <div className='max-w-5xl mx-auto px-8'>
          <h2 className='text-3xl font-bold text-center mb-12'>Pricing</h2>
          <div className='grid grid-cols-3 gap-6'>
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
    </div>
  )
}
