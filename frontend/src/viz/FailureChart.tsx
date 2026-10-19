import { useState, type PointerEvent } from 'react'
import type { EstimatorKey } from '../ope/estimators'
import { ESTIMATORS } from '../ope/meta'
import { fmt } from '../ope/format'
import type { FailureStudyResult } from '../ope/study'
import { useElementWidth } from '../ui/useElementWidth'
import { Marker, MarkerGlyph } from './Marker'
import { linear, niceTicks, tickLabel } from './scale'

const HEIGHT = 320
const M = { top: 16, right: 16, bottom: 44, left: 52 }

export default function FailureChart({ data, showNaive, current }: { data: FailureStudyResult; showNaive: boolean; current: number }) {
  const [ref, width] = useElementWidth<HTMLDivElement>()
  const [hover, setHover] = useState<number | null>(null)
  const visible = ESTIMATORS.filter((e) => showNaive || e.key !== 'naive')
  const yMax = Math.max(0.01, ...visible.flatMap((e) => data.errors[e.key])) * 1.1
  const x = linear(0, 1, M.left, width - M.right)
  const y = linear(0, yMax, HEIGHT - M.bottom, M.top)
  const yTicks = niceTicks(0, yMax, 4)
  const yStep = yTicks.length > 1 ? yTicks[1] - yTicks[0] : 0.1
  const currentIdx = Math.round(Math.min(1, Math.max(0, current)) * (data.cs.length - 1))
  const idx = hover ?? currentIdx
  const last = data.cs.length - 1

  const onMove = (event: PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect()
    const c = (event.clientX - rect.left - M.left) / (width - M.left - M.right)
    setHover(Math.round(Math.min(1, Math.max(0, c)) * last))
  }
  const line = (k: EstimatorKey) => data.cs.map((c, i) => `${i ? 'L' : 'M'}${x(c).toFixed(1)},${y(data.errors[k][i]).toFixed(1)}`).join('')

  return (
    <div className="flex flex-col gap-xl">
      <div ref={ref} className="w-full">
        <svg
          width={width}
          height={HEIGHT}
          role="img"
          aria-label={`Mean absolute error against confounding from 0 to 1. At c = 1: ${ESTIMATORS.map((e) => `${e.name} ${fmt(data.errors[e.key][last])}`).join(', ')}.`}
          className="block touch-none"
          onPointerMove={onMove}
          onPointerLeave={() => setHover(null)}
        >
          {yTicks.map((t) => (
            <g key={t}>
              <line x1={M.left} x2={width - M.right} y1={y(t)} y2={y(t)} strokeWidth={1} className="stroke-line" />
              <text x={M.left - 8} y={y(t)} dy="0.35em" textAnchor="end" className="fill-fg-muted text-caption tabular-nums">
                {tickLabel(t, yStep)}
              </text>
            </g>
          ))}
          {data.cs.map((c, i) =>
            i % 2 === 0 ? (
              <text key={c} x={x(c)} y={HEIGHT - M.bottom + 20} textAnchor="middle" className="fill-fg-muted text-caption tabular-nums">
                {c.toFixed(1)}
              </text>
            ) : null,
          )}
          <text x={(M.left + width - M.right) / 2} y={HEIGHT - 4} textAnchor="middle" className="fill-fg-muted text-caption">
            Hidden confounding strength c →
          </text>

          <rect x={x(data.cs[idx]) - 14} y={M.top} width={28} height={HEIGHT - M.bottom - M.top} rx={8} className="fill-primary-soft" />

          {visible.map((e) => (
            <path key={e.key} d={line(e.key)} pathLength={1} fill="none" strokeWidth={2.5} strokeLinejoin="round" className={`ds-draw ${e.stroke}`} />
          ))}
          {visible.map((e) => data.cs.map((c, i) => <Marker key={`${e.key}-${c}`} meta={e} cx={x(c)} cy={y(data.errors[e.key][i])} r={i === idx ? 7 : 4} />))}
        </svg>
      </div>

      <div className="flex flex-col gap-md">
        <p className="text-small text-fg-muted">
          Average miss at c = <span className="font-semibold tabular-nums text-fg">{data.cs[idx].toFixed(1)}</span>
          {hover === null ? ' (your Lab setting, hover the chart to explore)' : ''}
        </p>
        <ul className="grid grid-cols-2 gap-sm sm:grid-cols-3 lg:grid-cols-6">
          {ESTIMATORS.map((e) => (
            <li key={e.key} className="flex items-center gap-sm rounded-md bg-surface-sunken px-md py-sm">
              <MarkerGlyph meta={e} />
              <span className="text-small font-medium text-fg">{e.name}</span>
              <span className="ml-auto text-small tabular-nums text-fg-muted">{fmt(data.errors[e.key][idx])}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
