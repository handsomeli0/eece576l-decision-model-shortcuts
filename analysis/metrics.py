"""Flip rate (name swap) and polarity gap (negated wording) from a probe file and a model's scored rows.

    python analysis/metrics.py --probe probes/out/dv7-dev-fr.jsonl --rows runs/e1/v7base-dv7-dev-fr
    python analysis/metrics.py --probe probes/out/dv7-dev-pg.jsonl --rows runs/e1/v7base-dv7-dev-pg
    # E2: paired difference against the baseline on the same probe (same bootstrap resamples)
    python analysis/metrics.py --probe ...-fr.jsonl --rows runs/e2/a1-... --reference runs/e2/baseline-... --out results/a1-fr.json

--rows / --reference: a kev.benchmark output directory (its rows.json) or a rows.json file; probes/qwen_lp.py writes the
same format. Bootstrap: 2,000 resamples of _meta.group_id (questions about one state move together), 95% percentile
intervals. Standard library only.
"""
import argparse
import collections
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import read_jsonl   # noqa: E402


def load_rows(path):
    p = Path(path)
    p = p / "rows.json" if p.is_dir() else p
    return {r["id"]: r for r in json.loads(p.read_text(encoding="utf-8"))}


def auroc(scores, labels):
    """Mann-Whitney AUROC with average ranks for ties; None if one class is missing."""
    pos = sum(labels); neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return None
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    rank_pos = sum(r for r, y in zip(ranks, labels) if y)
    return (rank_pos - pos * (pos + 1) / 2) / (pos * neg)


def balanced_acc(preds, labels):
    tp = sum(p and y for p, y in zip(preds, labels)); pos = sum(labels)
    tn = sum((not p) and (not y) for p, y in zip(preds, labels)); neg = len(labels) - pos
    if pos == 0 or neg == 0:
        return None
    return (tp / pos + tn / neg) / 2


def ci(values):
    v = sorted(x for x in values if x is not None)
    if not v:
        return None
    return [round(v[int(0.025 * (len(v) - 1))], 4), round(v[int(0.975 * (len(v) - 1))], 4)]


def rnd(x):
    return None if x is None else round(x, 4)


# ---------------------------------------------------------------- name swap (FR)

def fr_units(probe, rows):
    """One unit per (question, name pair): the side (pos/neg definition) selected in each arm."""
    units = collections.defaultdict(dict)
    missing = 0
    for rec in probe:
        m = rec["_meta"]; row = rows.get(m["id"])
        if row is None:
            missing += 1; continue
        keys, p = row["keys"], row["p"]
        sel = keys[max(range(len(p)), key=p.__getitem__)]
        p_pos = p[keys.index(m["pos_name"])]
        key = (m["orig_id"], m["qid"], m["pair"])
        units[key][m["arm"]] = {"sel_pos": sel == m["pos_name"], "p_pos": p_pos}
        units[key].update(cat=m["pair_cat"], group=m["group_id"], task=m["task"], gold_pos=m["gold_side"] == "pos", pair=m["pair"])
    done = [u for u in units.values() if "aligned" in u and "swapped" in u]
    return done, missing


def fr_stats(units):
    by_cat = collections.defaultdict(list)
    for u in units:
        by_cat[u["cat"]].append(u)
    out = {}
    for cat, us in by_cat.items():
        flips = [u["aligned"]["sel_pos"] != u["swapped"]["sel_pos"] for u in us]
        d = {"n": len(us), "fr": sum(flips) / len(us)}
        for arm in ("aligned", "swapped"):
            y = [u["gold_pos"] for u in us]
            d[f"bal_acc_{arm}"] = balanced_acc([u[arm]["sel_pos"] for u in us], y)
            d[f"auc_{arm}"] = auroc([u[arm]["p_pos"] for u in us], y)
        out[cat] = d
    if "neutral" in out:
        for cat in out:
            out[cat]["delta_fr"] = out[cat]["fr"] - out["neutral"]["fr"]
    return out


# ---------------------------------------------------------------- negated wording (PG)

def pg_units(probe, rows):
    units = collections.defaultdict(dict)
    missing = 0
    for rec in probe:
        m = rec["_meta"]; row = rows.get(m["id"])
        if row is None:
            missing += 1; continue
        keys, p = row["keys"], row["p"]
        p_yes = p[keys.index("true")]
        y = keys[row["label"]] == "true"
        key = (m["orig_id"], m["qid"])
        units[key][m["style"]] = {"p_yes": p_yes, "y": y}
        units[key].update(group=m["group_id"], task=m["task"])
    done = [u for u in units.values() if "orig" in u]
    return done, missing


def pg_stats(units):
    out = {}
    styles = sorted({s for u in units for s in u if s.startswith("S")})
    base = [u for u in units]
    out["orig"] = {"n": len(base), "auroc": auroc([u["orig"]["p_yes"] for u in base], [u["orig"]["y"] for u in base]),
                   "acc": sum((u["orig"]["p_yes"] >= 0.5) == u["orig"]["y"] for u in base) / len(base)}
    for s in styles:
        us = [u for u in units if s in u]
        a_orig = auroc([u["orig"]["p_yes"] for u in us], [u["orig"]["y"] for u in us])
        a_neg = auroc([u[s]["p_yes"] for u in us], [u[s]["y"] for u in us])
        out[s] = {"n": len(us), "auroc": a_neg,
                  "acc": sum((u[s]["p_yes"] >= 0.5) == u[s]["y"] for u in us) / len(us),
                  "pg": None if a_orig is None or a_neg is None else a_orig - a_neg,
                  "inconsistency": sum(abs(u["orig"]["p_yes"] + u[s]["p_yes"] - 1) for u in us) / len(us)}
    return out


