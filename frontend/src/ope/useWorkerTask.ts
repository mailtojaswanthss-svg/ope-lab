import { useEffect, useState } from 'react'
import { CancelledError, runTask } from './client.ts'
import type { TaskInput, TaskKind, TaskOutput } from './tasks.ts'

export interface WorkerTaskState<K extends TaskKind> {
  data: TaskOutput<K> | undefined
  pending: boolean
  error: string | null
}

/** Runs a worker task whenever `input` changes; keeps the previous result while recomputing. */
export function useWorkerTask<K extends TaskKind>(kind: K, input: TaskInput<K>, enabled = true): WorkerTaskState<K> {
  const key = JSON.stringify(input)
  const [state, setState] = useState<WorkerTaskState<K>>({ data: undefined, pending: enabled, error: null })

  useEffect(() => {
    if (!enabled) return
    let alive = true
    setState((s) => ({ ...s, pending: true, error: null }))
    const task = runTask(kind, JSON.parse(key) as TaskInput<K>)
    task.promise.then(
      (data) => {
        if (alive) setState({ data, pending: false, error: null })
      },
      (err: unknown) => {
        if (!alive || err instanceof CancelledError) return
        console.error(`[ope] ${kind} failed`, err)
        setState((s) => ({ ...s, pending: false, error: err instanceof Error ? err.message : String(err) }))
      },
    )
    return () => {
      alive = false
      task.cancel()
    }
  }, [kind, key, enabled])

  return state
}
