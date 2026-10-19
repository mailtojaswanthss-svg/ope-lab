import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { cn } from './cn'

type Variant = 'primary' | 'secondary' | 'ghost' | 'stage'
type Size = 'md' | 'sm'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  iconStart?: ReactNode
  iconEnd?: ReactNode
}

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-primary text-on-primary shadow-glow hover:bg-primary-hover hover:-translate-y-0.5 active:translate-y-0',
  secondary: 'border-thin border-line-strong bg-surface text-fg hover:bg-surface-muted hover:-translate-y-0.5 active:translate-y-0',
  ghost: 'text-fg-muted hover:bg-surface-muted hover:text-fg',
  stage: 'border-thin border-stage-ghost bg-stage-surface text-stage-fg hover:bg-stage-line',
}

const SIZES: Record<Size, string> = {
  md: 'h-11 px-xl text-body',
  sm: 'h-9 px-lg text-small',
}

export default function Button({ variant = 'primary', size = 'md', iconStart, iconEnd, className, children, type = 'button', ...rest }: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        'group inline-flex shrink-0 cursor-pointer items-center justify-center gap-sm rounded-full font-semibold whitespace-nowrap transition-ds disabled:cursor-not-allowed disabled:opacity-50',
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...rest}
    >
      {iconStart}
      {children}
      {iconEnd && <span className="transition-ds group-hover:translate-x-0.5">{iconEnd}</span>}
    </button>
  )
}

export function IconButton({
  label,
  icon,
  variant = 'ghost',
  className,
  ...rest
}: Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'> & { label: string; icon: ReactNode; variant?: Variant }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      className={cn('inline-flex size-10 shrink-0 cursor-pointer items-center justify-center rounded-full transition-ds', VARIANTS[variant], className)}
      {...rest}
    >
      {icon}
    </button>
  )
}
