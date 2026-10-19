/**
 * Deterministic RNG for the in-browser lab.
 * mulberry32 for uniforms + Box–Muller for normals. Results match the Python
 * app statistically, not bit-for-bit (NumPy uses a different generator).
 */
export interface Rng {
  uniform(): number
  normal(): number
  int(maxExclusive: number): number
}

export function createRng(seed: number): Rng {
  let state = seed >>> 0
  let spare: number | null = null

  const uniform = () => {
    state = (state + 0x6d2b79f5) >>> 0
    let t = state
    t = Math.imul(t ^ (t >>> 15), t | 1)
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61)
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }

  const normal = () => {
    if (spare !== null) {
      const s = spare
      spare = null
      return s
    }
    let u = 0
    while (u <= Number.EPSILON) u = uniform()
    const v = uniform()
    const mag = Math.sqrt(-2 * Math.log(u))
    spare = mag * Math.sin(2 * Math.PI * v)
    return mag * Math.cos(2 * Math.PI * v)
  }

  return {
    uniform,
    normal,
    int: (maxExclusive: number) => Math.floor(uniform() * maxExclusive),
  }
}
