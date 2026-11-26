"""Shared helpers: JSONL I/O, template matching, question rewriting and option definitions.

Records use Kev's labelled-request shape (kev.data.load_records): {"state", "questions": {qid: {...,"label","src"}}, "_meta"}.
Pure standard library, so it runs anywhere (the GPU steps import kev separately).
"""
import copy
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def write_jsonl(path, records):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def load_json(name):
    return json.loads((ROOT / "templates" / name).read_text(encoding="utf-8"))


TEMPLATES = load_json("templates.json")
SPLITS = load_json("splits.json")
NEGATIONS = ("S1", "S2", "S3")
PARAPHRASES = ("P1", "P2")


def is_clean(record):
    return record.get("_meta", {}).get("variant", "clean") == "clean"


def get_text(instructions):
    """The question string, whether instructions is a plain string or Kev's {"question", "focus"} object."""
    if isinstance(instructions, dict):
        return instructions.get("question")
    return instructions if isinstance(instructions, str) else None


def set_text(instructions, text):
    if isinstance(instructions, dict):
        return {**instructions, "question": text}
    return text


def match(src, instructions):
    """Named groups of the source's question pattern, or None when the source has no template or the text differs."""
    spec = TEMPLATES["questions"].get(src)
    text = get_text(instructions)
    if spec is None or text is None:
        return None
    m = re.match(spec["pattern"], text)
    return m.groupdict() if m else None


def fill(template, groups):
    out = template
    for k, v in groups.items():
        out = out.replace("{" + k + "}", v)   # plain replace: quoted sentences may contain braces
    return out


def has_style(src, style):
    return style in TEMPLATES["questions"].get(src, {})


def rewrite(q, style):
    """A copy of noul question q under a negation (S1-S3: gold flips, true/false definitions and targets swap) or a
    paraphrase (P1-P2: gold and definitions kept). None if the source has no template for that style."""
    groups = match(q.get("src"), q.get("instructions"))
    if groups is None or not has_style(q["src"], style):
        return None
    new = copy.deepcopy(q)
    new["instructions"] = set_text(q["instructions"], fill(TEMPLATES["questions"][q["src"]][style], groups))
    if style in NEGATIONS:
        new["label"] = not bool(q["label"])
        if q.get("criteria"):
            c = q["criteria"]
            new["criteria"] = {"true": c.get("false"), "false": c.get("true")}
        if q.get("target") is not None:
            t = q["target"]
            new["target"] = {"true": t.get("false", 0.0), "false": t.get("true", 0.0)}
    return new


def definitions(q):
    """(d_neg, d_pos, gold_is_pos) for a binary question with usable definitions, else None.
    noul: the record's own true/false descriptions, else the hand-written ones for its source.
    choice with two described options: Kev's accept/reject policy questions (reject = negative side)."""
    if q["type"] == "noul":
        c = q.get("criteria") or {}
        if c.get("true") and c.get("false"):
            return c["false"], c["true"], bool(q["label"])
        spec = TEMPLATES["definitions"].get(q.get("src"))
        if spec is None:
            return None
        groups = match(q["src"], q["instructions"])
        if groups is None:
            return None    # the wording is not the source's original template (e.g. a negated copy)
        return fill(spec["false"], groups), fill(spec["true"], groups), bool(q["label"])
    if q["type"] == "choice" and set(q.get("criteria", {})) == {"accept", "reject"}:
        c = q["criteria"]
        if c["accept"] and c["reject"]:
            return c["reject"], c["accept"], q["label"] == "accept"
    return None
