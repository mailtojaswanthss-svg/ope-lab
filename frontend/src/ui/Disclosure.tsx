import { useId, useState, type ReactNode } from 'react'
import { ChevronDown } from 'lucide-react'
import { cn } from './cn'

/** Progressive disclosure with an animated height transition. */
export default function Disclosure({
  title,
  hint,
  icon,
  defaultOpen = false,
  children,
  className,
}: {
  title: string
  hint?: string
  icon?: ReactNode
  defaultOpen?: boolean
  children: ReactNode
  className?: string
}) {
  const [open, setOpen] = useState(defaultOpen)
  const id = useId()
  return (
    <div className={className}>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => setOpen((o) => !o)}
        className="flex w-full cursor-pointer items-center gap-md rounded-md text-left transition-ds hover:text-primary-ink"
      >
        {icon}
        <span className="flex flex-1 flex-col">
          <span className="text-small font-semibold text-fg">{title}</span>
          {hint && <span className="text-caption text-fg-muted">{hint}</span>}
        </span>
        <ChevronDown size={16} aria-hidden className={cn('shrink-0 text-fg-muted transition-ds', open && 'rotate-180')} />
      </button>
      <div id={id} className="ds-collapse" data-open={open} inert={!open}>
        <div>
          <div className="pt-lg">{children}</div>
        </div>
      </div>
    </div>
  )
}
