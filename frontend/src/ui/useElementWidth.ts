import { useEffect, useRef, useState, type RefObject } from 'react'

/** Content-box width of an element, kept in sync with ResizeObserver. */
export function useElementWidth<T extends Element>(fallback = 640): [RefObject<T | null>, number] {
  const ref = useRef<T>(null)
  const [width, setWidth] = useState(fallback)
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new ResizeObserver(([entry]) => {
      const w = Math.round(entry.contentRect.width)
      if (w > 0) setWidth(w)
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])
  return [ref, width]
}
