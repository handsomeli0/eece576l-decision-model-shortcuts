#!/usr/bin/env bash
# The final test-split run (plan section 8): every model scored once on the locked test probes and test suites.
# About 8.5 h on the 8 GB 4060 for 12 models. Run it once, after every model is trained; do not tune anything on its results.
#   scripts/test_all.sh            (skips a step whose output already exists, so it can resume after an interruption)
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$PROJ"
T="$PROJ/runs/train"
# E1 models (v7base, baseline, qwen)
scripts/e1.sh test
# E2 variants, seed 2 (baseline = the stage-1 replication, scored in e1)
for v in a1 a2 a1a2 c1; do
  if [ -d "$T/$v-s2" ]; then scripts/score.sh "$v" "$T/$v-s2" e2 test; else echo "skip $v-s2"; fi
done
# seed 3 (its baseline was trained through --data as "none")
for v in none a1 a2 a1a2 c1; do
  n=$([ $v = none ] && echo baseline || echo $v)
  if [ -d "$T/$v-s3" ]; then scripts/score.sh "$n" "$T/$v-s3" e2s3 test; else echo "skip $v-s3"; fi
done
# accuracy, ECE, Brier, NLL on the locked test partitions of both suites
mkdir -p runs/test
models=("v7base=$V7BASE" "baseline=$BASELINE")
for v in a1 a2 a1a2 c1; do models+=("$v=$T/$v-s2"); done
for v in none a1 a2 a1a2 c1; do models+=("$([ $v = none ] && echo baseline || echo $v)-s3=$T/$v-s3"); done
for pair in "${models[@]}"; do
  name=${pair%%=*}; run=${pair#*=}
  [ "$name" = v7base ] || [ -d "$run" ] || continue
  for s in decision transfer; do
    suite=$([ $s = decision ] && echo "$V7" || echo "$TV4"); out="$PROJ/runs/test/$name-$s"
    [ -f "$out/report.json" ] && continue
    rm -rf "$out"
    (cd "$KEV" && python -m kev.benchmark --run "$run" --suite "$suite" --allow-test --device cuda --out "$out") | tail -3
  done
done
python analysis/accuracy.py --split test
scripts/tables.sh test
