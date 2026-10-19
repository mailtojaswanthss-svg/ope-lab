import { Suspense } from 'react'
import { OpeProvider } from './ope/OpeProvider'
import { ThemeProvider } from './ui/theme'
import BottomNav from './app/BottomNav'
import TopBar from './app/TopBar'
import { NavProvider, useNav } from './app/nav'
import type { TabId } from './app/tabs'
import Estimators from './pages/Estimators'
import Home from './pages/Home'
import Lab from './pages/Lab'
import RealData from './pages/RealData'
import Story from './pages/Story'
import Studies from './pages/Studies'
import Team from './pages/Team'

const PAGES: Record<TabId, () => React.JSX.Element> = {
  home: Home,
  story: Story,
  estimators: Estimators,
  lab: Lab,
  studies: Studies,
  'real-data': RealData,
  team: Team,
}

function Shell() {
  const { tab } = useNav()
  const Page = PAGES[tab]
  return (
    <div className="min-h-svh bg-canvas font-body text-fg">
      <TopBar />
      <main key={tab} className="mx-auto max-w-content animate-page-in px-lg pt-xl pb-4xl md:px-xl md:pt-2xl lg:pb-section">
        <Suspense>
          <Page />
        </Suspense>
      </main>
      <footer className="mx-auto hidden max-w-content px-xl pb-2xl text-caption text-fg-subtle lg:block">
        OPE Lab · Perceptron Hackathon 2026 · Simulated data for demonstration.
      </footer>
      <BottomNav />
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <OpeProvider>
        <NavProvider>
          <Shell />
        </NavProvider>
      </OpeProvider>
    </ThemeProvider>
  )
}
