import { executeTask, type TaskInput, type TaskKind, type TaskOutput, type TaskResponse } from './tasks.ts'

/**
 * One worker per task kind so a slow decision map never blocks the bootstrap.
 * A new request for a busy kind terminates the in-flight worker: true
 * cancellation instead of letting stale computations queue up.
 */
interface Slot {
  worker: Worker
  busyId: number | null
}

const slots = new Map<TaskKind, Slot>()
let nextId = 1
let workersUnavailable = typeof Worker === 'undefined'

export class CancelledError extends Error {
  constructor() {
    super('cancelled')
    this.name = 'CancelledError'
  }
}

function spawn(): Worker | null {
  if (workersUnavailable) return null
  try {
    return new Worker(new URL('./worker.ts', import.meta.url), { type: 'module' })
  } catch (err) {
    console.warn('[ope] Web Worker unavailable, computing on the main thread.', err)
    workersUnavailable = true
    return null
  }
}

export interface RunningTask<K extends TaskKind> {
  promise: Promise<TaskOutput<K>>
  cancel(): void
}

export function runTask<K extends TaskKind>(kind: K, input: TaskInput<K>): RunningTask<K> {
  const id = nextId++
  let rejectFn: (e: unknown) => void = () => {}
  let settled = false

  let slot = slots.get(kind)
  if (slot && slot.busyId !== null) {
    slot.worker.terminate()
    slots.delete(kind)
    slot = undefined
  }
  if (!slot) {
    const worker = spawn()
    if (worker) {
      slot = { worker, busyId: null }
      slots.set(kind, slot)
    }
  }

  // Main-thread fallback (deferred so the UI can paint the pending state first).
  if (!slot) {
    let timer = 0
    const promise = new Promise<TaskOutput<K>>((resolve, reject) => {
      rejectFn = reject
      timer = window.setTimeout(() => {
        try {
          resolve(executeTask(kind, input))
        } catch (err) {
          reject(err)
        }
        settled = true
      }, 16)
    })
    return {
      promise,
      cancel: () => {
        if (settled) return
        window.clearTimeout(timer)
        rejectFn(new CancelledError())
      },
    }
  }

  const active = slot
  active.busyId = id
  const promise = new Promise<TaskOutput<K>>((resolve, reject) => {
    rejectFn = reject
    const onMessage = (event: MessageEvent<TaskResponse>) => {
      if (event.data.id !== id) return
      cleanup()
      if (event.data.ok) resolve(event.data.output as TaskOutput<K>)
      else reject(new Error(event.data.error))
    }
    const onError = (event: ErrorEvent) => {
      cleanup()
      slots.delete(kind)
      active.worker.terminate()
      reject(new Error(event.message || 'Worker crashed'))
    }
    const cleanup = () => {
      settled = true
      active.busyId = null
      active.worker.removeEventListener('message', onMessage)
      active.worker.removeEventListener('error', onError)
    }
    active.worker.addEventListener('message', onMessage)
    active.worker.addEventListener('error', onError)
    active.worker.postMessage({ id, kind, input })
  })

  return {
    promise,
    cancel: () => {
      if (settled) return
      settled = true
      if (slots.get(kind) === active && active.busyId === id) {
        active.worker.terminate()
        slots.delete(kind)
      }
      rejectFn(new CancelledError())
    },
  }
}
