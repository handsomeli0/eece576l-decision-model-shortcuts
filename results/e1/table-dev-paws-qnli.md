### decision-v7 dev, paws and qnli only (chosen after E1: post hoc) (95% group bootstrap)

| model | FR neutral | FR seen | FR A1-train | FR held-out | FR random | dFR seen [CI] | dFR A1-train [CI] | dFR held-out [CI] | AUROC orig | PG S1 [CI] | PG S2 [CI] | PG S3 [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | - | - | - | - | - | - | - | - | - | - | - | - |
| qwen | - | - | - | - | - | - | - | - | - | - | - | - |
| v7base | - | - | - | - | - | - | - | - | - | - | - | - |

### transfer-v4 dev, paws and qnli only (chosen after E1: post hoc) (95% group bootstrap)

| model | FR neutral | FR seen | FR A1-train | FR held-out | FR random | dFR seen [CI] | dFR A1-train [CI] | dFR held-out [CI] | AUROC orig | PG S1 [CI] | PG S2 [CI] | PG S3 [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.019 | 0.384 | 0.400 | 0.317 | 0.044 | +0.366 [+0.30, +0.44] | +0.381 [+0.32, +0.46] | +0.298 [+0.24, +0.36] | - | - | - | - |
| qwen | 0.200 | 0.309 | 0.163 | 0.163 | 0.081 | +0.109 [+0.07, +0.15] | -0.037 [-0.08, +0.00] | -0.037 [-0.08, +0.01] | - | - | - | - |
| v7base | 0.025 | 0.491 | 0.575 | 0.352 | 0.033 | +0.466 [+0.39, +0.54] | +0.550 [+0.48, +0.62] | +0.327 [+0.27, +0.38] | - | - | - | - |
