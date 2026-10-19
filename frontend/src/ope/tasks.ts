import { runBootstrap, type BootstrapResult } from './bootstrap.ts'
import { runSensitivity, type SensitivityResult } from './sensitivity.ts'
import { runDecisionMap, runFailureStudy, type DecisionMapResult, type FailureStudyResult } from './study.ts'
import type { SimParams } from './simulate.ts'

export interface TaskMap {
  bootstrap: { input: { params: SimParams; b: number }; output: BootstrapResult }
  failure: { input: { n: number; overlap: number; noise: number; seed: number }; output: FailureStudyResult }
  decision: { input: { noise: number; seed: number }; output: DecisionMapResult }
  sensitivity: { input: { params: SimParams }; output: SensitivityResult }
}

export type TaskKind = keyof TaskMap
export type TaskInput<K extends TaskKind> = TaskMap[K]['input']
export type TaskOutput<K extends TaskKind> = TaskMap[K]['output']

export interface TaskRequest<K extends TaskKind = TaskKind> {
  id: number
  kind: K
  input: TaskInput<K>
}

export type TaskResponse = { id: number; ok: true; output: unknown } | { id: number; ok: false; error: string }

export function executeTask<K extends TaskKind>(kind: K, input: TaskInput<K>): TaskOutput<K> {
  switch (kind) {
    case 'bootstrap': {
      const i = input as TaskInput<'bootstrap'>
      return runBootstrap(i.params, i.b) as TaskOutput<K>
    }
    case 'failure':
      return runFailureStudy(input as TaskInput<'failure'>) as TaskOutput<K>
    case 'decision':
      return runDecisionMap(input as TaskInput<'decision'>) as TaskOutput<K>
    case 'sensitivity':
      return runSensitivity((input as TaskInput<'sensitivity'>).params) as TaskOutput<K>
    default:
      throw new Error(`Unknown task: ${String(kind)}`)
  }
}
