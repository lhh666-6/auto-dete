import subprocess
import sys
from pathlib import Path

from auto_decte_live_agent import runner


def test_run_utf8_captures_non_gbk_output(tmp_path: Path) -> None:
    completed = runner._run_utf8(
        [
            sys.executable,
            "-c",
            "import sys; sys.stdout.buffer.write('agent\u00a0message'.encode('utf-8'))",
        ],
        cwd=tmp_path,
        timeout=30,
    )

    assert isinstance(completed, subprocess.CompletedProcess)
    assert completed.returncode == 0
    assert completed.stdout == "agent\u00a0message"
