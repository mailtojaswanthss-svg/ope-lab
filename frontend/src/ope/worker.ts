import { executeTask, type TaskRequest, type TaskResponse } from './tasks.ts'

self.onmessage = (event: MessageEvent<TaskRequest>) => {
  const { id, kind, input } = event.data
  let response: TaskResponse
  try {
    response = { id, ok: true, output: executeTask(kind, input) }
  } catch (err) {
    response = { id, ok: false, error: err instanceof Error ? err.message : String(err) }
  }
  self.postMessage(response)
}
