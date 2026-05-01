// src/components/RiskGauge.tsx

import { useEffect, useState } from 'react'

const color = (s: number) => s < 45 ? '#22C55E' : s < 70 ? '#F59E0B' : '#EF4444'
const label = (s: number) => s < 45 ? 'ALLOW' : s < 70 ? 'STEP-UP' : 'HOLD'
const bg = (s: number) => s < 45 ? 'bg-green-900/30' : s < 70 ? 'bg-amber-900/30' : 'bg-red-900/30'

export function RiskGauge({ score }: { score: number }) {
    const [display, setDisplay] = useState(0)
    useEffect(() => { const t = setTimeout(() => setDisplay(score), 80); return () => clearTimeout(t) }, [score])

    const stroke = 2 * Math.PI * 45
    const dash = stroke * (display / 100)
    const c = color(display)

    return (
    <div className='flex flex-col items-center gap-3'>
        <svg viewBox='0 0 100 100' className='w-48 h-48 drop-shadow-lg'>
            <circle cx='50' cy='50' r='45' fill='none' stroke='#1E293B' strokeWidth='8'/>
            <circle cx='50' cy='50' r='45' fill='none'
            stroke={c} strokeWidth='8'
            strokeDasharray={`${dash} ${stroke}`}
            strokeLinecap='round'
            transform='rotate(-90 50 50)'
            style={{ transition: 'stroke-dasharray 0.5s ease, stroke 0.3s ease' }}
            />
            <text x='50' y='46' textAnchor='middle' fontSize='22' fontWeight='bold' fill={c}>{display}</text>
            <text x='50' y='62' textAnchor='middle' fontSize='8' fill='#64748B'>RISK SCORE</text>
            </svg>
            <span className={`px-4 py-1 rounded-full font-mono text-sm font-bold border ${bg(display)}`}
            style={{ color: c, borderColor: c }}>
            {label(display)}
        </span>
    </div>
    )
}
