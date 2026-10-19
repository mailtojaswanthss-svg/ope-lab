import type { HTMLAttributes, PointerEvent } from 'react'
import { cn } from './cn'

export type FlutePalette = 'home' | 'story' | 'estimators' | 'lab' | 'studies' | 'real-data' | 'team' | 'solid'

interface FlutedGlassProps extends HTMLAttributes<HTMLElement> {
  /** A spectrum from global.css (--ds-gradient-*), or `solid` to tint with a bg-* class. */
  palette?: FlutePalette
  /** Where the readability shade sits behind text. */
  scrim?: 'center' | 'start' | 'none'
  size?: 'md' | 'sm'
  /** Light follows the pointer. */
  interactive?: boolean
  /** Slowly slide the spectrum. Use on large hero surfaces only. */
  drift?: boolean
  as?: 'div' | 'section' | 'header' | 'span'
}

/** Fluted-glass surface: a drifting color spectrum seen through vertical glass ribs. */
export default function FlutedGlass({
  palette = 'home',
  scrim = 'center',
  size = 'md',
  interactive = false,
  drift = false,
  as: Tag = 'div',
  className,
  onPointerMove,
  onPointerLeave,
  children,
  ...rest
}: FlutedGlassProps) {
  const move = (e: PointerEvent<HTMLElement>) => {
    if (interactive) {
      const r = e.currentTarget.getBoundingClientRect()
      e.currentTarget.style.setProperty('--flute-x', `${(((e.clientX - r.left) / r.width) * 100).toFixed(1)}%`)
      e.currentTarget.style.setProperty('--flute-y', `${(((e.clientY - r.top) / r.height) * 100).toFixed(1)}%`)
    }
    onPointerMove?.(e)
  }
  const leave = (e: PointerEvent<HTMLElement>) => {
    if (interactive) {
      e.currentTarget.style.removeProperty('--flute-x')
      e.currentTarget.style.removeProperty('--flute-y')
    }
    onPointerLeave?.(e)
  }
  return (
    <Tag
      data-palette={palette}
      data-scrim={scrim}
      data-size={size}
      data-drift={drift}
      className={cn('ds-fluted', className)}
      onPointerMove={move}
      onPointerLeave={leave}
      {...rest}
    >
      {children}
    </Tag>
  )
}
