import { spawn } from 'node:child_process'
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = '@auto-decte/dsh-plugin'
export const inject = ['tools']

export interface Config {
  dataRoot: string
  implementationRoot: string
  pythonExecutable: string
  timeoutMs?: number
}

interface BridgeEnvelope {
  ok: boolean
  bridge_version: string
  operation?: string
  result?: unknown
  error?: { type?: string; message?: string }
}

interface ProposeResult {
  candidate_id: string
  certificate_id: string
  evidence_file_id: string
  evidence_uri: string
  expected_fact_version: number
}

interface VerifyResult {
  verified: boolean
  failures: string[]
  certificate_id: string
  candidate_id: string
  form_id: string
  field_key: string
  value: number
  expected_fact_version: number
  current_fact_version: number
}

const BRIDGE_VERSION = 'auto-decte.dsh-bridge.v1'
const MAX_OUTPUT_BYTES = 1024 * 1024

async function callBridge<T>(
  config: Config,
  request: Record<string, unknown>,
  signal: AbortSignal,
): Promise<T> {
  if (!config.dataRoot || !config.implementationRoot || !config.pythonExecutable) {
    throw new Error('AUTO_DECTE_CONFIG_INVALID')
  }
  const timeoutMs = config.timeoutMs ?? 10_000
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) {
    throw new Error('AUTO_DECTE_TIMEOUT_INVALID')
  }
  const payload = JSON.stringify({
    bridge_version: BRIDGE_VERSION,
    surface: 'model',
    data_root: config.dataRoot,
    ...request,
  })

  return await new Promise<T>((resolve, reject) => {
    const child = spawn(
      config.pythonExecutable,
      ['-m', 'app.integrations.dsh_bridge'],
      {
        cwd: config.implementationRoot,
        env: { ...process.env, PYTHONPATH: config.implementationRoot },
        windowsHide: true,
        stdio: ['pipe', 'pipe', 'pipe'],
      },
    )
    let stdout: Buffer = Buffer.alloc(0)
    let stderr: Buffer = Buffer.alloc(0)
    let settled = false
    const finish = (error?: Error, value?: T) => {
      if (settled) return
      settled = true
      clearTimeout(timer)
      signal.removeEventListener('abort', abort)
      if (error) reject(error)
      else resolve(value as T)
    }
    const terminate = (code: string) => {
      child.kill()
      finish(new Error(code))
    }
    const append = (current: Buffer, chunk: Buffer): Buffer => {
      const next = Buffer.concat([current, chunk])
      if (next.byteLength > MAX_OUTPUT_BYTES) terminate('AUTO_DECTE_BRIDGE_OUTPUT_LIMIT')
      return next
    }
    child.stdout.on('data', (chunk: Buffer) => { stdout = append(stdout, chunk) })
    child.stderr.on('data', (chunk: Buffer) => { stderr = append(stderr, chunk) })
    child.on('error', () => finish(new Error('AUTO_DECTE_BRIDGE_UNAVAILABLE')))
    child.on('close', (code) => {
      if (settled) return
      let envelope: BridgeEnvelope
      try {
        envelope = JSON.parse(stdout.toString('utf8')) as BridgeEnvelope
      } catch {
        finish(new Error('AUTO_DECTE_BRIDGE_INVALID_JSON'))
        return
      }
      if (code !== 0 || envelope.ok !== true || envelope.bridge_version !== BRIDGE_VERSION) {
        const detail = envelope.error?.message ?? stderr.toString('utf8').trim()
        finish(new Error(`AUTO_DECTE_BRIDGE_REJECTED${detail ? `: ${detail}` : ''}`))
        return
      }
      finish(undefined, envelope.result as T)
    })
    const abort = () => terminate('AUTO_DECTE_BRIDGE_ABORTED')
    signal.addEventListener('abort', abort, { once: true })
    const timer = setTimeout(() => terminate('AUTO_DECTE_BRIDGE_TIMEOUT'), timeoutMs)
    child.stdin.end(payload)
  })
}

export function apply(ctx: Context, config: Config): void {
  ctx.tools.register(defineTool({
    name: 'auto_decte_propose',
    description: 'Persist an AI suggestion as a parent-linked candidate; never commits a fact.',
    parameters: {
      form_id: { type: 'string', required: true },
      field_id: { type: 'string', required: true },
      parent_certificate_id: { type: 'string', required: true },
      value: { type: 'number', required: true },
      confidence: { type: 'number', required: true },
      session_id: { type: 'string', required: true },
      execution_id: { type: 'string', required: true },
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          candidate_id: { type: 'string', required: true },
          certificate_id: { type: 'string', required: true },
          evidence_file_id: { type: 'string', required: true },
          evidence_uri: { type: 'string', required: true },
          expected_fact_version: { type: 'integer', required: true },
        },
        additionalProperties: false,
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
    },
    async execute(args, exec) {
      return await callBridge<ProposeResult>(
        config, { operation: 'propose', ...args }, exec.signal,
      )
    },
  }))

  ctx.tools.register(defineTool({
    name: 'auto_decte_verify',
    description: 'Read and hash-check a persisted AUTO-DECTE candidate and its evidence.',
    parameters: {
      certificate_id: { type: 'string', required: true },
    },
    output: {
      schema: {
        type: 'object',
        properties: {
          verified: { type: 'boolean', required: true },
          failures: { type: 'array', items: { type: 'string' }, required: true },
          certificate_id: { type: 'string', required: true },
          candidate_id: { type: 'string', required: true },
          form_id: { type: 'string', required: true },
          field_key: { type: 'string', required: true },
          value: { type: 'number', required: true },
          expected_fact_version: { type: 'integer', required: true },
          current_fact_version: { type: 'integer', required: true },
        },
        additionalProperties: false,
      },
      render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
    },
    async execute(args, exec) {
      return await callBridge<VerifyResult>(
        config, { operation: 'verify', ...args }, exec.signal,
      )
    },
  }))
}
