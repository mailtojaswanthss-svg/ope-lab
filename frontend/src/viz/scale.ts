export const linear = (d0: number, d1: number, r0: number, r1: number) => (v: number) =>
  d1 === d0 ? (r0 + r1) / 2 : r0 + ((v - d0) / (d1 - d0)) * (r1 - r0)

/** ~`count` round tick values spanning [lo, hi]. */
export function niceTicks(lo: number, hi: number, count = 5): number[] {
  if (!Number.isFinite(lo) || !Number.isFinite(hi) || hi <= lo) return [lo]
  const raw = (hi - lo) / count
  const mag = 10 ** Math.floor(Math.log10(raw))
  const norm = raw / mag
  const step = (norm >= 5 ? 10 : norm >= 2 ? 5 : norm >= 1 ? 2 : 1) * mag
  const start = Math.ceil(lo / step) * step
  const out: number[] = []
  for (let v = start; v <= hi + step * 1e-9; v += step) out.push(Math.round(v / step) * step)
  return out
}

export const tickLabel = (v: number, step: number) => {
  const digits = Math.max(0, Math.min(3, -Math.floor(Math.log10(step || 1))))
  return v.toFixed(digits)
}
