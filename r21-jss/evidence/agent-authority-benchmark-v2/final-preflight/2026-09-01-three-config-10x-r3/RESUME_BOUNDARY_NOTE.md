# Final R3 resume boundary

R2 completed exactly one G1/B1/V1/repetition-1 coordinate and wrote checkpoint `0001.json` before
its post-run freeze verification rejected Python cache files created by the Codex-managed MCP
subprocess. The terminal is retained and must not be rerun. R3 changes no scenario, prompt, model,
seed, retry rule, scoring rule, or admission mechanism; it adds only an explicit
`PYTHONDONTWRITEBYTECODE=1` entry to the MCP subprocess environment. R3 resumes the same 1,260-cell
plan and the same Final output root at the next absent coordinate.
