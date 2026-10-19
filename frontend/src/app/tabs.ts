import { Compass, Database, FlaskConical, Home, LineChart, Scale, Users, type LucideIcon } from 'lucide-react'
import type { Tone } from '../ui/Badge'

export type TabId = 'home' | 'story' | 'estimators' | 'lab' | 'studies' | 'real-data' | 'team'

export interface Accent {
  tone: Tone
  soft: string
  ink: string
  solid: string
  from: string
  blob: string
  blob2: string
}

export interface AppTab {
  id: TabId
  label: string
  short: string
  icon: LucideIcon
  blurb: string
  accent: Accent
}

// Literal class strings so Tailwind can see every accent combination.
const A = {
  primary: { tone: 'primary', soft: 'bg-primary-soft', ink: 'text-primary-ink', solid: 'bg-primary', from: 'from-primary-soft', blob: 'bg-primary', blob2: 'bg-pink' },
  orange: { tone: 'orange', soft: 'bg-orange-soft', ink: 'text-orange-ink', solid: 'bg-orange', from: 'from-orange-soft', blob: 'bg-orange', blob2: 'bg-yellow' },
  blue: { tone: 'blue', soft: 'bg-blue-soft', ink: 'text-blue-ink', solid: 'bg-blue', from: 'from-blue-soft', blob: 'bg-blue', blob2: 'bg-primary' },
  teal: { tone: 'teal', soft: 'bg-teal-soft', ink: 'text-teal-ink', solid: 'bg-teal', from: 'from-teal-soft', blob: 'bg-teal', blob2: 'bg-blue' },
  pink: { tone: 'pink', soft: 'bg-pink-soft', ink: 'text-pink-ink', solid: 'bg-pink', from: 'from-pink-soft', blob: 'bg-pink', blob2: 'bg-primary' },
  yellow: { tone: 'yellow', soft: 'bg-yellow-soft', ink: 'text-yellow-ink', solid: 'bg-yellow', from: 'from-yellow-soft', blob: 'bg-yellow', blob2: 'bg-orange' },
  green: { tone: 'green', soft: 'bg-green-soft', ink: 'text-green-ink', solid: 'bg-green', from: 'from-green-soft', blob: 'bg-green', blob2: 'bg-teal' },
} satisfies Record<string, Accent>

export const TABS: AppTab[] = [
  { id: 'home', label: 'Home', short: 'Home', icon: Home, blurb: 'The big question in one screen.', accent: A.primary },
  { id: 'story', label: 'The story', short: 'Story', icon: Compass, blurb: 'Why raw data fools you, in three short chapters.', accent: A.orange },
  { id: 'estimators', label: 'Estimators', short: 'Methods', icon: Scale, blurb: 'Meet the six ways to guess the other world.', accent: A.blue },
  { id: 'lab', label: 'Lab', short: 'Lab', icon: FlaskConical, blurb: 'Simulate a world and watch every estimator guess.', accent: A.teal },
  { id: 'studies', label: 'Studies', short: 'Studies', icon: LineChart, blurb: 'Stress tests: confounding, regimes and robustness.', accent: A.pink },
  { id: 'real-data', label: 'Real data', short: 'Data', icon: Database, blurb: 'How to run it on the Open Bandit Dataset.', accent: A.yellow },
  { id: 'team', label: 'Team', short: 'Team', icon: Users, blurb: 'Who built OPE Lab.', accent: A.green },
]

export const TAB_BY_ID = Object.fromEntries(TABS.map((t) => [t.id, t])) as Record<TabId, AppTab>
