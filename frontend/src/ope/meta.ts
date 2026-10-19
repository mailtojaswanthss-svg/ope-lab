import type { EstimatorKey } from './estimators.ts'

export type MarkerShape = 'cross' | 'triangle' | 'square' | 'diamond' | 'pentagon' | 'circle'

export interface EstimatorMeta {
  key: EstimatorKey
  name: string
  longName: string
  marker: MarkerShape
  /** Literal class names so Tailwind can see them. */
  fill: string
  stroke: string
  bg: string
  blurb: string
  formula: string
  failsWhen: string
}

export const ESTIMATORS: EstimatorMeta[] = [
  {
    key: 'naive',
    name: 'Naive',
    longName: 'Naive observational',
    marker: 'cross',
    fill: 'fill-est-naive',
    stroke: 'stroke-est-naive',
    bg: 'bg-est-naive',
    blurb: 'Average the reward of everyone the old policy treated, and call it the new policy’s value.',
    formula: 'mean( R | A = 1 )',
    failsWhen: 'treatment was targeted. It measures who got treated, not what treatment does.',
  },
  {
    key: 'replay',
    name: 'Replay',
    longName: 'Replay (matched rows)',
    marker: 'triangle',
    fill: 'fill-est-replay',
    stroke: 'stroke-est-replay',
    bg: 'bg-est-replay',
    blurb: 'Keep only the rows where the old policy happened to agree with the new one, then average.',
    formula: 'mean( R | A = πₑ(X) )',
    failsWhen: 'the agreeing rows are not representative of everyone the new policy would serve.',
  },
  {
    key: 'dm',
    name: 'DM',
    longName: 'Direct method',
    marker: 'square',
    fill: 'fill-est-dm',
    stroke: 'stroke-est-dm',
    bg: 'bg-est-dm',
    blurb: 'Fit a reward model q̂(x, a), then ask it what the new policy would earn on every row.',
    formula: 'mean( q̂(X, πₑ(X)) )',
    failsWhen: 'the reward model is misspecified or must extrapolate where the old policy never went.',
  },
  {
    key: 'ipw',
    name: 'IPW',
    longName: 'Inverse propensity weighting',
    marker: 'diamond',
    fill: 'fill-est-ipw',
    stroke: 'stroke-est-ipw',
    bg: 'bg-est-ipw',
    blurb: 'Reweight matching rows by 1 / p̂(A|X), so choices the old policy rarely made count for more.',
    formula: 'mean( 1[A = πₑ] · R / p̂(A|X) )',
    failsWhen: 'overlap is poor. A handful of huge weights dominate and the variance explodes.',
  },
  {
    key: 'snipw',
    name: 'SNIPW',
    longName: 'Self-normalized IPW',
    marker: 'pentagon',
    fill: 'fill-est-snipw',
    stroke: 'stroke-est-snipw',
    bg: 'bg-est-snipw',
    blurb: 'IPW divided by the total weight. Trades a sliver of bias for much steadier estimates.',
    formula: 'Σ w·R / Σ w',
    failsWhen: 'the effective sample size collapses, leaving only a few rows to carry the estimate.',
  },
  {
    key: 'dr',
    name: 'DR',
    longName: 'Doubly robust',
    marker: 'circle',
    fill: 'fill-est-dr',
    stroke: 'stroke-est-dr',
    bg: 'bg-est-dr',
    blurb: 'Start from the model’s guess, then correct it with weighted residuals. Right if either piece is right.',
    formula: 'mean( q̂(X, πₑ) + w·(R − q̂(X, A)) )',
    failsWhen: 'both the propensity and reward models are wrong, or a hidden confounder fools them both.',
  },
]

export const ESTIMATOR_BY_KEY = Object.fromEntries(ESTIMATORS.map((e) => [e.key, e])) as Record<EstimatorKey, EstimatorMeta>
