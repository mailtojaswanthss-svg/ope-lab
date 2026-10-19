import { simulate, V_STAR } from './simulate.ts'
import { ESTIMATOR_KEYS, estimateAll, type EstimatorKey } from './estimators.ts'

export interface FailureStudyResult {
  n: number
  cs: number[]
  /** Mean absolute error per estimator, aligned with `cs`. */
  errors: Record<EstimatorKey, number[]>
}

export const FAILURE_SEEDS = 5

export function runFailureStudy(opts: { n: number; overlap: number; noise: number; seed: number }): FailureStudyResult {
  const n = Math.min(opts.n, 5000)
  const cs = Array.from({ length: 11 }, (_, i) => i / 10)
  const errors = Object.fromEntries(ESTIMATOR_KEYS.map((k) => [k, [] as number[]])) as Record<EstimatorKey, number[]>

  for (const c of cs) {
    const sums = Object.fromEntries(ESTIMATOR_KEYS.map((k) => [k, 0])) as Record<EstimatorKey, number>
    for (let s = 0; s < FAILURE_SEEDS; s++) {
      const ds = simulate({ n, confounding: c, overlap: opts.overlap, noise: opts.noise, seed: opts.seed + s })
      const est = estimateAll(ds).estimates
      for (const k of ESTIMATOR_KEYS) sums[k] += Math.abs(est[k] - V_STAR)
    }
    for (const k of ESTIMATOR_KEYS) errors[k].push(sums[k] / FAILURE_SEEDS)
  }
  return { n, cs, errors }
}

export const DECISION_CONFOUNDING = [0, 0.4, 0.8]
export const DECISION_OVERLAP = [0.2, 0.5, 0.9]
export const DECISION_REPS = 20
export const DECISION_N = 2000

export interface DecisionCell {
  confounding: number
  overlap: number
  rmse: Record<EstimatorKey, number>
  winner: EstimatorKey
  runnerUp: EstimatorKey
  tie: boolean
}

export interface DecisionMapResult {
  /** cells[row = confounding][col = overlap] */
  cells: DecisionCell[][]
}

const CONTENDERS = ESTIMATOR_KEYS.filter((k) => k !== 'naive')

export function runDecisionMap(opts: { noise: number; seed: number }): DecisionMapResult {
  const cells = DECISION_CONFOUNDING.map((c) =>
    DECISION_OVERLAP.map((o): DecisionCell => {
      const sq = Object.fromEntries(ESTIMATOR_KEYS.map((k) => [k, [] as number[]])) as Record<EstimatorKey, number[]>
      for (let rep = 0; rep < DECISION_REPS; rep++) {
        const ds = simulate({ n: DECISION_N, confounding: c, overlap: o, noise: opts.noise, seed: opts.seed + rep })
        const est = estimateAll(ds).estimates
        for (const k of ESTIMATOR_KEYS) sq[k].push((est[k] - V_STAR) ** 2)
      }
      const rmse = Object.fromEntries(
        ESTIMATOR_KEYS.map((k) => [k, Math.sqrt(sq[k].reduce((s, v) => s + v, 0) / DECISION_REPS)]),
      ) as Record<EstimatorKey, number>

      const [winner, runnerUp] = [...CONTENDERS].sort((p, q) => rmse[p] - rmse[q])
      // Paired test on squared errors: is the runner-up distinguishable from the winner?
      const d = sq[runnerUp].map((v, i) => v - sq[winner][i])
      const mean = d.reduce((s, v) => s + v, 0) / d.length
      const sd = Math.sqrt(d.reduce((s, v) => s + (v - mean) ** 2, 0) / Math.max(1, d.length - 1))
      const se = sd / Math.sqrt(d.length)
      return { confounding: c, overlap: o, rmse, winner, runnerUp, tie: mean < 1.96 * se }
    }),
  )
  return { cells }
}
