import type { EstimateMap, EstimatorKey, PointResult } from './estimators.ts'
import { ESTIMATORS } from './meta.ts'
import { fmt, fmtSigned } from './format.ts'
import { V_STAR } from './simulate.ts'

const CONTENDERS = ESTIMATORS.filter((e) => e.key !== 'naive')

/** Corrected (non-Naive) estimator closest to the truth. */
export function closestContender(estimates: EstimateMap): EstimatorKey | null {
  let best: EstimatorKey | null = null
  for (const e of CONTENDERS) {
    const err = Math.abs(estimates[e.key] - V_STAR)
    if (Number.isFinite(err) && (best === null || err < Math.abs(estimates[best] - V_STAR))) best = e.key
  }
  return best
}

export function labInsight(point: PointResult) {
  const naiveErr = point.estimates.naive - V_STAR
  const best = closestContender(point.estimates)
  const bestMeta = ESTIMATORS.find((e) => e.key === best)
  const bestErr = best ? Math.abs(point.estimates[best] - V_STAR) : Number.NaN
  const naivePart =
    Math.abs(naiveErr) < 0.02
      ? `Naive happens to land close this time (${fmtSigned(naiveErr)}).`
      : `Naive ${naiveErr > 0 ? 'overshoots' : 'undershoots'} the truth by ${fmtSigned(naiveErr)}: it credits the policy for who it treated.`
  const bestPart = bestMeta ? ` ${bestMeta.name} lands within ${fmt(bestErr)} of the truth.` : ''
  const essPart = point.health.essPct < 0.1 ? ' Careful: the effective sample size has collapsed below 10% of N.' : ''
  return naivePart + bestPart + essPart
}
