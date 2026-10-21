# Reproduce the post-submission offline output audit

Use Python 3 standard library. From this directory:

```text
python -B -m unittest -v test_analysis.py
python -B analysis.py
```

The analyzer reads original B raw files and the original frozen outcome table. It does not import a provider module, access credentials, call a model or rewrite original scores. It extracts only the frozen `parse_action` function AST and executes that function with `json`, so parseability means the original runner's accepted format, not a newly stricter schema. Its known semantic limits remain those of that parser.

`PROTOCOL.md` records the fixed diagnostic rules and the prior visibility of the 18 invalid-output records. This is retrospective evidence classification, not prospective preregistration.

- `attempts.csv`: one physical provider attempt; prefix counted once. A format-repair model decision is separate from a transport retry. Includes raw paths, stop reason, text availability, parseability, request/response evidence and actual error evidence.
- `arms.csv`: all 256 original B arms, original outcome and cost columns plus diagnostic fields. Missing original values remain blank. Join other audits by `pair_id,policy`.
- `invalid-output-arms.csv`: convenience subset of the 18 original failures; it does not redefine any denominator.
- `pairs.csv`: all 128 paired positions and bound-minus-context differences. Both any-truncation and terminal-truncation position are retained.
- `summary.json`, `integrity.json`: aggregate results, coverage and input-integrity checks.
- `inputs-sha256-before.json`, `inputs-sha256-after.json`: 10,409 original inputs. The first baseline is never overwritten; subsequent runs fail if inputs differ. Includes all B files (including states/safe boundaries), original analysis CSV/JSON, frozen manifests and parser/runner source.
- `test-red.txt`, `test-transport-red.txt`, `test-results.txt`: retained test development evidence. The latter documents the completed 19-test pass; re-running tests verifies the current files.
- `RESULTS.md`: compact interpretation and proposed wording, without editing the submission.

No reconstructed HTTP request body is represented as raw evidence: the original adapter saved prompts and responses, while the configured cap is established by the frozen configuration/source. No natural-ended malformed response, HTTP failure or transport retry was observed in this B audit; classifiers preserve them as distinct possibilities rather than converting them into truncation.

The analyzer overwrites only its derived files in this directory. `RESULTS.md` is a human-written interpretation of the retained machine-readable result and is not regenerated. `integrity.json` hashes the analysis, tests and protocol used for its run. All responses are kept; there is no exclusion-based effect, selective rerun, or new inferential claim.
