import type { CSSProperties } from 'react'
import { ArrowRight, Calculator, CircleHelp, Cpu, EyeOff, Globe, GraduationCap, Megaphone, Scale, ScrollText, ShoppingBag, Stethoscope, Target, Ticket } from 'lucide-react'
import { ESTIMATOR_BY_KEY } from '../ope/meta'
import { closestContender } from '../ope/insights'
import { fmt, fmtSigned } from '../ope/format'
import { useOpe } from '../ope/OpeProvider'
import { V_STAR } from '../ope/simulate'
import AnimatedNumber from '../ui/AnimatedNumber'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import Card from '../ui/Card'
import Disclosure from '../ui/Disclosure'
import FlutedGlass from '../ui/FlutedGlass'
import { cn } from '../ui/cn'
import TwoWorldsPath from '../viz/TwoWorldsPath'
import { MarkerGlyph } from '../viz/Marker'
import { useNav } from '../app/nav'
import { TABS } from '../app/tabs'

const FACTS = [
  { icon: EyeOff, value: '1', label: 'hidden confounder' },
  { icon: Scale, value: '6', label: 'estimators compared' },
  { icon: Cpu, value: '0', label: 'servers: it runs in your browser' },
]

const STEPS = [
  { icon: Globe, title: 'Simulate a world', text: 'Customers get a visible trait X and a hidden trait U. Because we built the world, we know the true answer V*.', c: 'bg-blue-soft text-blue-ink', bar: 'bg-blue' },
  { icon: ScrollText, title: 'Log the old policy', text: 'An old rule hands out coupons, partly based on U. We only record what it chose and what happened.', c: 'bg-pink-soft text-pink-ink', bar: 'bg-pink' },
  { icon: Calculator, title: 'Estimate six ways', text: 'Each estimator guesses what the new policy would have earned, using the logs alone.', c: 'bg-teal-soft text-teal-ink', bar: 'bg-teal' },
  { icon: Target, title: 'Score against the truth', text: 'Compare every guess with V*, so you can see which method was right and by how much.', c: 'bg-orange-soft text-orange-ink', bar: 'bg-orange' },
]

const USES = [
  { icon: Ticket, title: 'Coupons & promotions', q: 'Would a new targeting rule have earned more than the one you ran?', c: 'bg-orange-soft text-orange-ink' },
  { icon: ShoppingBag, title: 'Recommendations', q: 'Can yesterday’s clicks score a new ranking without an A/B test?', c: 'bg-pink-soft text-pink-ink' },
  { icon: Stethoscope, title: 'Treatment rules', q: 'Is a new rule better, judged from records where doctors chose who got what?', c: 'bg-teal-soft text-teal-ink' },
  { icon: Megaphone, title: 'Ads & pricing', q: 'Will a new bidding or discount policy pay off before you spend real budget?', c: 'bg-blue-soft text-blue-ink' },
  { icon: GraduationCap, title: 'Learning apps', q: 'Which hint or lesson order helps students most, judged from past sessions?', c: 'bg-green-soft text-green-ink' },
  { icon: Scale, title: 'Policy reviews', q: 'Did a program work, or did it just reach people who would have done well anyway?', c: 'bg-primary-soft text-primary-ink' },
]

const FAQ = [
  {
    q: 'Is any of this real data?',
    a: 'The Story, Lab and Studies use simulated customers, so the true answer is known and every estimate can be checked. The Real data tab explains how to run the Python app on the Open Bandit Dataset.',
  },
  {
    q: 'Why not just run an A/B test?',
    a: 'Experiments cost time, money and sometimes risk. Off-policy evaluation answers “what if?” from logs you already have, so you only test the most promising ideas.',
  },
  {
    q: 'Which estimator should I trust?',
    a: 'It depends on the world. Doubly robust is the safest default, and you should check the weights before trusting IPW. The Decision map in Studies shows the winner in nine kinds of world.',
  },
  {
    q: 'What can no estimator fix?',
    a: 'A confounder the logs never recorded. That’s why the Sensitivity study asks how much hidden bias it would take to change the answer.',
  },
  {
    q: 'Does anything leave my browser?',
    a: 'No. The simulation and all six estimators run on your device in a background thread (a Web Worker).',
  },
]

function SectionTitle({ id, title, lead }: { id: string; title: string; lead?: string }) {
  return (
    <div className="flex flex-col gap-xs">
      <p id={id} role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
        {title}
      </p>
      {lead && <p className="max-w-prose text-body text-fg-muted">{lead}</p>}
    </div>
  )
}

