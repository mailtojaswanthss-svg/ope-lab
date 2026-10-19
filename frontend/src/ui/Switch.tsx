import { useId } from 'react'
import { cn } from './cn'

export default function Switch({
  label,
  description,
  checked,
  onChange,
}: {
  label: string
  description?: string
  checked: boolean
  onChange: (checked: boolean) => void
}) {
  const id = useId()
  return (
    <div className="flex items-start justify-between gap-lg">
      <div className="flex flex-col gap-2xs">
        <span id={`${id}-l`} className="text-small font-semibold text-fg">
          {label}
        </span>
        {description && (
          <span id={`${id}-d`} className="text-caption text-fg-muted">
            {description}
          </span>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-labelledby={`${id}-l`}
        aria-describedby={description ? `${id}-d` : undefined}
        onClick={() => onChange(!checked)}
        className={cn('relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full transition-ds', checked ? 'bg-primary' : 'bg-line-strong')}
      >
        <span aria-hidden className={cn('ml-0.5 size-5 rounded-full bg-surface shadow-sm transition-ds', checked && 'translate-x-5')} />
      </button>
    </div>
  )
}
