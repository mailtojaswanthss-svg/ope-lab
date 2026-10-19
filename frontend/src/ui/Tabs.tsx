import { useRef, type KeyboardEvent, type ReactNode } from 'react'
import { cn } from './cn'

export interface TabItem<T extends string> {
  id: T
  label: string
  icon?: ReactNode
}

interface TabsProps<T extends string> {
  items: TabItem<T>[]
  value: T
  onChange: (id: T) => void
  label: string
  idPrefix: string
  className?: string
}

/** Segmented tab list (WAI-ARIA tabs, arrow-key navigation). Pair with <TabPanel>. */
export default function Tabs<T extends string>({ items, value, onChange, label, idPrefix, className }: TabsProps<T>) {
  const refs = useRef<(HTMLButtonElement | null)[]>([])
  const onKey = (e: KeyboardEvent, i: number) => {
    const delta = e.key === 'ArrowRight' ? 1 : e.key === 'ArrowLeft' ? -1 : 0
    const jump = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : null
    if (!delta && jump === null) return
    e.preventDefault()
    const next = jump ?? (i + delta + items.length) % items.length
    onChange(items[next].id)
    refs.current[next]?.focus()
  }
  return (
    <div role="tablist" aria-label={label} className={cn('inline-flex max-w-full gap-2xs overflow-x-auto rounded-full bg-surface-sunken p-xs', className)}>
      {items.map((t, i) => {
        const active = t.id === value
        return (
          <button
            key={t.id}
            ref={(el) => {
              refs.current[i] = el
            }}
            type="button"
            role="tab"
            id={`${idPrefix}-tab-${t.id}`}
            aria-selected={active}
            aria-controls={`${idPrefix}-panel-${t.id}`}
            tabIndex={active ? 0 : -1}
            onClick={() => onChange(t.id)}
            onKeyDown={(e) => onKey(e, i)}
            className={cn(
              'inline-flex h-9 shrink-0 cursor-pointer items-center gap-sm rounded-full px-lg text-small font-semibold whitespace-nowrap transition-ds',
              active ? 'bg-surface text-fg shadow-sm' : 'text-fg-muted hover:text-fg',
            )}
          >
            {t.icon}
            {t.label}
          </button>
        )
      })}
    </div>
  )
}

export function TabPanel({ idPrefix, id, children, className }: { idPrefix: string; id: string; children: ReactNode; className?: string }) {
  return (
    <div role="tabpanel" id={`${idPrefix}-panel-${id}`} aria-labelledby={`${idPrefix}-tab-${id}`} className={cn('animate-page-in', className)}>
      {children}
    </div>
  )
}
