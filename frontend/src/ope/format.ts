export const fmt = (v: number, digits = 3) => (Number.isFinite(v) ? v.toFixed(digits) : '—')

export const fmtSigned = (v: number, digits = 3) => {
  if (!Number.isFinite(v)) return '—'
  const s = v.toFixed(digits)
  return v >= 0 ? `+${s}` : s.replace('-', '−')
}

export type Tone = 'success' | 'warning' | 'danger'

/** |err| < 0.02 → success, < 0.08 → warning, otherwise danger. */
export const errorTone = (err: number): Tone => {
  const a = Math.abs(err)
  if (!Number.isFinite(a)) return 'danger'
  if (a < 0.02) return 'success'
  if (a < 0.08) return 'warning'
  return 'danger'
}

export const TONE_TEXT: Record<Tone, string> = {
  success: 'text-success',
  warning: 'text-warning',
  danger: 'text-danger',
}
