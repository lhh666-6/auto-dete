"""Compare the r23 package against the r22-concise baseline.

Reports every differing/added/removed file so the intentional Claude changes
can be separated from accidental drift.
"""
import hashlib
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = ROOT.parent / "2026-09-08-r22-concise"
NEW = ROOT

IGNORE_PARTS = {"out", "__pycache__", ".pytest_cache", ".hypothesis"}
IGNORE_FILES = {"MANIFEST-r22.json", "MANIFEST-r23.json"}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def walk(root):
    out = {}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in IGNORE_PARTS for part in p.parts):
            continue
        if rel in IGNORE_FILES:
            continue
        out[rel] = digest(p)
    return out


base, new = walk(BASE), walk(NEW)
added = sorted(set(new) - set(base))
removed = sorted(set(base) - set(new))
changed = sorted(rel for rel in set(base) & set(new) if base[rel] != new[rel])

print(f"baseline files: {len(base)}  new files: {len(new)}")
print(f"\nADDED ({len(added)}):")
for rel in added:
    print("  +", rel)
print(f"\nREMOVED ({len(removed)}):")
for rel in removed:
    print("  -", rel)
print(f"\nCHANGED ({len(changed)}):")
for rel in changed:
    print("  ~", rel)
