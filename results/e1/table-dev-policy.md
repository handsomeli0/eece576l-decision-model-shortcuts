### decision-v7 dev, policy (accept/reject) questions only (95% group bootstrap)

| model | FR neutral | FR seen | FR A1-train | FR held-out | FR random | dFR seen [CI] | dFR A1-train [CI] | dFR held-out [CI] | AUROC orig | PG S1 [CI] | PG S2 [CI] | PG S3 [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.062 | 0.102 | 0.094 | 0.109 | 0.013 | +0.039 [-0.03, +0.12] | +0.031 [-0.04, +0.10] | +0.047 [-0.01, +0.11] | - | - | - | - |
| qwen | 0.016 | 0.012 | 0.098 | 0.339 | 0.000 | -0.004 [-0.03, +0.03] | +0.082 [+0.03, +0.14] | +0.323 [+0.30, +0.34] | - | - | - | - |
| v7base | 0.012 | 0.012 | 0.012 | 0.026 | 0.008 | +0.000 [-0.01, +0.01] | +0.000 [-0.02, +0.02] | +0.014 [+0.00, +0.03] | - | - | - | - |

### transfer-v4 dev, policy (accept/reject) questions only (95% group bootstrap)

| model | FR neutral | FR seen | FR A1-train | FR held-out | FR random | dFR seen [CI] | dFR A1-train [CI] | dFR held-out [CI] | AUROC orig | PG S1 [CI] | PG S2 [CI] | PG S3 [CI] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.062 | 0.073 | 0.088 | 0.080 | 0.021 | +0.010 [+0.00, +0.03] | +0.026 [+0.00, +0.07] | +0.017 [+0.00, +0.04] | - | - | - | - |
| qwen | 0.203 | 0.005 | 0.125 | 0.319 | 0.000 | -0.198 [-0.29, -0.11] | -0.078 [-0.20, +0.05] | +0.116 [+0.02, +0.21] | - | - | - | - |
| v7base | 0.068 | 0.052 | 0.078 | 0.087 | 0.007 | -0.016 [-0.11, +0.08] | +0.010 [-0.09, +0.11] | +0.019 [-0.06, +0.10] | - | - | - | - |
