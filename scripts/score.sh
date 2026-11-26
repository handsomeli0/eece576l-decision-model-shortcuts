#!/usr/bin/env bash
# Score one model on the probe sets and compute its metrics.
#   scripts/score.sh <name> <checkpoint | qwen> <exp> [split]      e.g. scripts/score.sh baseline "$BASELINE" e1 dev
# split: dev (default) or test. Test probes are scored once, at the end (plan section 8).
# Rows go to runs/<exp>/<name>-<tag>-<probe>/, metrics to results/<exp>/<name>-<tag>-<probe>.{json,txt}.
set -euo pipefail
source "$(dirname "$0")/env.sh"
name=$1; run=$2; exp=$3; split=${4:-dev}
[ "$run" != qwen ] && [ -e "$run" ] && run=$(realpath "$run")   # kev.benchmark runs from $KEV, so a local run needs an absolute path
[ "$split" = dev ] || [ "$split" = test ] || { echo "split is dev or test" >&2; exit 1; }
mkdir -p "$PROJ/runs/$exp" "$PROJ/results/$exp"
for tag in dv7-$split tv4-$split; do
  for probe in fr pg; do
    data="$PROJ/probes/out/$tag-$probe.jsonl"; rows="$PROJ/runs/$exp/$name-$tag-$probe"; res="$PROJ/results/$exp/$name-$tag-$probe"
    if [ ! -f "$rows/rows.json" ]; then
      rm -rf "$rows"   # a half-written directory from an interrupted run
      start=$(date +%s)
      if [ "$run" = qwen ]; then
        python "$PROJ/probes/qwen_lp.py" --data "$data" --out "$rows"
      else
        (cd "$KEV" && python -m kev.benchmark --run "$run" --data "$data" --rotations $ROTATIONS --device cuda --out "$rows")
      fi
      echo "$name $tag $probe $(( $(date +%s) - start )) s" >> "$PROJ/runs/$exp/timing.log"
    fi
    python "$PROJ/analysis/metrics.py" --probe "$data" --rows "$rows" --out "$res.json" | tee "$res.txt"
  done
done
