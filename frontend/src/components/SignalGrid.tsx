interface SignalGridProps {
  signals: Record<string, boolean>
  drivers?: string[]   // top signal drivers from scoring engine
}

const SIGNAL_LABELS: Record<string, string> = {
  call_forwarding_active:     'Call Forwarding',
  sim_swapped_recent:         'SIM Swap',
  device_swapped:             'Device Swap',
  number_verification_failed: 'Number Verify',
  number_recycled:            'Number Recycled',
  kyc_match_score_low:        'KYC Match',
  kyc_tenure_short:           'KYC Tenure',
  customer_insight_spike:     'Usage Spike',
  location_outside_region:    'Location Zone',
  location_no_baseline:       'No Baseline',
  population_density_anomaly: 'Pop. Density',
  region_device_sparse:       'Region Sparse',
  device_identifier_new:      'New Device',
  device_unreachable:         'Unreachable',
  device_roaming_anomaly:     'Roaming Anomaly',
}

// Signals that trigger an immediate HOLD via the fast path rule engine
const FAST_PATH_TRIGGERS = new Set([
  'call_forwarding_active',
  'sim_swapped_recent',
  'device_swapped',
  'number_recycled',
  'number_verification_failed',
])

export function SignalGrid({ signals, drivers = [] }: SignalGridProps) {
  const driverSet = new Set(drivers)

  return (
    <div className='grid grid-cols-2 gap-2'>
      {Object.entries(signals).map(([key, flagged]) => {
        const isDriver  = driverSet.has(key)
        const isTrigger = flagged && FAST_PATH_TRIGGERS.has(key)

        return (
          <div
            key={key}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono
              transition-all duration-300
              ${flagged
                ? 'bg-red-900/40 border border-red-700 text-red-300'
                : 'bg-slate-800 border border-slate-700 text-slate-400'
              }
              ${isDriver ? 'ring-1 ring-yellow-500/60' : ''}
            `}
          >
            {/* Status dot */}
            <span
              className={`w-2 h-2 rounded-full shrink-0 ${
                flagged ? 'bg-red-400 animate-pulse' : 'bg-green-500'
              }`}
            />

            {/* Signal label */}
            <span className='flex-1 truncate'>
              {SIGNAL_LABELS[key] ?? key}
            </span>

            {/* Fast path trigger badge */}
            {isTrigger && (
              <span className='ml-1 px-1.5 py-0.5 rounded text-[9px] font-bold
                bg-yellow-500 text-black shrink-0 leading-tight'>
                FAST PATH
              </span>
            )}

            {/* Top driver badge (from AI/weighted scorer) */}
            {isDriver && !isTrigger && (
              <span className='ml-1 px-1.5 py-0.5 rounded text-[9px] font-bold
                bg-orange-600 text-white shrink-0 leading-tight'>
                DRIVER
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}
