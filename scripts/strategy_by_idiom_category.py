"""
Part 18: Strategy Effectiveness by Idiom Category.

Without semantic labels for idioms, we use four proxy categorisations available
from existing metadata:
  • Difficulty quartile (from idiom_difficulty.parquet)
  • Dictionary coverage — in_xinhua / in_thuocl (from idiom_metadata.parquet)
  • 4-character vs non-4-character structure
  • Source language

For each category × strategy we compare error rate, mean edit distance, and
within-cell CV to ask: does any strategy consistently outperform the others for
a particular kind of idiom?

Outputs
-------
data/processed/strategy_by_category.csv
figures/strategy_by_category.png
figures/strategy_error_by_difficulty.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import kruskal

from utils import STRATEGY_COLORS as COLORS, SOURCE_COLORS, OUTLIER_PERCENTILE

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

LABELS     = ["Creatively", "Analogy", "Author"]
TRANS_COLS = ["translate_creatively", "translate_analogy", "translate_author"]
SPAN_COLS  = ["span_creatively",      "span_analogy",      "span_author"]

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data …")
df   = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
diff = pd.read_parquet(PROC / "idiom_difficulty.parquet")
meta = pd.read_parquet(PROC / "idiom_metadata.parquet")
cs   = pd.read_parquet(PROC / "context_sensitivity.parquet")
print(f"  Raw: {len(df):,} | Difficulty: {len(diff):,} | CS: {len(cs):,}")

# ── Build error flags ──────────────────────────────────────────────────────────
print("Computing error flags …")
for tcol, scol, label in zip(TRANS_COLS, SPAN_COLS, LABELS):
    df[f"err_{label}"] = [sp not in tr for sp, tr in zip(
        df[scol].fillna("").astype(str),
        df[tcol].fillna("").astype(str))]

# ── Attach difficulty quartile ─────────────────────────────────────────────────
diff["difficulty_q"] = pd.qcut(diff["difficulty"], 4,
                                labels=["Q1 (easy)", "Q2", "Q3", "Q4 (hard)"])
df = df.merge(diff[["idiom", "source_language", "difficulty", "difficulty_q"]],
              on=["idiom", "source_language"], how="left")

# ── Attach metadata ────────────────────────────────────────────────────────────
df = df.merge(meta[["idiom", "in_xinhua", "in_thuocl"]], on="idiom", how="left")
df["in_xinhua"] = df["in_xinhua"].fillna(False)
df["in_thuocl"] = df["in_thuocl"].fillna(False)
df["is_4char"]  = df["idiom"].str.len() == 4

# Attach CV per (idiom, source, target)
cs_mean_cv = cs.groupby(["idiom", "source_language", "target_language"])[
    ["cv_Creatively", "cv_Analogy", "cv_Author"]].mean().reset_index()
df = df.merge(cs_mean_cv, on=["idiom", "source_language", "target_language"], how="left")

# ── Compute per-category × strategy stats ─────────────────────────────────────
CATEGORIES = {
    "difficulty_q":   ("Difficulty Quartile", ["Q1 (easy)", "Q2", "Q3", "Q4 (hard)"]),
    "in_xinhua":      ("In Xinhua Dictionary", [False, True]),
    "is_4char":       ("4-Character Idiom",    [False, True]),
    "source_language":("Source Language",      ["Chinese", "Japanese", "Korean"]),
}

all_records = []
for cat_col, (cat_name, cat_vals) in CATEGORIES.items():
    for val in cat_vals:
        mask = df[cat_col] == val
        sub  = df[mask]
        for label in LABELS:
            row = {
                "category":       cat_name,
                "category_value": str(val),
                "strategy":       label,
                "n":              len(sub),
                "error_pct":      sub[f"err_{label}"].mean() * 100,
                "mean_cv":        sub[f"cv_{label}"].mean(),
                "mean_trans_len": sub[f"translate_{label.lower()}"].str.len().mean(),
            }
            all_records.append(row)

cat_df = pd.DataFrame(all_records)
cat_df.to_csv(PROC / "strategy_by_category.csv", index=False)
print(f"  Saved → data/processed/strategy_by_category.csv")

# Print summary
print("\n  Error rate (%) by strategy and difficulty quartile:")
pivot = cat_df[cat_df["category"] == "Difficulty Quartile"].pivot_table(
    index="category_value", columns="strategy", values="error_pct"
)[LABELS]
print(pivot.to_string())

print("\n  Mean CV by strategy and dictionary coverage (in_xinhua):")
pivot2 = cat_df[cat_df["category"] == "In Xinhua Dictionary"].pivot_table(
    index="category_value", columns="strategy", values="mean_cv"
)[LABELS]
print(pivot2.to_string())

# Kruskal–Wallis: does difficulty quartile affect error rate per strategy?
print("\n  Kruskal–Wallis test (difficulty quartile effect on error rate):")
for label in LABELS:
    groups = [df[df["difficulty_q"] == q][f"err_{label}"].dropna()
              for q in ["Q1 (easy)", "Q2", "Q3", "Q4 (hard)"]]
    H, p = kruskal(*groups)
    print(f"  {label:<14} H={H:.1f}  p={p:.2e}")

# ── Fig: error rate by difficulty quartile per strategy ───────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: error rate by difficulty quartile
sub = cat_df[cat_df["category"] == "Difficulty Quartile"]
x = np.arange(4)
width = 0.28
q_labels = ["Q1 (easy)", "Q2", "Q3", "Q4 (hard)"]
for i, (label, color) in enumerate(zip(LABELS, COLORS)):
    vals = [sub[(sub["strategy"] == label) & (sub["category_value"] == q)]["error_pct"].values[0]
            for q in q_labels]
    axes[0].bar(x + i * width, vals, width, label=label, color=color, alpha=0.85)
axes[0].set_xticks(x + width)
axes[0].set_xticklabels(q_labels, rotation=10, ha="right")
axes[0].set_ylabel("Span error rate (%)")
axes[0].set_title("Span Error Rate by Difficulty Quartile & Strategy",
                  fontweight="bold")
axes[0].legend()

# Right: mean CV by source language per strategy
sub2 = cat_df[cat_df["category"] == "Source Language"]
srcs = ["Chinese", "Japanese", "Korean"]
x2 = np.arange(3)
for i, (label, color) in enumerate(zip(LABELS, COLORS)):
    vals2 = [sub2[(sub2["strategy"] == label) & (sub2["category_value"] == s)]["mean_cv"].values[0]
             for s in srcs]
    axes[1].bar(x2 + i * width, vals2, width, label=label, color=color, alpha=0.85)
axes[1].set_xticks(x2 + width)
axes[1].set_xticklabels(srcs)
axes[1].set_ylabel("Mean within-cell CV")
axes[1].set_title("Within-Cell CV by Source Language & Strategy",
                  fontweight="bold")
axes[1].legend()

fig.tight_layout()
fig.savefig(FIG / "strategy_by_category.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/strategy_by_category.png")

# ── Fig: full facet grid — all categories × error rate ───────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
axes = axes.flatten()

for ax, (cat_col, (cat_name, cat_vals)) in zip(axes, CATEGORIES.items()):
    sub = cat_df[cat_df["category"] == cat_name]
    pivot = sub.pivot_table(index="category_value", columns="strategy",
                             values="error_pct")[LABELS]
    pivot = pivot.reindex([str(v) for v in cat_vals])
    x = np.arange(len(cat_vals))
    for i, (label, color) in enumerate(zip(LABELS, COLORS)):
        ax.bar(x + i * 0.28, pivot[label], 0.28, label=label, color=color, alpha=0.85)
    ax.set_xticks(x + 0.28)
    ax.set_xticklabels([str(v) for v in cat_vals], rotation=15, ha="right")
    ax.set_ylabel("Error rate (%)")
    ax.set_title(f"Error Rate by {cat_name}", fontweight="bold")
    ax.legend(fontsize=8)

fig.suptitle("Span Error Rate by Strategy Across Idiom Categories",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "strategy_error_by_difficulty.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/strategy_error_by_difficulty.png")

print("\nDone.")
