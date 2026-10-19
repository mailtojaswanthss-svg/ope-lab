import { FlaskConical, Moon, Sun } from 'lucide-react'
import Button, { IconButton } from '../ui/Button'
import FlutedGlass from '../ui/FlutedGlass'
import { cn } from '../ui/cn'
import { useTheme } from '../ui/theme'
import { useNav } from './nav'
import { TABS } from './tabs'

export default function TopBar() {
  const { tab, go } = useNav()
  const { theme, toggleTheme } = useTheme()

  return (
    <header className="sticky top-0 z-40 border-b-thin border-line bg-canvas/80 backdrop-blur-lg">
      <div className="mx-auto flex h-16 max-w-content items-center gap-lg px-lg md:px-xl">
        <button type="button" onClick={() => go('home')} className="flex cursor-pointer items-center gap-sm rounded-md" aria-label="OPE Lab home">
          <FlutedGlass as="span" size="sm" scrim="none" className="flex size-9 items-center justify-center rounded-lg shadow-md">
            <FlaskConical size={18} aria-hidden />
          </FlutedGlass>
          <span className="font-display text-h3 font-bold text-fg">OPE Lab</span>
        </button>

        <nav aria-label="Sections" className="ml-lg hidden flex-1 items-center gap-2xs lg:flex">
          {TABS.filter((t) => t.id !== 'home').map((t) => {
            const active = tab === t.id
            const Icon = t.icon
            return (
              <button
                key={t.id}
                type="button"
                aria-current={active ? 'page' : undefined}
                onClick={() => go(t.id)}
                className={cn(
                  'inline-flex h-9 cursor-pointer items-center gap-sm rounded-full px-md text-small font-semibold transition-ds',
                  active ? cn(t.accent.soft, t.accent.ink) : 'text-fg-muted hover:bg-surface-muted hover:text-fg',
                )}
              >
                <Icon size={16} aria-hidden />
                {t.label}
              </button>
            )
          })}
        </nav>

        <div className="ml-auto flex items-center gap-sm">
          <IconButton
            label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            onClick={toggleTheme}
            icon={theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          />
          {tab !== 'lab' && (
            <Button size="sm" className="hidden sm:inline-flex" onClick={() => go('lab')} iconStart={<FlaskConical size={16} />}>
              Open the Lab
            </Button>
          )}
        </div>
      </div>
    </header>
  )
}
