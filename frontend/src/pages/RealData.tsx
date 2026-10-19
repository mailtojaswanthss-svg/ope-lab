import type { CSSProperties } from 'react'
import { Database, Dices, LayoutGrid, MousePointerClick, Shirt, Sparkles, Terminal } from 'lucide-react'
import Badge from '../ui/Badge'
import Card, { CardTitle } from '../ui/Card'
import FlutedGlass, { type FlutePalette } from '../ui/FlutedGlass'
import { cn } from '../ui/cn'
import PageHeader from '../app/PageHeader'

const FACTS: { value: string; label: string; palette: FlutePalette }[] = [
  { value: '≈26M', label: 'logged recommendation impressions', palette: 'estimators' },
  { value: '80', label: 'fashion items in the “All” campaign', palette: 'studies' },
  { value: '3', label: 'recommendation slots on each screen', palette: 'lab' },
  { value: '2', label: 'live logging policies, run side by side', palette: 'story' },
]

const ANATOMY = [
  { icon: LayoutGrid, k: 'Context X', v: 'User and item features at the moment of the recommendation.', c: 'bg-blue-soft text-blue-ink' },
  { icon: Shirt, k: 'Action A', v: 'Which item was shown, and in which of the three slots.', c: 'bg-pink-soft text-pink-ink' },
  { icon: MousePointerClick, k: 'Reward R', v: 'Did the user click? 1 for a click, 0 otherwise.', c: 'bg-teal-soft text-teal-ink' },
  { icon: Dices, k: 'Propensity', v: 'The logging policy’s probability of that action, recorded at serve time.', c: 'bg-orange-soft text-orange-ink' },
]

const STEPS = [
  { cmd: 'pip install -r requirements.txt', note: 'Installs the Python app and obp 0.4.1 (Open Bandit Pipeline).' },
  { cmd: 'streamlit run app.py', note: 'Starts OPE Lab locally at localhost:8501.' },
  { cmd: 'Open the “Real Data” tab', note: 'Follow its instructions to download the dataset. Results appear only when the raw files are present.' },
]

export default function RealData() {
  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader
        tab="real-data"
        eyebrow="Real data"
        title="From simulation to a real storefront"
        lead="The Python app evaluates real fashion recommendations from ZOZOTOWN, Japan’s largest fashion e-commerce site, using the Open Bandit Dataset."
      />

      <section aria-labelledby="obd-facts" className="flex flex-col gap-lg">
        <p id="obd-facts" role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
          The Open Bandit Dataset at a glance
        </p>
        <ul className="ds-stagger grid gap-lg sm:grid-cols-2 lg:grid-cols-4">
          {FACTS.map((f, i) => (
            <li key={f.label} style={{ '--i': i } as CSSProperties}>
              <FlutedGlass palette={f.palette} size="sm" interactive className="flex h-full flex-col gap-xs rounded-xl p-xl shadow-md transition-ds hover:-translate-y-1 hover:shadow-lg">
                <span className="ds-text-glow font-body text-stat font-bold text-on-flute">{f.value}</span>
                <span className="ds-text-glow text-small font-medium text-on-flute-muted">{f.label}</span>
              </FlutedGlass>
            </li>
          ))}
        </ul>
        <p className="text-caption text-fg-subtle">
          Collected on ZOZOTOWN in late 2019 across three campaigns (All, Men’s and Women’s). Source: Saito et al., “Open Bandit Dataset and Pipeline”.
        </p>
      </section>

      <div className="grid gap-xl lg:grid-cols-12">
        <Card className="flex flex-col gap-lg lg:col-span-7">
          <div className="flex items-center gap-md">
            <span className="flex size-10 items-center justify-center rounded-lg bg-primary-soft text-primary-ink">
              <Sparkles size={18} aria-hidden />
            </span>
            <CardTitle>Why it’s perfect for testing OPE</CardTitle>
          </div>
          <p className="text-body text-pretty text-fg">
            Two policies ran live on the same site at the same time: one picked items <strong>uniformly at random</strong>, the other used{' '}
            <strong>Bernoulli Thompson Sampling</strong>.
          </p>
          <p className="text-body text-pretty text-fg-muted">
            So you can estimate Thompson Sampling’s click rate from the random policy’s logs, then check the guess against the clicks it actually got. It’s the
            same check the Lab does with V*, but on real customers.
          </p>
          <div className="flex flex-wrap gap-sm">
            <Badge label="Random → logging policy" tone="blue" dot />
            <Badge label="Thompson Sampling → policy to evaluate" tone="pink" dot />
            <Badge label="Its real clicks → ground truth" tone="orange" dot />
          </div>
        </Card>
        <Card className="flex flex-col items-center justify-center gap-lg py-3xl text-center lg:col-span-5">
          <span className="flex size-16 animate-float-slow items-center justify-center rounded-2xl bg-yellow-soft text-yellow-ink">
            <Database size={30} aria-hidden />
          </span>
          <CardTitle>Not loaded in this browser demo</CardTitle>
          <Badge label="No data loaded" tone="yellow" dot />
          <p className="max-w-80 text-small text-fg-muted">We never show made-up numbers, so nothing appears here until you run the real files locally.</p>
        </Card>
      </div>

      <section aria-labelledby="anatomy-title" className="flex flex-col gap-lg">
        <p id="anatomy-title" role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
          Anatomy of one logged row
        </p>
        <ul className="ds-stagger grid gap-lg sm:grid-cols-2 lg:grid-cols-4">
          {ANATOMY.map((a, i) => (
            <li key={a.k} style={{ '--i': i } as CSSProperties} className="flex flex-col gap-md rounded-xl border-thin border-line bg-surface p-xl shadow-sm">
              <span className={cn('flex size-11 items-center justify-center rounded-lg', a.c)}>
                <a.icon size={20} aria-hidden />
              </span>
              <p className="text-body font-semibold text-fg">{a.k}</p>
              <p className="text-small text-fg-muted">{a.v}</p>
            </li>
          ))}
        </ul>
      </section>

      <Card className="flex flex-col gap-xl">
        <CardTitle>Run it locally in 3 steps</CardTitle>
        <ol className="ds-stagger grid gap-lg md:grid-cols-3">
          {STEPS.map((s, i) => (
            <li key={s.cmd} style={{ '--i': i } as CSSProperties} className="flex gap-lg">
              <FlutedGlass as="span" palette="real-data" size="sm" scrim="none" className="flex size-10 shrink-0 items-center justify-center rounded-full font-display text-body font-bold">
                {i + 1}
              </FlutedGlass>
              <div className="flex min-w-0 flex-col gap-xs">
                <code className="flex items-center gap-sm self-start rounded-md bg-surface-sunken px-md py-xs text-small break-all text-fg">
                  {i < 2 && <Terminal size={14} aria-hidden className="shrink-0 text-fg-muted" />}
                  {s.cmd}
                </code>
                <p className="text-small text-fg-muted">{s.note}</p>
              </div>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  )
}
