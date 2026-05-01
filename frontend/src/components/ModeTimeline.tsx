interface ModeTimelineProps { activeMode: number }

const MODES = [
  { num: 1, name: 'Pre-emptive', desc: '14 signals, <300ms' },
  { num: 2, name: 'Live Enforcement', desc: 'Consent gate + location' },
  { num: 3, name: 'Post-Mortem', desc: 'Evidence trail' },
]

export function ModeTimeline({ activeMode }: ModeTimelineProps) {
  return (
    <div className='flex items-center gap-0'>
      {MODES.map((m, i) => (
        <div key={m.num} className='flex items-center'>
          <div className={`flex flex-col items-center p-3 rounded-lg min-w-[100px] text-center
            ${activeMode === m.num ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'}`}>
            <span className='text-lg font-bold'>M{m.num}</span>
            <span className='text-xs font-semibold'>{m.name}</span>
            <span className='text-xs opacity-70'>{m.desc}</span>
          </div>
          {i < 2 && <div className={`h-0.5 w-8 ${activeMode > m.num ? 'bg-blue-500' : 'bg-slate-700'}`} />}
        </div>
      ))}
    </div>
  )
}
