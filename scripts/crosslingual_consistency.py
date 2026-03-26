"""
Cross-Lingual Consistency Analysis.

Outputs
-------
data/processed/crosslingual_consistency.csv  – per-(source_language, idiom) CV of
                                               translation length across 10 target
                                               languages, plus high/low resource means.
figures/cv_by_resource_level.png
figures/span_heatmap.png
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
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).parent.parent
df   = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TRANS  = ["translate_creatively", "translate_analogy", "translate_author"]
LABELS = ["Creatively", "Analogy", "Author"]
COLORS = ["#4C72B0", "#DD8452", "#55A868"]

HIGH_RES = {"English","French","German","Spanish","Italian","Russian"}
LOW_RES  = {"Arabic","Bengali","Hindi","Swahili"}

for col, lbl in zip(TRANS, LABELS):
    df[f"tlen_{lbl}"] = df[col].str.len()

# ── CV of translation length across 10 target languages per (src, idiom, strat) ──
# Aggregate to per-language means first, then compute CV across the 10 languages.
# (Computing CV on raw rows would conflate within-language sentence variance
#  with the between-language variance we actually want to measure.)
print("Computing CV across target languages…")
cv_records = []
for (src, idiom), grp in df.groupby(["source_language", "idiom"]):
    row = {"source_language": src, "idiom": idiom}
    for lbl in LABELS:
        lang_means = grp.groupby("target_language")[f"tlen_{lbl}"].mean()
        row[f"cv_{lbl}"] = lang_means.std() / lang_means.mean() if lang_means.mean() > 0 else np.nan
    cv_records.append(row)
cv_df = pd.DataFrame(cv_records)

print("\nMean CV of translation length across target languages:")
for lbl in LABELS:
    print(f"  {lbl:<14} {cv_df[f'cv_{lbl}'].mean():.3f}")

# ── High vs low resource comparison ──────────────────────────────────────────
df["resource"] = df["target_language"].apply(
    lambda l: "high" if l in HIGH_RES else "low")

print("\nMean translation length by resource level:")
for lbl in LABELS:
    hi = df[df["resource"]=="high"][f"tlen_{lbl}"].mean()
    lo = df[df["resource"]=="low"] [f"tlen_{lbl}"].mean()
    stat, p = mannwhitneyu(
        df[df["resource"]=="high"][f"tlen_{lbl}"].dropna(),
        df[df["resource"]=="low"] [f"tlen_{lbl}"].dropna(),
        alternative="two-sided")
    print(f"  {lbl:<14} high={hi:.1f}  low={lo:.1f}  MWU p={p:.2e}")

# ── Fig 4a: CV distribution by source language × strategy ────────────────────
cv_melt = pd.melt(
    cv_df, id_vars=["source_language"],
    value_vars=[f"cv_{l}" for l in LABELS],
    var_name="Strategy", value_name="CV"
)
cv_melt["Strategy"] = cv_melt["Strategy"].str.replace("cv_","")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.boxplot(data=cv_melt.dropna(), x="source_language", y="CV", hue="Strategy",
            palette=COLORS, flierprops=dict(marker=".", alpha=0.3), ax=axes[0])
axes[0].set_title("CV of Translation Length\nby Source Language & Strategy", fontweight="bold")
axes[0].set_ylabel("Coefficient of Variation")
axes[0].set_xlabel("")
axes[0].legend(title="Strategy", fontsize=8)

# ── Fig 4b: high vs low resource length box ──────────────────────────────────
tlen_melt = pd.melt(
    df[["resource"] + [f"tlen_{l}" for l in LABELS]].rename(
        columns={f"tlen_{l}": l for l in LABELS}),
    id_vars=["resource"], var_name="Strategy", value_name="Length"
).dropna()
sns.boxplot(data=tlen_melt, x="Strategy", y="Length", hue="resource",
            palette={"high":"#5B9BD5","low":"#ED7D31"},
            flierprops=dict(marker=".", alpha=0.15), ax=axes[1])
axes[1].set_title("Translation Length:\nHigh vs Low Resource Target Languages", fontweight="bold")
axes[1].set_ylabel("Character count")
axes[1].set_ylim(0, 400)
axes[1].legend(title="Resource level")
fig.tight_layout()
fig.savefig(FIG / "cv_by_resource_level.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/cv_by_resource_level.png")

# ── Fig 4c: heatmap — median span length per (src × tgt) ─────────────────────
span_cols = ["source_language","target_language","span_creatively","span_analogy","span_author"]
spdf = df[span_cols].copy()
for sc in ["span_creatively","span_analogy","span_author"]:
    spdf[sc] = spdf[sc].str.len()

fig, axes = plt.subplots(1, 3, figsize=(16, 4))
for ax, sc, lbl in zip(axes, ["span_creatively","span_analogy","span_author"], LABELS):
    pivot = spdf.groupby(["source_language","target_language"])[sc].median().unstack()
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.3, ax=ax, cbar_kws={"shrink":0.8})
    ax.set_title(f"Median Span Length\n({lbl})", fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("" if ax != axes[0] else "Source language")
fig.suptitle("Median Span Length (chars) per Language Pair", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "span_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/span_heatmap.png")

# ── Save processed output ──────────────────────────────────────────────────────
out_path = PROC / "crosslingual_consistency.csv"
cv_df.to_csv(out_path, index=False)
print(f"Saved → {out_path}")
