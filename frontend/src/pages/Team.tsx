import type { CSSProperties } from 'react'
import { BrainCircuit, Cpu, Database, FlaskConical, Lock, Repeat, ShieldCheck, Workflow } from 'lucide-react'
import Avatar from '../ui/Avatar'
import Badge from '../ui/Badge'
import Card, { CardTitle } from '../ui/Card'
import FlutedGlass from '../ui/FlutedGlass'
import { cn } from '../ui/cn'
import PageHeader from '../app/PageHeader'

const MEMBERS = ['A', 'B', 'C', 'D']

const PRINCIPLES = [
  { icon: ShieldCheck, title: 'No made-up numbers', text: 'Every figure is computed live. If there is no data, we say so instead of guessing.', c: 'bg-green-soft text-green-ink' },
  { icon: Lock, title: 'Private by design', text: 'Simulations run on your device. Nothing is uploaded or tracked.', c: 'bg-blue-soft text-blue-ink' },
  { icon: Repeat, title: 'Reproducible', text: 'Every world has a seed. Share it and anyone gets the same customers.', c: 'bg-pink-soft text-pink-ink' },
]

const STACK = [
  { icon: Workflow, label: 'React + TypeScript', c: 'bg-blue-soft text-blue-ink' },
  { icon: Cpu, label: 'Web Worker estimators', c: 'bg-teal-soft text-teal-ink' },
  { icon: BrainCircuit, label: 'Python + Streamlit', c: 'bg-orange-soft text-orange-ink' },
  { icon: Database, label: 'Open Bandit Pipeline', c: 'bg-yellow-soft text-yellow-ink' },
]

export default function Team() {
  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader tab="team" eyebrow="Team" title="The people behind the lab" lead="Built for the Perceptron Hackathon 2026, Problem 3: “Did the policy actually work, or did it just look like it did?”" />

      <ul className="ds-stagger grid gap-lg sm:grid-cols-2 xl:grid-cols-4">
        {MEMBERS.map((m, i) => (
          <li key={m} style={{ '--i': i } as CSSProperties} className="group flex flex-col overflow-hidden rounded-xl border-thin border-line bg-surface shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md">
            <FlutedGlass as="span" aria-hidden palette={(['estimators', 'lab', 'studies', 'story'] as const)[i]} scrim="none" className="h-16" />
            <div className="-mt-xl flex flex-col items-start gap-lg px-xl pb-xl">
              <div className="flex w-full items-end justify-between">
                <span className="rounded-full bg-surface p-xs transition-ds group-hover:scale-105">
                  <Avatar initials={m} index={i} />
                </span>
                <Badge label="Placeholder" />
              </div>
              <div className="flex flex-col gap-2xs">
                <p role="heading" aria-level={2} className="text-h3 font-semibold text-fg">
                  Team member
                </p>
                <p className="text-small text-fg-muted">Name & role to be added</p>
              </div>
            </div>
          </li>
        ))}
      </ul>

      <div className="grid gap-xl lg:grid-cols-12">
        <Card className="flex flex-col gap-lg lg:col-span-7">
          <CardTitle>About the project</CardTitle>
          <p className="text-body text-pretty text-fg">
            Companies judge new policies (who gets a coupon, which item to recommend) from logs collected under an old policy. Those logs are biased by the
            old policy’s own choices, so the obvious average can look like a win when it isn’t.
          </p>
          <p className="text-body text-pretty text-fg-muted">
            OPE Lab makes that trap visible. It simulates worlds where the truth is known, races six estimators against it, and stress-tests them under hidden
            bias and poor overlap, so you can see which methods to trust and when.
          </p>
          <div className="flex flex-col gap-sm border-t-thin border-line pt-lg">
            <p className="text-caption font-semibold tracking-wider text-fg-muted uppercase">Built with</p>
            <ul className="flex flex-wrap gap-sm">
              {STACK.map((s) => (
                <li key={s.label} className={cn('inline-flex items-center gap-sm rounded-full px-md py-xs text-small font-semibold', s.c)}>
                  <s.icon size={14} aria-hidden />
                  {s.label}
                </li>
              ))}
            </ul>
          </div>
        </Card>
        <ul className="ds-stagger flex flex-col gap-md lg:col-span-5">
          {PRINCIPLES.map((p, i) => (
            <li key={p.title} style={{ '--i': i } as CSSProperties} className="flex items-start gap-lg rounded-xl border-thin border-line bg-surface p-lg shadow-sm">
              <span className={cn('flex size-11 shrink-0 items-center justify-center rounded-lg', p.c)}>
                <p.icon size={20} aria-hidden />
              </span>
              <span className="flex flex-col gap-2xs">
                <span className="text-body font-semibold text-fg">{p.title}</span>
                <span className="text-small text-fg-muted">{p.text}</span>
              </span>
            </li>
          ))}
        </ul>
      </div>

      <FlutedGlass palette="home" interactive drift className="flex flex-col gap-md rounded-2xl p-xl shadow-lg sm:flex-row sm:items-center sm:justify-between md:p-2xl">
        <p className="ds-text-glow flex items-center gap-sm font-body text-h3 font-bold text-on-flute">
          <FlaskConical size={20} aria-hidden /> Off&#8209;Policy Evaluation Lab
        </p>
        <p className="ds-text-glow text-small text-on-flute-muted">Simulated data for demonstration, not a real-world result. Every number is computed in your browser.</p>
      </FlutedGlass>
    </div>
  )
}
