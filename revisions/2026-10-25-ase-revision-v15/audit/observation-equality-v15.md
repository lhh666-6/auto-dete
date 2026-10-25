# Observation equality repair: v15 offline receipt

Status: PASS. No model calls, trace recollection, new hosted experiments, or changes to historical experiment counts. This receipt is separate from all archived test totals and Alloy command results.

## Frozen provenance

- Upstream commit: `c6d512843c905cab6d8521dd8c914f7fb26d85ae`.
- Upstream path: `latest/code/formal-fixed/observation_witnesses.py`.
- Original raw-byte SHA-256: `32bed3ae1aed344c3bf5c57c7f7e545e4e05836a154ae14d278be3aebd6b7832`.
- Original extraction: `git show COMMIT:PATH` via `subprocess.check_output`, preserving bytes. A byte-exact copy is shipped at `qa/upstream/observation_witnesses.py`; the regression script reads that bundled file, verifies its fixed hash, and loads it only in memory. No Git installation or repository is needed for replay. The original Git source and v14 revision were not edited.
- Standalone derivative: `qa/observation_witnesses_v15.py`.
- Derivative SHA-256: `68ee924d21f72c5841ab11e252ff394b0e2b8022e9b2ede5fd6a0611352ec2b9`.
- Regression script SHA-256: `5d0e7fd1f9a4a38de2da5051c3ef41d8cd1e0838da8aa2743e7ed8b8d6268d0b`.
- All new/edited source, document and receipt files use LF, except the byte-exact bundled historical blob, whose original mixed line endings are deliberately preserved. The derivative normalizes the copied source's mixed line endings to LF; its source hash therefore intentionally differs from the frozen raw-byte hash.

## Repair and scope

The original checker mixed canonical serialization in attribution, effect detection and source checks with Python equality in D_V projections, history connections/endpoints and freshness. The derivative emits canonical serialized values for all three D_V value roles. It compares commit snapshot maps using canonical JSON equality. Because expected/observed discriminators are typed `Any`, it applies the same encoding to D_F and the corresponding freshness check together. Identifier comparisons remain opaque string equality; no identifier is parsed or decoded.

The existing convention is sorted-key, whitespace-minimal `json.dumps` serialization, distinguishing `1` from `true` and `2` from `2.0`, while ignoring dictionary insertion order. This change does not introduce a generic JSON validator, a domain-specific numeric normalization, or new semantics for arbitrary non-JSON inputs. The inherited serializer and finite witness scope remain explicit. T1b uses canonical observations over the declared well-formed history domain; the implementation checks do not establish a universal admission theorem.

## Results

The frozen and derived `verify()` calls both pass the original five omission pairs, the separate candidate-instance identity pair and the copy-forward control. These seven preserved constructions are not counted among the 38 new regression checks.

All **38 new regression checks pass**. There are 36 matrix checks: four pairs (integer/Boolean, integer/float, nested numeric/Boolean changes, reordered equal dictionaries) across nine checks (each of the three D_V roles, attribution, changed fields, source resolution, endpoint, commit connection, and D_F/freshness consistency). The remaining two checks reproduce the actual review counterexamples in the original byte-exact module and verify their repair in the derivative.

1. Authorization counterexample: both original histories pass the domain check, their full projections compare equal in Python, and their outcomes differ. The derivative retains both in the domain but distinguishes their full projections, consistently with their different attribution outcomes.
2. Endpoint counterexample: the frozen domain accepts an integer-1 commit with a Boolean-true declared endpoint and reports an admissible local outcome. The derivative rejects the history with `commit sequence does not reach successor values`. Its raw local-outcome function still returns its local classification if called directly on this invalid history; this is intentional because that function is conditional on the domain and is not a general admission oracle.

Full individual checks, historical/derived counterexample outputs, source hashes and derived witness observations are in `audit/observation-equality-v15.json`. The original 13-regression equality receipt, selected 85-test run, 72 Alloy command matches, five witness class pairs, and all reported experimental sample sizes remain historical figures, unchanged by these 38 checks.

## Reproduction

From the repository root, using standard-library Python only (the same relative commands work from an extracted v15 directory after omitting the revision prefix):

```text
python -B revisions/2026-10-25-ase-revision-v15/qa/observation_witnesses_v15.py
python -B revisions/2026-10-25-ase-revision-v15/qa/test_observation_equality_v15.py
```

The second command verifies the bundled frozen source hash, reproduces its two defects in memory, verifies all preserved constructions, runs the 38 new checks, and regenerates the JSON receipt. By default it writes `audit/observation-equality-v15.json` next to the `qa` directory. To preserve the issued receipt while rerunning, append `--output PATH/TO/TEMPORARY-RESULT.json`; `--upstream PATH` optionally selects another exact copy of the frozen blob (the expected hash remains mandatory). It never invokes the model, accesses hosted experiment services, or modifies the frozen blob. The standalone checker itself does not need Git or any historical source at runtime. The regression harness requires only its bundled original blob, the derivative, and standard-library Python.

## Standalone package validation

Copied only the derivative, regression harness and `qa/upstream/observation_witnesses.py` to an independent temporary directory outside the repository. Ran the copied harness with the absolute Python executable, `-B`, an empty `PATH` (no Git resolution possible), and `--output temporary-output/result.json`. Result: PASS, all 38 new checks and seven preserved constructions; the requested JSON existed and no default audit directory was written. The temporary directory was then removed. The issued audit JSON was left unchanged by this package-validation run.
