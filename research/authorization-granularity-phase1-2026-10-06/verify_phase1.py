"""Fresh verification of the isolated phase-one artifacts and frozen inputs."""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
FROZEN = ROOT / 'revisions/2026-09-12-r30-submission-candidate/code/formal-fixed/observation_witnesses.py'

def run(args, cwd, log):
    result = subprocess.run([sys.executable, '-B', *args], cwd=cwd, capture_output=True, text=True, encoding='utf-8')
    (OUT / log).write_text(result.stdout + result.stderr, encoding='utf-8')
    if result.returncode:
        raise RuntimeError((result.stdout + result.stderr)[-6000:])

def main():
    run(['-m', 'unittest', 'discover', '-s', 'tests', '-v'], OUT / 'formal', 'canonical-green.txt')
    run(['observation_witnesses.py', '--json', '../observation-report.json'], OUT / 'formal', 'witness-verification.txt')
    run(['-m', 'unittest', 'test_audit_corrections', '-v'], OUT, 'correction-green.txt')
    run(['audit_corrections.py'], OUT, 'correction-audit-run.txt')
    original_hash = hashlib.sha256(FROZEN.read_bytes()).hexdigest()
    assert original_hash == '32bed3ae1aed344c3bf5c57c7f7e545e4e05836a154ae14d278be3aebd6b7832'
    repaired = OUT / 'formal/observation_witnesses.py'
    (OUT / 'canonical-repair.diff').write_text(''.join(difflib.unified_diff(FROZEN.read_text(encoding='utf-8').splitlines(keepends=True), repaired.read_text(encoding='utf-8').splitlines(keepends=True), fromfile='frozen/observation_witnesses.py', tofile='phase1/observation_witnesses.py')), encoding='utf-8')
    prior_inputs = json.loads((ROOT / 'reviews/structural-audit-2026-10-06/input-file-hashes.json').read_text(encoding='utf-8'))
    changes = [r['path'] for r in prior_inputs if hashlib.sha256((ROOT / r['path']).read_bytes()).hexdigest() != r['sha256']]
    assert not changes, changes
    old = ROOT / 'revisions/2026-08-27-jss-r21-live-agent-performance/source/implementation/app/domain/authority.py'
    current = ROOT / 'revisions/2026-09-12-r30-submission-candidate/code/implementation-fixed/app/domain/authority.py'
    def node(path, name):
        return ast.dump(next(n for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n, ast.FunctionDef) and n.name == name), include_attributes=False)
    builder_same = node(old, 'build_provenance_trace') == node(current, 'build_provenance_trace')
    assert builder_same
    summary = json.loads((OUT / 'correction-summary.json').read_text(encoding='utf-8'))
    counts = summary['counts']
    assert counts['corrections_found'] == counts['chains_without_failures'] == 84
    assert counts['P6_traces_checked'] == counts['record_versions_checked'] == 168
    assert counts['candidate_certificates_checked'] == counts['evidence_checks'] == 252
    assert counts['unchanged_fields_checked'] == 0
    assert not summary['failure_codes'] and not summary['frozen_inputs_changed_during_audit']
    manifest = json.loads((OUT / 'correction-input-hashes.json').read_text(encoding='utf-8'))
    result = {'formal_tests_passed': 24, 'audit_tests_passed': 12, 'frozen_observation_sha256': original_hash, 'repaired_observation_sha256': hashlib.sha256(repaired.read_bytes()).hexdigest(), 'prior_audit_inputs_rechecked': len(prior_inputs), 'prior_audit_inputs_changed': changes, 'phase1_audit_inputs_hashed': len(manifest), 'historical_and_r30_P6_builder_AST_identical': builder_same, 'correction_counts': counts, 'proof_status': 'D1 is a written two-direction mathematical proof, not a machine-checked proof; D3 not started'}
    (OUT / 'verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
