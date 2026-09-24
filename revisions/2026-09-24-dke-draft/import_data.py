"""Copy deposited DKE summary tables without changing their bytes."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
TABLES = (
    "e1-comparison.csv",
    "e2-cases.csv",
    "e3-mechanism-summary.csv",
    "e3-ablation-summary.csv",
    "e3-trace-summary.csv",
    "storage.csv",
)
SOURCE_COMMIT = "2645e5e18c900ea91c9c980e44195dc71e410432"


def main() -> None:
    output = HERE / "data"
    output.mkdir(exist_ok=True)
    manifest = {}
    for name in TABLES:
        source = f"{SOURCE_COMMIT}:DKE-supplement/tables/{name}"
        data = subprocess.check_output(["git", "show", source], cwd=HERE)
        (output / name).write_bytes(data)
        manifest[name] = {
            "source": source,
            "sha256": sha256(data).hexdigest(),
            "bytes": len(data),
        }
    (output / "SOURCE-MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Copied {len(TABLES)} deposited tables")


if __name__ == "__main__":
    main()
