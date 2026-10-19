import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from 'react'
import { TABS, type TabId } from './tabs'

const IDS = TABS.map((t) => t.id)

function readHash(): TabId {
  const h = window.location.hash.replace(/^#\/?/, '')
  return (IDS as string[]).includes(h) ? (h as TabId) : 'home'
}

const NavContext = createContext<{ tab: TabId; go: (id: TabId) => void } | null>(null)

/** Hash-based tabs (#/lab) so every view is linkable and the back button works. */
export function NavProvider({ children }: { children: ReactNode }) {
  const [tab, setTab] = useState<TabId>(readHash)

  useEffect(() => {
    const onHash = () => setTab(readHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    window.scrollTo({ top: 0 })
    // Move focus to the new page's heading for keyboard and screen-reader users.
    const frame = requestAnimationFrame(() => document.getElementById('page-title')?.focus({ preventScroll: true }))
    return () => cancelAnimationFrame(frame)
  }, [tab])

  const go = useCallback((id: TabId) => {
    if (readHash() === id) setTab(id)
    else window.location.hash = `/${id}`
  }, [])

  return <NavContext.Provider value={{ tab, go }}>{children}</NavContext.Provider>
}

export function useNav() {
  const ctx = useContext(NavContext)
  if (!ctx) throw new Error('useNav must be used inside <NavProvider>')
  return ctx
}
