"""Did a fix cost accuracy or calibration? Kev's own benchmark metrics for every model, and each variant minus its baseline.

    python analysis/accuracy.py --split test     # runs/test/<name>-{decision,transfer}/ (scripts/test_all.sh writes them)
    python analysis/accuracy.py --split dev      # runs/train/<run>-{decision,transfer}/ (scripts/train.sh writes them)

Point values are kev.benchmark's report.json "clean" block (clean questions of knowable records, every question weighted
equally): accuracy, NLL, ECE, Brier. Differences use Kev's own paired cluster bootstrap (kev.metrics.paired_bootstrap,
micro, 2,000 resamples; a record's sibling questions move together), against the same-seed baseline:
    seed 2 variants (a1, a2, a1a2, c1)       vs baseline      (the stage-1 replication)
    seed 3 variants (a1-s3, ...)             vs baseline-s3
    baseline                                 vs v7base        (replication check)
Dev mode has no v7base or seed-2 baseline run in runs/train; pass them with --extra name=dir (a kev.benchmark output
directory without its -decision / -transfer suffix). Writes results/accuracy/table-<split>.{md,json}. Needs Kev (numpy).
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, os.environ.get("KEV") or str(ROOT / "third_party" / "kev"))
from kev.metrics import paired_bootstrap   # noqa: E402

SUITES = {"decision": "decision-v7", "transfer": "transfer-v4"}
ORDER = ["v7base", "baseline", "a1", "a2", "a1a2", "c1", "baseline-s3", "a1-s3", "a2-s3", "a1a2-s3", "c1-s3"]
METRICS = [("acc", "acc", "{:.4f}"), ("nll", "NLL", "{:.4f}"), ("ece", "ECE", "{:.4f}"), ("brier", "Brier", "{:.4f}")]


def reference(name):
    if name == "baseline":
        return "v7base"
    if name in ("v7base", "baseline-s3"):
        return None
    return "baseline-s3" if name.endswith("-s3") else "baseline"


def runs(split, extra):
    """{model name: directory prefix}; a model's suite runs are <prefix>-decision and <prefix>-transfer."""
    found = {}
    if split == "test":
        for d in sorted((ROOT / "runs" / "test").glob("*-decision")):
            found[d.name[: -len("-decision")]] = d.parent / d.name[: -len("-decision")]
    else:
        for d in sorted((ROOT / "runs" / "train").glob("*-s[0-9]-decision")):
            run = d.name[: -len("-decision")]
            variant, seed = run.rsplit("-s", 1)
            name = "baseline" if variant == "none" else variant
            found[name if seed == "2" else f"{name}-s{seed}"] = d.parent / run
    for item in extra:
        name, _, path = item.partition("=")
        found[name] = Path(path)
    return found


def load(prefix, suite):
    d = Path(f"{prefix}-{suite}")
    if not (d / "report.json").exists():
        return None
    report = json.loads((d / "report.json").read_text(encoding="utf-8"))
    rows = json.loads((d / "rows.json").read_text(encoding="utf-8")) if (d / "rows.json").exists() else None
    return {"report": report, "rows": rows, "dir": str(d)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--extra", action="append", default=[], help="name=directory prefix, e.g. baseline=$KEV/runs/repl-v7base-dev")
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    found = runs(a.split, a.extra)
    names = [n for n in ORDER if n in found] + sorted(n for n in found if n not in ORDER)
    lines, values = [], {}
    for short, suite in SUITES.items():
        data = {n: load(found[n], short) for n in names}
        data = {n: d for n, d in data.items() if d}
        if not data:
            continue
        head = ["model"] + [label for _, label, _ in METRICS] + ["reference", "Δacc [95% CI]", "ΔNLL [95% CI]"]
        lines += [f"\n### {suite} {a.split}: Kev benchmark metrics (clean questions of knowable records)\n",
                  "| " + " | ".join(head) + " |", "|---" * len(head) + "|"]
        for n, d in data.items():
            clean = d["report"]["clean"]
            entry = {k: clean.get(k) for k, _, _ in METRICS} | {"n": clean.get("n"), "dir": d["dir"]}
            cells = [fmt.format(clean[k]) if clean.get(k) is not None else "-" for k, _, fmt in METRICS]
            ref = reference(n)
            if ref in data and d["rows"] and data[ref]["rows"]:
                entry["reference"] = ref
                for metric in ("acc", "nll", "brier"):
                    b = paired_bootstrap(d["rows"], data[ref]["rows"], samples=a.boot, metric=metric, aggregation="micro")
                    entry[f"delta_{metric}"] = {"value": round(b[f"micro_{metric}_delta"], 4), "ci95": [round(x, 4) for x in b["ci95"]]}
                cells.append(ref)
                for metric in ("acc", "nll"):
                    dd = entry[f"delta_{metric}"]
                    cells.append(f"{dd['value']:+.4f} [{dd['ci95'][0]:+.3f}, {dd['ci95'][1]:+.3f}]")
            else:
                cells += ["-", "-", "-"]
            values.setdefault(suite, {})[n] = entry
            lines.append(f"| {n} | " + " | ".join(cells) + " |")
    if not values:
        raise SystemExit(f"no benchmark reports found for split {a.split}")
    lines.append("\nΔ = model minus reference (paired cluster bootstrap, micro). Lower NLL is better; seed-3 models "
                 "are compared with the seed-3 baseline.")
    text = "\n".join(lines).strip() + "\n"
    out = ROOT / "results" / "accuracy" / f"table-{a.split}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"split": a.split, "values": values}, indent=1), encoding="utf-8")
    print(text)
    print(f"written {out}")


if __name__ == "__main__":
    main()
