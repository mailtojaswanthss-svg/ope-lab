import { createRng } from './rng.ts'
import { resample, simulate, type SimParams } from './simulate.ts'
import { ESTIMATOR_KEYS, estimateAll, type EstimatorKey } from './estimators.ts'

export interface Interval {
  lo: number
  hi: number
  se: number
}

export interface BootstrapResult {
  b: number
  intervals: Record<EstimatorKey, Interval>
}

export const effectiveB = (n: number, b: number) => (n > 10_000 ? Math.min(b, 50) : b)

function quantile(sorted: number[], q: number) {
  if (sorted.length === 0) return Number.NaN
  const pos = (sorted.length - 1) * q
  const lo = Math.floor(pos)
  const hi = Math.ceil(pos)
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo)
}

/** Percentile 95% CIs; every replicate refits both nuisance models. */
export function runBootstrap(params: SimParams, bRequested: number): BootstrapResult {
  const ds = simulate(params)
  const b = effectiveB(params.n, bRequested)
  const rng = createRng(params.seed ^ 0x9e3779b9)
  const draws = Object.fromEntries(ESTIMATOR_KEYS.map((k) => [k, [] as number[]])) as Record<EstimatorKey, number[]>

  for (let rep = 0; rep < b; rep++) {
    const est = estimateAll(resample(ds, rng.int)).estimates
    for (const k of ESTIMATOR_KEYS) if (Number.isFinite(est[k])) draws[k].push(est[k])
  }

  const intervals = {} as Record<EstimatorKey, Interval>
  for (const k of ESTIMATOR_KEYS) {
    const v = draws[k].sort((p, q) => p - q)
    const mean = v.reduce((s, x) => s + x, 0) / Math.max(1, v.length)
    const variance = v.reduce((s, x) => s + (x - mean) ** 2, 0) / Math.max(1, v.length - 1)
    intervals[k] = { lo: quantile(v, 0.025), hi: quantile(v, 0.975), se: Math.sqrt(variance) }
  }
  return { b, intervals }
}
