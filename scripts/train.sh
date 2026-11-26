#!/usr/bin/env bash
# E2: train one variant (about 1.7 h for A1, about 2.3 h for A2, A1+A2 and C1 on the 4060).
#   scripts/train.sh <variant> [seed]      variant: a1 | a2 | a1a2 | c1 | none   (none = baseline through --data)
set -euo pipefail
source "$(dirname "$0")/env.sh"
v=$1; seed=${2:-2}
data="$PROJ/data/$v-s$seed.jsonl"; out="$PROJ/runs/train/$v-s$seed"
[ -f "$data" ] || python "$PROJ/augment/make.py" --train "$PROJ/data/decision-v7-train.jsonl" --variant "$v" --seed "$seed" --out "$data"
[ -e "$out" ] && { echo "$out exists" >&2; exit 1; }
mkdir -p "$PROJ/runs/train"
cd "$KEV"
python -m kev.train --suite "$V7" --data "$data" $TRAIN_FLAGS --seed "$seed" --out "$out" 2>&1 | tee "$out.log"
python -m kev.benchmark --run "$out" --suite "$V7" --device cuda --out "$out-decision"
python -m kev.benchmark --run "$out" --suite "$TV4" --device cuda --out "$out-transfer"
