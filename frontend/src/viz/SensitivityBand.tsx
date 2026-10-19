import { fmt } from '../ope/format'
import { V_STAR } from '../ope/simulate'
import type { SensitivityResult } from '../ope/sensitivity'
import { useElementWidth } from '../ui/useElementWidth'
import { linear, niceTicks, tickLabel } from './scale'

const HEIGHT = 320
const M = { top: 20, right: 20, bottom: 44, left: 56 }

export default function SensitivityBand({ data }: { data: SensitivityResult }) {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const all = [...data.lower, ...data.upper, V_STAR].filter(Number.isFinite)
  const lo = Math.min(...all)
  const hi = Math.max(...all)
  const pad = Math.max(0.01, (hi - lo) * 0.08)
  const x = linear(1, 3, M.left, width - M.right)
  const y = linear(lo - pad, hi + pad, HEIGHT - M.bottom, M.top)
  const yTicks = niceTicks(lo - pad, hi + pad, 4)
  const yStep = yTicks.length > 1 ? yTicks[1] - yTicks[0] : 0.1
  const last = data.lambdas.length - 1

  const path = (vals: number[]) => data.lambdas.map((l, i) => `${i ? 'L' : 'M'}${x(l).toFixed(1)},${y(vals[i]).toFixed(1)}`).join('')
  const lowerRev = data.lambdas
    .map((l, i) => `L${x(l).toFixed(1)},${y(data.lower[i]).toFixed(1)}`)
    .reverse()
    .join('')

  return (
    <div ref={ref} className="w-full">
      <svg
        width={width}
        height={HEIGHT}
        role="img"
        aria-label={`Sensitivity band for SNIPW. At Λ = 3 the bounds are ${fmt(data.lower[last])} to ${fmt(data.upper[last])}. True value ${fmt(V_STAR)}.${data.lambdaStar ? ` Bounds first cover the truth at Λ = ${data.lambdaStar.toFixed(2)}.` : ' Bounds never cover the truth for Λ ≤ 3.'}`}
        className="block"
      >
        <defs>
          <linearGradient id="sens-band" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" className="[stop-color:var(--color-teal)]" stopOpacity={0.35} />
            <stop offset="100%" className="[stop-color:var(--color-primary)]" stopOpacity={0.25} />
          </linearGradient>
        </defs>
        {yTicks.map((t) => (
          <g key={t}>
            <line x1={M.left} x2={width - M.right} y1={y(t)} y2={y(t)} strokeWidth={1} className="stroke-line" />
            <text x={M.left - 8} y={y(t)} dy="0.35em" textAnchor="end" className="fill-fg-muted text-caption tabular-nums">
              {tickLabel(t, yStep)}
            </text>
          </g>
        ))}
        {[1, 1.5, 2, 2.5, 3].map((t) => (
          <text key={t} x={x(t)} y={HEIGHT - M.bottom + 20} textAnchor="middle" className="fill-fg-muted text-caption tabular-nums">
            {t.toFixed(1)}
          </text>
        ))}
        <text x={(M.left + width - M.right) / 2} y={HEIGHT - 4} textAnchor="middle" className="fill-fg-muted text-caption">
          How much hidden bias we allow (Λ) →
        </text>

        <path d={`${path(data.upper)}${lowerRev}Z`} fill="url(#sens-band)" className="animate-page-in" />
        <path d={path(data.upper)} pathLength={1} fill="none" strokeWidth={2.5} className="ds-draw stroke-teal" />
        <path d={path(data.lower)} pathLength={1} fill="none" strokeWidth={2.5} className="ds-draw stroke-primary" />

        <line x1={M.left} x2={width - M.right} y1={y(V_STAR)} y2={y(V_STAR)} strokeWidth={2.5} className="stroke-insight" />
        <text x={width - M.right} y={y(V_STAR)} dy={-8} textAnchor="end" className="fill-insight-ink text-caption font-semibold">
          truth {fmt(V_STAR)}
        </text>

        {data.lambdaStar !== null && (
          <g>
            <line x1={x(data.lambdaStar)} x2={x(data.lambdaStar)} y1={M.top} y2={HEIGHT - M.bottom} strokeWidth={1.5} strokeDasharray="4 4" className="stroke-fg-muted" />
            <text x={x(data.lambdaStar)} y={M.top} dx={6} dy="0.8em" className="fill-fg text-caption font-semibold">
              Λ* {data.lambdaStar.toFixed(2)}
            </text>
          </g>
        )}

        {Number.isFinite(data.point) && <circle cx={x(1)} cy={y(data.point)} r={6} className="fill-fg stroke-surface" strokeWidth={2} />}
        <text x={x(data.lambdas[last])} y={y(data.upper[last])} dy={-8} textAnchor="end" className="fill-teal-ink text-caption font-medium">
          best case
        </text>
        <text x={x(data.lambdas[last])} y={y(data.lower[last])} dy={16} textAnchor="end" className="fill-primary-ink text-caption font-medium">
          worst case
        </text>
      </svg>
    </div>
  )
}
