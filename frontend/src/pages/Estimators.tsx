import type { CSSProperties } from 'react'
import { ArrowRight, Check, Code2, EyeOff, Layers, Minus, Repeat, ShieldCheck, TriangleAlert, XCircle, Gauge } from 'lucide-react'
import { ESTIMATORS, ESTIMATOR_BY_KEY } from '../ope/meta'
import type { EstimatorKey } from '../ope/estimators'
import { useOpe, type PresetId } from '../ope/OpeProvider'
import Badge, { type Tone } from '../ui/Badge'
import Button from '../ui/Button'
import Disclosure from '../ui/Disclosure'
import FlutedGlass from '../ui/FlutedGlass'
import { cn } from '../ui/cn'
import PageHeader from '../app/PageHeader'
import { useNav } from '../app/nav'
import { MarkerGlyph } from '../viz/Marker'

const RULES = [
  { icon: XCircle, text: 'Never trust Naive on targeted data', c: 'bg-danger-soft text-danger-ink' },
  { icon: Gauge, text: 'Check the weights before IPW', c: 'bg-warning-soft text-warning-ink' },
  { icon: ShieldCheck, text: 'When in doubt, start with DR', c: 'bg-success-soft text-success-ink' },
]

type Level = 'Low' | 'Medium' | 'High' | 'Depends'
const LEVEL_TONE: Record<Level, Tone> = { Low: 'success', Medium: 'warning', High: 'danger', Depends: 'blue' }

// Rules of thumb in this simulation. Bias assumes no hidden confounder unless noted.
const CHEAT: { key: EstimatorKey; model: boolean; weights: boolean; bias: Level; variance: Level; best: string }[] = [
  { key: 'naive', model: false, weights: false, bias: 'High', variance: 'Low', best: 'The old policy was a fair coin flip' },
  { key: 'replay', model: false, weights: false, bias: 'Depends', variance: 'Medium', best: 'Logging was uniformly random' },
  { key: 'dm', model: true, weights: false, bias: 'Depends', variance: 'Low', best: 'The reward model is well specified' },
  { key: 'ipw', model: false, weights: true, bias: 'Low', variance: 'High', best: 'Overlap is good and weights stay small' },
  { key: 'snipw', model: false, weights: true, bias: 'Low', variance: 'Medium', best: 'Overlap is fair and you want stability' },
  { key: 'dr', model: true, weights: true, bias: 'Low', variance: 'Medium', best: 'You are unsure: the safest default' },
]

const ASSUMPTIONS: { icon: typeof EyeOff; title: string; promise: string; breaks: string; preset: PresetId; cta: string; c: string; bar: string }[] = [
  {
    icon: EyeOff,
    title: 'No hidden confounding',
    promise: 'Everything that drove the old decisions was recorded in the data.',
    breaks: 'A hidden trait U steers treatment. Weights and models only see X, so every method inherits some bias.',
    preset: 'confounder',
    cta: 'Try a hidden confounder',
    c: 'bg-pink-soft text-pink-ink',
    bar: 'bg-pink',
  },
  {
    icon: Layers,
    title: 'Overlap',
    promise: 'The old policy sometimes tried every option for every kind of customer.',
    breaks: 'When it almost never explores, a few rows get huge weights and IPW-style estimates swing wildly.',
    preset: 'overlap',
    cta: 'Try low overlap',
    c: 'bg-blue-soft text-blue-ink',
    bar: 'bg-blue',
  },
  {
    icon: Repeat,
    title: 'Stable outcomes',
    promise: 'One customer’s coupon doesn’t change another’s outcome, and the world stays the same between logging and launch.',
    breaks: 'If it doesn’t, no estimator built from past logs can be trusted. OPE Lab’s simulation keeps this one true.',
    preset: 'easy',
    cta: 'See the easy case',
    c: 'bg-teal-soft text-teal-ink',
    bar: 'bg-teal',
  },
]

