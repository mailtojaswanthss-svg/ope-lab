import { useRef, useState, type KeyboardEvent } from 'react'
import { Check, Download, EyeOff, Leaf, Shuffle, SlidersHorizontal, Target } from 'lucide-react'
import { effectiveB, type BootstrapResult } from '../ope/bootstrap'
import type { PointResult } from '../ope/estimators'
import { ESTIMATORS, ESTIMATOR_BY_KEY } from '../ope/meta'
import { errorTone, fmt, fmtSigned } from '../ope/format'
import { closestContender, labInsight } from '../ope/insights'
import { PRESETS, useOpe, type PresetId } from '../ope/OpeProvider'
import { V_STAR } from '../ope/simulate'
import { useWorkerTask } from '../ope/useWorkerTask'
import AnimatedNumber from '../ui/AnimatedNumber'
import Badge from '../ui/Badge'
import Button, { IconButton } from '../ui/Button'
import Card, { CardTitle } from '../ui/Card'
import Disclosure from '../ui/Disclosure'
import RangeSlider from '../ui/RangeSlider'
import Select from '../ui/Select'
import Switch from '../ui/Switch'
import Tabs, { TabPanel } from '../ui/Tabs'
import { cn } from '../ui/cn'
import Insight from '../app/Insight'
import PageHeader from '../app/PageHeader'
import DotWhisker from '../viz/DotWhisker'
import { MarkerGlyph } from '../viz/Marker'

const N_OPTIONS = [1000, 2000, 5000, 10000, 20000].map((n) => ({ value: String(n), label: `${n.toLocaleString('en-US')} customers` }))
const B_OPTIONS = [50, 100, 200].map((b) => ({ value: String(b), label: `${b} resamples` }))

const SCENARIO_STYLE: Record<Exclude<PresetId, 'custom'>, { icon: typeof Leaf; chip: string; ring: string; tagline: string }> = {
  easy: { icon: Leaf, chip: 'bg-green-soft text-green-ink', ring: 'border-green', tagline: 'A fair world. Everyone should do well.' },
  overlap: { icon: Target, chip: 'bg-blue-soft text-blue-ink', ring: 'border-blue', tagline: 'The old policy almost never explores.' },
  confounder: { icon: EyeOff, chip: 'bg-pink-soft text-pink-ink', ring: 'border-pink', tagline: 'A hidden trait decides who gets the coupon.' },
}

function ScenarioPicker({ value, onPick }: { value: PresetId; onPick: (id: PresetId) => void }) {
  const refs = useRef<(HTMLButtonElement | null)[]>([])
  const onKey = (e: KeyboardEvent, i: number) => {
    const d = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0
    if (!d) return
    e.preventDefault()
    const next = (i + d + PRESETS.length) % PRESETS.length
    onPick(PRESETS[next].id)
    refs.current[next]?.focus()
  }
  const focusIdx = Math.max(0, PRESETS.findIndex((p) => p.id === value))
  return (
    <div role="radiogroup" aria-label="Scenario" className="grid gap-md md:grid-cols-3">
      {PRESETS.map((p, i) => {
        const s = SCENARIO_STYLE[p.id]
        const active = value === p.id
        return (
          <button
            key={p.id}
            ref={(el) => {
              refs.current[i] = el
            }}
            type="button"
            role="radio"
            aria-checked={active}
            tabIndex={i === focusIdx ? 0 : -1}
            onClick={() => onPick(p.id)}
            onKeyDown={(e) => onKey(e, i)}
            className={cn(
              'group relative flex cursor-pointer items-start gap-md rounded-xl border-thick bg-surface p-lg text-left transition-ds hover:-translate-y-0.5',
              active ? cn(s.ring, 'shadow-md') : 'border-line hover:border-line-strong',
            )}
          >
            <span className={cn('flex size-11 shrink-0 items-center justify-center rounded-lg transition-ds group-hover:scale-110', s.chip)}>
              <s.icon size={20} aria-hidden />
            </span>
            <span className="flex flex-col gap-2xs">
              <span className="text-body font-semibold text-fg">{p.label}</span>
              <span className="text-small text-fg-muted">{s.tagline}</span>
            </span>
            {active && (
              <span className={cn('absolute top-md right-md flex size-6 animate-pop items-center justify-center rounded-full', s.chip)}>
                <Check size={14} aria-hidden />
              </span>
            )}
          </button>
        )
      })}
    </div>
  )
}

