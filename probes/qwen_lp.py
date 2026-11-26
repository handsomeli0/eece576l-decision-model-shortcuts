"""Untrained baseline: Qwen3.5-0.8B-Base read out by next-token log-probabilities over option letters.

    python probes/qwen_lp.py --data probes/out/dv7-dev-fr.jsonl --out runs/e1/qwen-dv7-dev-fr
    python probes/qwen_lp.py --data probes/out/dv7-dev-pg.jsonl --out runs/e1/qwen-dv7-dev-pg --limit 40   # smoke test

Prompt (as in Kev's scripts/base_mmlu_probe.py, but each option shows its name AND definition, since the name is what
the name-swap probe changes):

    <state>
    <instructions>
    A. <name>: <definition>
    B. <name>: <definition>
    Answer:

Options use Kev's own rendering (kev.api.render / option_text): a yes/no question becomes "no: <false definition>" and
"yes: <true definition>" (bare "no"/"yes" without definitions), in that order, with keys ["false", "true"]. Every
question is scored under all K cyclic rotations of its options (K = 2 here), and the letter log-probabilities are
averaged per option, so letter position cannot count as a flip. Writes rows.json (kev.benchmark row format, so
analysis/metrics.py and kev.compare read it) and report.json. Needs the Kev environment (torch, transformers, fla).
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from kev.api import option_text, render

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import read_jsonl   # noqa: E402

BASE = "Qwen/Qwen3.5-0.8B-Base"
REVISION = "dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68"   # the revision Kev-0.8B was trained from
LETTERS = "ABCDEFGH"


def options(q):
    """(keys, option texts) in Kev's order."""
    if q["type"] == "noul":
        c = q.get("criteria") or {}
        return ["false", "true"], [option_text("no", c.get("false")), option_text("yes", c.get("true"))]
    if q["type"] == "choice":
        return list(q["criteria"]), [option_text(k, v) for k, v in q["criteria"].items()]
    raise ValueError(f"unsupported question type {q['type']}")


def label_index(q, keys):
    return keys.index(q["label"]) if q["type"] == "choice" else int(bool(q["label"]))


def prompt(state, instructions, opts):
    return f"{render(state)}\n{render(instructions)}\n" + "\n".join(f"{LETTERS[i]}. {o}" for i, o in enumerate(opts)) + "\nAnswer:"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="a probe file from probes/build.py (or any labelled-request JSONL)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--base", default=BASE)
    ap.add_argument("--revision", default=REVISION)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--limit", type=int, help="score only the first N records (smoke test)")
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        raise SystemExit(f"{out} exists; pick a new --out")
    records = read_jsonl(a.data)[: a.limit]
    tok = AutoTokenizer.from_pretrained(a.base, revision=a.revision)
    dtype = torch.bfloat16 if a.device != "cpu" else torch.float32
    model = AutoModelForCausalLM.from_pretrained(a.base, revision=a.revision, dtype=dtype).to(a.device).eval()
    letter_ids = [tok.encode(" " + L, add_special_tokens=False) for L in LETTERS]
    if any(len(t) != 1 for t in letter_ids) or len({t[0] for t in letter_ids}) != len(LETTERS):
        raise SystemExit("letter tokens are not single, distinct tokens")
    letter_ids = [t[0] for t in letter_ids]
    rows, t0, hits = [], time.time(), 0
    with torch.no_grad():
        for n, r in enumerate(records):
            m = r["_meta"]
            for qid, q in r["questions"].items():
                keys, opts = options(q)
                k = len(keys)
                logp = [[] for _ in range(k)]
                for rot in range(k):
                    order = [(i + rot) % k for i in range(k)]          # order[slot] = option shown in that slot
                    ids = tok(prompt(r["state"], q["instructions"], [opts[i] for i in order]), return_tensors="pt").to(a.device)
                    logits = model(**ids).logits[0, -1].float()
                    lp = torch.log_softmax(logits[letter_ids[:k]], -1).tolist()
                    for slot, i in enumerate(order):
                        logp[i].append(lp[slot])
                mean = [sum(v) / len(v) for v in logp]
                z = max(mean); w = [math.exp(x - z) for x in mean]; p = [x / sum(w) for x in w]
                y = label_index(q, keys)
                hits += int(max(range(k), key=p.__getitem__) == y)
                rows.append({"id": m["id"], "group": m.get("group_id", m["id"]), "question": qid, "source": m.get("source", q.get("src")),
                             "task": q.get("src"), "type": q["type"], "variant": m.get("variant", "clean"), "keys": keys, "label": y,
                             "parent": m.get("orig_id", m["id"]), "p": p, "rotation_logp": logp})
            if (n + 1) % 500 == 0:
                el = time.time() - t0
                print(f"{n + 1}/{len(records)}  {el / (n + 1):.3f} s/record  acc {hits / len(rows):.3f}", flush=True)
    out.mkdir(parents=True)
    (out / "rows.json").write_text(json.dumps(rows), encoding="utf-8")
    report = {"base": a.base, "revision": a.revision, "data": a.data, "records": len(records), "rows": len(rows),
              "readout": "next-token log-probs over ' A'/' B'..., averaged over all cyclic option rotations",
              "acc": round(hits / max(len(rows), 1), 4), "wall_seconds": round(time.time() - t0, 1),
              "peak_device_bytes": torch.cuda.max_memory_allocated() if a.device.startswith("cuda") else None}
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
