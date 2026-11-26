"""Tables 1 and 2 (plan section 5) from scored probe rows.

    python analysis/table.py --exp e1 --split dev
        Table 1: every model scored under runs/e1/, with 95% group-bootstrap intervals.
    python analysis/table.py --exp e2 --split dev --reference baseline --reference-exp e1
        Table 2: every model under runs/e2/ minus the baseline (scored in E1), paired bootstrap on the same groups.

Writes results/<exp>/table-<split>.md and prints it. Standard library only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import read_jsonl            # noqa: E402
from analysis.metrics import analyse, fr_units, load_rows, pg_units   # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SUITES = {"dv7": "decision-v7", "tv4": "transfer-v4"}
FR_COLS = [("kev_seen", "seen"), ("a1_train", "A1-train"), ("heldout", "held-out"), ("random_test", "random")]
PG_COLS = ["S1", "S2", "S3"]


def flat(kind, stats):
    """Every number of a stats block as "<group>.<field>" (the same keys as metrics.headline)."""
    return {f"{k}.{f}": v for k, d in stats.items() for f, v in d.items() if isinstance(v, float)}


def fmt(v, c=None, signed=False):
    if v is None:
        return "-"
    s = f"{v:+.3f}" if signed else f"{v:.3f}"
    return s if not c else f"{s} [{c[0]:+.2f}, {c[1]:+.2f}]" if signed else f"{s} [{c[0]:.2f}, {c[1]:.2f}]"


def models(exp, split):
    found = {}
    for d in sorted((ROOT / "runs" / exp).glob(f"*-*-{split}-*")):
        m = re.match(rf"(.+)-(dv7|tv4)-{split}-(fr|pg)$", d.name)
        if m and (d / "rows.json").exists():
            found.setdefault(m.group(1), set()).add((m.group(2), m.group(3)))
    return found


def has_definitions(record):
    c = record["questions"]["q"].get("criteria") or {}
    return bool(c.get("true") and c.get("false"))


def is_policy(record):
    return record["_meta"]["task"].startswith("composition")


# Slices: (description, keep FR record?, keep PG record?). None drops that probe from the slice. All but the last are
# defined by question structure, before looking at any result; paws-qnli was picked after E1 and is labelled post hoc.
SLICES = {
    "all": ("all questions", lambda r: True, lambda r: True),
    "policy": ("policy (accept/reject) questions only", is_policy, None),
    "nonpolicy": ("all but the policy questions", lambda r: not is_policy(r), None),
    "nodef": ("yes/no questions without option definitions", None, lambda r: not has_definitions(r)),
    "withdef": ("yes/no questions with option definitions", None, has_definitions),
    "paws-qnli": ("paws and qnli only (chosen after E1: post hoc)", lambda r: r["_meta"]["task"] in ("paws", "qnli"), None),
}
EMPTY = {"stats": {}, "ci95": {}, "difference": {}}


def result(exp, name, tag, probe, ref=None, boot=2000, keep=lambda r: True):
    if keep is None:
        return EMPTY
    data = [r for r in read_jsonl(ROOT / "probes" / "out" / f"{tag}-{probe}.jsonl") if keep(r)]
    make = fr_units if probe == "fr" else pg_units
    units, _ = make(data, load_rows(ROOT / "runs" / exp / f"{name}-{tag}-{probe}"))
    if not units:
        return EMPTY
    ref_units = make(data, load_rows(ref))[0] if ref else None
    return analyse(probe, units, ref_units, boot)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True)
    ap.add_argument("--split", default="dev")
    ap.add_argument("--reference", help="model name to subtract (Table 2)")
    ap.add_argument("--reference-exp", default=None, help="experiment directory the reference was scored in (default --exp)")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--slice", choices=list(SLICES), default="all", help="restrict to a group of questions (see SLICES)")
    a = ap.parse_args()
    what, keep_fr, keep_pg = SLICES[a.slice]
    ref_exp = a.reference_exp or a.exp
    lines, values = [], {}
    for tag, suite in SUITES.items():
        tag = f"{tag}-{a.split}"
        if a.reference:
            title = f"{suite} {a.split}, {what}: difference from {a.reference} (95% paired bootstrap)"
            head = ["model"] + [f"dFR {c}" for _, c in FR_COLS] + [f"PG {s}" for s in PG_COLS]
        else:
            title = f"{suite} {a.split}, {what} (95% group bootstrap)"
            head = (["model", "FR neutral"] + [f"FR {c}" for _, c in FR_COLS] + [f"dFR {c} [CI]" for _, c in FR_COLS[:3]]
                    + ["AUROC orig"] + [f"PG {s} [CI]" for s in PG_COLS])
        lines += [f"\n### {title}\n", "| " + " | ".join(head) + " |", "|---" * len(head) + "|"]
        for name, have in models(a.exp, a.split).items():
            if (tag[:3], "fr") not in have or (tag[:3], "pg") not in have or name == a.reference:
                continue
            ref = lambda p: ROOT / "runs" / ref_exp / f"{a.reference}-{tag}-{p}" if a.reference else None
            fr = result(a.exp, name, tag, "fr", ref("fr"), a.boot, keep_fr)
            pg = result(a.exp, name, tag, "pg", ref("pg"), a.boot, keep_pg)
            values.setdefault(suite, {})[name] = (
                {**fr["difference"], **pg["difference"]} if a.reference else
                {k: {"value": v, "ci95": {**fr["ci95"], **pg["ci95"]}.get(k)} for k, v in {**flat("fr", fr["stats"]), **flat("pg", pg["stats"])}.items()})
            if a.reference:
                d = {**fr["difference"], **pg["difference"]}
                cells = [fmt(d.get(f"{k}.delta_fr", {}).get("value"), d.get(f"{k}.delta_fr", {}).get("ci95"), True) for k, _ in FR_COLS]
                cells += [fmt(d.get(f"{s}.pg", {}).get("value"), d.get(f"{s}.pg", {}).get("ci95"), True) for s in PG_COLS]
            else:
                s, c = fr["stats"], fr["ci95"]
                cells = [fmt(s.get("neutral", {}).get("fr"))] + [fmt(s.get(k, {}).get("fr")) for k, _ in FR_COLS]
                cells += [fmt(s.get(k, {}).get("delta_fr"), c.get(f"{k}.delta_fr"), True) for k, _ in FR_COLS[:3]]
                ps, pc = pg["stats"], pg["ci95"]
                cells += [fmt(ps.get("orig", {}).get("auroc"))] + [fmt(ps.get(st, {}).get("pg"), pc.get(f"{st}.pg"), True) for st in PG_COLS]
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
    text = "\n".join(lines).strip() + "\n"
    out = ROOT / "results" / a.exp / f"table-{a.split}{'-vs-' + a.reference if a.reference else ''}{'' if a.slice == 'all' else '-' + a.slice}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"exp": a.exp, "split": a.split, "reference": a.reference, "slice": a.slice, "values": values}, indent=1), encoding="utf-8")
    print(text)
    print(f"written {out}")


if __name__ == "__main__":
    main()
