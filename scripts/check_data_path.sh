#!/usr/bin/env bash
# Does training from our exported file (--data) match training from the suite (--suite)? 30 steps each; the loss
# lines must be identical. If they are, every variant trains with --data and differs from the baseline only in data.
set -euo pipefail
source "$(dirname "$0")/env.sh"
out="$PROJ/runs/check"; rm -rf "$out"; mkdir -p "$out"
cd "$KEV"
python -m kev.train --suite "$V7" $TRAIN_FLAGS --seed 2 --max_steps 30 --out "$out/suite" 2>&1 | tee "$out/suite.log"
python -m kev.train --suite "$V7" --data "$PROJ/data/none-s2.jsonl" $TRAIN_FLAGS --seed 2 --max_steps 30 --out "$out/data" 2>&1 | tee "$out/data.log"
grep -o 'step [0-9]*/[0-9]* loss [0-9.]*' "$out/suite.log" > "$out/suite.loss"
grep -o 'step [0-9]*/[0-9]* loss [0-9.]*' "$out/data.log"  > "$out/data.loss"
paste "$out/suite.loss" "$out/data.loss"
diff -q "$out/suite.loss" "$out/data.loss" && echo "IDENTICAL: --data path matches --suite" || echo "DIFFERENT: see $out/*.log"
