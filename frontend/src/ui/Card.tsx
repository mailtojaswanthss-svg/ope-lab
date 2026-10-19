import type { ReactNode } from 'react'
import { cn } from './cn'

type Variant = 'default' | 'sunken' | 'stage'

const VARIANTS: Record<Variant, string> = {
  default: 'border-thin border-line bg-surface shadow-sm',
  sunken: 'bg-surface-sunken',
  stage: 'bg-linear-to-br from-stage to-stage-deep text-stage-fg shadow-lg',
}

export default function Card({ children, variant = 'default', className }: { children: ReactNode; variant?: Variant; className?: string }) {
  return <div className={cn('rounded-xl p-xl', VARIANTS[variant], className)}>{children}</div>
}

export function CardTitle({ children, className, onStage }: { children: ReactNode; className?: string; onStage?: boolean }) {
  return (
    <p role="heading" aria-level={3} className={cn('text-h3 font-semibold', onStage ? 'text-stage-fg' : 'text-fg', className)}>
      {children}
    </p>
  )
}
