import type { ReactNode } from 'react'
import { cn } from '../ui/cn'
import { TAB_BY_ID, type TabId } from './tabs'

/** Colorful, animated page header. Each tab gets its own accent. */
export default function PageHeader({ tab, eyebrow, title, lead, children }: { tab: TabId; eyebrow: string; title: ReactNode; lead?: ReactNode; children?: ReactNode }) {
  const t = TAB_BY_ID[tab]
  const Icon = t.icon
  return (
    <header className={cn('relative isolate overflow-hidden rounded-2xl border-thin border-line bg-linear-to-br via-surface to-surface p-xl md:p-3xl', t.accent.from)}>
      <span aria-hidden className={cn('absolute -top-24 -right-16 -z-10 size-72 animate-float rounded-full opacity-25 blur-3xl', t.accent.blob)} />
      <span aria-hidden className={cn('absolute right-1/3 -bottom-32 -z-10 size-64 animate-float-slow rounded-full opacity-15 blur-3xl', t.accent.blob2)} />
      <div className="flex max-w-prose flex-col gap-lg">
        <span className={cn('inline-flex items-center gap-sm self-start rounded-full px-md py-xs text-caption font-semibold tracking-wider uppercase', t.accent.soft, t.accent.ink)}>
          <Icon size={14} aria-hidden />
          {eyebrow}
        </span>
        <p id="page-title" role="heading" aria-level={1} tabIndex={-1} className="font-display text-h1 font-semibold text-balance text-fg outline-none">
          {title}
        </p>
        {lead && <p className="text-lead text-pretty text-fg-muted">{lead}</p>}
        {children}
      </div>
    </header>
  )
}
