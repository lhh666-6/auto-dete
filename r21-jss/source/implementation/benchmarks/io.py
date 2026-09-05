import hashlib
import json
from collections.abc import Iterable
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    return value


def write_json(path: Path, rows: Iterable[Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [_jsonable(row) for row in rows]
    encoded = (json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    path.write_bytes(encoded)
    return hashlib.sha256(encoded).hexdigest()
