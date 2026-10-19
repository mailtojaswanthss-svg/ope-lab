import { useTween } from './motion'

/** Counts smoothly to `value` whenever it changes. */
export default function AnimatedNumber({ value, format }: { value: number; format: (v: number) => string }) {
  const v = useTween(value)
  return <span className="tabular-nums">{format(v)}</span>
}
