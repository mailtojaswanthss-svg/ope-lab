import type { CSSProperties } from 'react'
import { FlaskConical } from 'lucide-react'
import Avatar from '../ui/Avatar'
import Badge from '../ui/Badge'
import Card from '../ui/Card'
import PageHeader from '../app/PageHeader'

const MEMBERS = ['A', 'B', 'C', 'D']

export default function Team() {
  return (
    <div className="flex flex-col gap-2xl">
      <PageHeader tab="team" eyebrow="Team" title="The people behind the lab" lead="Built for the Perceptron Hackathon 2026, Problem 3: “Did the policy actually work, or did it just look like it did?”" />
      <ul className="ds-stagger grid gap-lg sm:grid-cols-2 xl:grid-cols-4">
        {MEMBERS.map((m, i) => (
          <li key={m} style={{ '--i': i } as CSSProperties} className="flex flex-col items-start gap-lg rounded-xl border-thin border-line bg-surface p-xl shadow-sm transition-ds hover:-translate-y-1 hover:shadow-md">
            <div className="flex w-full items-center justify-between">
              <Avatar initials={m} index={i} />
              <Badge label="Placeholder" />
            </div>
            <div className="flex flex-col gap-2xs">
              <p role="heading" aria-level={2} className="text-h3 font-semibold text-fg">
                Team member
              </p>
              <p className="text-small text-fg-muted">Name & role to be added</p>
            </div>
          </li>
        ))}
      </ul>
      <Card variant="stage" className="flex flex-col gap-md sm:flex-row sm:items-center sm:justify-between">
        <p className="flex items-center gap-sm font-display text-h3 font-semibold">
          <FlaskConical size={20} aria-hidden className="text-stage-accent" /> OPE Lab
        </p>
        <p className="text-small text-stage-fg-muted">Simulated data for demonstration, not a real-world result. Every number is computed in your browser.</p>
      </Card>
    </div>
  )
}
