import type { CSSProperties } from 'react'
import { ArrowRight, Code2, ShieldCheck, TriangleAlert, XCircle, Gauge } from 'lucide-react'
import { ESTIMATORS } from '../ope/meta'
import Button from '../ui/Button'
import Disclosure from '../ui/Disclosure'
import { cn } from '../ui/cn'
import PageHeader from '../app/PageHeader'
import { useNav } from '../app/nav'
import { MarkerGlyph } from '../viz/Marker'

const RULES = [
  { icon: XCircle, text: 'Never trust Naive on targeted data', c: 'bg-danger-soft text-danger-ink' },
  { icon: Gauge, text: 'Check the weights before IPW', c: 'bg-warning-soft text-warning-ink' },
  { icon: ShieldCheck, text: 'When in doubt, start with DR', c: 'bg-success-soft text-success-ink' },
]

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
            <span aria-hidden className={cn('absolute inset-x-0 top-0 h-1.5', e.bg)} />
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

      <div className="flex flex-col items-start justify-between gap-lg rounded-2xl bg-linear-to-r from-blue-soft via-primary-soft to-teal-soft p-xl sm:flex-row sm:items-center md:p-2xl">
        <div className="flex flex-col gap-xs">
          <p className="font-display text-h2 font-semibold text-fg">Ready to see them race?</p>
          <p className="text-body text-fg-muted">Pick a world in the Lab and watch all six guess at once.</p>
        </div>
        <Button onClick={() => go('lab')} iconEnd={<ArrowRight size={18} />}>
          Open the Lab
        </Button>
      </div>
    </div>
  )
}
