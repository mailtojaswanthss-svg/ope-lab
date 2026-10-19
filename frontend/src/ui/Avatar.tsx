import { cn } from './cn'

const TONES = ['bg-primary-soft text-primary-ink', 'bg-teal-soft text-teal-ink', 'bg-orange-soft text-orange-ink', 'bg-pink-soft text-pink-ink']

export default function Avatar({ initials, index = 0 }: { initials: string; index?: number }) {
  return (
    <span aria-hidden className={cn('inline-flex size-14 items-center justify-center rounded-full font-display text-h3 font-semibold', TONES[index % TONES.length])}>
      {initials}
    </span>
  )
}
