#!/usr/bin/env bash
# E1: both failures before any fix. Three models, no training. About 1 to 1.5 h on the 4060 for dev.
#   scripts/e1.sh [dev|test]
set -euo pipefail
source "$(dirname "$0")/env.sh"
split=${1:-dev}
"$PROJ/scripts/score.sh" v7base   "$V7BASE"   e1 "$split"
"$PROJ/scripts/score.sh" baseline "$BASELINE" e1 "$split"
"$PROJ/scripts/score.sh" qwen     qwen        e1 "$split"
python "$PROJ/analysis/table.py" --exp e1 --split "$split"
