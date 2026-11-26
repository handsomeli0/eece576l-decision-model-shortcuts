#!/usr/bin/env bash
# The final test-split run (plan section 8): every model scored once on the locked test probes and test suites.
# About 5 h on the 8 GB 4060. Run it once, after every model is trained; do not tune anything on its results.
#   scripts/test_all.sh            (skips a step whose output already exists, so it can resume after an interruption)
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$PROJ"
T="$PROJ/runs/train"
# E1 models (v7base, baseline, qwen): probes on test, then Table 1
scripts/e1.sh test
# E2 variants: probes on test
for v in a1 a2 a1a2 c1; do
  [ -d "$T/$v-s2" ] && scripts/score.sh "$v" "$T/$v-s2" e2 test || echo "skip $v: no $T/$v-s2"
done
# accuracy, ECE, Brier, NLL on the locked test partitions of both suites
mkdir -p runs/test
for pair in "v7base=$V7BASE" "baseline=$BASELINE" "a1=$T/a1-s2" "a2=$T/a2-s2" "a1a2=$T/a1a2-s2" "c1=$T/c1-s2"; do
  name=${pair%%=*}; run=${pair#*=}
  for s in decision transfer; do
    suite=$([ $s = decision ] && echo "$V7" || echo "$TV4"); out="$PROJ/runs/test/$name-$s"
    [ -f "$out/report.json" ] && continue
    [ "$name" = v7base ] || [ -d "$run" ] || continue
    rm -rf "$out"
    (cd "$KEV" && python -m kev.benchmark --run "$run" --suite "$suite" --allow-test --device cuda --out "$out") | tail -3
  done
done
python analysis/table.py --exp e2 --split test --reference baseline --reference-exp e1
python analysis/figures.py --table results/e2/table-test-vs-baseline.json --out results/figures
