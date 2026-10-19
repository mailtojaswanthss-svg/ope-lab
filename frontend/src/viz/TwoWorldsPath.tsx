import { useId } from 'react'
import { cn } from '../ui/cn'
import { usePrefersReducedMotion } from '../ui/motion'

const TRUNK = 'M0,300 C140,300 260,250 420,220'
const REALITY = 'M420,220 C600,184 760,96 1200,70'
const COUNTERFACTUAL = 'M420,220 C620,256 860,300 1200,262'

const cubic = (p0: number[], p1: number[], p2: number[], p3: number[], t: number) => {
  const u = 1 - t
  return [0, 1].map((i) => u * u * u * p0[i] + 3 * u * u * t * p1[i] + 3 * u * t * t * p2[i] + t * t * t * p3[i])
}
const T = [0.16, 0.34, 0.52, 0.7, 0.88]
const realityPts = T.map((t) => cubic([420, 220], [600, 184], [760, 96], [1200, 70], t))
const cfPts = T.map((t) => cubic([420, 220], [620, 256], [860, 300], [1200, 262], t))
const STARS = Array.from({ length: 46 }, (_, i) => {
  const a = Math.sin(i * 12.9898) * 43758.5453
  const b = Math.sin(i * 78.233) * 12345.6789
  return { x: (a - Math.floor(a)) * 1200, y: (b - Math.floor(b)) * 360, r: i % 5 === 0 ? 1.8 : 1.1 }
})

/** One logged path (solid) and the counterfactual it hides (dotted). */
export default function TwoWorldsPath({ className }: { className?: string }) {
  const reduced = usePrefersReducedMotion()
  const uid = useId().replace(/:/g, '')
  const maskId = `cf-mask-${uid}`
  const glowId = `glow-${uid}`

  return (
    <svg viewBox="0 0 1200 360" preserveAspectRatio="xMidYMid meet" className={cn('h-auto w-full overflow-visible', className)} aria-hidden>
      <defs>
        <filter id={glowId} x="-10%" y="-50%" width="120%" height="200%">
          <feGaussianBlur stdDeviation="8" />
        </filter>
        <mask id={maskId} maskUnits="userSpaceOnUse" x="0" y="0" width="1200" height="360">
          <path d={COUNTERFACTUAL} pathLength={1} fill="none" stroke="white" strokeWidth={24} className="ds-draw ds-draw-late" />
        </mask>
      </defs>

      {STARS.map((s, i) => (
        <circle key={i} cx={s.x} cy={s.y} r={s.r} className="fill-stage-ghost opacity-40" />
      ))}

      <path d={TRUNK} pathLength={1} fill="none" strokeWidth={4} strokeLinecap="round" className="ds-draw stroke-stage-fg" />

      <path d={REALITY} fill="none" strokeWidth={12} className="stroke-stage-accent opacity-30" filter={`url(#${glowId})`} />
      <path id={`reality-${uid}`} d={REALITY} pathLength={1} fill="none" strokeWidth={4} strokeLinecap="round" className="ds-draw ds-draw-late stroke-stage-accent" />

      <g mask={`url(#${maskId})`}>
        <path id={`cf-${uid}`} d={COUNTERFACTUAL} fill="none" strokeWidth={4} strokeLinecap="round" strokeDasharray="0.1 14" className="stroke-pink" />
      </g>

      <g className="ds-fade-late">
        {realityPts.map(([x, y], i) => (
          <circle key={`r${i}`} cx={x} cy={y} r={6} className="fill-stage-accent stroke-stage" strokeWidth={3} />
        ))}
        {cfPts.map(([x, y], i) => (
          <circle key={`c${i}`} cx={x} cy={y} r={6} fill="none" strokeWidth={2} strokeDasharray="2 3" className="stroke-pink" />
        ))}
        <circle cx={420} cy={220} r={14} className="fill-stage stroke-stage-fg" strokeWidth={3} />
        <circle cx={420} cy={220} r={5} className="fill-insight" />
      </g>

      {!reduced && (
        <g className="ds-fade-late">
          <circle r={5} className="fill-stage-fg">
            <animateMotion dur="6s" begin="0s" repeatCount="indefinite" rotate="auto">
              <mpath href={`#reality-${uid}`} />
            </animateMotion>
          </circle>
          <circle r={5} fill="none" strokeWidth={2} className="stroke-pink">
            <animateMotion dur="6s" begin="0s" repeatCount="indefinite" rotate="auto">
              <mpath href={`#cf-${uid}`} />
            </animateMotion>
          </circle>
        </g>
      )}
    </svg>
  )
}
