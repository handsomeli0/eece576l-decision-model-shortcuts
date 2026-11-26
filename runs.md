# Run log

One line per GPU run. Times from `training_metrics.json` (`wall_seconds`, `peak_device_bytes`) or `runs/<exp>/timing.log`.
Hardware: RTX 4060 8 GB, WSL2 Ubuntu 24.04, torch 2.8.0+cu128, triton 3.7.1, fla 0.5.2. Flags in `scripts/env.sh`.

| date | run | what | wall | peak mem | result | notes |
|---|---|---|---|---|---|---|
| 2026-11-26 | `$KEV/runs/repl-v7base` | stage-1 replication, seed 2, `--batch 2 --accum 4 --checkpointing 1` | 6,212 s (3,144 steps, 30,370 records) | 4.64 GiB | decision-v7 dev 0.8165 (v7-base 0.8291) | paired difference CI includes 0: accepted as the E2 baseline |
