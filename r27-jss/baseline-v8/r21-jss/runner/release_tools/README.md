# R17 release verification

`r17_release.py` provides a standard-library-only manifest verifier and typed
comparators:

- `verify-manifest`: exact archive-content integrity;
- `compare-exact`: byte-exact regenerated paper inputs;
- `compare-correctness`: timing-insensitive Alloy, refinement, catalogue,
  quality, lifecycle, and correctness-command semantics; and
- `compare-performance`: exact grid plus finite positive measurement checks,
  with timing ratios retained descriptively rather than forced to byte equality.

Run the ten regression tests with:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'runner')
python -B -m pytest -p no:cacheprovider runner/release_tools/tests -q
```
