"""A stratified sample of probe items as readable Markdown, for hand-checking the labels and wordings.

    python probes/review/sample.py --n 25 --out probes/review/sample-50.md   # 25 name-swap + 25 negated-question items
"""
import argparse
import collections
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import read_jsonl, get_text   # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out"


def short(state, n=320):
    s = state if isinstance(state, str) else str(state)
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + " ..."


def stratified(items, key, n, rng):
    by = collections.defaultdict(list)
    for it in items: by[key(it)].append(it)
    for v in by.values(): rng.shuffle(v)
    out, keys = [], sorted(by)
    while len(out) < n and any(by.values()):
        for k in keys:
            if by[k] and len(out) < n: out.append(by[k].pop())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=25)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rng = random.Random(0)
    lines = ["# Probe items to hand-check", "",
             "For each item, check that the gold answer is right for the shown wording, and that a negated or renamed version",
             "says what it should. Mark problems in the last line of an item. States are cut at 320 characters.", ""]
    fr = [r for t in ("dv7-dev", "tv4-dev") for r in read_jsonl(OUT / f"{t}-fr.jsonl")]
    arms = collections.defaultdict(dict)
    for r in fr:
        m = r["_meta"]; arms[(m["orig_id"], m["qid"], m["pair"])][m["arm"]] = r
    pick = stratified([v for v in arms.values() if len(v) == 2], lambda v: v["aligned"]["_meta"]["task"], a.n, rng)
    lines += ["## A. Name swap", "", "Each question appears twice: names bound to their usual meaning (aligned), then swapped. "
              "The gold answer must follow the definition, so it changes name between the two arms.", ""]
    for i, v in enumerate(pick, 1):
        al = v["aligned"]; m = al["_meta"]; q = al["questions"]["q"]
        lines += [f"### A{i}. {m['task']} ({m['pair_cat']}: {m['pair']})", "", f"> {short(al['state'])}", "", f"**Question:** {get_text(q['instructions'])}", ""]
        for arm in ("aligned", "swapped"):
            qq = v[arm]["questions"]["q"]
            opts = "; ".join(f"`{k}`: {d}" for k, d in qq["criteria"].items())
            lines.append(f"- {arm}: {opts}  **gold: `{qq['label']}`**")
        lines += ["- check: OK / problem:", ""]
    pg = [r for t in ("dv7-dev", "tv4-dev") for r in read_jsonl(OUT / f"{t}-pg.jsonl")]
    groups = collections.defaultdict(dict)
    for r in pg:
        m = r["_meta"]; groups[(m["orig_id"], m["qid"])][m["style"]] = r
    pick = stratified(list(groups.values()), lambda g: g["orig"]["_meta"]["task"], a.n, rng)
    lines += ["## B. Negated questions", "", "The original wording, then each negated style (S3 is held out of training). "
              "The gold flips under negation. Where a question has yes/no definitions, they swap too.", ""]
    for i, g in enumerate(pick, 1):
        o = g["orig"]; m = o["_meta"]
        lines += [f"### B{i}. {m['task']}", "", f"> {short(o['state'])}", ""]
        for st in ("orig", "S1", "S2", "S3"):
            if st not in g: continue
            q = g[st]["questions"]["q"]; c = q.get("criteria") or {}
            defs = f" (yes = {c.get('true')}; no = {c.get('false')})" if c else ""
            lines.append(f"- {st}: {get_text(q['instructions'])}  **gold: {'yes' if q['label'] else 'no'}**{defs}")
        lines += ["- check: OK / problem:", ""]
    Path(a.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {a.out}: {a.n} name-swap and {a.n} negated items")


if __name__ == "__main__":
    main()
