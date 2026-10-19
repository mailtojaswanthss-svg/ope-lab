import { useState, type ReactNode } from 'react'
import { ArrowRight, Grid3x3, ShieldCheck, TrendingDown } from 'lucide-react'
import { ESTIMATOR_BY_KEY, ESTIMATORS } from '../ope/meta'
import { fmt } from '../ope/format'
import { useOpe } from '../ope/OpeProvider'
import type { DecisionMapResult, FailureStudyResult } from '../ope/study'
import type { SensitivityResult } from '../ope/sensitivity'
import { V_STAR } from '../ope/simulate'
import { useWorkerTask } from '../ope/useWorkerTask'
import Badge, { type Tone } from '../ui/Badge'
import Button from '../ui/Button'
import Card, { CardTitle } from '../ui/Card'
import Switch from '../ui/Switch'
import Tabs, { TabPanel } from '../ui/Tabs'
import { cn } from '../ui/cn'
import Insight from '../app/Insight'
import PageHeader from '../app/PageHeader'
import TaskStatus, { TaskError, TaskSkeleton } from '../app/TaskStatus'
import { useNav } from '../app/nav'
import DecisionGrid from '../viz/DecisionGrid'
import FailureChart from '../viz/FailureChart'
import SensitivityBand from '../viz/SensitivityBand'

type StudyId = 'failure' | 'decision' | 'sensitivity'

function StudyCard({ title, question, status, children }: { title: string; question: string; status: ReactNode; children: ReactNode }) {
  return (
    <Card className="flex flex-col gap-xl">
      <div className="flex flex-wrap items-start justify-between gap-md">
        <div className="flex flex-col gap-2xs">
          <CardTitle>{title}</CardTitle>
          <p className="text-body text-fg-muted">{question}</p>
        </div>
        {status}
      </div>
      {children}
    </Card>
  )
}

function failureInsight(d: FailureStudyResult) {
  const last = d.cs.length - 1
  const corrected = ESTIMATORS.filter((e) => e.key !== 'naive')
  const worst = corrected.reduce((w, e) => (d.errors[e.key][last] > d.errors[w.key][last] ? e : w), corrected[0])
  return `With maximum hidden bias, Naive misses by ${fmt(d.errors.naive[last])} on average (it started at ${fmt(d.errors.naive[0])}). The worst corrected method, ${worst.name}, misses by only ${fmt(d.errors[worst.key][last])}.`
}

function Failure() {
  const { sim } = useOpe()
  const [showNaive, setShowNaive] = useState(true)
  const study = useWorkerTask('failure', { n: sim.n, overlap: sim.overlap, noise: sim.noise, seed: sim.seed })
  return (
    <div className="flex flex-col gap-xl">
      <StudyCard title="Turn up the hidden bias" question="As the hidden trait drives more of the decision, how far off does each method land?" status={<TaskStatus pending={study.pending} error={study.error} />}>
        <div className="max-w-80">
          <Switch label="Include Naive" description="Hide it to zoom in on the others." checked={showNaive} onChange={setShowNaive} />
        </div>
        <TaskError error={study.error} />
        {study.data ? (
          <div className={cn('transition-ds', study.pending && 'opacity-50')}>
            <FailureChart data={study.data} showNaive={showNaive} current={sim.confounding} />
          </div>
        ) : (
          !study.error && <TaskSkeleton label="Simulating 55 worlds…" />
        )}
      </StudyCard>
      {study.data && <Insight>{failureInsight(study.data)}</Insight>}
    </div>
  )
}

function decisionInsight(d: DecisionMapResult) {
  const cells = d.cells.flat()
  const ties = cells.filter((c) => c.tie).length
  const wins = new Map<string, number>()
  for (const c of cells) if (!c.tie) wins.set(c.winner, (wins.get(c.winner) ?? 0) + 1)
  const top = [...wins.entries()].sort((p, q) => q[1] - p[1])[0]
  const base = `${ties} of 9 worlds are a statistical tie: several corrected methods are equally good there.`
  return top ? `${base} ${ESTIMATOR_BY_KEY[top[0] as keyof typeof ESTIMATOR_BY_KEY].name} wins outright in ${top[1]}.` : `${base} No single method dominates.`
}

