"""Build the two probe sets from a frozen Kev suite split.

    python probes/build.py --suite ~/eece576l/kev/evals/v7/decision-v7 --split development --tag dv7-dev --out probes/out
    python probes/build.py --suite ~/eece576l/kev/evals/v4/transfer-v4 --split test        --tag tv4-test --out probes/out

Writes <tag>-fr.jsonl (name swap), <tag>-pg.jsonl (negated wording) and <tag>-manifest.json. Every record holds one
question and carries _meta.probe/orig_id/qid/... so analysis/metrics.py can pair the arms. Score them with
    python -m kev.benchmark --run <ckpt> --data probes/out/<tag>-fr.jsonl --rotations 2 --out runs/<name>
"""
import argparse
import collections
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import SPLITS, is_clean, match, read_jsonl, rewrite, definitions, write_jsonl, NEGATIONS   # noqa: E402

FR_EXCLUDE = {"boolq"}    # generic "the passage supports a yes answer" definitions (Sun et al. exclude these)
PG_EXCLUDE = {"boolq"}    # natural questions: hand negation deferred


def meta(record, qid, q, **extra):
    m = record["_meta"]
    return {"id": None, "group_id": m.get("group_id", m["id"]), "source": m.get("source", q["src"]), "variant": "clean",
            "orig_id": m["id"], "qid": qid, "task": q["src"], **extra}


def fr_records(record, qid, q):
    """Aligned and swapped bindings for every name pair. Option order is [negative name, positive name] in both arms;
    score with --rotations 2 so position does not count as a flip."""
    d = definitions(q)
    if d is None or q["src"] in FR_EXCLUDE:
        return []
    d_neg, d_pos, gold_pos = d
    out = []
    for cat, pairs in SPLITS["name_pairs"].items():
        for n_neg, n_pos in pairs:
            for arm in ("aligned", "swapped"):
                bind = {n_neg: d_neg, n_pos: d_pos} if arm == "aligned" else {n_neg: d_pos, n_pos: d_neg}
                gold_name = next(n for n, dd in bind.items() if dd == (d_pos if gold_pos else d_neg))
                nq = {"type": "choice", "instructions": copy.deepcopy(q["instructions"]), "criteria": bind,
                      "label": gold_name, "src": q["src"]}
                m = meta(record, qid, q, probe="fr", pair_cat=cat, pair=f"{n_neg}/{n_pos}", arm=arm,
                         gold_side="pos" if gold_pos else "neg", pos_name=n_pos if arm == "aligned" else n_neg)
                m["id"] = f"fr|{record['_meta']['id']}|{qid}|{n_neg}/{n_pos}|{arm}"
                out.append({"state": record["state"], "questions": {"q": nq}, "_meta": m})
    return out


def pg_records(record, qid, q):
    """Original wording plus each negation style S1-S3 (gold flipped)."""
    if q["type"] != "noul" or q["src"] in PG_EXCLUDE or match(q["src"], q["instructions"]) is None:
        return []
    out = []
    for style in ("orig",) + NEGATIONS:
        nq = copy.deepcopy(q) if style == "orig" else rewrite(q, style)
        if nq is None:
            continue
        m = meta(record, qid, q, probe="pg", style=style, orig_label=bool(q["label"]))
        m["id"] = f"pg|{record['_meta']['id']}|{qid}|{style}"
        out.append({"state": record["state"], "questions": {"q": nq}, "_meta": m})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True, help="Kev suite directory, e.g. ~/eece576l/kev/evals/v7/decision-v7")
    ap.add_argument("--split", choices=["development", "test"], required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", default="probes/out")
    a = ap.parse_args()
    records = [r for r in read_jsonl(Path(a.suite).expanduser() / f"{a.split}.jsonl") if is_clean(r)]
    fr, pg, unmatched = [], [], collections.Counter()
    for r in records:
        for qid, q in r["questions"].items():
            binary = q["type"] == "noul" or (q["type"] == "choice" and len(q.get("criteria", {})) == 2)
            if not binary:
                continue
            got_fr, got_pg = fr_records(r, qid, q), pg_records(r, qid, q)
            fr += got_fr; pg += got_pg
            if not got_fr and not got_pg:
                unmatched[q["src"]] += 1
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / f"{a.tag}-fr.jsonl", fr)
    write_jsonl(out / f"{a.tag}-pg.jsonl", pg)
    count = lambda rs, key: dict(collections.Counter(r["_meta"][key] for r in rs))
    # the suite as e.g. "v7/decision-v7", so the manifest is the same on every machine
    manifest = {"suite": "/".join(Path(a.suite).expanduser().parts[-2:]), "split": a.split, "source_records": len(records),
                "fr": {"records": len(fr), "questions": len({(r["_meta"]["orig_id"], r["_meta"]["qid"]) for r in fr}),
                       "by_task": count(fr, "task"), "by_pair_cat": count(fr, "pair_cat")},
                "pg": {"records": len(pg), "questions": len({(r["_meta"]["orig_id"], r["_meta"]["qid"]) for r in pg}),
                       "by_task": count(pg, "task"), "by_style": count(pg, "style")},
                "binary_questions_skipped": dict(unmatched)}
    (out / f"{a.tag}-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
