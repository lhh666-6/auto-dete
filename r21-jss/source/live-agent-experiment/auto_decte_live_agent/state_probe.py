"""Independent raw-relational digest probe for a live-agent scenario database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import create_engine

from tests.conformance.oracle import database_digest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    database = args.database.resolve()
    if not database.is_file():
        raise FileNotFoundError(database)
    engine = create_engine(f"sqlite:///{database}")
    print(json.dumps({"database_digest": database_digest(engine)}, sort_keys=True))
    engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