# ---------------------------------------------------------------- bootstrap

def resample(units, rng):
    groups = collections.defaultdict(list)
    for u in units:
        groups[u["group"]].append(u)
    keys = list(groups)
    def draw():
        out = []
        for _ in keys:
            out.extend(groups[keys[rng.randrange(len(keys))]])
        return out
    return draw


def headline(kind, stats):
    """The numbers that get intervals: delta_fr and fr per category, or pg and auroc per style."""
    flat = {}
    for k, d in stats.items():
        for f in (("fr", "delta_fr", "auc_swapped") if kind == "fr" else ("pg", "auroc", "inconsistency")):
            if d.get(f) is not None:
                flat[f"{k}.{f}"] = d[f]
    return flat


def analyse(kind, units, ref_units=None, B=2000, seed=0):
    compute = fr_stats if kind == "fr" else pg_stats
    point = compute(units)
    result = {"stats": {k: {f: rnd(v) if isinstance(v, float) else v for f, v in d.items()} for k, d in point.items()}}
    by_task = collections.defaultdict(list)
    for u in units:
        by_task[u["task"]].append(u)
    result["by_task"] = {t: {k: {f: rnd(v) if isinstance(v, float) else v for f, v in d.items()} for k, d in compute(us).items()}
                         for t, us in sorted(by_task.items())}
    rng = random.Random(seed)
    if ref_units is None:
        draw = resample(units, rng)
        samples = [headline(kind, compute(draw())) for _ in range(B)]
        result["ci95"] = {k: ci([s.get(k) for s in samples]) for k in headline(kind, point)}
        return result
    # paired: resample the same groups for model and reference
    ref_point = compute(ref_units)
    result["reference_stats"] = {k: {f: rnd(v) if isinstance(v, float) else v for f, v in d.items()} for k, d in ref_point.items()}
    groups = collections.defaultdict(lambda: ([], []))
    for u in units: groups[u["group"]][0].append(u)
    for u in ref_units: groups[u["group"]][1].append(u)
    keys = list(groups)
    diffs, own = collections.defaultdict(list), collections.defaultdict(list)
    for _ in range(B):
        a, b = [], []
        for _ in keys:
            g = groups[keys[rng.randrange(len(keys))]]
            a.extend(g[0]); b.extend(g[1])
        ha, hb = headline(kind, compute(a)), headline(kind, compute(b))
        for k in ha:
            own[k].append(ha[k])
            if k in hb:
                diffs[k].append(ha[k] - hb[k])
    hp, hr = headline(kind, point), headline(kind, ref_point)
    result["ci95"] = {k: ci(own[k]) for k in hp}
    result["difference"] = {k: {"value": rnd(hp[k] - hr[k]), "ci95": ci(diffs[k])} for k in hp if k in hr}
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", required=True)
    ap.add_argument("--rows", required=True)
    ap.add_argument("--reference", help="rows of the model to compare against (paired bootstrap)")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--out")
    a = ap.parse_args()
    probe = read_jsonl(a.probe)
    kind = probe[0]["_meta"]["probe"]
    make = fr_units if kind == "fr" else pg_units
    units, missing = make(probe, load_rows(a.rows))
    ref_units = None
    if a.reference:
        ref_units, _ = make(probe, load_rows(a.reference))
    res = {"probe": a.probe, "kind": kind, "rows": a.rows, "reference": a.reference, "units": len(units),
           "missing_rows": missing, **analyse(kind, units, ref_units, a.boot)}
    text = json.dumps(res, indent=2)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
    s = res["stats"]
    if kind == "fr":
        print(f"{'names':12} {'n':>5} {'FR':>7} {'dFR':>7} {'dFR 95% CI':>18} {'AUC al':>7} {'AUC sw':>7}")
        for cat in ("kev_seen", "a1_train", "heldout", "random_test", "neutral"):
            if cat in s:
                d = s[cat]; c = res.get("ci95", {}).get(f"{cat}.delta_fr")
                print(f"{cat:12} {d['n']:5} {d['fr']:7.3f} {d.get('delta_fr', 0):7.3f} {str(c):>18} {d['auc_aligned'] or 0:7.3f} {d['auc_swapped'] or 0:7.3f}")
    else:
        print(f"{'wording':8} {'n':>5} {'AUROC':>7} {'acc':>6} {'PG':>7} {'PG 95% CI':>18} {'incons':>7}")
        for st in ("orig", "S1", "S2", "S3"):
            if st in s:
                d = s[st]; c = res.get("ci95", {}).get(f"{st}.pg")
                pg = "-" if d.get("pg") is None else f"{d['pg']:.3f}"
                inc = "-" if d.get("inconsistency") is None else f"{d['inconsistency']:.3f}"
                print(f"{st:8} {d['n']:5} {d['auroc'] or 0:7.3f} {d['acc']:6.3f} {pg:>7} {str(c or '-'):>18} {inc:>7}")
    if "difference" in res:
        print("difference vs reference:")
        for k, d in res["difference"].items():
            if k.endswith(("delta_fr", ".pg")):
                print(f"  {k:24} {d['value']:+.3f} {d['ci95']}")
    if missing:
        print(f"WARNING: {missing} probe records have no scored row", file=sys.stderr)


if __name__ == "__main__":
    main()
