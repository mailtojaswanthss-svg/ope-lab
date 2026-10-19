import { createRng } from './rng.ts'

export interface SimParams {
  n: number
  confounding: number
  overlap: number
  noise: number
  seed: number
}

export interface Dataset {
  n: number
  x: Float64Array
  a: Uint8Array
  r: Float64Array
  /** Target policy action πₑ(X) = 1[X > 0]. */
  piE: Uint8Array
}

/** True value of the target policy: 0.6 + 0.2·φ(0) = 0.6 + 0.2/√(2π). */
export const V_STAR = 0.6 + 0.2 / Math.sqrt(2 * Math.PI)

export const sigmoid = (z: number) => 1 / (1 + Math.exp(-z))

/** Logging-policy sharpness. Low overlap → steep, nearly deterministic π₀. */
export const overlapToSharpness = (overlap: number) => 0.5 + 5 * (1 - overlap)

export function simulate({ n, confounding, overlap, noise, seed }: SimParams): Dataset {
  const rng = createRng(seed)
  const L = overlapToSharpness(overlap)
  const x = new Float64Array(n)
  const a = new Uint8Array(n)
  const r = new Float64Array(n)
  const piE = new Uint8Array(n)

  for (let i = 0; i < n; i++) {
    const xi = rng.normal()
    const ui = rng.normal() // hidden confounder — never exposed to estimators
    const p0 = sigmoid(L * xi + 3 * confounding * ui)
    const ai = rng.uniform() < p0 ? 1 : 0
    const eps = rng.normal()
    x[i] = xi
    a[i] = ai
    r[i] = 0.5 + 0.3 * xi + ai * (0.2 + 0.2 * xi + 0.5 * ui) + 0.4 * ui + noise * eps
    piE[i] = xi > 0 ? 1 : 0
  }

  return { n, x, a, r, piE }
}

/** Row-resample (with replacement) for bootstrap replicates. */
export function resample(ds: Dataset, pick: (n: number) => number): Dataset {
  const { n } = ds
  const x = new Float64Array(n)
  const a = new Uint8Array(n)
  const r = new Float64Array(n)
  const piE = new Uint8Array(n)
  for (let i = 0; i < n; i++) {
    const j = pick(n)
    x[i] = ds.x[j]
    a[i] = ds.a[j]
    r[i] = ds.r[j]
    piE[i] = ds.piE[j]
  }
  return { n, x, a, r, piE }
}
