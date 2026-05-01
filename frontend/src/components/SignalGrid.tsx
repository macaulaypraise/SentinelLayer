interface SignalGridProps { signals: Record<string, boolean> }

const SIGNAL_LABELS: Record<string, string> = {
  call_forwarding_active: 'Call Forwarding',
  sim_swapped_recent: 'SIM Swap',
  device_swapped: 'Device Swap',
  number_verification_failed: 'Number Verify',
  number_recycled: 'Number Recycled',
  kyc_match_score_low: 'KYC Match',
  kyc_tenure_short: 'KYC Tenure',
  customer_insight_spike: 'Usage Spike',
  location_outside_region: 'Location Zone',
  location_no_baseline: 'No Baseline',
  population_density_anomaly: 'Pop. Density',
  region_device_sparse: 'Region Sparse',
  device_identifier_new: 'New Device',
  device_unreachable: 'Unreachable',
}

export function SignalGrid({ signals }: SignalGridProps) {
  return (
    <div className='grid grid-cols-2 gap-2'>
      {Object.entries(signals).map(([key, flagged]) => (
        <div key={key}
          className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-mono
            ${flagged ? 'bg-red-900/40 border border-red-700 text-red-300' : 'bg-slate-800 border border-slate-700 text-slate-400'}`}>
          <span className={`w-2 h-2 rounded-full shrink-0 ${flagged ? 'bg-red-400' : 'bg-green-500'}`} />
          {SIGNAL_LABELS[key] ?? key}
        </div>
      ))}
    </div>
  )
}
