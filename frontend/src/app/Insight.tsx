import type { ReactNode } from 'react'
import { Lightbulb } from 'lucide-react'
import { cn } from '../ui/cn'

/** The "aha" line. Orange is reserved for insights and the truth. */
export default function Insight({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div role="note" className={cn('relative flex items-start gap-lg overflow-hidden rounded-xl border-thin border-line bg-surface p-xl shadow-sm', className)}>
      <span aria-hidden className="absolute inset-y-0 left-0 w-1.5 bg-linear-to-b from-orange to-pink" />
      <span className="flex size-10 shrink-0 items-center justify-center rounded-full bg-orange-soft text-orange-ink">
        <Lightbulb size={20} aria-hidden />
      </span>
      <div className="text-body text-pretty text-fg">{children}</div>
    </div>
  )
}
