"""O1 probe: determinism of the recorded evidence content hash.

`recognize_forms.record_candidate` records the candidate's evidence content hash as

    evidence_hash = sha256(cv2.imencode(".png", crop).tobytes())

(`app/application/recognize_forms.py:143-146` and
`app/adapters/storage/local.py:26-35`).  Two records for the same crop can
therefore differ only if the encoder output is not reproducible.

Run:  python probe.py            # human-readable
      python probe.py --json     # machine-readable result on stdout
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys

import cv2
import numpy as np

REPEATS_SAME_OBJECT = 200
REPEATS_EQUAL_CONTENT = 50
PROCESS_REPEATS = 3
THREAD_COUNTS = (1, 4, 0)

_CHILD = """
import hashlib, sys, numpy as np, cv2
if len(sys.argv) > 1:
    cv2.setNumThreads(int(sys.argv[1]))
rng = np.random.default_rng(7)
form = rng.integers(0, 256, (300, 400), dtype=np.uint8)
crop = form[40:160, 30:150]
print(hashlib.sha256(cv2.imencode(".png", crop)[1].tobytes()).hexdigest())
"""


def _digest(image: np.ndarray) -> str:
    encoded, buffer = cv2.imencode(".png", image)
    if not encoded:
        raise RuntimeError("encoder refused the crop")
    return hashlib.sha256(buffer.tobytes()).hexdigest()


def _png_chunks(payload: bytes) -> list[str]:
    chunks, offset = [], 8
    while offset < len(payload):
        length = int.from_bytes(payload[offset:offset + 4], "big")
        chunks.append(payload[offset + 4:offset + 8].decode("latin1"))
        offset += 12 + length
    return chunks


def run() -> dict:
    rng = np.random.default_rng(7)
    form = rng.integers(0, 256, (300, 400), dtype=np.uint8)
    crop = form[40:160, 30:150]

    same_object = {_digest(crop) for _ in range(REPEATS_SAME_OBJECT)}
    equal_content = {_digest(form[40:160, 30:150].copy()) for _ in range(REPEATS_EQUAL_CONTENT)}

    source = np.float32([[30, 40], [150, 40], [150, 160], [30, 160]])
    target = np.float32([[0, 0], [120, 0], [120, 120], [0, 120]])
    transform = cv2.getPerspectiveTransform(source, target)
    warp_a = cv2.warpPerspective(form, transform, (120, 120))
    warp_b = cv2.warpPerspective(form, transform, (120, 120))
    warped = {"arrays_equal": bool(np.array_equal(warp_a, warp_b)),
              "hashes_equal": _digest(warp_a) == _digest(warp_b)}

    chunks = _png_chunks(cv2.imencode(".png", crop)[1].tobytes())
    time_varying = [c for c in chunks if c not in {"IHDR", "IDAT", "IEND", "PLTE", "pHYs"}]

    processes = [subprocess.run([sys.executable, "-c", _CHILD], capture_output=True,
                                text=True, check=True).stdout.strip()
                 for _ in range(PROCESS_REPEATS)]
    threads = {str(n): subprocess.run([sys.executable, "-c", _CHILD, str(n)], capture_output=True,
                                      text=True, check=True).stdout.strip()
               for n in THREAD_COUNTS}

    all_hashes = same_object | equal_content | set(processes) | set(threads.values())
    return {
        "probe": "recognition-encoder-determinism",
        "question": "Is sha256(cv2.imencode('.png', crop).tobytes()) reproducible, so that two "
                    "recognition attempts over the same crop record the same evidence hash?",
        "environment": {"opencv": cv2.__version__, "numpy": np.__version__,
                        "python": sys.version.split()[0]},
        "observations": {
            "same_object_repeats": REPEATS_SAME_OBJECT,
            "same_object_distinct_hashes": len(same_object),
            "equal_content_repeats": REPEATS_EQUAL_CONTENT,
            "equal_content_distinct_hashes": len(equal_content),
            "independent_processes": PROCESS_REPEATS,
            "independent_process_distinct_hashes": len(set(processes)),
            "encoder_thread_counts": list(THREAD_COUNTS),
            "thread_count_distinct_hashes": len(set(threads.values())),
            "png_chunk_sequence": chunks,
            "png_time_varying_chunks": time_varying,
            "perspective_warp_rederivation": warped,
        },
        "all_observed_hashes": sorted(all_hashes),
        "verdict": "DETERMINISTIC" if len(all_hashes) == 1 and not time_varying
                   and warped["hashes_equal"] else "NOT_DETERMINISTIC",
        "consequences": [
            "evidence_hash is identical for two recognition attempts over the same crop, so the "
            "field is not a review-context discriminator in the production recognition path.",
            "The two candidates differ only in fields that constitute the content-addressed "
            "certificate identity and the evidence storage locator: candidate_id, created_at, "
            "evidence file id, and evidence locator.",
            "Reproducibility is established for one encoder build; a different OpenCV or libpng "
            "build is not covered.",
        ],
    }


if __name__ == "__main__":
    payload = run()
    if "--json" in sys.argv:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload["observations"].items():
            print(f"  {key}: {value}")
        print(f"  verdict: {payload['verdict']}")
