import type { ReactNode } from 'react'
import FlutedGlass from '../ui/FlutedGlass'
import { TAB_BY_ID, type TabId } from './tabs'

/** Fluted-glass page header. Each tab has its own spectrum (--ds-gradient-<tab>). */
export default function PageHeader({ tab, eyebrow, title, lead, children }: { tab: TabId; eyebrow: string; title: ReactNode; lead?: ReactNode; children?: ReactNode }) {
  const Icon = TAB_BY_ID[tab].icon
  return (
    <FlutedGlass as="header" palette={tab} scrim="start" interactive drift className="animate-rise rounded-2xl p-xl shadow-lg md:px-3xl md:py-4xl">
      <div className="flex max-w-prose flex-col gap-lg">
        <span className="inline-flex items-center gap-sm self-start rounded-full border-thin border-glass-line bg-glass px-md py-xs text-caption font-semibold tracking-wider text-on-flute uppercase backdrop-blur-md">
          <Icon size={14} aria-hidden />
          {eyebrow}
        </span>
        <p id="page-title" role="heading" aria-level={1} tabIndex={-1} className="ds-text-glow font-body text-h1 font-bold tracking-tight text-balance text-on-flute outline-none">
          {title}
        </p>
        {lead && <p className="ds-text-glow text-lead text-pretty text-on-flute-muted">{lead}</p>}
        {children}
      </div>
    </FlutedGlass>
  )
}