export default function Home() {
  const { go } = useNav()
  const { point } = useOpe()
  const best = closestContender(point.estimates)
  const bestMeta = best ? ESTIMATOR_BY_KEY[best] : null

  return (
    <div className="flex flex-col gap-section">
      <FlutedGlass
        as="section"
        aria-labelledby="page-title"
        palette="home"
        interactive
        drift
        className="flex min-h-120 animate-rise flex-col items-center justify-center gap-xl rounded-2xl px-xl py-4xl text-center shadow-lg md:px-3xl"
      >
        <span className="inline-flex items-center gap-sm rounded-full border-thin border-glass-line bg-glass px-md py-xs text-caption font-semibold text-on-flute backdrop-blur-md">
          <span aria-hidden className="size-1.5 animate-pulse rounded-full bg-on-flute" />
          Perceptron Hackathon 2026 · Problem 3
        </span>
        <p id="page-title" role="heading" aria-level={1} tabIndex={-1} className="ds-text-glow font-body text-display font-bold text-balance text-on-flute outline-none">
          Off&#8209;Policy Evaluation Lab
        </p>
        <p className="ds-text-glow max-w-prose text-lead font-medium text-pretty text-on-flute-muted">Did the policy actually work, or did it just look like it did?</p>
        <div className="flex flex-wrap justify-center gap-md">
          <Button variant="light" onClick={() => go('lab')} iconEnd={<ArrowRight size={18} />}>
            Try the Lab
          </Button>
          <Button variant="glass" onClick={() => go('story')}>
            See how it works
          </Button>
        </div>
        <ul className="ds-stagger mt-lg flex flex-wrap justify-center gap-sm">
          {FACTS.map((f, i) => (
            <li
              key={f.label}
              style={{ '--i': i } as CSSProperties}
              className="inline-flex items-center gap-sm rounded-full border-thin border-glass-line bg-glass px-lg py-sm text-small text-on-flute backdrop-blur-md"
            >
              <f.icon size={16} aria-hidden />
              <span className="font-bold">{f.value}</span>
              <span className="text-on-flute-muted">{f.label}</span>
            </li>
          ))}
        </ul>
      </FlutedGlass>

      <section aria-labelledby="worlds-title">
        <Card variant="stage" className="relative isolate grid items-center gap-2xl overflow-hidden md:p-3xl lg:grid-cols-12">
          <span aria-hidden className="absolute -top-32 -left-24 -z-10 size-96 animate-float rounded-full bg-primary opacity-25 blur-3xl" />
          <span aria-hidden className="absolute -right-24 -bottom-40 -z-10 size-96 animate-float-slow rounded-full bg-pink opacity-20 blur-3xl" />
          <div className="flex flex-col gap-lg lg:col-span-5">
            <Badge label="The core idea" tone="stage" dot className="self-start" />
            <p id="worlds-title" role="heading" aria-level={2} className="font-display text-h1 font-semibold text-balance">
              Your logs show one world.{' '}
              <span className="bg-linear-to-r from-stage-accent via-flute-2 to-flute-9 bg-clip-text text-transparent">We rebuild the other.</span>
            </p>
            <p className="text-body text-pretty text-stage-fg-muted">
              The data shows what the old policy did. Off-policy evaluation estimates what a new policy <em>would</em> have done, without running it. OPE
              Lab shows which methods get that right.
            </p>
          </div>
          <div className="flex flex-col gap-lg lg:col-span-7">
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
        </Card>
      </section>

      <section aria-labelledby="teaser-title" className="flex flex-col gap-xl">
        <div className="flex flex-wrap items-end justify-between gap-lg">
          <SectionTitle id="teaser-title" title="One world, simulated just now" lead="5,000 customers, a hidden trait, and three very different answers." />
          <Button variant="secondary" onClick={() => go('lab')} iconEnd={<ArrowRight size={16} />}>
            Change the world
          </Button>
        </div>
        <div className="ds-stagger grid gap-lg md:grid-cols-3">
          <Card className="relative overflow-hidden">
            <FlutedGlass as="span" aria-hidden palette="solid" size="sm" scrim="none" className="absolute inset-x-0 top-0 h-2 bg-est-naive" />
            <p className="flex items-center gap-sm text-small font-semibold text-fg-muted">
              <MarkerGlyph meta={ESTIMATOR_BY_KEY.naive} /> What the raw data says
            </p>
            <p className="mt-md font-display text-stat font-semibold text-fg">
              <AnimatedNumber value={point.estimates.naive} format={(v) => fmt(v)} />
            </p>
            <Badge className="mt-md" tone="danger" label={`Off by ${fmtSigned(point.estimates.naive - V_STAR)}`} />
          </Card>
          <FlutedGlass palette="estimators" size="sm" scrim="center" className="rounded-xl p-xl shadow-lg">
            <p className="ds-text-glow text-small font-semibold text-on-flute-muted">The truth (known, because we built the world)</p>
            <p className="ds-text-glow mt-md font-display text-stat font-semibold text-on-flute">
              <AnimatedNumber value={V_STAR} format={(v) => fmt(v)} />
            </p>
            <span className="mt-md inline-flex rounded-full border-thin border-glass-line bg-glass px-md py-2xs text-caption font-semibold text-on-flute">V* · ground truth</span>
          </FlutedGlass>
          <Card className="relative overflow-hidden">
            <FlutedGlass as="span" aria-hidden palette="solid" size="sm" scrim="none" className={cn('absolute inset-x-0 top-0 h-2', bestMeta?.bg ?? 'bg-green')} />
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

      <section aria-labelledby="how-title" className="flex flex-col gap-xl">
        <SectionTitle id="how-title" title="How OPE Lab works" lead="Four steps, repeated every time you move a slider." />
        <ol className="ds-stagger grid gap-lg sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s, i) => (
            <li key={s.title} style={{ '--i': i } as CSSProperties} className="group relative flex flex-col gap-md overflow-hidden rounded-xl border-thin border-line bg-surface p-xl shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md">
              <span aria-hidden className={cn('absolute inset-x-0 bottom-0 h-1 origin-left scale-x-0 transition-ds group-hover:scale-x-100', s.bar)} />
              <div className="flex items-center justify-between">
                <span className={cn('flex size-11 items-center justify-center rounded-lg transition-ds group-hover:scale-110', s.c)}>
                  <s.icon size={20} aria-hidden />
                </span>
                <span aria-hidden className="font-display text-h1 font-semibold text-line-strong">{i + 1}</span>
              </div>
              <p className="text-h3 font-semibold text-fg">{s.title}</p>
              <p className="text-small text-fg-muted">{s.text}</p>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="uses-title" className="flex flex-col gap-xl">
        <SectionTitle id="uses-title" title="Where this question shows up" lead="Wherever a past policy chose who got what, the same trap is waiting." />
        <ul className="ds-stagger grid gap-lg sm:grid-cols-2 lg:grid-cols-3">
          {USES.map((u, i) => (
            <li key={u.title} style={{ '--i': i } as CSSProperties} className="group flex items-start gap-lg rounded-xl border-thin border-line bg-surface p-xl shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md">
              <span className={cn('flex size-12 shrink-0 items-center justify-center rounded-full transition-ds group-hover:-rotate-6', u.c)}>
                <u.icon size={22} aria-hidden />
              </span>
              <span className="flex flex-col gap-xs">
                <span className="text-body font-semibold text-fg">{u.title}</span>
                <span className="text-small text-fg-muted">{u.q}</span>
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="start-title" className="flex flex-col gap-xl">
        <SectionTitle id="start-title" title="Where do you want to start?" />
        <ul className="ds-stagger grid gap-lg sm:grid-cols-2 lg:grid-cols-3">
          {TABS.filter((t) => t.id !== 'home').map((t, i) => (
            <li key={t.id} style={{ '--i': i } as CSSProperties}>
              <button
                type="button"
                onClick={() => go(t.id)}
                className="group flex h-full w-full cursor-pointer flex-col overflow-hidden rounded-xl border-thin border-line bg-surface text-left shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md"
              >
                <FlutedGlass as="span" palette={t.id} scrim="none" className="flex h-24 items-end p-lg">
                  <span className="flex size-12 items-center justify-center rounded-lg border-thin border-glass-line bg-glass text-on-flute backdrop-blur-md transition-ds group-hover:scale-110 group-hover:-rotate-6">
                    <t.icon size={22} aria-hidden />
                  </span>
                </FlutedGlass>
                <span className="flex flex-1 flex-col gap-sm p-xl">
                  <span className="text-h3 font-semibold text-fg">{t.label}</span>
                  <span className="text-small text-fg-muted">{t.blurb}</span>
                  <span className={cn('mt-auto inline-flex items-center gap-xs pt-sm text-small font-semibold', t.accent.ink)}>
                    Open <ArrowRight size={16} aria-hidden className="transition-ds group-hover:translate-x-1" />
                  </span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="faq-title" className="grid gap-xl lg:grid-cols-12">
        <div className="flex flex-col gap-lg lg:col-span-4">
          <span className="flex size-12 items-center justify-center rounded-full bg-primary-soft text-primary-ink">
            <CircleHelp size={22} aria-hidden />
          </span>
          <SectionTitle id="faq-title" title="Questions people ask" lead="Short answers. The tabs above have the long ones." />
        </div>
        <Card className="flex flex-col lg:col-span-8">
          {FAQ.map((f, i) => (
            <Disclosure key={f.q} title={f.q} defaultOpen={i === 0} className={cn('py-lg', i > 0 && 'border-t-thin border-line')}>
              <p className="text-body text-pretty text-fg-muted">{f.a}</p>
            </Disclosure>
          ))}
        </Card>
      </section>
    </div>
  )
}
