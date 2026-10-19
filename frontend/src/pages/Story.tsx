import { useState, type CSSProperties } from 'react'
import { ArrowLeft, ArrowRight, Check, EyeOff, FunctionSquare, Ticket, Split, Sigma } from 'lucide-react'
import { fmt } from '../ope/format'
import { V_STAR } from '../ope/simulate'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import Card, { CardTitle } from '../ui/Card'
import Disclosure from '../ui/Disclosure'
import { cn } from '../ui/cn'
import Insight from '../app/Insight'
import PageHeader from '../app/PageHeader'
import { useNav } from '../app/nav'

const CHAPTERS = [
  { title: 'The coupon dilemma', icon: Ticket },
  { title: 'Two worlds', icon: Split },
  { title: 'Ground truth', icon: Sigma },
]

function Dilemma() {
  return (
    <div className="flex flex-col gap-xl">
      <div className="grid gap-lg md:grid-cols-2">
        <Card className="flex flex-col gap-md">
          <p className="text-small font-semibold text-teal-ink">Got a coupon</p>
          <p className="font-display text-stat font-semibold text-fg">$150</p>
          <div className="h-3 overflow-hidden rounded-full bg-surface-sunken" aria-hidden>
            <div className="h-full origin-left animate-[ds-grow_1.2s_var(--ds-ease-out)_both] rounded-full bg-linear-to-r from-teal to-blue" style={{ width: '100%' }} />
          </div>
          <p className="text-small text-fg-muted">average spend</p>
        </Card>
        <Card className="flex flex-col gap-md">
          <p className="text-small font-semibold text-fg-muted">No coupon</p>
          <p className="font-display text-stat font-semibold text-fg">$80</p>
          <div className="h-3 overflow-hidden rounded-full bg-surface-sunken" aria-hidden>
            <div className="h-full origin-left animate-[ds-grow_1.2s_var(--ds-ease-out)_both] rounded-full bg-fg-subtle" style={{ width: '53%' }} />
          </div>
          <p className="text-small text-fg-muted">average spend</p>
        </Card>
      </div>
      <Card className="flex flex-col gap-md">
        <div className="flex flex-wrap items-center justify-between gap-md">
          <CardTitle>Why the $70 gap lies</CardTitle>
          <Badge label="Illustrative example" />
        </div>
        <p className="text-body text-fg">
          Coupons weren’t handed out at random. The old policy targeted loyal big spenders: people who would have spent more <em>anyway</em>.
        </p>
        <p className="text-body text-fg-muted">So the gap mixes what the coupon does with who received it. The raw data can’t tell them apart.</p>
      </Card>
      <Insight>
        <p className="font-display text-h3 font-semibold">Was it the coupon, or were they already big spenders?</p>
        <p className="mt-xs text-small text-fg-muted">Off-policy evaluation answers exactly this question.</p>
      </Insight>
    </div>
  )
}

const LOGGED = [1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1]
const TARGET = [1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1]

