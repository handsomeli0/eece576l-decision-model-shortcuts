# Shared settings. Every run script sources this:  source scripts/env.sh
# KEV is the Kev checkout with its .venv (its commit must match third_party/kev, see scripts/check_kev.sh).
export PROJ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export KEV="${KEV:-$HOME/eece576l/kev}"
[ -f "$KEV/.venv/bin/activate" ] || { echo "no Kev venv at $KEV/.venv (set KEV=...)" >&2; return 1 2>/dev/null || exit 1; }
source "$KEV/.venv/bin/activate"
export V7="$KEV/evals/v7/decision-v7"
export TV4="$KEV/evals/v4/transfer-v4"
export BASE="Qwen/Qwen3.5-0.8B-Base"
export BASE_REV="dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68"
export V7BASE="jaredpalmer/kev-0.8b@v7-base"            # released stage-1 checkpoint (E1 reference)
export BASELINE="${BASELINE:-$KEV/runs/repl-v7base}"     # our own stage-1 replication (E2 baseline)
# Stage-1 recipe (provenance.json of v7-base) with the 8 GB memory flags. Same flags for every variant.
export TRAIN_FLAGS="--base $BASE --base_revision $BASE_REV --epochs 2 --lr 1e-4 --batch 2 --accum 4 --checkpointing 1 --dtype bf16 --p_none_pair 0.25 --device cuda"
# Probe scoring: average every choice question over both option orders, so position cannot count as a name flip.
export ROTATIONS=2
