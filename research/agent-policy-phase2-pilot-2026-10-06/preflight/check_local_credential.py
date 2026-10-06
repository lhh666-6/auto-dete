import subprocess
script = "$s=(Get-Content -LiteralPath 'C:/Users/lenovo/.codex/local-secrets/phase2-dsh-api.dpapi' -Raw).Trim() | ConvertTo-SecureString; Write-Output 'decryption-readable'"
p = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command', script], capture_output=True, text=True)
print({'returncode': p.returncode, 'diagnostic': p.stderr[:1200], 'readable': p.stdout.strip() == 'decryption-readable'})
