import { cn } from '../ui/cn'
import type { EstimatorMeta, MarkerShape } from '../ope/meta'

function polygon(cx: number, cy: number, r: number, sides: number, rotation = -Math.PI / 2) {
  const pts: string[] = []
  for (let i = 0; i < sides; i++) {
    const t = rotation + (i * 2 * Math.PI) / sides
    pts.push(`${(cx + r * Math.cos(t)).toFixed(2)},${(cy + r * Math.sin(t)).toFixed(2)}`)
  }
  return `M${pts.join('L')}Z`
}

export function markerPath(shape: MarkerShape, cx: number, cy: number, r: number) {
  switch (shape) {
    case 'cross': {
      const k = r * 0.8
      return `M${cx - k},${cy - k}L${cx + k},${cy + k}M${cx + k},${cy - k}L${cx - k},${cy + k}`
    }
    case 'triangle':
      return polygon(cx, cy + r * 0.15, r * 1.1, 3)
    case 'square': {
      const k = r * 0.8
      return `M${cx - k},${cy - k}H${cx + k}V${cy + k}H${cx - k}Z`
    }
    case 'diamond':
      return polygon(cx, cy, r * 1.05, 4)
    case 'pentagon':
      return polygon(cx, cy, r, 5)
    case 'circle':
      return `M${cx - r * 0.85},${cy}a${r * 0.85},${r * 0.85} 0 1,0 ${r * 1.7},0a${r * 0.85},${r * 0.85} 0 1,0 ${-r * 1.7},0`
  }
}

interface MarkerProps {
  meta: EstimatorMeta
  cx: number
  cy: number
  r?: number
  /** Outline class separating the glyph from its background. */
  outline?: string
}

/** Estimator glyph inside a chart <svg>: shape + color, never color alone. */
export function Marker({ meta, cx, cy, r = 6, outline = 'stroke-surface' }: MarkerProps) {
  const d = markerPath(meta.marker, cx, cy, r)
  if (meta.marker === 'cross') return <path d={d} fill="none" strokeWidth={r * 0.55} strokeLinecap="round" className={meta.stroke} />
  return <path d={d} strokeWidth={1.5} strokeLinejoin="round" className={cn(meta.fill, outline)} />
}

export function MarkerGlyph({ meta, className }: { meta: EstimatorMeta; className?: string }) {
  return (
    <svg viewBox="-8 -8 16 16" aria-hidden className={cn('size-4 shrink-0 overflow-visible', className)}>
      <Marker meta={meta} cx={0} cy={0} r={6} outline="stroke-transparent" />
    </svg>
  )
}
