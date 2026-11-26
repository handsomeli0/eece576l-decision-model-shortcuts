"""Write a frozen suite's training partition to JSONL (checksum-verified by kev.suite.load_split), the input to
augment/make.py. Run inside Kev's environment:

    python scripts/export_train.py --suite ~/eece576l/kev/evals/v7/decision-v7 --out data/decision-v7-train.jsonl
"""
import argparse
import collections
import json
import sys
from pathlib import Path

from kev.suite import load_split, read_manifest, validate_training

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import write_jsonl   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    suite = Path(a.suite).expanduser()
    records = load_split(suite, "train")
    validate_training(records, read_manifest(suite))
    write_jsonl(a.out, records)
    by_source = collections.Counter(r["_meta"]["source"] for r in records)
    print(json.dumps({"suite": str(suite), "records": len(records), "by_source": dict(by_source)}, indent=2))


if __name__ == "__main__":
    main()
