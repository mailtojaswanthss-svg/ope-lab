import { cn } from './cn'

export type Tone = 'neutral' | 'primary' | 'success' | 'warning' | 'danger' | 'teal' | 'orange' | 'pink' | 'blue' | 'yellow' | 'green' | 'stage'

export const TONE_SOFT: Record<Tone, string> = {
  neutral: 'bg-surface-sunken text-fg-muted',
  primary: 'bg-primary-soft text-primary-ink',
  success: 'bg-success-soft text-success-ink',
  warning: 'bg-warning-soft text-warning-ink',
  danger: 'bg-danger-soft text-danger-ink',
  teal: 'bg-teal-soft text-teal-ink',
  orange: 'bg-orange-soft text-orange-ink',
  pink: 'bg-pink-soft text-pink-ink',
  blue: 'bg-blue-soft text-blue-ink',
  yellow: 'bg-yellow-soft text-yellow-ink',
  green: 'bg-green-soft text-green-ink',
  stage: 'bg-stage-surface text-stage-fg',
}

const DOT: Record<Tone, string> = {
  neutral: 'bg-fg-subtle',
  primary: 'bg-primary',
  success: 'bg-success',
  warning: 'bg-warning',
  danger: 'bg-danger',
  teal: 'bg-teal',
  orange: 'bg-orange',
  pink: 'bg-pink',
  blue: 'bg-blue',
  yellow: 'bg-yellow',
  green: 'bg-green',
  stage: 'bg-stage-accent',
}

export default function Badge({ label, tone = 'neutral', dot, pulse, className }: { label: string; tone?: Tone; dot?: boolean; pulse?: boolean; className?: string }) {
  return (
    <span className={cn('inline-flex items-center gap-xs rounded-full px-md py-2xs text-caption font-semibold whitespace-nowrap', TONE_SOFT[tone], className)}>
      {(dot || pulse) && <span aria-hidden className={cn('size-1.5 rounded-full', DOT[tone], pulse && 'animate-pulse')} />}
      {label}
    </span>
  )
}
