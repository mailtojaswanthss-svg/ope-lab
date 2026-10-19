import { useId } from 'react'
import { ChevronDown } from 'lucide-react'

export default function Select({
  label,
  description,
  value,
  options,
  onChange,
}: {
  label: string
  description?: string
  value: string
  options: { value: string; label: string }[]
  onChange: (value: string) => void
}) {
  const id = useId()
  return (
    <div className="flex flex-col gap-xs">
      <label htmlFor={id} className="text-small font-semibold text-fg">
        {label}
      </label>
      <div className="relative">
        <select
          id={id}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          aria-describedby={description ? `${id}-d` : undefined}
          className="h-11 w-full cursor-pointer appearance-none rounded-md border-thin border-line-strong bg-surface pr-3xl pl-md text-body text-fg transition-ds hover:border-primary"
        >
          {options.map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
        <ChevronDown size={16} aria-hidden className="pointer-events-none absolute top-1/2 right-md -translate-y-1/2 text-fg-muted" />
      </div>
      {description && (
        <p id={`${id}-d`} className="text-caption text-fg-muted">
          {description}
        </p>
      )}
    </div>
  )
}
