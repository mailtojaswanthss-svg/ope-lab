import Badge from '../ui/Badge'

export default function TaskStatus({ pending, error }: { pending: boolean; error: string | null }) {
  if (pending) return <Badge label="Computing…" tone="primary" pulse />
  if (error) return <Badge label="Failed" tone="danger" dot />
  return <Badge label="Up to date" tone="success" dot />
}

export function TaskError({ error }: { error: string | null }) {
  if (!error) return null
  return <p className="text-small text-danger-ink">This study couldn’t be computed ({error}). Everything else still works.</p>
}

export function TaskSkeleton({ label }: { label: string }) {
  return (
    <div className="flex h-80 items-center justify-center rounded-lg bg-surface-sunken">
      <p className="animate-pulse text-small font-medium text-fg-muted">{label}</p>
    </div>
  )
}
