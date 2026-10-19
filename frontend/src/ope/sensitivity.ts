import { simulate, V_STAR, type SimParams } from './simulate.ts'
import { fitPropensity, importanceWeights } from './estimators.ts'

export interface SensitivityResult {
  lambdas: number[]
  lower: number[]
  upper: number[]
  point: number
  lambdaStar: number | null
}

export const LAMBDA_MAX = 3
export const LAMBDA_POINTS = 40

/**
 * Marginal sensitivity model on SNIPW over matched rows: each weight may lie in
 * [w/Λ, w·Λ]. The extreme self-normalized mean is attained by a threshold rule
 * on sorted rewards, so each Λ is an O(n) scan over prefix sums.
 */
export function runSensitivity(params: SimParams): SensitivityResult {
  const ds = simulate(params)
  const { w } = importanceWeights(ds, fitPropensity(ds))

  const rows: { r: number; w: number }[] = []
  for (let i = 0; i < ds.n; i++) if (w[i] > 0) rows.push({ r: ds.r[i], w: w[i] })
  rows.sort((p, q) => p.r - q.r)
  const m = rows.length

  // Prefix sums over ascending rewards.
  const W = new Float64Array(m + 1)
  const WR = new Float64Array(m + 1)
  for (let i = 0; i < m; i++) {
    W[i + 1] = W[i] + rows[i].w
    WR[i + 1] = WR[i] + rows[i].w * rows[i].r
  }
  const totW = W[m]
  const totWR = WR[m]
  const point = totW > 0 ? totWR / totW : Number.NaN

  const lambdas = Array.from({ length: LAMBDA_POINTS }, (_, i) => 1 + ((LAMBDA_MAX - 1) * i) / (LAMBDA_POINTS - 1))
  const lower: number[] = []
  const upper: number[] = []

  for (const lam of lambdas) {
    const up = lam
    const dn = 1 / lam
    let hi = -Infinity
    let lo = Infinity
    for (let k = 0; k <= m; k++) {
      // Rows [0, k) form the low-reward block, rows [k, m) the high-reward block.
      const lowW = W[k]
      const lowWR = WR[k]
      const highW = totW - lowW
      const highWR = totWR - lowWR
      const upperVal = (dn * lowWR + up * highWR) / (dn * lowW + up * highW)
      const lowerVal = (up * lowWR + dn * highWR) / (up * lowW + dn * highW)
      if (upperVal > hi) hi = upperVal
      if (lowerVal < lo) lo = lowerVal
    }
    lower.push(m > 0 ? lo : Number.NaN)
    upper.push(m > 0 ? hi : Number.NaN)
  }

  const idx = lambdas.findIndex((_, i) => lower[i] <= V_STAR && V_STAR <= upper[i])
  return { lambdas, lower, upper, point, lambdaStar: idx >= 0 ? lambdas[idx] : null }
}
