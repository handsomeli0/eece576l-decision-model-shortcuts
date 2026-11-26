#!/usr/bin/env bash
# CPU only, a few minutes: export the train split, build the probe sets, build every training variant.
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$PROJ"
mkdir -p data probes/out
[ -f data/decision-v7-train.jsonl ] || python scripts/export_train.py --suite "$V7" --out data/decision-v7-train.jsonl
for split in development test; do
  s=$([ $split = development ] && echo dev || echo test)
  python probes/build.py --suite "$V7"  --split $split --tag dv7-$s --out probes/out > /dev/null
  python probes/build.py --suite "$TV4" --split $split --tag tv4-$s --out probes/out > /dev/null
done
for v in none a1 a2 a1a2 c1; do
  python augment/make.py --train data/decision-v7-train.jsonl --variant $v --seed "${SEED:-2}" --out data/$v-s${SEED:-2}.jsonl > /dev/null
done
python - <<'PY'
import json, glob
for f in sorted(glob.glob("probes/out/*-manifest.json")):
    m = json.load(open(f)); print(f"{f:36} FR {m['fr']['questions']:4} q / {m['fr']['records']:5} rec   PG {m['pg']['questions']:4} q / {m['pg']['records']:5} rec")
for f in sorted(glob.glob("data/*.stats.json")):
    s = json.load(open(f)); print(f"{f:36} {s['records']:6} records  {s['questions_by_type']}")
PY