function downloadCsv(point: PointResult, boot: BootstrapResult | undefined, meta: Record<string, number>) {
  const header = [
    '# OPE Lab results (simulated in the browser)',
    `# ${Object.entries(meta)
      .map(([k, v]) => `${k}=${v}`)
      .join(', ')}`,
    `# true_value=${V_STAR.toFixed(6)}`,
    'estimator,estimate,error,ci_low,ci_high,se',
  ]
  const num = (x: number | undefined) => (x !== undefined && Number.isFinite(x) ? x.toFixed(6) : '')
  const rows = ESTIMATORS.map((e) => {
    const v = point.estimates[e.key]
    const ci = boot?.intervals[e.key]
    return [e.longName, num(v), num(v - V_STAR), num(ci?.lo), num(ci?.hi), num(ci?.se)].join(',')
  })
  const url = URL.createObjectURL(new Blob([[...header, ...rows].join('\n') + '\n'], { type: 'text/csv;charset=utf-8' }))
  const link = document.createElement('a')
  link.href = url
  link.download = `ope_lab_results_seed_${meta.seed}.csv`
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

function EstimateTiles({ point, boot, pending }: { point: PointResult; boot?: BootstrapResult; pending: boolean }) {
  return (
    <ul className="ds-stagger grid gap-md sm:grid-cols-2 lg:grid-cols-3">
      {ESTIMATORS.map((e, i) => {
        const v = point.estimates[e.key]
        const err = v - V_STAR
        const ci = boot?.intervals[e.key]
        return (
          <li key={e.key} style={{ '--i': i } as React.CSSProperties} className="relative flex flex-col gap-sm overflow-hidden rounded-lg bg-surface-sunken p-lg">
            <span aria-hidden className={cn('absolute inset-y-0 left-0 w-1', e.bg)} />
            <p className="flex items-center gap-sm text-small font-semibold text-fg">
              <MarkerGlyph meta={e} /> {e.longName}
            </p>
            <p className="font-display text-h2 font-semibold text-fg">
              <AnimatedNumber value={v} format={(x) => fmt(x)} />
            </p>
            <div className="flex flex-wrap items-center gap-sm">
              <Badge label={`error ${fmtSigned(err)}`} tone={errorTone(err)} dot />
              <span className="text-caption tabular-nums text-fg-muted">
                {ci && Number.isFinite(ci.lo) ? `95% CI ${fmt(ci.lo)} – ${fmt(ci.hi)}` : pending ? 'interval computing…' : 'interval unavailable'}
              </span>
            </div>
          </li>
        )
      })}
    </ul>
  )
}

function WeightHealth({ point, n }: { point: PointResult; n: number }) {
  const h = point.health
  const low = h.essPct < 0.1
  const items = [
    { label: 'Effective sample size', value: Math.round(h.ess).toLocaleString('en-US'), note: `${(h.essPct * 100).toFixed(1)}% of ${n.toLocaleString('en-US')}`, c: 'text-teal-ink' },
    { label: 'Largest weight', value: fmt(h.maxW, 2), note: 'biggest 1 / p̂(A|X)', c: 'text-primary-ink' },
    { label: 'Matched rows', value: h.matched.toLocaleString('en-US'), note: 'where both policies agree', c: 'text-blue-ink' },
    { label: 'Propensity range', value: `${fmt(h.pMin, 2)}–${fmt(h.pMax, 2)}`, note: 'clipped to [0.01, 0.99]', c: 'text-pink-ink' },
  ]
  return (
    <div className="flex flex-col gap-lg">
      <div className="flex flex-wrap items-center gap-md">
        <Badge label={low ? 'Low effective sample size' : 'Weights look healthy'} tone={low ? 'warning' : 'success'} dot />
        <p className="text-small text-fg-muted">
          {low ? 'A few rows carry most of the weight, so IPW-style estimates swing wildly.' : 'No single customer dominates the weighted estimates.'}
        </p>
      </div>
      <ul className="ds-stagger grid gap-md sm:grid-cols-2 lg:grid-cols-4">
        {items.map((it, i) => (
          <li key={it.label} style={{ '--i': i } as React.CSSProperties} className="flex flex-col gap-xs rounded-lg bg-surface-sunken p-lg">
            <p className="text-small text-fg-muted">{it.label}</p>
            <p className={cn('font-display text-h2 font-semibold tabular-nums', it.c)}>{it.value}</p>
            <p className="text-caption text-fg-subtle">{it.note}</p>
          </li>
        ))}
      </ul>
    </div>
  )
}

type DetailTab = 'estimates' | 'health'

export default function Lab() {
  const { params, setParam, applyPreset, presetId, reroll, sim, b, point, settling } = useOpe()
  const [showNaiveWorld, setShowNaiveWorld] = useState(true)
  const [detail, setDetail] = useState<DetailTab>('estimates')
  const bootstrap = useWorkerTask('bootstrap', { params: sim, b })
  const best = closestContender(point.estimates)
  const bestMeta = best ? ESTIMATOR_BY_KEY[best] : null
  const naiveErr = point.estimates.naive - V_STAR

  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader tab="lab" eyebrow="Live simulation" title="Pick a world. Watch six estimators guess." lead="Choose a scenario below. Every change simulates a fresh world in your browser and races all six methods against the truth." />

      <section aria-label="Scenario" className="flex flex-col gap-md">
        <div className="flex items-center gap-md">
          <p className="text-small font-semibold tracking-wider text-fg-muted uppercase">1 · Choose a scenario</p>
          {presetId === 'custom' && <Badge label="Custom settings" tone="primary" dot />}
        </div>
        <ScenarioPicker value={presetId} onPick={(id) => applyPreset(id)} />
      </section>

      <div className="grid items-start gap-xl xl:grid-cols-12">
        <div className="flex flex-col gap-xl xl:col-span-8">
          <p className="text-small font-semibold tracking-wider text-fg-muted uppercase">2 · See who gets it right</p>
          <div className="grid gap-md sm:grid-cols-3">
            <div className="rounded-xl bg-orange-soft p-lg">
              <p className="text-caption font-semibold text-orange-ink">The truth</p>
              <p className="mt-xs font-display text-h1 font-semibold text-orange-ink">{fmt(V_STAR)}</p>
            </div>
            <div className="rounded-xl bg-danger-soft p-lg">
              <p className="text-caption font-semibold text-danger-ink">Naive guess</p>
              <p className="mt-xs font-display text-h1 font-semibold text-danger-ink">
                <AnimatedNumber value={point.estimates.naive} format={(v) => fmt(v)} />
              </p>
              <p className="text-caption text-danger-ink">off by {fmtSigned(naiveErr)}</p>
            </div>
            <div className="rounded-xl bg-success-soft p-lg">
              <p className="text-caption font-semibold text-success-ink">Best fix · {bestMeta?.name ?? '—'}</p>
              <p className="mt-xs font-display text-h1 font-semibold text-success-ink">
                <AnimatedNumber value={best ? point.estimates[best] : Number.NaN} format={(v) => fmt(v)} />
              </p>
              <p className="text-caption text-success-ink">off by {best ? fmtSigned(point.estimates[best] - V_STAR) : '—'}</p>
            </div>
          </div>

          <Card variant="stage" className="flex flex-col gap-xl md:p-2xl">
            <div className="flex flex-wrap items-start justify-between gap-md">
              <div className="flex flex-col gap-2xs">
                <CardTitle onStage>Six guesses vs. the truth</CardTitle>
                <p className="text-small text-stage-fg-muted">The closer a marker sits to the orange line, the better the guess.</p>
              </div>
              {bootstrap.pending || settling ? (
                <Badge label="Simulating…" tone="stage" pulse />
              ) : bootstrap.error ? (
                <Badge label="Intervals unavailable" tone="danger" dot />
              ) : (
                <Badge label={`95% intervals · ${bootstrap.data?.b ?? b} resamples`} tone="stage" dot />
              )}
            </div>
            <DotWhisker estimates={point.estimates} intervals={bootstrap.data?.intervals} intervalsPending={bootstrap.pending} best={best} showNaiveWorld={showNaiveWorld} />
            <ul className="flex flex-wrap gap-x-xl gap-y-sm text-caption text-stage-fg-muted">
              <li className="flex items-center gap-sm">
                <span aria-hidden className="h-0.5 w-6 bg-insight" /> Truth (reality)
              </li>
              {showNaiveWorld && (
                <li className="flex items-center gap-sm">
                  <span aria-hidden className="w-6 border-t-thick border-dotted border-pink" /> Naive world
                </li>
              )}
              <li className="flex items-center gap-sm">
                <span aria-hidden className="size-3 rounded-full bg-stage-accent opacity-50" /> Closest correction
              </li>
              <li className="flex items-center gap-sm">
                <span aria-hidden className="h-0.5 w-6 bg-stage-fg-muted" /> 95% interval
              </li>
            </ul>
            {bootstrap.error && <p className="text-small text-stage-fg-muted">Intervals failed ({bootstrap.error}). The estimates are still live.</p>}
          </Card>

          <Insight>
            <p aria-live="polite">{labInsight(point)}</p>
          </Insight>
        </div>

        <Card className="flex flex-col gap-xl xl:sticky xl:top-24 xl:col-span-4">
          <div className="flex items-center gap-md">
            <span className="flex size-10 items-center justify-center rounded-lg bg-teal-soft text-teal-ink">
              <SlidersHorizontal size={18} aria-hidden />
            </span>
            <CardTitle>Fine-tune the world</CardTitle>
          </div>
          <RangeSlider
            label="Hidden bias"
            description="How much the hidden trait U decides who gets treated (c)."
            value={params.confounding}
            min={0}
            max={1}
            step={0.05}
            ends={['none', 'strong']}
            onChange={(v) => setParam('confounding', v)}
          />
          <RangeSlider
            label="Overlap"
            description="How often the old policy tried both options."
            value={params.overlap}
            min={0.05}
            max={1}
            step={0.05}
            ends={['rarely', 'often']}
            onChange={(v) => setParam('overlap', v)}
          />

          <div className="border-t-thin border-line pt-lg">
            <Disclosure title="More options" hint="Noise, sample size, intervals, seed">
              <div className="flex flex-col gap-xl">
                <RangeSlider label="Reward noise" value={params.noise} min={0} max={1} step={0.05} onChange={(v) => setParam('noise', v)} />
                <Select label="Sample size" options={N_OPTIONS} value={String(params.n)} onChange={(v) => setParam('n', Number(v))} />
                <Select
                  label="Bootstrap resamples"
                  description={effectiveB(params.n, params.b) < params.b ? 'Capped at 50 above 10,000 customers' : undefined}
                  options={B_OPTIONS}
                  value={String(params.b)}
                  onChange={(v) => setParam('b', Number(v))}
                />
                <div className="flex items-center justify-between gap-md rounded-lg bg-surface-sunken px-lg py-md">
                  <div className="flex flex-col">
                    <span className="text-caption text-fg-muted">Random seed</span>
                    <span className="font-mono text-body font-medium tabular-nums text-fg">{params.seed}</span>
                  </div>
                  <IconButton label="Roll a new random seed" variant="secondary" icon={<Shuffle size={16} />} onClick={reroll} />
                </div>
                <Switch label="Show the naive world" description="Dotted line at the Naive guess." checked={showNaiveWorld} onChange={setShowNaiveWorld} />
              </div>
            </Disclosure>
          </div>
        </Card>
      </div>

      <Card className="flex flex-col gap-xl">
        <div className="flex flex-wrap items-center justify-between gap-lg">
          <div className="flex flex-col gap-2xs">
            <p className="text-small font-semibold tracking-wider text-fg-muted uppercase">3 · Dig deeper</p>
            <p className="text-small text-fg-muted">
              Seed {sim.seed} · {sim.n.toLocaleString('en-US')} customers · error = estimate − truth
            </p>
          </div>
          <Button
            variant="secondary"
            size="sm"
            iconStart={<Download size={16} />}
            onClick={() =>
              downloadCsv(point, bootstrap.data, {
                seed: sim.seed,
                n: sim.n,
                confounding: sim.confounding,
                overlap: sim.overlap,
                noise: sim.noise,
                bootstrap_b: bootstrap.data?.b ?? b,
              })
            }
          >
            Download CSV
          </Button>
        </div>
        <Tabs
          idPrefix="lab-detail"
          label="Result details"
          value={detail}
          onChange={setDetail}
          items={[
            { id: 'estimates', label: 'All estimates' },
            { id: 'health', label: 'Weight health' },
          ]}
        />
        <TabPanel key={detail} idPrefix="lab-detail" id={detail}>
          {detail === 'estimates' ? <EstimateTiles point={point} boot={bootstrap.data} pending={bootstrap.pending} /> : <WeightHealth point={point} n={sim.n} />}
        </TabPanel>
        <p className="text-caption text-fg-subtle">
          A TypeScript port of the Python app’s estimators. Results match it statistically, not bit for bit, because the random generator differs.
        </p>
      </Card>
    </div>
  )
}
