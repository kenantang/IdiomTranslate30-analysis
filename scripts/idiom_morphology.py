"""
Idiom Morphology & Structural Analysis.

Outputs
-------
data/processed/idiom_morphology_stats.csv  – per-length-bucket expansion ratios and
                                              span-to-translation ratios per strategy,
                                              plus per-(source_language, strategy)
                                              Spearman ρ for sentence vs translation length.
figures/idiom_length_distribution.png
figures/quintile_analysis.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")


from pathlib import Path

import matplotlib.pyplot as plt

from utils import idiom_length_bucket, BUCKET_ORDER, STRATEGY_COLORS as COLORS
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr

ROOT = Path(__file__).parent.parent
df   = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TRANS  = ["translate_creatively", "translate_analogy", "translate_author"]
LABELS = ["Creatively", "Analogy", "Author"]

sent_len = df["sentence"].str.len().replace(0, np.nan)
for col, lbl in zip(TRANS, LABELS):
    df[f"exp_{lbl}"]  = df[col].str.len() / sent_len
    df[f"tlen_{lbl}"] = df[col].str.len()

df["idiom_len"] = df["idiom"].str.len()
df["sent_len"]  = df["sentence"].str.len()

# ── Fig 5a: idiom length distribution per source language ────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=False)
for ax, (lang, grp), color in zip(axes, df.groupby("source_language"), COLORS):
    unique_idioms = grp.drop_duplicates("idiom")["idiom_len"]
    ax.hist(unique_idioms, bins=range(2, 18), color=color, edgecolor="white", alpha=0.85)
    ax.set_title(f"{lang}\n(n={unique_idioms.nunique():,} unique idioms)", fontweight="bold")
    ax.set_xlabel("Idiom length (chars)")
    ax.set_ylabel("Count of unique idioms" if ax is axes[0] else "")
    ax.axvline(4, color="red", lw=1.5, ls="--", label="4-char")
    pct4 = (unique_idioms == 4).mean() * 100
    ax.text(4.15, ax.get_ylim()[1]*0.9, f"{pct4:.0f}% 4-char", color="red", fontsize=9)
    ax.legend(fontsize=8)
fig.suptitle("Idiom Character Length Distribution by Source Language", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "idiom_length_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/idiom_length_distribution.png")

for lang, grp in df.groupby("source_language"):
    pct4 = (grp.drop_duplicates("idiom")["idiom_len"] == 4).mean() * 100
    print(f"  {lang}: {pct4:.1f}% of unique idioms are 4 characters")

# ── Quintile analysis (H29) ───────────────────────────────────────────────────
# Bucket by actual length: 3, 4, 5, 6, 7+  (idiom_length_bucket from utils)
df["idiom_len_bucket"] = df["idiom"].apply(idiom_length_bucket)
bucket_order = BUCKET_ORDER

quintile_stats = []
for q in bucket_order:
    grp = df[df["idiom_len_bucket"] == q]
    if grp.empty:
        continue
    row = {"bucket": q, "n_rows": len(grp)}
    for lbl in LABELS:
        span_col = f"span_{['creatively','analogy','author'][LABELS.index(lbl)]}"
        row[f"exp_{lbl}"]  = grp[f"exp_{lbl}"].mean()
        row[f"slen_{lbl}"] = (grp[span_col].str.len() / grp[f"tlen_{lbl}"]).mean()
    quintile_stats.append(row)
qdf = pd.DataFrame(quintile_stats)
print("\nBucket analysis (mean expansion ratio by idiom length):")
print(qdf[["bucket","n_rows"] + [f"exp_{l}" for l in LABELS]].to_string(index=False))

# ── Fig 5b: quintile plot ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
x = np.arange(len(qdf))
w = 0.26
for i, (lbl, color) in enumerate(zip(LABELS, COLORS)):
    axes[0].bar(x + i*w, qdf[f"exp_{lbl}"], w, label=lbl, color=color)
axes[0].set_xticks(x + w)
axes[0].set_xticklabels([f"{r} chars\n(n={n:,})" for r, n in
                          zip(qdf["bucket"], qdf["n_rows"])], fontsize=8)
axes[0].set_title("Mean Expansion Ratio\nby Idiom Length Quintile", fontweight="bold")
axes[0].set_ylabel("Mean expansion ratio")
axes[0].legend(title="Strategy")

# ── Sentence context length vs translation length (Spearman) ─────────────────
print("\nSpearman ρ: sentence length vs translation length (per strategy):")
sp_data = []
for lbl in LABELS:
    sub = df[["source_language","idiom","sent_len",f"tlen_{lbl}"]].dropna()
    # Per-language
    for lang, grp in sub.groupby("source_language"):
        r, p = spearmanr(grp["sent_len"], grp[f"tlen_{lbl}"])
        sp_data.append({"lang": lang, "strategy": lbl, "rho": r, "p": p})
        print(f"  {lang:<12} {lbl:<14} ρ={r:.3f}  p={p:.2e}")
spdf = pd.DataFrame(sp_data)

sp_pivot = spdf.pivot_table(index="lang", columns="strategy", values="rho")
sns.heatmap(sp_pivot, annot=True, fmt=".3f", cmap="coolwarm", center=0,
            linewidths=0.5, ax=axes[1], cbar_kws={"label": "Spearman ρ"})
axes[1].set_title("Spearman ρ: Sentence Length\nvs Translation Length", fontweight="bold")
axes[1].set_ylabel("")
fig.tight_layout()
fig.savefig(FIG / "quintile_analysis.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/quintile_analysis.png")

# ── Save processed output ──────────────────────────────────────────────────────
# Bucket stats
bucket_out = qdf.copy()
bucket_out.to_csv(PROC / "idiom_morphology_bucket_stats.csv", index=False)
print("Saved → data/processed/idiom_morphology_bucket_stats.csv")

# Spearman results
spearman_out = pd.DataFrame(sp_data)
spearman_out.to_csv(PROC / "idiom_morphology_spearman.csv", index=False)
print("Saved → data/processed/idiom_morphology_spearman.csv")
