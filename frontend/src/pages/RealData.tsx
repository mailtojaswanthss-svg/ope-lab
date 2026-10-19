import type { CSSProperties } from 'react'
import { Database, Terminal } from 'lucide-react'
import Badge from '../ui/Badge'
import Card, { CardTitle } from '../ui/Card'
import PageHeader from '../app/PageHeader'

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
      <div className="grid gap-xl lg:grid-cols-12">
        <Card className="flex flex-col items-center justify-center gap-lg py-3xl text-center lg:col-span-5">
          <span className="flex size-16 animate-float-slow items-center justify-center rounded-2xl bg-yellow-soft text-yellow-ink">
            <Database size={30} aria-hidden />
          </span>
          <CardTitle>Open Bandit Dataset (ZOZOTOWN)</CardTitle>
          <Badge label="No data loaded" tone="yellow" dot />
          <p className="max-w-80 text-small text-fg-muted">Not loaded in this browser demo. We never show made-up numbers, so nothing appears here until you run the real files.</p>
        </Card>
        <Card className="flex flex-col gap-xl lg:col-span-7">
          <CardTitle>Run it locally in 3 steps</CardTitle>
          <ol className="ds-stagger flex flex-col gap-lg">
            {STEPS.map((s, i) => (
              <li key={s.cmd} style={{ '--i': i } as CSSProperties} className="flex gap-lg">
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-linear-to-br from-yellow to-orange font-display text-body font-bold text-on-primary">{i + 1}</span>
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
    </div>
  )
}
