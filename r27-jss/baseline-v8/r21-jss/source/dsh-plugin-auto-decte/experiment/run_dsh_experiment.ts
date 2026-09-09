import { spawnSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdirSync, readFileSync, writeFileSync, existsSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { Context } from '@deepseek-ai/cordis'
import { CallId } from '@deepseek-ai/dsh-llm'
import SystemPrompt from '@deepseek-ai/dsh-system-prompt'
import ToolRuntime from '@deepseek-ai/dsh-tools'
import * as AutoDectePlugin from '../src/plugin.js'

const BRIDGE_VERSION = 'auto-decte.dsh-bridge.v1'

interface HostEnvelope {
  ok: boolean
  result?: Record<string, unknown>
  error?: { message?: string }
}

interface Fixture {
  form_id: string
  field_id: string
  parent_certificate_id: string
}

interface ToolSuccess {
  isError: false
  value: Record<string, unknown>
}

function sha256(path: string): string {
  return createHash('sha256').update(readFileSync(path)).digest('hex')
}

function hostCall(
  python: string,
  implementationRoot: string,
  dataRoot: string,
  operation: string,
  values: Record<string, unknown> = {},
): Record<string, unknown> {
  const request = JSON.stringify({
    bridge_version: BRIDGE_VERSION,
    surface: 'host',
    operation,
    data_root: dataRoot,
    ...values,
  })
  const child = spawnSync(python, ['-m', 'app.integrations.dsh_bridge'], {
    cwd: implementationRoot,
    env: { ...process.env, PYTHONPATH: implementationRoot },
    input: request,
    encoding: 'utf8',
    timeout: 15_000,
    windowsHide: true,
    maxBuffer: 1024 * 1024,
  })
  const envelope = JSON.parse(child.stdout) as HostEnvelope
  if (child.status !== 0 || !envelope.ok || !envelope.result) {
    throw new Error(envelope.error?.message ?? `host bridge exited ${child.status}`)
  }
  return envelope.result
}

async function runtime(config: AutoDectePlugin.Config) {
  const ctx = new Context()
  await ctx.plugin(SystemPrompt)
  await ctx.plugin(ToolRuntime)
  const pluginFiber = await ctx.plugin(AutoDectePlugin, config)
  return { ctx, pluginFiber }
}

function toolValue(result: unknown): Record<string, unknown> {
  const typed = result as ToolSuccess
  if (typed.isError) throw new Error(`tool failed: ${JSON.stringify(result)}`)
  return typed.value
}

function fixture(
  python: string,
  implementationRoot: string,
  dataRoot: string,
): Fixture {
  mkdirSync(dataRoot, { recursive: true })
  return hostCall(python, implementationRoot, dataRoot, 'init-fixture') as unknown as Fixture
}

function authorityDigest(
  python: string,
  implementationRoot: string,
  dataRoot: string,
): string {
  return String(
    hostCall(python, implementationRoot, dataRoot, 'export-receipt').authority_state_sha256,
  )
}

async function propose(
  ctx: Context,
  id: string,
  seed: Fixture,
  value = 8,
): Promise<Record<string, unknown>> {
  return toolValue(await ctx.tools.execute({
    callId: CallId(id),
    name: 'auto_decte_propose',
    arguments: {
      form_id: seed.form_id,
      field_id: seed.field_id,
      parent_certificate_id: seed.parent_certificate_id,
      value,
      confidence: 0.73,
      session_id: `SESSION-${id}`,
      execution_id: `EXEC-${id}`,
    },
    signal: new AbortController().signal,
  }))
}

async function main(): Promise<void> {
  const [outputArg, implementationArg, pythonArg, dshRootArg] = process.argv.slice(2)
  if (!outputArg || !implementationArg || !pythonArg || !dshRootArg) {
    throw new Error('usage: run_dsh_experiment OUTPUT IMPLEMENTATION PYTHON DSH_ROOT')
  }
  const output = resolve(outputArg)
  const implementationRoot = resolve(implementationArg)
  const python = resolve(pythonArg)
  const dshRoot = resolve(dshRootArg)
  if (existsSync(output)) throw new Error(`refusing to overwrite existing output: ${output}`)
  mkdirSync(output, { recursive: false })
  const scenariosRoot = join(output, 'scenarios')
  mkdirSync(scenariosRoot)

  const baseConfig: AutoDectePlugin.Config = {
    dataRoot: '',
    implementationRoot,
    pythonExecutable: python,
    timeoutMs: 15_000,
  }
  const results: Record<string, unknown> = {}

  // D1: real pinned Cordis plugin lifecycle + ToolRuntime composition.
  const d1Root = join(scenariosRoot, 'D1')
  fixture(python, implementationRoot, d1Root)
  const d1 = await runtime({ ...baseConfig, dataRoot: d1Root })
  const names = d1.ctx.tools.schemas().map(schema => schema.name).sort()
  results.D1 = {
    passed: JSON.stringify(names) === JSON.stringify(['auto_decte_propose', 'auto_decte_verify']),
    tool_names: names,
    exact_tool_count: names.length,
  }

  // D2: a model-surface call persists only a candidate at fact version zero.
  const d2Root = join(scenariosRoot, 'D2')
  const d2Seed = fixture(python, implementationRoot, d2Root)
  const d2Runtime = await runtime({ ...baseConfig, dataRoot: d2Root })
  const d2Proposal = await propose(d2Runtime.ctx, 'D2', d2Seed)
  const d2Receipt = hostCall(python, implementationRoot, d2Root, 'export-receipt')
  const d2Form = (d2Receipt.forms as Array<Record<string, unknown>>)[0]
  results.D2 = {
    passed: d2Form?.current_record_version === 0,
    proposal: d2Proposal,
    current_fact_version: d2Form?.current_record_version,
  }

  // D3: a separate trusted host accepts exactly one successor version.
  const d3Root = join(scenariosRoot, 'D3')
  const d3Seed = fixture(python, implementationRoot, d3Root)
  const d3Runtime = await runtime({ ...baseConfig, dataRoot: d3Root })
  const d3Proposal = await propose(d3Runtime.ctx, 'D3', d3Seed)
  const d3Confirm = hostCall(python, implementationRoot, d3Root, 'host-confirm', {
    certificate_id: d3Proposal.certificate_id,
    value: 8,
    expected_version: 0,
    actor_id: 'reviewer-1',
  })
  results.D3 = { passed: d3Confirm.fact_version === 1, confirmation: d3Confirm }

  // D4: host correction preserves the AI candidate while authorizing a different value.
  const d4Root = join(scenariosRoot, 'D4')
  const d4Seed = fixture(python, implementationRoot, d4Root)
  const d4Runtime = await runtime({ ...baseConfig, dataRoot: d4Root })
  const d4Proposal = await propose(d4Runtime.ctx, 'D4', d4Seed, 8)
  const d4Confirm = hostCall(python, implementationRoot, d4Root, 'host-confirm', {
    certificate_id: d4Proposal.certificate_id,
    value: 9,
    expected_version: 0,
    actor_id: 'reviewer-1',
  })
  const d4Receipt = hostCall(python, implementationRoot, d4Root, 'export-receipt')
  results.D4 = {
    passed: (d4Confirm.values as Record<string, unknown>).total_quantity === 9,
    proposed_value: 8,
    authorized_value: (d4Confirm.values as Record<string, unknown>).total_quantity,
    receipt: d4Receipt,
  }

  // D5: stale re-confirmation rejects and leaves database bytes unchanged.
  const d5Root = join(scenariosRoot, 'D5')
  const d5Seed = fixture(python, implementationRoot, d5Root)
  const d5Runtime = await runtime({ ...baseConfig, dataRoot: d5Root })
  const d5Proposal = await propose(d5Runtime.ctx, 'D5', d5Seed)
  hostCall(python, implementationRoot, d5Root, 'host-confirm', {
    certificate_id: d5Proposal.certificate_id, value: 8, expected_version: 0,
  })
  const d5Before = authorityDigest(python, implementationRoot, d5Root)
  let d5Rejected = false
  try {
    hostCall(python, implementationRoot, d5Root, 'host-confirm', {
      certificate_id: d5Proposal.certificate_id, value: 8, expected_version: 0,
    })
  } catch { d5Rejected = true }
  const d5After = authorityDigest(python, implementationRoot, d5Root)
  results.D5 = { passed: d5Rejected && d5Before === d5After, rejected: d5Rejected, before: d5Before, after: d5After }

  // D6: a byte mutation is detected before authority admission; DB is unchanged.
  const d6Root = join(scenariosRoot, 'D6')
  const d6Seed = fixture(python, implementationRoot, d6Root)
  const d6Runtime = await runtime({ ...baseConfig, dataRoot: d6Root })
  const d6Proposal = await propose(d6Runtime.ctx, 'D6', d6Seed)
  const evidencePath = join(d6Root, 'evidence', String(d6Proposal.evidence_uri))
  const bytes = readFileSync(evidencePath)
  const mutated = Buffer.from(bytes)
  mutated[0] = mutated[0] === 0 ? 1 : mutated[0] - 1
  writeFileSync(evidencePath, mutated)
  const d6Verify = toolValue(await d6Runtime.ctx.tools.execute({
    callId: CallId('D6-VERIFY'), name: 'auto_decte_verify',
    arguments: { certificate_id: d6Proposal.certificate_id },
    signal: new AbortController().signal,
  }))
  const d6Before = authorityDigest(python, implementationRoot, d6Root)
  let d6Rejected = false
  try {
    hostCall(python, implementationRoot, d6Root, 'host-confirm', {
      certificate_id: d6Proposal.certificate_id, value: 8, expected_version: 0,
    })
  } catch { d6Rejected = true }
  const d6After = authorityDigest(python, implementationRoot, d6Root)
  results.D6 = {
    passed: d6Verify.verified === false && d6Rejected && d6Before === d6After,
    verification: d6Verify, rejected: d6Rejected, before: d6Before, after: d6After,
  }

  // D7: no confirmation tool exists on the model surface.
  const d7Root = join(scenariosRoot, 'D7')
  fixture(python, implementationRoot, d7Root)
  const d7Runtime = await runtime({ ...baseConfig, dataRoot: d7Root })
  const d7Db = join(d7Root, 'database', 'demo.db')
  const d7Before = sha256(d7Db)
  const d7Attempt = await d7Runtime.ctx.tools.execute({
    callId: CallId('D7'), name: 'auto_decte_confirm', arguments: {},
    signal: new AbortController().signal,
  })
  const d7After = sha256(d7Db)
  results.D7 = { passed: d7Attempt.isError && d7Before === d7After, result: d7Attempt, before: d7Before, after: d7After }

  // D8: unavailable bridge fails closed and changes no authority bytes.
  const d8Root = join(scenariosRoot, 'D8')
  const d8Seed = fixture(python, implementationRoot, d8Root)
  const d8Db = join(d8Root, 'database', 'demo.db')
  const d8Before = sha256(d8Db)
  const d8Runtime = await runtime({
    ...baseConfig, dataRoot: d8Root, pythonExecutable: join(d8Root, 'missing-python.exe'),
  })
  const d8Attempt = await d8Runtime.ctx.tools.execute({
    callId: CallId('D8'), name: 'auto_decte_propose',
    arguments: {
      form_id: d8Seed.form_id, field_id: d8Seed.field_id,
      parent_certificate_id: d8Seed.parent_certificate_id, value: 8, confidence: 0.73,
      session_id: 'SESSION-D8', execution_id: 'EXEC-D8',
    },
    signal: new AbortController().signal,
  })
  const d8After = sha256(d8Db)
  results.D8 = { passed: d8Attempt.isError && d8Before === d8After, result: d8Attempt, before: d8Before, after: d8After }

  // D9: Cordis unload removes both schemas; persisted evidence remains independently readable.
  const d9Root = join(scenariosRoot, 'D9')
  const d9Seed = fixture(python, implementationRoot, d9Root)
  const d9Runtime = await runtime({ ...baseConfig, dataRoot: d9Root })
  const d9Proposal = await propose(d9Runtime.ctx, 'D9', d9Seed)
  await d9Runtime.pluginFiber.dispose()
  const afterUnload = d9Runtime.ctx.tools.schemas().map(schema => schema.name)
  const d9Offline = hostCall(python, implementationRoot, d9Root, 'export-receipt')
  results.D9 = {
    passed: afterUnload.length === 0 && Boolean(d9Offline.forms),
    schemas_after_unload: afterUnload,
    certificate_id: d9Proposal.certificate_id,
    offline_receipt: d9Offline,
  }

  const passed = Object.values(results).every(value => (value as Record<string, unknown>).passed === true)
  const receipt = {
    schema_version: 'auto-decte.dsh-experiment-receipt.v1',
    passed,
    denominator: 9,
    passed_count: Object.values(results).filter(value => (value as Record<string, unknown>).passed === true).length,
    dsh: { tag: 'dsh-v0.1.1-rc.2', commit: 'b150a551b' },
    runtime: { node: process.version, platform: process.platform, arch: process.arch },
    results,
  }
  const receiptPath = join(output, 'receipt.json')
  mkdirSync(dirname(receiptPath), { recursive: true })
  writeFileSync(receiptPath, `${JSON.stringify(receipt, null, 2)}\n`)
  writeFileSync(join(output, 'run_metadata.json'), `${JSON.stringify({
    schema_version: 'auto-decte.dsh-run-metadata.v1',
    dsh_root: dshRoot,
    dsh_lock_sha256: sha256(join(dshRoot, 'pnpm-lock.yaml')),
    plugin_sha256: sha256(resolve(dirname(fileURLToPath(import.meta.url)), '..', 'src', 'plugin.ts')),
    implementation_root: implementationRoot,
    python,
  }, null, 2)}\n`)
  if (!passed) process.exitCode = 1
}

await main()
