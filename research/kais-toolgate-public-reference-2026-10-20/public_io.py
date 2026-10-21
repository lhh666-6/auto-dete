"""Small shared artifact helpers, without policy or scoring logic."""
import gzip
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FEASIBILITY = ROOT.parent / "kais-toolgate-feasibility-2026-10-20"
SPRINT = ROOT.parent / "kais-external-baseline-sprint-2026-10-15"
PILOT = SPRINT / "vendor/pilot"


def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def read(path):
    path = Path(path)
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (canon(value) + "\n").encode()
    if path.suffix == ".gz":
        data = gzip.compress(data, mtime=0)
    with path.open("xb") as stream:
        stream.write(data)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump_sql(path):
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        names = [r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {name: sorted([dict(r) for r in connection.execute(
            'SELECT * FROM "' + name.replace('"', '""') + '"')], key=canon) for name in names}
