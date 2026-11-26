"""Training-data transforms for E2. Input: the exported decision-v7 train split (scripts/export_train.py).

    python augment/make.py --train data/decision-v7-train.jsonl --variant a1   --out data/a1.jsonl
    python augment/make.py --train data/decision-v7-train.jsonl --variant a2   --out data/a2.jsonl
    python augment/make.py --train data/decision-v7-train.jsonl --variant a1a2 --out data/a1a2.jsonl
    python augment/make.py --train data/decision-v7-train.jsonl --variant c1   --out data/c1.jsonl
    python augment/make.py --train data/decision-v7-train.jsonl --variant none --out data/baseline.jsonl   # identity (for the --data check)

a1   name randomization: with probability rho, a binary question with definitions becomes a two-option choice whose
     names are random 5-letter strings or a training polar pair bound in random order; the label follows the definition.
a2   polarity pairing: every templated yes/no question gets an extra record with a negated wording (S1 or S2 only),
     the gold flipped and its true/false definitions swapped.
c1   paraphrase control: the same extra records as a2, but with a same-polarity paraphrase (P1 or P2) and the gold kept.
a1a2 a2 first, then a1 over every record (originals and the new negated ones).
Writes <out> and <out>.stats.json. Deterministic for a given --seed.
"""
import argparse
import collections
import copy
import json
import random
import string
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import SPLITS, definitions, match, read_jsonl, rewrite, write_jsonl   # noqa: E402

TRAIN_NEG = SPLITS["negation_styles"]["train"]
PARA = SPLITS["paraphrase_styles"]
A1 = SPLITS["a1"]
A1_PAIRS = SPLITS["name_pairs"]["kev_seen"] + SPLITS["name_pairs"]["a1_train"]
RESERVED = {n for cat in ("heldout", "neutral", "random_test") for pair in SPLITS["name_pairs"][cat] for n in pair}


def random_name(rng):
    while True:
        s = "".join(rng.choice(string.ascii_lowercase) for _ in range(A1["random_len"]))
        if s not in RESERVED:
            return s


def pair_records(records, rng, stats, kind):
    """a2 / c1: one extra single-question record per templated yes/no question."""
    styles = TRAIN_NEG if kind == "a2" else PARA
    extra = []
    for r in records:
        for qid, q in r["questions"].items():
            if q["type"] != "noul" or match(q.get("src"), q.get("instructions")) is None:
                if q["type"] == "noul": stats[f"{kind}_no_template"][q.get("src")] += 1
                continue
            style = rng.choice(styles)
            nq = rewrite(q, style)
            if nq is None:
                stats[f"{kind}_no_style"][q.get("src")] += 1
                continue
            m = copy.deepcopy(r["_meta"])
            m["id"] = f"{m['id']}|{kind}|{qid}"
            m["aug"] = {"kind": kind, "style": style, "parent": r["_meta"]["id"], "qid": qid}
            extra.append({"state": r["state"], "questions": {qid: nq}, "_meta": m})
            stats[f"{kind}_added"][q["src"]] += 1
            stats[f"{kind}_style"][style] += 1
    return records + extra


def a1_question(q, rng, stats):
    """The question unchanged, or (with probability rho) as a choice with randomized names."""
    d = definitions(q)
    if d is None or q.get("target") is not None:
        if q["type"] == "noul": stats["a1_no_definitions"][q.get("src")] += 1
        return q
    if rng.random() >= A1["rho"]:
        stats["a1_kept"][q["src"]] += 1
        return q
    d_neg, d_pos, gold_pos = d
    if rng.random() < A1["p_random"]:
        a, b = random_name(rng), random_name(rng)
        while b == a: b = random_name(rng)
        kind = "random"
    else:
        a, b = rng.choice(A1_PAIRS)
        kind = f"{a}/{b}"
    if rng.random() < 0.5:
        bind = {a: d_neg, b: d_pos}      # aligned with the names' own polarity (for polar pairs)
    else:
        bind = {a: d_pos, b: d_neg}      # reversed binding
    names = list(bind); rng.shuffle(names)
    gold_def = d_pos if gold_pos else d_neg
    nq = {k: v for k, v in q.items() if k not in ("criteria", "label", "type")}
    nq.update(type="choice", criteria={n: bind[n] for n in names}, label=next(n for n in names if bind[n] == gold_def))
    stats["a1_converted"][q["src"]] += 1
    stats["a1_names"][kind] += 1
    return nq


def a1(records, rng, stats):
    out = []
    for r in records:
        new = copy.deepcopy(r)
        negated = r["_meta"].get("aug", {}).get("kind") == "a2"
        qs = {}
        for qid, q in r["questions"].items():
            if negated and not q.get("criteria"):
                # a negated question without its own definitions: the hand-written definitions describe the original
                # wording, so they would bind to the wrong side. Leave it as a plain yes/no question.
                stats["a1_skipped_negated_without_definitions"][q.get("src")] += 1
                qs[qid] = q
            else:
                qs[qid] = a1_question(q, rng, stats)
        new["questions"] = qs
        out.append(new)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--variant", choices=["none", "a1", "a2", "a1a2", "c1"], required=True)
    ap.add_argument("--seed", type=int, default=2)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    records = read_jsonl(a.train)
    rng = random.Random(f"augment:{a.variant}:{a.seed}")
    stats = collections.defaultdict(collections.Counter)
    if a.variant in ("a2", "a1a2"):
        records = pair_records(records, rng, stats, "a2")
    if a.variant == "c1":
        records = pair_records(records, rng, stats, "c1")
    if a.variant in ("a1", "a1a2"):
        records = a1(records, rng, stats)
    ids = [r["_meta"]["id"] for r in records]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate record ids")
    write_jsonl(a.out, records)
    qtypes = collections.Counter(q["type"] for r in records for q in r["questions"].values())
    summary = {"variant": a.variant, "seed": a.seed, "input": a.train, "records": len(records),
               "questions_by_type": dict(qtypes), **{k: dict(v) for k, v in stats.items()}}
    Path(a.out + ".stats.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
