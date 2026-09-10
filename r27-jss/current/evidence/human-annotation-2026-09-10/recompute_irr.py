"""Recompute the r27 human-annotation agreement statistics from the published labels.

Input: labels-A1-A2-normalized.csv, which contains the 360 benign runs with
A1/A2 labels, the frozen rule label, the evaluability flag, and the
adjudicated label.  The script uses only the Python standard library.

The reference archive's intervals remain authoritative; this script exists so a
reviewer can reproduce the agreement coefficients and the case-, model-, and
cell-level bootstrap intervals from the published per-run labels without the
private author key or the original xlsx files.

Usage:
    python recompute_irr.py --labels labels-A1-A2-normalized.csv \
        --out recomputed-irr.json --replicates 5000 --seed 20260910
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


def cohen_kappa(pairs, categories):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    a_counts = Counter(a for a, _ in pairs)
    b_counts = Counter(b for _, b in pairs)
    pe = sum((a_counts.get(c, 0) / n) * (b_counts.get(c, 0) / n) for c in categories)
    if pe >= 1.0:
        return None
    return (po - pe) / (1.0 - pe)


def ac1(pairs, categories):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    q = len(categories)
    if q < 2:
        return None
    prevalence = {}
    for c in categories:
        prevalence[c] = (sum(1 for a, _ in pairs if a == c) +
                         sum(1 for _, b in pairs if b == c)) / (2 * n)
    pe = sum(prevalence[c] * (1 - prevalence[c]) for c in categories) / (q - 1)
    if pe >= 1.0:
        return None
    return (po - pe) / (1.0 - pe)


def pabak(pairs, categories):
    n = len(pairs)
    if n == 0:
        return None
    po = sum(1 for a, b in pairs if a == b) / n
    q = len(categories)
    if q < 2:
        return None
    return (q * po - 1.0) / (q - 1.0)


def confusion(pairs, categories):
    matrix = {a: {b: 0 for b in categories} for a in categories}
    for a, b in pairs:
        matrix[a][b] += 1
    return matrix


def percentile(values, q):
    if not values:
        return None
    values = sorted(values)
    pos = (len(values) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return values[lo]
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def bootstrap_ci(rows, pairs_from_rows, categories, unit_key, replicates, seed):
    rng = random.Random(seed)
    groups = defaultdict(list)
    for row in rows:
        groups[unit_key(row)].append(row)
    group_keys = list(groups)
    estimates = []
    for _ in range(replicates):
        sample = []
        for _ in range(len(group_keys)):
            sample.extend(groups[rng.choice(group_keys)])
        value = cohen_kappa(pairs_from_rows(sample), categories)
        if value is not None and not math.isnan(value):
            estimates.append(value)
    return {
        "ci95": [percentile(estimates, 0.025), percentile(estimates, 0.975)],
        "valid_replicates": len(estimates),
        "replicates": replicates,
    }


def human_pairs(rows, human):
    return [(row[human], row["rule_label"]) for row in rows
            if row["evaluable"] == "1" and row[human] in {"0", "1"}
            and row["rule_label"] in {"0", "1"}]


def inter_pairs(rows):
    return [(row["A1_label"], row["A2_label"]) for row in rows
            if row["A1_label"] in {"0", "1", "9"} and row["A2_label"] in {"0", "1", "9"}]


def summarize(pairs, categories):
    n = len(pairs)
    return {
        "n": n,
        "po": sum(1 for a, b in pairs if a == b) / n if n else None,
        "kappa": cohen_kappa(pairs, categories),
        "ac1": ac1(pairs, categories),
        "pabak": pabak(pairs, categories),
        "confusion": confusion(pairs, categories),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--replicates", type=int, default=5000)
    parser.add_argument("--seed", type=int, default=20260910)
    args = parser.parse_args()

    rows = list(csv.DictReader(open(args.labels, encoding="utf-8-sig", newline="")))
    report = {
        "input": str(Path(args.labels)),
        "rows": len(rows),
        "replicates": args.replicates,
        "seed": args.seed,
        "inter_human_3cat": summarize(inter_pairs(rows), ["0", "1", "9"]),
        "a1_rule": summarize(human_pairs(rows, "A1_label"), ["0", "1"]),
        "a2_rule": summarize(human_pairs(rows, "A2_label"), ["0", "1"]),
        "case_level_ci": {
            "inter_human_3cat": bootstrap_ci(
                rows, inter_pairs, ["0", "1", "9"], lambda r: r["case_id"],
                args.replicates, args.seed),
            "a1_rule": bootstrap_ci(
                rows, lambda s: human_pairs(s, "A1_label"), ["0", "1"],
                lambda r: r["case_id"], args.replicates, args.seed),
            "a2_rule": bootstrap_ci(
                rows, lambda s: human_pairs(s, "A2_label"), ["0", "1"],
                lambda r: r["case_id"], args.replicates, args.seed),
        },
        "model_level_ci": {
            "inter_human_3cat": bootstrap_ci(
                rows, inter_pairs, ["0", "1", "9"], lambda r: r["model_config_id"],
                args.replicates, args.seed + 1),
            "a1_rule": bootstrap_ci(
                [r for r in rows if r["evaluable"] == "1"],
                lambda s: human_pairs(s, "A1_label"), ["0", "1"],
                lambda r: r["model_config_id"], args.replicates, args.seed + 1),
            "a2_rule": bootstrap_ci(
                [r for r in rows if r["evaluable"] == "1"],
                lambda s: human_pairs(s, "A2_label"), ["0", "1"],
                lambda r: r["model_config_id"], args.replicates, args.seed + 1),
        },
        "cell_level_ci": {
            "inter_human_3cat": bootstrap_ci(
                rows, inter_pairs, ["0", "1", "9"],
                lambda r: (r["model_config_id"], r["scenario_id"]),
                args.replicates, args.seed + 2),
            "a1_rule": bootstrap_ci(
                [r for r in rows if r["evaluable"] == "1"],
                lambda s: human_pairs(s, "A1_label"), ["0", "1"],
                lambda r: (r["model_config_id"], r["scenario_id"]),
                args.replicates, args.seed + 2),
            "a2_rule": bootstrap_ci(
                [r for r in rows if r["evaluable"] == "1"],
                lambda s: human_pairs(s, "A2_label"), ["0", "1"],
                lambda r: (r["model_config_id"], r["scenario_id"]),
                args.replicates, args.seed + 2),
        },
    }
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