function Decision() {
  const { sim, params } = useOpe()
  const map = useWorkerTask('decision', { noise: sim.noise, seed: sim.seed })
  return (
    <div className="flex flex-col gap-xl">
      <StudyCard title="Which method should you trust?" question="Nine kinds of world, 20 simulations each. The winner has the smallest typical error." status={<TaskStatus pending={map.pending} error={map.error} />}>
        <TaskError error={map.error} />
        {map.data ? (
          <div className={cn('transition-ds', map.pending && 'opacity-50')}>
            <DecisionGrid data={map.data} confounding={params.confounding} overlap={params.overlap} />
          </div>
        ) : (
          !map.error && <TaskSkeleton label="Running 180 simulations…" />
        )}
        <p className="text-caption text-fg-subtle">Naive is excluded. “Tie” means the runner-up isn’t significantly worse (95% paired test).</p>
      </StudyCard>
      {map.data && <Insight>{decisionInsight(map.data)}</Insight>}
    </div>
  )
}

function verdict(d: SensitivityResult): { value: string; tone: Tone; badge: string; text: string } {
  if (d.lambdaStar === null) return { value: 'Λ* > 3', tone: 'danger', badge: 'Not covered', text: 'Even allowing every weight to be off by 3×, the range never reaches the truth.' }
  const tight = d.lambdaStar <= 1.3
  return {
    value: `Λ* = ${d.lambdaStar.toFixed(2)}`,
    tone: tight ? 'success' : 'warning',
    badge: tight ? 'Robust' : 'Needs a wide band',
    text: `Allow each weight to be off by ${d.lambdaStar.toFixed(2)}× and the plausible range already covers the truth (${fmt(V_STAR, 4)}).`,
  }
}

function Sensitivity() {
  const { sim } = useOpe()
  const sens = useWorkerTask('sensitivity', { params: sim })
  const v = sens.data ? verdict(sens.data) : null
  return (
    <div className="grid items-start gap-xl lg:grid-cols-12">
      <Card variant="stage" className="relative isolate flex flex-col gap-lg overflow-hidden lg:col-span-4">
        <span aria-hidden className="absolute -top-16 -right-16 -z-10 size-56 animate-float rounded-full bg-teal opacity-30 blur-3xl" />
        <p className="text-small font-semibold text-stage-fg-muted">How much hidden bias until we’re wrong?</p>
        <p className="font-display text-stat font-semibold">{v ? v.value : 'Λ* …'}</p>
        {v && <Badge label={v.badge} tone={v.tone} dot className="self-start" />}
        <p className="text-body text-stage-fg-muted">{v ? v.text : 'Computing the bounds…'}</p>
      </Card>
      <div className="lg:col-span-8">
        <StudyCard title="The plausible range as bias grows" question="Each weight may be up to Λ× too big or too small. The band is every answer that’s still possible." status={<TaskStatus pending={sens.pending} error={sens.error} />}>
          <TaskError error={sens.error} />
          {sens.data ? (
            <div className={cn('transition-ds', sens.pending && 'opacity-50')}>
              <SensitivityBand data={sens.data} />
            </div>
          ) : (
            !sens.error && <TaskSkeleton label="Computing bounds…" />
          )}
        </StudyCard>
      </div>
    </div>
  )
}

export default function Studies() {
  const { go } = useNav()
  const { sim } = useOpe()
  const [study, setStudy] = useState<StudyId>('failure')
  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader tab="studies" eyebrow="Stress tests" title="Push the estimators until they break" lead="Three experiments, one at a time. Each one uses the world you set up in the Lab.">
        <div className="flex flex-wrap items-center gap-md">
          <Badge label={`Lab world: bias ${sim.confounding.toFixed(2)} · overlap ${sim.overlap.toFixed(2)}`} tone="pink" dot />
          <Button variant="ghost" size="sm" onClick={() => go('lab')} iconEnd={<ArrowRight size={16} />}>
            Change it
          </Button>
        </div>
      </PageHeader>

      <Tabs
        idPrefix="studies"
        label="Studies"
        value={study}
        onChange={setStudy}
        className="self-start"
        items={[
          { id: 'failure', label: 'Failure study', icon: <TrendingDown size={16} aria-hidden /> },
          { id: 'decision', label: 'Decision map', icon: <Grid3x3 size={16} aria-hidden /> },
          { id: 'sensitivity', label: 'Sensitivity', icon: <ShieldCheck size={16} aria-hidden /> },
        ]}
      />
      <TabPanel key={study} idPrefix="studies" id={study}>
        {study === 'failure' ? <Failure /> : study === 'decision' ? <Decision /> : <Sensitivity />}
      </TabPanel>
    </div>
  )
}
