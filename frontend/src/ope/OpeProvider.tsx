import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { estimateAll, type PointResult } from './estimators.ts'
import { simulate, type SimParams } from './simulate.ts'

export interface LabParams {
  confounding: number
  overlap: number
  noise: number
  n: number
  b: number
  seed: number
}

export type PresetId = 'easy' | 'overlap' | 'confounder' | 'custom'

export const PRESETS: { id: Exclude<PresetId, 'custom'>; label: string; description: string; confounding: number; overlap: number }[] = [
  { id: 'easy', label: 'Easy case', description: 'No hidden confounding, generous overlap (c 0.0 · overlap 0.9)', confounding: 0, overlap: 0.9 },
  { id: 'overlap', label: 'Low overlap', description: 'Near-deterministic logging policy (c 0.0 · overlap 0.1)', confounding: 0, overlap: 0.1 },
  { id: 'confounder', label: 'Hidden confounder', description: 'U drives who gets treated (c 0.8 · overlap 0.8)', confounding: 0.8, overlap: 0.8 },
]

export const DEFAULT_PARAMS: LabParams = { confounding: 0.5, overlap: 0.7, noise: 0.3, n: 5000, b: 100, seed: 42 }

interface OpeContextValue {
  params: LabParams
  setParam: <K extends keyof LabParams>(key: K, value: LabParams[K]) => void
  applyPreset: (id: PresetId) => void
  presetId: PresetId
  reroll: () => void
  /** Debounced simulation parameters used by every computation. */
  sim: SimParams
  b: number
  point: PointResult
  settling: boolean
}

const OpeContext = createContext<OpeContextValue | null>(null)

const approx = (p: number, q: number) => Math.abs(p - q) < 1e-9

function useDebounced<T>(value: T, ms: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = window.setTimeout(() => setDebounced(value), ms)
    return () => window.clearTimeout(t)
  }, [value, ms])
  return debounced
}

export function OpeProvider({ children }: { children: ReactNode }) {
  const [params, setParams] = useState<LabParams>(DEFAULT_PARAMS)

  const setParam = useCallback(<K extends keyof LabParams>(key: K, value: LabParams[K]) => {
    setParams((p) => ({ ...p, [key]: value }))
  }, [])

  const applyPreset = useCallback((id: PresetId) => {
    const preset = PRESETS.find((p) => p.id === id)
    if (!preset) return
    // Matches the Python app: presets also reset N and noise.
    setParams((p) => ({ ...p, confounding: preset.confounding, overlap: preset.overlap, n: 5000, noise: 0.3 }))
  }, [])

  const reroll = useCallback(() => {
    setParams((p) => ({ ...p, seed: 1000 + Math.floor(Math.random() * 99000) }))
  }, [])

  const presetId: PresetId =
    PRESETS.find(
      (p) => approx(p.confounding, params.confounding) && approx(p.overlap, params.overlap) && params.n === 5000 && approx(params.noise, 0.3),
    )?.id ?? 'custom'

  const debounced = useDebounced(params, 150)
  const sim = useMemo<SimParams>(
    () => ({ n: debounced.n, confounding: debounced.confounding, overlap: debounced.overlap, noise: debounced.noise, seed: debounced.seed }),
    [debounced.n, debounced.confounding, debounced.overlap, debounced.noise, debounced.seed],
  )
  const point = useMemo(() => estimateAll(simulate(sim)), [sim])

  const value: OpeContextValue = {
    params,
    setParam,
    applyPreset,
    presetId,
    reroll,
    sim,
    b: debounced.b,
    point,
    settling: debounced !== params,
  }

  return <OpeContext.Provider value={value}>{children}</OpeContext.Provider>
}

export function useOpe() {
  const ctx = useContext(OpeContext)
  if (!ctx) throw new Error('useOpe must be used inside <OpeProvider>')
  return ctx
}
