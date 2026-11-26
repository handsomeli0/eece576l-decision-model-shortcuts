#!/usr/bin/env bash
# Every table and figure for one split, from the scored rows under runs/ (CPU only, about 30 to 60 min with 2,000 resamples).
#   scripts/tables.sh [dev|test]
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$PROJ"
split=${1:-dev}
for sl in all policy nonpolicy nodef withdef paws-qnli; do
  python analysis/table.py --exp e1 --split "$split" --slice $sl > /dev/null
  python analysis/table.py --exp e2 --split "$split" --slice $sl > /dev/null
  python analysis/table.py --exp e2 --split "$split" --slice $sl --reference baseline --reference-exp e1 > /dev/null
  echo "tables done: $sl"
done
python analysis/figures.py --table "results/e2/table-$split-vs-baseline.json" --out results/figures
ls results/e1/table-$split* results/e2/table-$split*
