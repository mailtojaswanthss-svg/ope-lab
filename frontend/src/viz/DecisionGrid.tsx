import type { CSSProperties } from 'react'
import { ESTIMATOR_BY_KEY } from '../ope/meta'
import { fmt } from '../ope/format'
import { DECISION_CONFOUNDING, DECISION_OVERLAP, type DecisionMapResult } from '../ope/study'
import Badge from '../ui/Badge'
import { cn } from '../ui/cn'
import { MarkerGlyph } from './Marker'

const nearest = (values: number[], v: number) => values.reduce((best, cur, i) => (Math.abs(cur - v) < Math.abs(values[best] - v) ? i : best), 0)

export default function DecisionGrid({ data, confounding, overlap }: { data: DecisionMapResult; confounding: number; overlap: number }) {
  const hereRow = nearest(DECISION_CONFOUNDING, confounding)
  const hereCol = nearest(DECISION_OVERLAP, overlap)

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-140 border-separate border-spacing-sm">
        <caption className="sr-only">Lowest-error estimator for each combination of confounding (rows) and overlap (columns)</caption>
        <thead>
          <tr>
            <th scope="col" className="w-28 text-left text-caption font-medium text-fg-subtle">
              hidden bias ↓ · overlap →
            </th>
            {DECISION_OVERLAP.map((o) => (
              <th key={o} scope="col" className="text-left text-small font-semibold text-fg-muted">
                overlap {o.toFixed(1)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="ds-stagger">
          {data.cells.map((row, ri) => (
            <tr key={DECISION_CONFOUNDING[ri]} style={{ '--i': ri } as CSSProperties}>
              <th scope="row" className="text-left text-small font-semibold text-fg-muted">
                c = {DECISION_CONFOUNDING[ri].toFixed(1)}
              </th>
              {row.map((cell, ci) => {
                const here = ri === hereRow && ci === hereCol
                const winner = ESTIMATOR_BY_KEY[cell.winner]
                const runner = ESTIMATOR_BY_KEY[cell.runnerUp]
                return (
                  <td key={cell.overlap} className={cn('rounded-lg bg-surface-sunken p-lg align-top transition-ds hover:-translate-y-0.5 hover:shadow-md', here && 'outline-ds outline-primary')}>
                    <div className="flex h-full flex-col gap-sm">
                      <span aria-hidden className={cn('h-1.5 w-10 rounded-full', cell.tie ? 'bg-linear-to-r from-est-dm to-est-dr' : winner.bg)} />
                      {cell.tie ? (
                        <>
                          <p className="text-body font-semibold text-fg">Tie</p>
                          <p className="flex flex-wrap items-center gap-xs text-caption text-fg-muted">
                            <MarkerGlyph meta={winner} className="size-3" /> {winner.name} ≈ <MarkerGlyph meta={runner} className="size-3" /> {runner.name}
                          </p>
                        </>
                      ) : (
                        <>
                          <p className="flex items-center gap-sm text-body font-semibold text-fg">
                            <MarkerGlyph meta={winner} /> {winner.name}
                          </p>
                          <p className="text-caption text-fg-muted">clear winner</p>
                        </>
                      )}
                      <p className="text-caption tabular-nums text-fg-subtle">error ≈ {fmt(cell.rmse[cell.winner])}</p>
                      {here && <Badge label="Your Lab world" tone="primary" dot />}
                    </div>
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
