import type { ReactNode } from 'react'

/** Lightweight hover/focus hint. Never the only place critical info lives. */
export default function Tooltip({ content, children }: { content: string; children: ReactNode }) {
  return (
    <span className="group relative inline-flex">
      {children}
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-sm -translate-x-1/2 translate-y-1 rounded-md bg-fg px-sm py-2xs text-caption font-medium whitespace-nowrap text-canvas opacity-0 transition-ds group-focus-within:translate-y-0 group-focus-within:opacity-100 group-hover:translate-y-0 group-hover:opacity-100"
      >
        {content}
      </span>
    </span>
  )
}
