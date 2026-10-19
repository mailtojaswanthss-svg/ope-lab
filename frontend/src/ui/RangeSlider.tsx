import { useId } from 'react'
import * as Slider from '@radix-ui/react-slider'

interface RangeSliderProps {
  label: string
  description?: string
  value: number
  min: number
  max: number
  step: number
  onChange: (value: number) => void
  format?: (value: number) => string
  /** Low / high end captions under the track. */
  ends?: [string, string]
}

export default function RangeSlider({ label, description, value, min, max, step, onChange, format = (v) => v.toFixed(2), ends }: RangeSliderProps) {
  const labelId = useId()
  const descId = useId()
  return (
    <div className="flex flex-col gap-sm">
      <div className="flex items-baseline justify-between gap-md">
        <span id={labelId} className="text-small font-semibold text-fg">
          {label}
        </span>
        <span className="rounded-sm bg-primary-soft px-sm text-small font-semibold tabular-nums text-primary-ink">{format(value)}</span>
      </div>
      {description && (
        <p id={descId} className="text-caption text-fg-muted">
          {description}
        </p>
      )}
      <Slider.Root
        className="relative flex h-6 w-full touch-none select-none items-center"
        value={[value]}
        min={min}
        max={max}
        step={step}
        onValueChange={([v]) => onChange(Number((Math.round(v / step) * step).toFixed(6)))}
      >
        <Slider.Track className="relative h-1.5 grow overflow-hidden rounded-full bg-surface-sunken">
          <Slider.Range className="absolute h-full rounded-full bg-linear-to-r from-primary to-pink" />
        </Slider.Track>
        <Slider.Thumb
          aria-labelledby={labelId}
          aria-describedby={description ? descId : undefined}
          aria-valuetext={format(value)}
          className="block size-5 cursor-grab rounded-full border-thick border-primary bg-surface shadow-md transition-ds hover:scale-110 active:cursor-grabbing"
        />
      </Slider.Root>
      {ends && (
        <div className="flex justify-between text-caption text-fg-subtle">
          <span>{ends[0]}</span>
          <span>{ends[1]}</span>
        </div>
      )}
    </div>
  )
}
