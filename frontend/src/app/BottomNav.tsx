import { cn } from '../ui/cn'
import { useNav } from './nav'
import { TABS } from './tabs'

/** < lg: thumb-friendly tab bar. */
export default function BottomNav() {
  const { tab, go } = useNav()
  return (
    <nav aria-label="Sections" className="fixed inset-x-0 bottom-0 z-40 border-t-thin border-line bg-surface/90 pb-[env(safe-area-inset-bottom)] backdrop-blur-lg lg:hidden">
      <ul className="mx-auto grid max-w-content grid-cols-7">
        {TABS.map((t) => {
          const active = tab === t.id
          const Icon = t.icon
          return (
            <li key={t.id}>
              <button
                type="button"
                aria-current={active ? 'page' : undefined}
                onClick={() => go(t.id)}
                className={cn('flex w-full cursor-pointer flex-col items-center gap-2xs py-sm transition-ds', active ? t.accent.ink : 'text-fg-subtle hover:text-fg')}
              >
                <span className={cn('flex h-7 w-12 items-center justify-center rounded-full transition-ds', active && t.accent.soft)}>
                  <Icon size={18} aria-hidden />
                </span>
                <span className="text-caption font-semibold">{t.short}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
