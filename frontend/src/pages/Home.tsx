import type { CSSProperties } from 'react'
import { ArrowRight, Cpu, EyeOff, Scale } from 'lucide-react'
import { ESTIMATOR_BY_KEY } from '../ope/meta'
import { closestContender } from '../ope/insights'
import { fmt, fmtSigned } from '../ope/format'
import { useOpe } from '../ope/OpeProvider'
import { V_STAR } from '../ope/simulate'
import AnimatedNumber from '../ui/AnimatedNumber'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import Card from '../ui/Card'
import { cn } from '../ui/cn'
import TwoWorldsPath from '../viz/TwoWorldsPath'
import { MarkerGlyph } from '../viz/Marker'
import { useNav } from '../app/nav'
import { TABS } from '../app/tabs'

const FACTS = [
  { icon: EyeOff, value: '1', label: 'hidden confounder', tone: 'text-pink' },
  { icon: Scale, value: '6', label: 'estimators compared', tone: 'text-stage-accent' },
  { icon: Cpu, value: '0', label: 'servers: runs in your browser', tone: 'text-insight' },
]

export default function Home() {
  const { go } = useNav()
  const { point } = useOpe()
  const best = closestContender(point.estimates)
  const bestMeta = best ? ESTIMATOR_BY_KEY[best] : null

  return (
    <div className="flex flex-col gap-section">
      <section aria-labelledby="page-title" className="relative isolate overflow-hidden rounded-2xl bg-linear-to-br from-stage via-stage to-stage-deep px-xl py-3xl text-stage-fg shadow-lg md:px-3xl">
        <span aria-hidden className="absolute -top-32 -left-24 -z-10 size-96 animate-float rounded-full bg-primary opacity-30 blur-3xl" />
        <span aria-hidden className="absolute -right-24 -bottom-40 -z-10 size-96 animate-float-slow rounded-full bg-pink opacity-25 blur-3xl" />
        <span aria-hidden className="absolute top-1/3 right-1/3 -z-10 size-64 animate-float rounded-full bg-teal opacity-20 blur-3xl" />

        <div className="grid items-center gap-2xl lg:grid-cols-12">
          <div className="flex flex-col gap-xl lg:col-span-6">
            <Badge label="Perceptron Hackathon 2026 · Problem 3" tone="stage" pulse className="self-start" />
            <p id="page-title" role="heading" aria-level={1} tabIndex={-1} className="animate-rise font-display text-display font-semibold text-balance outline-none">
              Did the policy actually work,{' '}
              <span className="bg-linear-to-r from-stage-accent via-primary-soft to-pink bg-clip-text text-transparent">or did it just look like it?</span>
            </p>
            <p className="max-w-prose text-lead text-pretty text-stage-fg-muted">
              Your logs show one world: what the old policy did. OPE Lab rebuilds the other one, what a new policy <em>would</em> have done, and shows
              which methods get it right.
            </p>
            <div className="flex flex-wrap gap-md">
              <Button onClick={() => go('lab')} iconEnd={<ArrowRight size={18} />}>
                Try the Lab
              </Button>
              <Button variant="stage" onClick={() => go('story')}>
                See how it works
              </Button>
            </div>
          </div>

          <div className="flex flex-col gap-lg lg:col-span-6">
            <TwoWorldsPath />
            <ul className="flex flex-wrap gap-sm text-caption">
              <li className="inline-flex items-center gap-sm rounded-full bg-stage-surface px-md py-xs text-stage-fg-muted">
                <span aria-hidden className="h-1 w-6 rounded-full bg-stage-accent" /> Reality · old policy π₀
              </li>
              <li className="inline-flex items-center gap-sm rounded-full bg-stage-surface px-md py-xs text-stage-fg-muted">
                <span aria-hidden className="w-6 border-t-thick border-dotted border-pink" /> Counterfactual · new policy πₑ
              </li>
            </ul>
          </div>
        </div>

        <ul className="ds-stagger mt-3xl grid gap-md sm:grid-cols-3">
          {FACTS.map((f, i) => (
            <li key={f.label} style={{ '--i': i } as CSSProperties} className="flex items-center gap-md rounded-lg bg-stage-surface p-lg">
              <f.icon size={22} aria-hidden className={f.tone} />
              <span className="font-display text-h2 font-semibold">{f.value}</span>
              <span className="text-small text-stage-fg-muted">{f.label}</span>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="teaser-title" className="flex flex-col gap-xl">
        <div className="flex flex-wrap items-end justify-between gap-lg">
          <div className="flex flex-col gap-xs">
            <p id="teaser-title" role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
              One world, simulated just now
            </p>
            <p className="text-body text-fg-muted">5,000 customers, a hidden trait, and three very different answers.</p>
          </div>
          <Button variant="secondary" onClick={() => go('lab')} iconEnd={<ArrowRight size={16} />}>
            Change the world
          </Button>
        </div>
        <div className="ds-stagger grid gap-lg md:grid-cols-3">
          <Card className="relative overflow-hidden" >
            <span aria-hidden className="absolute inset-x-0 top-0 h-1.5 bg-est-naive" />
            <p className="flex items-center gap-sm text-small font-semibold text-fg-muted">
              <MarkerGlyph meta={ESTIMATOR_BY_KEY.naive} /> What the raw data says
            </p>
            <p className="mt-md font-display text-stat font-semibold text-fg">
              <AnimatedNumber value={point.estimates.naive} format={(v) => fmt(v)} />
            </p>
            <Badge className="mt-md" tone="danger" label={`Off by ${fmtSigned(point.estimates.naive - V_STAR)}`} />
          </Card>
          <Card className="relative overflow-hidden" variant="stage">
            <p className="text-small font-semibold text-stage-fg-muted">The truth (known, because we built the world)</p>
            <p className="mt-md font-display text-stat font-semibold text-insight">
              <AnimatedNumber value={V_STAR} format={(v) => fmt(v)} />
            </p>
            <Badge className="mt-md" tone="stage" label="V* · ground truth" />
          </Card>
          <Card className="relative overflow-hidden">
            <span aria-hidden className={cn('absolute inset-x-0 top-0 h-1.5', bestMeta?.bg ?? 'bg-green')} />
            <p className="flex items-center gap-sm text-small font-semibold text-fg-muted">
              {bestMeta && <MarkerGlyph meta={bestMeta} />} Best correction · {bestMeta?.name ?? '—'}
            </p>
            <p className="mt-md font-display text-stat font-semibold text-fg">
              <AnimatedNumber value={best ? point.estimates[best] : Number.NaN} format={(v) => fmt(v)} />
            </p>
            <Badge className="mt-md" tone="success" label={best ? `Off by ${fmtSigned(point.estimates[best] - V_STAR)}` : '—'} />
          </Card>
        </div>
      </section>

      <section aria-labelledby="start-title" className="flex flex-col gap-xl">
        <p id="start-title" role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
          Where do you want to start?
        </p>
        <ul className="ds-stagger grid gap-lg sm:grid-cols-2 lg:grid-cols-3">
          {TABS.filter((t) => t.id !== 'home').map((t, i) => (
            <li key={t.id} style={{ '--i': i } as CSSProperties}>
              <button
                type="button"
                onClick={() => go(t.id)}
                className="group flex h-full w-full cursor-pointer flex-col gap-md rounded-xl border-thin border-line bg-surface p-xl text-left shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md"
              >
                <span className={cn('flex size-12 items-center justify-center rounded-lg transition-ds group-hover:scale-110 group-hover:-rotate-6', t.accent.soft, t.accent.ink)}>
                  <t.icon size={22} aria-hidden />
                </span>
                <span className="text-h3 font-semibold text-fg">{t.label}</span>
                <span className="text-small text-fg-muted">{t.blurb}</span>
                <span className={cn('mt-auto inline-flex items-center gap-xs text-small font-semibold', t.accent.ink)}>
                  Open <ArrowRight size={16} aria-hidden className="transition-ds group-hover:translate-x-1" />
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