function TwoWorlds() {
  const observed = LOGGED.filter((a, i) => a === TARGET[i]).length
  return (
    <div className="flex flex-col gap-xl">
      <div className="grid gap-lg md:grid-cols-2">
        <Card className="flex flex-col gap-md border-l-thick border-l-teal">
          <span className="flex items-center gap-sm text-small font-semibold text-teal-ink">
            <span aria-hidden className="h-1 w-8 rounded-full bg-teal" /> The logged world · π₀
          </span>
          <p className="text-body text-fg">What actually happened. Real, solid, and biased toward whoever the old policy favored.</p>
        </Card>
        <Card className="flex flex-col gap-md border-l-thick border-l-pink">
          <span className="flex items-center gap-sm text-small font-semibold text-pink-ink">
            <span aria-hidden className="w-8 border-t-thick border-dotted border-pink" /> The target world · πₑ
          </span>
          <p className="text-body text-fg">What the new policy would have done. Wherever it disagrees with π₀, the outcome is simply missing.</p>
        </Card>
      </div>

      <Card variant="stage" className="flex flex-col gap-xl">
        <div className="flex flex-wrap items-baseline justify-between gap-md">
          <CardTitle onStage>Twelve customers, two policies</CardTitle>
          <Badge tone="stage" label={`${observed} of 12 outcomes visible under πₑ`} />
        </div>
        <div className="ds-stagger grid grid-cols-12 gap-x-xs gap-y-md sm:gap-x-md">
          {LOGGED.map((a, i) => {
            const seen = a === TARGET[i]
            return (
              <div key={i} style={{ '--i': i } as CSSProperties} className="flex flex-col items-center gap-sm">
                <span aria-hidden className={cn('size-5 rounded-full sm:size-7', a ? 'bg-stage-accent' : 'border-thick border-stage-accent')} />
                <span aria-hidden className={cn('size-5 rounded-full border-thick border-dotted border-pink sm:size-7', TARGET[i] === 1 && 'bg-pink/40')} />
                <span className={cn('text-small font-bold', seen ? 'text-stage-accent' : 'text-stage-ghost')}>{seen ? 'R' : '?'}</span>
              </div>
            )
          })}
        </div>
        <ul className="flex flex-wrap gap-x-xl gap-y-sm text-caption text-stage-fg-muted">
          <li className="flex items-center gap-sm">
            <span aria-hidden className="size-3 rounded-full bg-stage-accent" /> Row 1: coupon sent by π₀
          </li>
          <li className="flex items-center gap-sm">
            <span aria-hidden className="size-3 rounded-full border-thick border-dotted border-pink bg-pink/40" /> Row 2: coupon πₑ would send
          </li>
          <li className="flex items-center gap-sm">
            <span className="font-bold text-stage-accent">R</span> reward seen · <span className="font-bold text-stage-ghost">?</span> never observed
          </li>
        </ul>
      </Card>

      <ol className="ds-stagger grid gap-lg md:grid-cols-3">
        {[
          { t: 'Log', b: 'Record context X, the action A taken, and the reward R.', c: 'bg-teal-soft text-teal-ink' },
          { t: 'Reweight or model', b: 'Learn how likely each action was, or predict rewards directly.', c: 'bg-primary-soft text-primary-ink' },
          { t: 'Estimate', b: 'Combine them into V̂(πₑ): the value of the world we never saw.', c: 'bg-pink-soft text-pink-ink' },
        ].map((s, i) => (
          <li key={s.t} style={{ '--i': i } as CSSProperties} className="flex gap-md rounded-xl border-thin border-line bg-surface p-lg shadow-sm">
            <span className={cn('flex size-10 shrink-0 items-center justify-center rounded-full font-display text-h3 font-semibold', s.c)}>{i + 1}</span>
            <div className="flex flex-col gap-2xs">
              <p className="text-body font-semibold text-fg">{s.t}</p>
              <p className="text-small text-fg-muted">{s.b}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}

const DGP = [
  { sym: 'X ~ N(0, 1)', body: 'An observed customer feature, such as past spend.' },
  { sym: 'U ~ N(0, 1)', body: 'A hidden trait such as loyalty. Shapes both who is treated and how they respond.', hidden: true },
  { sym: 'π₀(A=1 | X, U) = σ(L·X + 3c·U)', body: 'The old policy. c = how much it leans on U; L = 0.5 + 5(1 − overlap).' },
  { sym: 'R = 0.5 + 0.3X + A(0.2 + 0.2X) + 0.4U + noise·ε', body: 'The reward. Treatment helps everyone a little, high-X customers more.' },
  { sym: 'πₑ(X) = 1[X > 0]', body: 'The new policy: treat only customers with positive X.' },
]

function GroundTruth() {
  return (
    <div className="flex flex-col gap-xl">
      <div className="grid gap-lg lg:grid-cols-12">
        <Card variant="stage" className="relative isolate flex flex-col gap-md overflow-hidden lg:col-span-7">
          <span aria-hidden className="absolute -top-20 -right-10 -z-10 size-64 animate-float rounded-full bg-orange opacity-30 blur-3xl" />
          <p className="text-small font-semibold text-stage-fg-muted">True value of the new policy</p>
          <p className="font-display text-display font-semibold text-insight">{fmt(V_STAR, 4)}</p>
          <p className="text-body text-stage-fg-muted">
            We simulate the world ourselves, so we know the answer exactly. Every chart draws it as a solid orange line: <strong className="text-stage-fg">reality</strong>.
          </p>
        </Card>
        <Card className="flex flex-col gap-md lg:col-span-5">
          <span className="flex size-12 items-center justify-center rounded-lg bg-pink-soft text-pink-ink">
            <EyeOff size={22} aria-hidden />
          </span>
          <CardTitle>Estimators only see X, never U</CardTitle>
          <p className="text-body text-fg-muted">Just like real life: the confounder is the thing nobody wrote down.</p>
        </Card>
      </div>
      <Card>
        <Disclosure
          title="Show the equations"
          hint="The exact world we simulate (optional)"
          icon={
            <span className="flex size-10 items-center justify-center rounded-lg bg-primary-soft text-primary-ink">
              <FunctionSquare size={20} aria-hidden />
            </span>
          }
        >
          <ul className="flex flex-col gap-lg">
            {DGP.map((row) => (
              <li key={row.sym} className="flex flex-col gap-xs">
                <div className="flex flex-wrap items-center gap-sm">
                  <code className="rounded-md bg-surface-sunken px-md py-xs text-small text-fg">{row.sym}</code>
                  {row.hidden && <Badge label="hidden from estimators" tone="warning" dot />}
                </div>
                <p className="text-small text-fg-muted">{row.body}</p>
              </li>
            ))}
            <li>
              <code className="rounded-md bg-orange-soft px-md py-xs text-small text-orange-ink">V* = 0.6 + 0.2·φ(0) = 0.6 + 0.2/√(2π)</code>
            </li>
          </ul>
        </Disclosure>
      </Card>
    </div>
  )
}

export default function Story() {
  const { go } = useNav()
  const [step, setStep] = useState(0)
  const panels = [<Dilemma key="d" />, <TwoWorlds key="t" />, <GroundTruth key="g" />]

  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader tab="story" eyebrow="3 short chapters" title="Why raw data can fool you" lead="Two minutes, three ideas. Read them in order or jump straight to the one you need." />

      <ol className="grid grid-cols-3 gap-sm" aria-label="Chapters">
        {CHAPTERS.map((c, i) => {
          const state = i < step ? 'done' : i === step ? 'current' : 'todo'
          return (
            <li key={c.title}>
              <button
                type="button"
                aria-current={state === 'current' ? 'step' : undefined}
                onClick={() => setStep(i)}
                className={cn(
                  'flex w-full cursor-pointer flex-col items-start gap-sm rounded-xl border-thin p-md text-left transition-ds sm:flex-row sm:items-center sm:p-lg',
                  state === 'current' ? 'border-orange bg-orange-soft shadow-md' : 'border-line bg-surface hover:-translate-y-0.5 hover:shadow-sm',
                )}
              >
                <span
                  className={cn(
                    'flex size-9 shrink-0 items-center justify-center rounded-full transition-ds',
                    state === 'current' ? 'bg-orange text-on-primary' : state === 'done' ? 'bg-green-soft text-green-ink' : 'bg-surface-sunken text-fg-muted',
                  )}
                >
                  {state === 'done' ? <Check size={16} aria-hidden /> : <c.icon size={16} aria-hidden />}
                </span>
                <span className="flex flex-col">
                  <span className="text-caption font-semibold text-fg-subtle">Chapter {i + 1}</span>
                  <span className={cn('text-small font-semibold', state === 'current' ? 'text-orange-ink' : 'text-fg')}>{c.title}</span>
                </span>
              </button>
            </li>
          )
        })}
      </ol>

      <section key={step} aria-label={CHAPTERS[step].title} className="animate-page-in">
        {panels[step]}
      </section>

      <div className="flex items-center justify-between gap-md">
        <Button variant="ghost" disabled={step === 0} onClick={() => setStep((s) => s - 1)} iconStart={<ArrowLeft size={16} />}>
          Back
        </Button>
        {step < CHAPTERS.length - 1 ? (
          <Button onClick={() => setStep((s) => s + 1)} iconEnd={<ArrowRight size={16} />}>
            Next: {CHAPTERS[step + 1].title}
          </Button>
        ) : (
          <Button onClick={() => go('estimators')} iconEnd={<ArrowRight size={16} />}>
            Meet the estimators
          </Button>
        )}
      </div>
    </div>
  )
}
