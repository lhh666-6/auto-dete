"""Phase 2/3/4/5/7 driver for the strengthened transactional value-audit baseline.

Run:
    python run_strong_baseline.py --out <evidence-root> [--stamp 2026-09-10]

Writes an independently versioned evidence tree (prompt v3.2 section 40) and
never overwrites a prior run.  Reads the paper repository only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strong_baseline import b0_bridge, cases, e1  # noqa: E402
from strong_baseline.analysis import (candidate_identity_relations,  # noqa: E402
                                      infer_review_origin, project, projection_digest)
from strong_baseline.core import canonical, diff_tables, raw_state, rows_as_dicts  # noqa: E402
from strong_baseline.mapping import BOUNDARIES, MAPPING  # noqa: E402
from strong_baseline.policies import (POLICY_B1, POLICY_FULL, POLICY_VERSION,  # noqa: E402
                                      candidate_content_hash)

VARIANTS = [("B1", POLICY_B1, None), ("B2", POLICY_B1, "B2"),
            ("B2plus", POLICY_B1, "B2plus"), ("Full", POLICY_FULL, None)]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False),
                    encoding="utf-8")


def db_file_digests(directory: Path) -> dict[str, str]:
    return {p.name: sha256_file(p) for p in sorted(directory.glob("*.db"))}


def zero_write_report(db: Path) -> dict:
    """Section 23: the raw digest is used only for zero-write / rollback checks."""
    return {"database_digest": hashlib.sha256(db.read_bytes()).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="evidence root, must not exist")
    parser.add_argument("--stamp", default="2026-09-10")
    parser.add_argument("--repo", default=str(b0_bridge.DEFAULT_REPO))
    parser.add_argument("--skip-wallclock", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo)
    out = Path(args.out)
    if out.exists():
        raise FileExistsError(f"Refusing to replace prior evidence: {out}")
    out.mkdir(parents=True)
    raw = out / "raw" / args.stamp
    normalized = out / "normalized"
    paper = out / "paper"

    pins = b0_bridge.verify_pins(repo)
    if not all(entry["match"] for entry in pins.values()):
        raise RuntimeError(f"frozen artifact digest mismatch: {pins}")

    # ---------------------------------------------------------------- Phase 3
    case_suites: dict[str, dict] = {}
    for tag, policy, variant in VARIANTS:
        suite_dir = raw / f"{tag.lower()}_cases"
        runs, dbs = cases.run_all_cases(policy, suite_dir, variant=variant)
        comparison = cases.compare_with_reference(runs)
        for record in dbs:
            record["file_digest"] = sha256_file(suite_dir / "db" / record["database_file"])
        summary = {
            "schema": f"auto-decte.strong-baseline.{tag.lower()}-cases.v1",
            "policy_tag": tag,
            "policy": policy,
            "variant": variant,
            "policy_version": POLICY_VERSION,
            "cases": len(runs),
            "runs": len(runs),
            "accepted_runs": sum(1 for r in runs
                                 if r["case_id"] != "paired-reviewed-candidate"
                                 and r["observed"].get("accepted") is True),
            "rejected_runs": sum(1 for r in runs
                                 if r["case_id"] != "paired-reviewed-candidate"
                                 and r["observed"].get("accepted") is False),
            "agreement_with_candidate_bound": comparison["agreement"],
            "divergence_from_candidate_bound": comparison["divergence"],
            "observed_vs_reference": comparison["observed"],
        }
        write_json(suite_dir / "runs.json", runs)
        write_json(suite_dir / "summary.json", summary)
        case_suites[tag] = {"summary": summary, "runs": runs, "dbs": dbs,
                            "dir": str(suite_dir.relative_to(out)), "comparison": comparison}

    # ---------------------------------------------------------------- Phase 4
    e1_records: dict[str, dict] = {}
    for tag, policy, variant in VARIANTS:
        for evidence_variant in ("a", "b"):
            clocks = ["deterministic"] if args.skip_wallclock else ["deterministic", "wallclock"]
            for clock_kind in clocks:
                key = f"{tag}__evidence_{evidence_variant}__clock_{clock_kind}"
                case_dir = raw / "e1" / key
                record = e1.run(case_dir,
                                policy=policy, variant=variant,
                                clock_kind=clock_kind,
                                distinct_evidence_hash=(evidence_variant == "b"))
                record["evidence_variant"] = evidence_variant
                record["database_files"] = sorted(p.name for p in case_dir.glob("*.db"))
                record["database_digests"] = db_file_digests(case_dir)
                for side in ("safe", "unsafe"):
                    record["histories"][side].pop("pre_state", None)
                e1_records[key] = record
                write_json(case_dir / "record.json", record)

    # ------------------------------------------------- Phase 1/5/7 analysis
    self_audit = {}
    for tag, policy, variant in VARIANTS:
        suite_dir = raw / f"{tag.lower()}_cases"
        sample = suite_dir / "db" / f"legal-correction__{variant or policy}.db"
        self_audit[tag] = {
            "policy": policy, "variant": variant,
            "candidate_identity_relations": candidate_identity_relations(sample),
            "declared_approval_columns": _columns(sample, "approvals"
                                                  if "approvals" in _tables(sample) else "decisions"),
            "review_origin_diagnostic_on_equal_value_substitution": infer_review_origin(
                raw_state(suite_dir / "db" / f"equal-value-substitution__{variant or policy}.db"),
                "review-1"),
        }
        rel = self_audit[tag]["candidate_identity_relations"]
        self_audit[tag]["implements_exact_candidate_obligation"] = rel["implements_exact_candidate_relation"]
        self_audit[tag]["section_20_used_candidate_recorded"] = (
            "used_candidate_json" in _columns(sample, "admission_attempts"))

    parity = {
        "existing_control_B0_vs_Full": {
            "source": "evidence/r27-standard-practice-baseline/run-2026-09-10/summary.json "
                      "(re-reproduced byte-identically in evidence/reproduction/b0-cf09d099)",
            "agreement": 7, "cases": 8,
            "divergence": ["equal-value-substitution", "paired-reviewed-candidate"],
        },
        "strengthened_control_B1_vs_Full": {
            "agreement": len(case_suites["B1"]["comparison"]["agreement"]),
            "cases": len(cases.CANDIDATE_BOUND_REFERENCE) - 1,
            "divergence": case_suites["B1"]["comparison"]["divergence"],
            "in_process_full_agreement": len(case_suites["Full"]["comparison"]["agreement"]),
            "in_process_full_cases": len(cases.CANDIDATE_BOUND_REFERENCE),
        },
        "optional_robustness_B2_vs_Full": {
            "divergence": case_suites["B2"]["comparison"]["divergence"]},
        "optional_robustness_B2plus_vs_Full": {
            "divergence": case_suites["B2plus"]["comparison"]["divergence"]},
        "per_case": {
            case_id: {tag: ({"states_equal": case_suites[tag]["runs"][i]["observed"]["states_equal"]}
                            if case_id == "paired-reviewed-candidate"
                            else case_suites[tag]["runs"][i]["observed"])
                      for tag in case_suites}
            for i, case_id in enumerate(cases.CANDIDATE_BOUND_REFERENCE)
        },
        "reference": cases.CANDIDATE_BOUND_REFERENCE,
    }

    e1_summary = {
        key: {
            "policy": record["policy"], "evidence_variant": record["evidence_variant"],
            "clock": record["clock"],
            "safe": record["actual_outcome"]["safe"],
            "unsafe": record["actual_outcome"]["unsafe"],
            "histories_indistinguishable_under_declared_projection":
                record["comparison"]["histories_indistinguishable_under_declared_projection"],
            "declared_projection_differing_tables":
                record["comparison"]["declared_projection_differing_tables"],
            "review_origin_status": record["review_origin_status"]["safe"]["status"],
            "implements_exact_candidate_relation":
                record["comparison"]["candidate_identity_relations"]["implements_exact_candidate_relation"],
            "selected_candidate_recorded": record["selected_candidate_if_recorded"]["unsafe"],
            "fairness_all_invariants_equal": record["fairness"]["all_invariants_equal"],
            "pair_content_equivalent": record["fairness"]["evidence_hash_shared_between_pair"],
        }
        for key, record in e1_records.items()
    }

    pair_table = e1_records["B1__evidence_a__clock_deterministic"]["candidate_pair_difference_table"]
    visibility = e1_records["B1__evidence_a__clock_deterministic"]["candidate_pair_field_visibility"]
    field_judgement = {
        field: {
            "differs_in_pair": spec["differs_in_pair"],
            "stored_by_B1": spec["stored_by_policy"],
            "owner_tables": spec["owner_tables"],
            "discriminates_safe_from_unsafe": spec["discriminates_histories"],
            "verdict": spec["verdict"],
        } for field, spec in visibility.items()
    }

    write_json(normalized / "case_results.json",
               {tag: case_suites[tag]["runs"] for tag in case_suites})
    write_json(normalized / "case_summaries.json",
               {tag: case_suites[tag]["summary"] for tag in case_suites})
    write_json(normalized / "parity.json", parity)
    write_json(normalized / "e1_results.json", e1_records)
    write_json(normalized / "e1_summary.json", e1_summary)
    write_json(normalized / "candidate_pair_difference_table.json", pair_table)
    write_json(normalized / "candidate_pair_field_visibility.json", field_judgement)
    write_json(normalized / "self_audit.json", self_audit)
    write_json(normalized / "formal_witness_mapping.json",
               {"mapping": MAPPING, "boundaries": BOUNDARIES})

    manifest = {
        "schema": "auto-decte.strong-baseline.manifest.v1",
        "policy_version": POLICY_VERSION,
        "stamp": args.stamp,
        # Deliberately not an absolute path: this evidence is deposited in a public
        # repository, and the frozen-artifact digests below already identify the
        # exact revision that was read.
        "repository": "resolved at run time (AUTODECTE_REPO or module ancestors)",
        "anchor_commit": _git_head(repo),
        "frozen_artifact_pins": pins,
        "b1_extends": b0_bridge.B0_MODULE_REL,
        "policies": {tag: {"policy": policy, "variant": variant}
                     for tag, policy, variant in VARIANTS},
        "sections_implemented": ["2", "3", "4", "5", "6", "7", "9", "10", "11", "12",
                                 "13", "14", "15", "16", "17", "18", "19", "20", "21",
                                 "22", "23", "24", "25", "26", "27", "28", "29", "30",
                                 "31", "37", "38", "39", "40", "41", "42", "43", "55"],
        "not_implemented_by_design": {
            "34_event_sourcing": "deferred by section 34 (scope control)",
            "35_performance": "deferred by sections 35-36 (framing risk)",
            "22_real_world_incident": "section 32: constructed scenario only",
        },
        "counts": {
            "case_suites": len(case_suites),
            "case_runs": sum(len(case_suites[t]["runs"]) for t in case_suites),
            "e1_records": len(e1_records),
            "database_files": sum(1 for _ in raw.rglob("*.db")),
        },
        "artifacts": {
            "raw": str(raw.relative_to(out)),
            "normalized": str(normalized.relative_to(out)),
            "paper": str(paper.relative_to(out)),
        },
    }
    write_json(out / "manifest.json", manifest)
    _write_paper(paper, pins, parity, e1_summary, field_judgement, self_audit)
    print(json.dumps({"manifest": manifest["counts"], "parity": parity,
                      "e1": {k: {"safe": v["safe"]["accepted"],
                                 "unsafe": v["unsafe"]["reason"],
                                 "indist": v["histories_indistinguishable_under_declared_projection"]}
                             for k, v in e1_summary.items()}},
                     ensure_ascii=False, indent=1))
    return 0


def _write_paper(paper: Path, pins, parity, e1_summary, field_judgement, self_audit) -> None:
    from strong_baseline.paper import CAPABILITY_TABLE, CHECKLIST

    def write(name: str, text: str) -> None:
        paper.mkdir(parents=True, exist_ok=True)
        (paper / name).write_text(text, encoding="utf-8")

    lines = ["# Existing control vs strengthened control (section 43)", "",
             "## Existing control: B0 `approval_log` vs Full", "",
             f"- agreement: {parity['existing_control_B0_vs_Full']['agreement']} of "
             f"{parity['existing_control_B0_vs_Full']['cases']} single-history cases",
             f"- divergence: {', '.join(parity['existing_control_B0_vs_Full']['divergence'])}", "",
             "## Strengthened control: B1 `transactional_value_audit` vs Full", "",
             f"- agreement: {parity['strengthened_control_B1_vs_Full']['agreement']} of "
             f"{parity['strengthened_control_B1_vs_Full']['cases']} single-history cases",
             f"- divergence: {', '.join(parity['strengthened_control_B1_vs_Full']['divergence'])}",
             f"- in-process Full reproduces the frozen reference on "
             f"{parity['strengthened_control_B1_vs_Full']['in_process_full_agreement']} of "
             f"{parity['strengthened_control_B1_vs_Full']['in_process_full_cases']} cases", "",
             "## Optional robustness controls", "",
             f"- B2 divergence: {', '.join(parity['optional_robustness_B2_vs_Full']['divergence']) or 'none'}",
             f"- B2plus divergence: {', '.join(parity['optional_robustness_B2plus_vs_Full']['divergence']) or 'none'}",
             "", "## Per-case outcomes", "",
             "| case | reference (Full) | B0/B1 class | B1 | B2 | B2plus | Full |",
             "|---|---|---|---|---|---|---|"]
    for case_id, observed in parity["per_case"].items():
        reference = parity["reference"][case_id]
        def cell(value):
            if "states_equal" in value:
                return f"states_equal={value['states_equal']}"
            return f"{'accept' if value['accepted'] else 'reject'} `{value['reason']}`"
        lines.append(f"| {case_id} | {cell(reference)} | | {cell(observed['B1'])} | "
                     f"{cell(observed['B2'])} | {cell(observed['B2plus'])} | {cell(observed['Full'])} |")
    write("table-parity.md", "\n".join(lines) + "\n")

    lines = ["# E1 identity-isolation control", "",
             "SAFE = review A, admit A. UNSAFE = review A, admit the equal-valued B.", "",
             "| policy | evidence variant | clock | SAFE | UNSAFE | indistinguishable under "
             "declared projection | review-origin diagnostic | records exact candidate relation |",
             "|---|---|---|---|---|---|---|---|"]
    for key, row in e1_summary.items():
        lines.append(
            f"| {row['policy']} | {row['evidence_variant']} | {row['clock']} | "
            f"{'accept' if row['safe']['accepted'] else 'reject'} | "
            f"{'accept' if row['unsafe']['accepted'] else 'reject'} `{row['unsafe']['reason']}` | "
            f"{row['histories_indistinguishable_under_declared_projection']} | "
            f"{row['review_origin_status']} | {row['implements_exact_candidate_relation']} |")
    write("table-e1-identity-isolation.md", "\n".join(lines) + "\n")

    lines = ["# Section 5 three-column capability table", "",
             "| capability | B0 has it | B0 anchor | B1 increment | B1 anchor |",
             "|---|---|---|---|---|"]
    for capability, has, anchor, increment, inc_anchor in CAPABILITY_TABLE:
        lines.append(f"| {capability} | {has} | `{anchor}` | {increment} | `{inc_anchor}` |")
    lines.append("")
    lines.append("Rows marked *yes* are capabilities B0 already satisfies and are explicitly "
                 "**not** claimed as B1 increments (section 5).")
    write("table-capability-3col.md", "\n".join(lines) + "\n")

    lines = ["# Section 16 per-field judgement for the concrete equal-valued pair", "",
             "| field | differs in pair | stored by B1 | owner tables | discriminates SAFE vs UNSAFE | verdict |",
             "|---|---|---|---|---|---|"]
    for field, spec in sorted(field_judgement.items()):
        lines.append(f"| `{field}` | {spec['differs_in_pair']} | {spec['stored_by_B1']} | "
                     f"{', '.join(spec['owner_tables']) or '-'} | "
                     f"{spec['discriminates_safe_from_unsafe']} | {spec['verdict']} |")
    write("table-field-visibility.md", "\n".join(lines) + "\n")

    lines = ["# Section 59 completion checklist", "", "| criterion | verdict | basis | anchor |",
             "|---|---|---|---|"]
    for criterion, verdict, basis, anchor in CHECKLIST:
        lines.append(f"| {criterion} | **{verdict}** | {basis} | `{anchor}` |")
    write("checklist-v32.md", "\n".join(lines) + "\n")

    lines = ["# Section 51b evidence anchors", "",
             "| frozen artifact | pinned SHA-256 | observed | match |", "|---|---|---|---|"]
    for rel, entry in pins.items():
        lines.append(f"| `{rel}` | `{entry['pinned']}` | `{entry['observed']}` | {entry['match']} |")
    lines += ["", "| policy | exact candidate relation | used candidate recorded | review origin |",
              "|---|---|---|---|"]
    for tag, audit in self_audit.items():
        lines.append(f"| {tag} | {audit['implements_exact_candidate_obligation']} | "
                     f"{audit['section_20_used_candidate_recorded']} | "
                     f"{audit['review_origin_diagnostic_on_equal_value_substitution']['status']} |")
    write("anchors.md", "\n".join(lines) + "\n")


def _tables(db: Path) -> list[str]:
    with closing(sqlite3.connect(db)) as con:
        return [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]


def _columns(db: Path, table: str) -> list[str]:
    with closing(sqlite3.connect(db)) as con:
        return [r[1] for r in con.execute(f'PRAGMA table_info("{table}")')]


def _git_head(repo: Path) -> str:
    """Resolve HEAD, tolerating both a normal .git directory and a worktree gitfile."""
    git = repo / ".git"
    try:
        if git.is_file():
            git = Path(git.read_text(encoding="utf-8").split("gitdir:", 1)[1].strip())
        # the per-worktree HEAD always lives in this gitdir ...
        head = (git / "HEAD").read_text(encoding="utf-8").strip()
        if head.startswith("ref:"):
            name = head.split(" ", 1)[1].strip()
            # ... but the ref itself may live in the common directory
            bases = [git]
            if (git / "commondir").exists():
                bases.append((git / (git / "commondir").read_text(encoding="utf-8").strip()).resolve())
            for base in bases:
                ref = base / name
                if ref.exists():
                    return ref.read_text(encoding="utf-8").strip()
                packed = base / "packed-refs"
                if packed.exists():
                    for line in packed.read_text(encoding="utf-8").splitlines():
                        if line.endswith(" " + name):
                            return line.split(" ", 1)[0]
            return "unresolved:" + name
        return head
    except (OSError, IndexError):
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
