"""Presentation figures from the JSON that analysis/table.py writes.

    python analysis/figures.py --table results/e2/table-dev-vs-baseline.json --out results/figures
        One PNG per suite: each variant minus the baseline, name swap (dFR) on the left and negated wording (PG) on the
        right, with 95% paired-bootstrap intervals. Below zero = the fix reduced that failure.

Needs matplotlib (in Kev's dev dependencies). The numbers are the ones in the matching table-*.md (the table view).
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                     # noqa: E402
from matplotlib import font_manager                 # noqa: E402

# Fixed categorical order: a model keeps its color whichever models are present.
MODELS = [("a1", "A1 names"), ("a2", "A2 negation"), ("a1a2", "A1+A2"), ("c1", "C1 paraphrase")]
COLORS = {"a1": "#257de0", "a2": "#f47230", "a1a2": "#00b894", "c1": "#f2a600"}
INK, INK2, GRID, SURFACE = "#191919", "#666666", "#e6e6e6", "#ffffff"
FR_GROUPS = [("kev_seen.delta_fr", "seen names\n(yes/no, accept/reject)"), ("heldout.delta_fr", "held-out names\n(approved/denied ...)")]
PG_GROUPS = [("S1.pg", "S1 \"not\""), ("S2.pg", "S2 \"is it false\""), ("S3.pg", "S3 reworded\n(held out)")]


def font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    return "Inter" if "Inter" in names else "DejaVu Sans"


def panel(ax, values, groups, title, present):
    n = len(present)
    width = 0.8 / max(n, 1)
    for i, m in enumerate(present):
        xs, ys, lo, hi, dots = [], [], [], [], []
        for g, (key, _) in enumerate(groups):
            d = values[m].get(key)
            v = None if not d else d.get("value", d.get("mean"))    # table.py JSON: value; seeds.py JSON: mean over seeds
            if v is None:
                continue
            x = g - 0.4 + width * (i + 0.5)
            ci = d.get("ci95") or [v, v]
            xs.append(x); ys.append(v); lo.append(v - ci[0]); hi.append(ci[1] - v)
            dots += [(x, sv) for sv in (d.get("seeds") or {}).values() if len(d["seeds"]) > 1]
        ax.bar(xs, ys, width=width, color=COLORS[m], edgecolor=SURFACE, linewidth=2, zorder=2,
               label=dict(MODELS)[m])
        ax.errorbar(xs, ys, yerr=[lo, hi], fmt="none", ecolor=INK2, elinewidth=1.2, capsize=0, zorder=3)
        if dots:   # one dot per seed, so the seed-to-seed spread is visible next to the interval
            ax.scatter([x for x, _ in dots], [y for _, y in dots], s=22, color=INK, edgecolor=SURFACE, linewidth=1.2, zorder=5,
                       label="single seed" if i == 0 else None)
    ax.axhline(0, color=INK, linewidth=1, zorder=4)
    ax.set_xticks(range(len(groups)), [label for _, label in groups])
    ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="semibold", pad=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK2, length=0, labelsize=9.5)


def figure(suite, values, split, out, seeds=False, slice_=None):
    present = [m for m, _ in MODELS if m in values]
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [2, 3]})
    fig.patch.set_facecolor(SURFACE)
    panel(left, values, FR_GROUPS, "Name swap: change in ΔFR", present)
    panel(right, values, PG_GROUPS, "Negated wording: change in PG", present)
    left.set_ylabel("variant minus baseline\n(below 0 = failure reduced)", color=INK2, fontsize=9.5)
    handles, labels = left.get_legend_handles_labels()
    order = sorted(range(len(labels)), key=lambda i: labels[i] == "single seed")   # models first, the seed dot last
    handles, labels = [handles[i] for i in order], [labels[i] for i in order]
    fig.legend(handles, labels, loc="upper left", ncol=len(handles), frameon=False, fontsize=9.5,
               labelcolor=INK, bbox_to_anchor=(0.003, 0.95))
    what = "mean of seeds 2 and 3 vs same-seed baseline (95% joint bootstrap; dots = single seeds)" if seeds else "each fix vs the baseline (95% paired bootstrap)"
    fig.suptitle(f"{suite} {split}{'' if slice_ in (None, 'all') else ' [' + slice_ + ']'}: {what}", x=0.01, ha="left",
                 color=INK, fontsize=13, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    path = out / f"e2-{suite}-{split}{'-seeds' if seeds else ''}{'' if slice_ in (None, 'all') else '-' + slice_}.png"
    fig.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(fig)
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", required=True, help="results/<exp>/table-<split>-vs-<reference>.json")
    ap.add_argument("--out", default="results/figures")
    a = ap.parse_args()
    t = json.loads(Path(a.table).read_text(encoding="utf-8"))
    if not t.get("reference") and "seeds" not in t:
        raise SystemExit("this figure needs a table made with --reference, or analysis/seeds.py output")
    plt.rcParams["font.family"] = font()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for suite, values in t["values"].items():
        print(figure(suite, values, t["split"], out, seeds="seeds" in t, slice_=t.get("slice")))


if __name__ == "__main__":
    main()
