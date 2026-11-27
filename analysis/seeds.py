"""Each variant minus its own-seed baseline, for every seed, and the seed average with a joint group bootstrap.

    python analysis/seeds.py --split dev                       # seeds 2 and 3 as laid out by the run scripts
    python analysis/seeds.py --split dev --slice policy

A seed is (experiment directory of the variants, experiment directory and name of that seed's baseline):
    seed 2: variants in runs/e2/, baseline = runs/e1/baseline-*   (Kev's stage-1 recipe, our replication)
    seed 3: variants in runs/e2s3/, baseline = runs/e2s3/baseline-*
Every resample draws one set of state groups and applies it to every model and seed, so the interval of the average
reflects question sampling; the spread between the per-seed columns shows seed-to-seed variation (two seeds are too
few to put an interval on that). Writes results/seeds/table-<split>[-<slice>].{md,json}. Standard library only.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import read_jsonl                                       # noqa: E402
from analysis.metrics import ci, fr_stats, fr_units, headline, load_rows, pg_stats, pg_units, rnd   # noqa: E402
from analysis.table import SLICES, SUITES                           # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SEEDS = {2: ("e2", "e1", "baseline"), 3: ("e2s3", "e2s3", "baseline")}
MODELS = ["a1", "a2", "a1a2", "c1"]
COLS = [("fr", "kev_seen.delta_fr", "dFR seen"), ("fr", "heldout.delta_fr", "dFR held-out"),
        ("pg", "S1.pg", "PG S1"), ("pg", "S2.pg", "PG S2"), ("pg", "S3.pg", "PG S3")]


def units_for(exp, name, tag, probe, keep):
    rows = ROOT / "runs" / exp / f"{name}-{tag}-{probe}"
    if keep is None or not (rows / "rows.json").exists():
        return None
    data = [r for r in read_jsonl(ROOT / "probes" / "out" / f"{tag}-{probe}.jsonl") if keep(r)]
    make = fr_units if probe == "fr" else pg_units
    units, _ = make(data, load_rows(rows))
    return units or None


def by_group(units):
    g = collections.defaultdict(list)
    for u in units:
        g[u["group"]].append(u)
    return g


def compare(model, tag, probe, keep, boot, seed=0):
    """{metric: {"seeds": {seed: diff}, "mean": avg, "ci95": [lo, hi]}} for one model, suite and probe."""
    pairs = {}
    for s, (exp, ref_exp, ref) in SEEDS.items():
        m, r = units_for(exp, model, tag, probe, keep), units_for(ref_exp, ref, tag, probe, keep)
        if m and r:
            pairs[s] = (by_group(m), by_group(r))
    if not pairs:
        return {}
    stats = fr_stats if probe == "fr" else pg_stats
    point = {s: (headline(probe, stats([u for v in m.values() for u in v])), headline(probe, stats([u for v in r.values() for u in v])))
             for s, (m, r) in pairs.items()}
    keys = sorted(set.union(*(set(g) for pair in pairs.values() for g in pair)))
    rng = random.Random(seed)
    draws = collections.defaultdict(list)
    for _ in range(boot):
        pick = [keys[rng.randrange(len(keys))] for _ in keys]
        per_seed = collections.defaultdict(list)
        for s, (m, r) in pairs.items():
            hm = headline(probe, stats([u for k in pick for u in m.get(k, [])]))
            hr = headline(probe, stats([u for k in pick for u in r.get(k, [])]))
            for k in hm:
                if k in hr:
                    per_seed[k].append(hm[k] - hr[k])
        for k, v in per_seed.items():
            if len(v) == len(pairs):
                draws[k].append(sum(v) / len(v))
    out = {}
    for k in {k for hm, hr in point.values() for k in hm if k in hr}:
        diffs = {s: hm[k] - hr[k] for s, (hm, hr) in point.items() if k in hm and k in hr}
        out[k] = {"seeds": {s: rnd(v) for s, v in diffs.items()}, "mean": rnd(sum(diffs.values()) / len(diffs)),
                  "ci95": ci(draws[k]) if len(diffs) == len(pairs) else None}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="dev")
    ap.add_argument("--slice", choices=list(SLICES), default="all")
    ap.add_argument("--boot", type=int, default=2000)
    a = ap.parse_args()
    what, keep_fr, keep_pg = SLICES[a.slice]
    lines, values = [], {}
    for short, suite in SUITES.items():
        tag = f"{short}-{a.split}"
        head = ["model"] + [label for _, _, label in COLS]
        lines += [f"\n### {suite} {a.split}, {what}: variant minus same-seed baseline",
                  "\nEach cell: seed-average [95% joint bootstrap] (seed 2 / seed 3).\n",
                  "| " + " | ".join(head) + " |", "|---" * len(head) + "|"]
        for model in MODELS:
            res = {**compare(model, tag, "fr", keep_fr, a.boot), **compare(model, tag, "pg", keep_pg, a.boot)}
            if not res:
                continue
            values.setdefault(suite, {})[model] = res
            cells = []
            for _, key, _ in COLS:
                d = res.get(key)
                if not d:
                    cells.append("-"); continue
                c = d["ci95"]
                per = " / ".join(f"{d['seeds'][s]:+.3f}" if s in d["seeds"] else "-" for s in SEEDS)
                cells.append(f"{d['mean']:+.3f}" + (f" [{c[0]:+.2f}, {c[1]:+.2f}]" if c else "") + f" ({per})")
            lines.append(f"| {model} | " + " | ".join(cells) + " |")
    text = "\n".join(lines).strip() + "\n"
    out = ROOT / "results" / "seeds" / f"table-{a.split}{'' if a.slice == 'all' else '-' + a.slice}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    out.with_suffix(".json").write_text(json.dumps({"split": a.split, "slice": a.slice, "seeds": {s: list(v) for s, v in SEEDS.items()},
                                                    "values": values}, indent=1), encoding="utf-8")
    print(text)
    print(f"written {out}")


if __name__ == "__main__":
    main()
