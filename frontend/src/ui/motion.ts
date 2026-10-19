import { useEffect, useRef, useState } from 'react'

const REDUCED = '(prefers-reduced-motion: reduce)'

export function usePrefersReducedMotion() {
  const [reduced, setReduced] = useState(() => typeof window !== 'undefined' && window.matchMedia(REDUCED).matches)
  useEffect(() => {
    const mq = window.matchMedia(REDUCED)
    const onChange = () => setReduced(mq.matches)
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])
  return reduced
}

/** Eases every number in `target` from its previous value (ease-out cubic). */
export function useTweenArray(target: number[], duration = 650): number[] {
  const reduced = usePrefersReducedMotion()
  const [value, setValue] = useState(target)
  const current = useRef(target)
  const key = target.map((v) => (Number.isFinite(v) ? v.toFixed(6) : 'x')).join('|')

  useEffect(() => {
    const from = current.current
    if (reduced || from.length !== target.length) {
      current.current = target
      setValue(target)
      return
    }
    const start = performance.now()
    let raf = 0
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const e = 1 - (1 - t) ** 3
      const next = target.map((v, i) => (Number.isFinite(v) && Number.isFinite(from[i]) ? from[i] + (v - from[i]) * e : v))
      current.current = next
      setValue(next)
      if (t < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, reduced, duration])

  return value
}

export function useTween(target: number, duration?: number) {
  return useTweenArray([target], duration)[0]
}
