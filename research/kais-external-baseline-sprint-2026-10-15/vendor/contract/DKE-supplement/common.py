from __future__ import annotations

import hashlib
import json
import platform
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent / 'dke-experiments'
IMPL = REPO / 'latest/code/implementation-fixed'
sys.path.insert(0, str(IMPL))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')


def database_state(path):
    with sqlite3.connect(path) as con:
        con.row_factory = sqlite3.Row
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {n: sorted([dict(r) for r in con.execute('SELECT * FROM "' + n.replace('"', '""') + '"')], key=canonical) for n in names}


def db_digest(path):
    return digest(database_state(path))


def environment():
    import sqlalchemy
    return {'python': sys.version, 'platform': platform.platform(), 'sqlite': sqlite3.sqlite_version,
            'sqlalchemy': sqlalchemy.__version__, 'source_commit': 'c6d512843c905cab6d8521dd8c914f7fb26d85ae',
            'hosted_model_calls': 0}


def context(candidate):
    # Retains rich review content, including evidence locator; only opaque identity
    # and per-instance acquisition time are omitted. These omissions are explicit.
    return {k: v for k, v in candidate.items() if k not in ('id', 'candidate_id', 'created_at')}


def summarize(rows, groups):
    import statistics
    result = []
    for key in sorted({tuple(r[k] for k in groups) for r in rows}):
        rs = [r for r in rows if tuple(r[k] for k in groups) == key]
        ms = sorted(r['latency_ns'] / 1e6 for r in rs)
        result.append(dict(zip(groups, key)) | {'n': len(rs), 'p50_ms': statistics.median(ms),
            'p95_ms': ms[int((len(ms)-1)*.95)], 'min_ms': ms[0], 'max_ms': ms[-1],
            'sql_min': min(r.get('sql_statements', 0) for r in rs),
            'sql_max': max(r.get('sql_statements', 0) for r in rs)})
    return result
