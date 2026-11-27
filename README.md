# Label or Definition? Surface-form shortcuts in typed decision models

EECE 576L final project (Minghan Li). The question: are the **name-swap** failure (Sun et al., arXiv 2609.26758) and
the **negated-question** failure (Arize's decision-model benchmark) one shortcut or two?

- **H1, shared shortcut:** the model keys on surface polarity (option names like `yes`/`accept`, positive question
  wording) instead of the option definitions. Fixing one failure should also reduce the other.
- **H0, separate shortcuts:** each fix only helps its own failure.

Models: [Kev-0.8B](https://github.com/jaredpalmer/kev) (Qwen3.5-0.8B-Base + LoRA + pointer head) and the untrained
Qwen3.5-0.8B-Base read out by option-letter log-probabilities. Data: Kev's frozen suites only (decision-v7 for
training and in-distribution tests, transfer-v4 for unseen sources).

## Experiments

| | question | models | training |
|---|---|---|---|
| E1 | Do both failures exist before any fix? | Kev v7-base, our stage-1 replication, Qwen log-prob | none |
| E2 | Does each fix reduce its own failure, the other one, or both? | baseline, A1, A2, A1+A2, C1 | 4 runs, about 2 h each |
| E3 | Does a fix transfer to names and wordings it never saw? | the E2 models | none |

Training variants (`augment/make.py`), all on the decision-v7 training split with the stage-1 recipe:

- **A1, name randomization:** half of the binary questions with definitions become two-option choices whose names are
  random strings or polar pairs bound in random order. The label follows the definition.
- **A2, polarity pairing:** each templated yes/no question gets a negated copy (styles S1, S2), gold flipped.
- **A1+A2:** both.
- **C1, paraphrase control:** the same number of extra records as A2, but same-polarity paraphrases. Rules out "more
  data" or "more wordings" as the explanation.

## Metrics (`analysis/metrics.py`)

- **FR, flip rate:** the share of questions whose chosen *definition* changes when the names are swapped between the two
  definitions. **ΔFR** = FR(polar names) - FR(neutral names `0/1`, `P/Q`), which removes plain instability.
- **PG, polarity gap:** AUROC of P(yes) on the original wording minus AUROC on a negated wording (S1 "not", S2 "Is it
  false that", S3 reworded opposite). Also the inconsistency mean |P(yes | q) + P(yes | not q) - 1|.
- 95% intervals from 2,000 bootstrap resamples of state groups. E2 differences use a paired bootstrap (same groups for
  both models). "Reduces" means the interval of the difference excludes 0.
- Held-out for E3: name pairs `absent/present`, `denied/approved`, `invalid/valid` and three random strings
  (`templates/splits.json`), and negation style S3. None of them is used in training.

## Layout

```
common.py              JSONL I/O, question templates, negation/paraphrase rewriting, option definitions
templates/             templates.json (wordings and hand-written definitions), splits.json (name pairs, styles, A1 knobs)
probes/build.py        name-swap (FR) and negated-question (PG) probe sets from a suite split
probes/qwen_lp.py      Qwen3.5-0.8B-Base letter log-prob readout (writes kev.benchmark-format rows)
probes/review/         a 50-item sample for hand-checking (sample-50.md)
augment/make.py        A1, A2, A1+A2, C1 training files
analysis/metrics.py    FR, ΔFR, balanced accuracy, AUC, AUROC, PG, inconsistency, group bootstrap
analysis/table.py      Tables 1 and 2 (Markdown plus a JSON of every value)
analysis/seeds.py      every variant minus its same-seed baseline, per seed and averaged (seeds 2 and 3)
analysis/figures.py    presentation figures from those JSON files
scripts/               env.sh (paths and the training recipe), prepare.sh, check_kev.sh, check_data_path.sh,
                       e1.sh, train.sh, score.sh, test_all.sh, export_train.py
third_party/kev        Kev at the pinned commit (git submodule)
runs.md                log of every GPU run
```

## Running it

Needs a working Kev environment (see Kev's README; on Windows, WSL2 with `triton==3.7.1`). The scripts use
`KEV=~/eece576l/kev` and its `.venv` by default. The analysis code is standard-library Python.

```bash
git clone --recursive https://github.com/handsomeli0/eece576l-decision-model-shortcuts && cd eece576l-decision-model-shortcuts
export KEV=~/eece576l/kev          # a Kev checkout at the commit of third_party/kev, with .venv set up
scripts/check_kev.sh               # the Kev commit matches the pin
scripts/prepare.sh                 # export the train split, build the probes and every training variant (CPU, minutes)
scripts/check_data_path.sh         # 30 steps: training from our exported file equals training from the suite
scripts/e1.sh dev                  # E1 on the development splits
scripts/train.sh a1                # E2 variants: a1, a2, a1a2, c1 (one at a time, about 2 h each on an 8 GB GPU)
scripts/score.sh a1 runs/train/a1-s2 e2 dev
python analysis/table.py --exp e2 --split dev --reference baseline --reference-exp e1
scripts/tables.sh dev               # every table, including slices (policy, nodef, ...), and the figures
```

The test splits are scored once, at the end, for every model: `scripts/test_all.sh` (about 5 h on an 8 GB GPU).
Figures: `python analysis/figures.py --table results/e2/table-dev-vs-baseline.json` (needs matplotlib).
Everything is deterministic for a given seed (default 2, the seed of Kev's stage-1 run).
