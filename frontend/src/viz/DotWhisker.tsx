import type { Interval } from '../ope/bootstrap'
import type { EstimateMap, EstimatorKey } from '../ope/estimators'
import { ESTIMATORS } from '../ope/meta'
import { fmt } from '../ope/format'
import { V_STAR } from '../ope/simulate'
import { cn } from '../ui/cn'
import { useTweenArray } from '../ui/motion'
import { useElementWidth } from '../ui/useElementWidth'
import { Marker } from './Marker'
import { linear, niceTicks, tickLabel } from './scale'

interface DotWhiskerProps {
  estimates: EstimateMap
  intervals?: Record<EstimatorKey, Interval>
  intervalsPending?: boolean
  best: EstimatorKey | null
  showNaiveWorld: boolean
}

const ROW = 46
const TOP = 40
const BOTTOM = 36
const K = ESTIMATORS.length

/** Lab results on the stage: one row per estimator, V* as the solid "reality" line. Values glide between runs. */
export default function DotWhisker({ estimates, intervals, intervalsPending, best, showNaiveWorld }: DotWhiskerProps) {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const narrow = width < 480
  const left = narrow ? 76 : 104
  const right = narrow ? 52 : 64
  const height = TOP + K * ROW + BOTTOM

  const values: number[] = [V_STAR]
  for (const e of ESTIMATORS) {
    if (Number.isFinite(estimates[e.key])) values.push(estimates[e.key])
    const ci = intervals?.[e.key]
    if (ci && Number.isFinite(ci.lo) && Number.isFinite(ci.hi)) values.push(ci.lo, ci.hi)
  }
  const rawLo = Math.min(...values)
  const rawHi = Math.max(...values)
  const pad = Math.max(0.02, (rawHi - rawLo) * 0.08)

  // Tween domain + all positions together so the chart glides instead of jumping.
  const target = [
    rawLo - pad,
    rawHi + pad,
    ...ESTIMATORS.map((e) => estimates[e.key]),
    ...ESTIMATORS.map((e) => intervals?.[e.key]?.lo ?? Number.NaN),
    ...ESTIMATORS.map((e) => intervals?.[e.key]?.hi ?? Number.NaN),
  ]
  const tw = useTweenArray(target)
  const [d0, d1] = tw
  const est = tw.slice(2, 2 + K)
  const ciLo = tw.slice(2 + K, 2 + 2 * K)
  const ciHi = tw.slice(2 + 2 * K, 2 + 3 * K)

  const x = linear(d0, d1, left, width - right)
  const ticks = niceTicks(d0, d1, narrow ? 3 : 5)
  const step = ticks.length > 1 ? ticks[1] - ticks[0] : 0.1
  const rowY = (i: number) => TOP + i * ROW + ROW / 2
  const naiveX = x(est[0])

  return (
    <div ref={ref} className="w-full">
      <svg width={width} height={height} role="img" aria-labelledby="dw-title dw-desc" className="block overflow-visible">
        <title id="dw-title">Estimates of the new policy’s value, with 95% bootstrap intervals</title>
        <desc id="dw-desc">{`True value ${fmt(V_STAR, 4)}. ` + ESTIMATORS.map((e) => `${e.name} ${fmt(estimates[e.key])}`).join(', ')}</desc>

        {ticks.map((t) => (
          <g key={t}>
            <line x1={x(t)} x2={x(t)} y1={TOP - 8} y2={height - BOTTOM} strokeWidth={1} className="stroke-stage-line" />
            <text x={x(t)} y={height - BOTTOM + 22} textAnchor="middle" className="fill-stage-fg-muted text-caption tabular-nums">
              {tickLabel(t, step)}
            </text>
          </g>
        ))}

        {ESTIMATORS.map((e, i) => (
          <rect key={e.key} x={0} y={rowY(i) - ROW / 2 + 3} width={width} height={ROW - 6} rx={10} className={i % 2 ? 'fill-transparent' : 'fill-stage-surface'} />
        ))}

        {showNaiveWorld && Number.isFinite(naiveX) && (
          <g>
            <line x1={naiveX} x2={naiveX} y1={TOP - 8} y2={height - BOTTOM} strokeWidth={2} strokeDasharray="0.1 7" strokeLinecap="round" className="stroke-pink" />
            <text x={naiveX} y={TOP - 16} textAnchor="end" dx={-6} className="fill-pink text-caption font-semibold">
              naive world
            </text>
          </g>
        )}

        <line x1={x(V_STAR)} x2={x(V_STAR)} y1={TOP - 8} y2={height - BOTTOM} strokeWidth={2.5} className="stroke-insight" />
        <text x={x(V_STAR)} y={TOP - 16} textAnchor="start" dx={6} className="fill-insight text-caption font-semibold">
          truth {fmt(V_STAR)}
        </text>

        {ESTIMATORS.map((e, i) => {
          const y = rowY(i)
          const v = est[i]
          const hasCi = Number.isFinite(ciLo[i]) && Number.isFinite(ciHi[i])
          return (
            <g key={e.key}>
              <Marker meta={e} cx={16} cy={y} r={6} outline="stroke-stage" />
              <text x={30} y={y} dy="0.35em" className="fill-stage-fg text-small font-semibold">
                {e.name}
              </text>
              {hasCi && (
                <g className={cn('transition-ds', intervalsPending ? 'opacity-40' : 'opacity-100')}>
                  <line x1={x(ciLo[i])} x2={x(ciHi[i])} y1={y} y2={y} strokeWidth={2} strokeLinecap="round" className="stroke-stage-fg-muted" />
                  <line x1={x(ciLo[i])} x2={x(ciLo[i])} y1={y - 6} y2={y + 6} strokeWidth={2} strokeLinecap="round" className="stroke-stage-fg-muted" />
                  <line x1={x(ciHi[i])} x2={x(ciHi[i])} y1={y - 6} y2={y + 6} strokeWidth={2} strokeLinecap="round" className="stroke-stage-fg-muted" />
                </g>
              )}
              {Number.isFinite(v) && (
                <>
                  {best === e.key && <circle cx={x(v)} cy={y} r={17} className="animate-pulse fill-stage-accent opacity-25" />}
                  <Marker meta={e} cx={x(v)} cy={y} r={8} outline="stroke-stage" />
                  <text x={width - 4} y={y} dy="0.35em" textAnchor="end" className="fill-stage-fg-muted text-caption tabular-nums">
                    {fmt(v)}
                  </text>
                </>
              )}
            </g>
          )
        })}
      </svg>
    </div>
  )
}
