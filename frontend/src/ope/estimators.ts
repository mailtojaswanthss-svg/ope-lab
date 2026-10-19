import { sigmoid, type Dataset } from './simulate.ts'

export const ESTIMATOR_KEYS = ['naive', 'replay', 'dm', 'ipw', 'snipw', 'dr'] as const
export type EstimatorKey = (typeof ESTIMATOR_KEYS)[number]
export type EstimateMap = Record<EstimatorKey, number>

export interface WeightHealth {
  ess: number
  essPct: number
  maxW: number
  matched: number
  pMin: number
  pMax: number
}

export interface PointResult {
  estimates: EstimateMap
  health: WeightHealth
}

const P_CLIP_LO = 0.01
const P_CLIP_HI = 0.99
const RIDGE_ALPHA = 1.0

/** Logistic regression of A on [1, X] via Newton/IRLS. */
export function fitPropensity(ds: Dataset): [number, number] {
  let b0 = 0
  let b1 = 0
  for (let iter = 0; iter < 25; iter++) {
    let g0 = 0
    let g1 = 0
    let h00 = 1e-8
    let h01 = 0
    let h11 = 1e-8
    for (let i = 0; i < ds.n; i++) {
      const xi = ds.x[i]
      const p = sigmoid(b0 + b1 * xi)
      const resid = ds.a[i] - p
      const wgt = p * (1 - p)
      g0 += resid
      g1 += resid * xi
      h00 += wgt
      h01 += wgt * xi
      h11 += wgt * xi * xi
    }
    const det = h00 * h11 - h01 * h01
    if (!Number.isFinite(det) || Math.abs(det) < 1e-12) break
    const d0 = (h11 * g0 - h01 * g1) / det
    const d1 = (h00 * g1 - h01 * g0) / det
    b0 += d0
    b1 += d1
    if (Math.abs(d0) + Math.abs(d1) < 1e-8) break
  }
  return [b0, b1]
}

/** Solve a small dense system with partial pivoting. */
function solve(A: number[][], b: number[]): number[] {
  const n = b.length
  const M = A.map((row, i) => [...row, b[i]])
  for (let c = 0; c < n; c++) {
    let piv = c
    for (let r = c + 1; r < n; r++) if (Math.abs(M[r][c]) > Math.abs(M[piv][c])) piv = r
    ;[M[c], M[piv]] = [M[piv], M[c]]
    const d = M[c][c] || 1e-12
    for (let r = c + 1; r < n; r++) {
      const f = M[r][c] / d
      for (let k = c; k <= n; k++) M[r][k] -= f * M[c][k]
    }
  }
  const out = new Array<number>(n).fill(0)
  for (let r = n - 1; r >= 0; r--) {
    let s = M[r][n]
    for (let k = r + 1; k < n; k++) s -= M[r][k] * out[k]
    out[r] = s / (M[r][r] || 1e-12)
  }
  return out
}

/** Ridge (α = 1, intercept unpenalized) of R on [1, X, A, A·X]. */
export function fitOutcome(ds: Dataset): number[] {
  const XtX = [0, 1, 2, 3].map(() => [0, 0, 0, 0])
  const Xty = [0, 0, 0, 0]
  const f = [0, 0, 0, 0]
  for (let i = 0; i < ds.n; i++) {
    const xi = ds.x[i]
    const ai = ds.a[i]
    f[0] = 1
    f[1] = xi
    f[2] = ai
    f[3] = ai * xi
    for (let j = 0; j < 4; j++) {
      Xty[j] += f[j] * ds.r[i]
      for (let k = 0; k < 4; k++) XtX[j][k] += f[j] * f[k]
    }
  }
  for (let j = 1; j < 4; j++) XtX[j][j] += RIDGE_ALPHA
  return solve(XtX, Xty)
}

const qHat = (beta: number[], x: number, a: number) => beta[0] + beta[1] * x + beta[2] * a + beta[3] * a * x

/** Importance weights w = 1[A = πₑ(X)] / p̂(A|X), with p̂ clipped to [0.01, 0.99]. */
export function importanceWeights(ds: Dataset, prop: [number, number]) {
  const w = new Float64Array(ds.n)
  let pMin = 1
  let pMax = 0
  for (let i = 0; i < ds.n; i++) {
    const p1 = Math.min(P_CLIP_HI, Math.max(P_CLIP_LO, sigmoid(prop[0] + prop[1] * ds.x[i])))
    if (p1 < pMin) pMin = p1
    if (p1 > pMax) pMax = p1
    if (ds.a[i] === ds.piE[i]) w[i] = 1 / (ds.a[i] === 1 ? p1 : 1 - p1)
  }
  return { w, pMin, pMax }
}

export function estimateAll(ds: Dataset): PointResult {
  const prop = fitPropensity(ds)
  const beta = fitOutcome(ds)
  const { w, pMin, pMax } = importanceWeights(ds, prop)
  const n = ds.n

  let treatedSum = 0
  let treatedN = 0
  let replaySum = 0
  let replayN = 0
  let dmSum = 0
  let ipwSum = 0
  let wSum = 0
  let w2Sum = 0
  let maxW = 0
  let drSum = 0
  let rMin = Infinity
  let rMax = -Infinity

  for (let i = 0; i < n; i++) {
    const xi = ds.x[i]
    const ai = ds.a[i]
    const ri = ds.r[i]
    const target = ds.piE[i]
    const wi = w[i]
    if (ri < rMin) rMin = ri
    if (ri > rMax) rMax = ri
    if (ai === 1) {
      treatedSum += ri
      treatedN++
    }
    if (ai === target) {
      replaySum += ri
      replayN++
    }
    const qTarget = qHat(beta, xi, target)
    dmSum += qTarget
    ipwSum += wi * ri
    wSum += wi
    w2Sum += wi * wi
    if (wi > maxW) maxW = wi
    drSum += qTarget + wi * (ri - qHat(beta, xi, ai))
  }

  const snipwRaw = wSum > 0 ? ipwSum / wSum : Number.NaN
  const ess = w2Sum > 0 ? (wSum * wSum) / w2Sum : 0

  return {
    estimates: {
      naive: treatedN > 0 ? treatedSum / treatedN : Number.NaN,
      replay: replayN > 0 ? replaySum / replayN : Number.NaN,
      dm: dmSum / n,
      ipw: ipwSum / n,
      snipw: Number.isNaN(snipwRaw) ? snipwRaw : Math.min(rMax, Math.max(rMin, snipwRaw)),
      dr: drSum / n,
    },
    health: { ess, essPct: n > 0 ? ess / n : 0, maxW, matched: replayN, pMin, pMax },
  }
}