function YesNo({ yes, label }: { yes: boolean; label: string }) {
  return (
    <span className={cn('inline-flex size-7 items-center justify-center rounded-full', yes ? 'bg-primary-soft text-primary-ink' : 'bg-surface-sunken text-fg-subtle')}>
      {yes ? <Check size={14} aria-label={`Uses ${label}`} /> : <Minus size={14} aria-label={`No ${label}`} />}
    </span>
  )
}

function CheatSheet() {
  return (
    <section aria-labelledby="cheat-title" className="flex flex-col gap-xl">
      <div className="flex flex-col gap-xs">
        <p id="cheat-title" role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
          Cheat sheet
        </p>
        <p className="max-w-prose text-body text-fg-muted">What each method needs, and the trade-off it makes between bias (wrong on average) and variance (jumpy from run to run).</p>
      </div>
      <div className="overflow-x-auto rounded-xl border-thin border-line bg-surface shadow-sm">
        <table className="w-full min-w-180 text-left text-small">
          <thead className="bg-surface-muted text-caption font-semibold tracking-wider text-fg-muted uppercase">
            <tr>
              <th scope="col" className="px-lg py-md">Method</th>
              <th scope="col" className="px-lg py-md">Reward model</th>
              <th scope="col" className="px-lg py-md">Propensity weights</th>
              <th scope="col" className="px-lg py-md">Bias</th>
              <th scope="col" className="px-lg py-md">Variance</th>
              <th scope="col" className="px-lg py-md">Shines when</th>
            </tr>
          </thead>
          <tbody>
            {CHEAT.map((r) => {
              const e = ESTIMATOR_BY_KEY[r.key]
              return (
                <tr key={r.key} className="border-t-thin border-line transition-ds hover:bg-surface-muted">
                  <th scope="row" className="px-lg py-md">
                    <span className="flex items-center gap-sm font-semibold text-fg">
                      <MarkerGlyph meta={e} /> {e.name}
                    </span>
                  </th>
                  <td className="px-lg py-md">
                    <YesNo yes={r.model} label="a reward model" />
                  </td>
                  <td className="px-lg py-md">
                    <YesNo yes={r.weights} label="propensity weights" />
                  </td>
                  <td className="px-lg py-md">
                    <Badge label={r.bias} tone={LEVEL_TONE[r.bias]} dot />
                  </td>
                  <td className="px-lg py-md">
                    <Badge label={r.variance} tone={LEVEL_TONE[r.variance]} dot />
                  </td>
                  <td className="px-lg py-md text-fg-muted">{r.best}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="text-caption text-fg-subtle">“Depends” means it hinges on something you can’t see in the logs: how the old policy chose, or how good the reward model is.</p>
    </section>
  )
}

function Assumptions() {
  const { go } = useNav()
  const { applyPreset } = useOpe()
  return (
    <section aria-labelledby="assume-title" className="flex flex-col gap-xl">
      <div className="flex flex-col gap-xs">
        <p id="assume-title" role="heading" aria-level={2} className="font-display text-h2 font-semibold text-fg">
          Three promises every method relies on
        </p>
        <p className="max-w-prose text-body text-fg-muted">Break one and the estimates drift. Each button opens the Lab in a world where that promise is under pressure.</p>
      </div>
      <ul className="ds-stagger grid gap-lg md:grid-cols-3">
        {ASSUMPTIONS.map((a, i) => (
          <li key={a.title} style={{ '--i': i } as CSSProperties} className="relative flex flex-col gap-md overflow-hidden rounded-xl border-thin border-line bg-surface p-xl shadow-sm">
            <FlutedGlass as="span" aria-hidden palette="solid" size="sm" scrim="none" className={cn('absolute inset-x-0 top-0 h-2', a.bar)} />
            <span className={cn('flex size-11 items-center justify-center rounded-lg', a.c)}>
              <a.icon size={20} aria-hidden />
            </span>
            <p className="text-h3 font-semibold text-fg">{a.title}</p>
            <p className="text-body text-fg">{a.promise}</p>
            <p className="text-small text-fg-muted">
              <strong className="text-fg">When it breaks:</strong> {a.breaks}
            </p>
            <Button
              variant="secondary"
              size="sm"
              className="mt-auto self-start"
              iconEnd={<ArrowRight size={16} />}
              onClick={() => {
                applyPreset(a.preset)
                go('lab')
              }}
            >
              {a.cta}
            </Button>
          </li>
        ))}
      </ul>
    </section>
  )
}

export default function Estimators() {
  const { go } = useNav()
  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader
        tab="estimators"
        eyebrow="The contenders"
        title="Six ways to guess the other world"
        lead="Each method makes a different bet about the missing outcomes. Every one has its own shape and color, and you’ll spot them in the Lab."
      >
        <ul className="flex flex-wrap gap-sm">
          {RULES.map((r) => (
            <li key={r.text} className={cn('inline-flex items-center gap-sm rounded-full px-md py-xs text-small font-semibold', r.c)}>
              <r.icon size={16} aria-hidden />
              {r.text}
            </li>
          ))}
        </ul>
      </PageHeader>

      <ul className="ds-stagger grid gap-lg md:grid-cols-2 xl:grid-cols-3">
        {ESTIMATORS.map((e, i) => (
          <li
            key={e.key}
            style={{ '--i': i } as CSSProperties}
            className="group relative flex flex-col gap-lg overflow-hidden rounded-xl border-thin border-line bg-surface p-xl shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md"
          >
            <FlutedGlass as="span" aria-hidden palette="solid" size="sm" scrim="none" className={cn('absolute inset-x-0 top-0 h-2', e.bg)} />
            <span aria-hidden className={cn('absolute -top-16 -right-16 size-40 rounded-full opacity-10 blur-2xl transition-ds group-hover:opacity-25', e.bg)} />
            <div className="flex items-center gap-md">
              <span className="flex size-12 shrink-0 items-center justify-center rounded-full bg-surface-sunken transition-ds group-hover:scale-110">
                <MarkerGlyph meta={e} className="size-6" />
              </span>
              <div className="flex flex-col">
                <p role="heading" aria-level={2} className="text-h3 font-bold text-fg">
                  {e.name}
                </p>
                <p className="text-small text-fg-muted">{e.longName}</p>
              </div>
            </div>
            <p className="text-body text-fg">{e.blurb}</p>
            <p className="flex items-start gap-sm rounded-lg bg-warning-soft p-md text-small text-warning-ink">
              <TriangleAlert size={16} aria-hidden className="mt-2xs shrink-0" />
              <span>
                <strong>Fails when</strong> {e.failsWhen}
              </span>
            </p>
            <Disclosure title="Show the formula" icon={<Code2 size={16} aria-hidden className="text-fg-muted" />} className="mt-auto">
              <code className="block rounded-md bg-surface-sunken p-md text-small text-fg">{e.formula}</code>
            </Disclosure>
          </li>
        ))}
      </ul>

      <CheatSheet />
      <Assumptions />

      <FlutedGlass palette="lab" scrim="start" interactive drift className="flex flex-col items-start justify-between gap-lg rounded-2xl p-xl shadow-lg sm:flex-row sm:items-center md:p-2xl">
        <div className="flex flex-col gap-xs">
          <p className="ds-text-glow font-body text-h2 font-bold text-on-flute">Ready to see them race?</p>
          <p className="ds-text-glow text-body text-on-flute-muted">Pick a world in the Lab and watch all six guess at once.</p>
        </div>
        <Button variant="light" onClick={() => go('lab')} iconEnd={<ArrowRight size={18} />}>
          Open the Lab
        </Button>
      </FlutedGlass>
    </div>
  )
}
