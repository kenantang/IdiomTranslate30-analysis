"""
Part 19: Semantic Consistency Audit.

True semantic faithfulness requires ground-truth reference translations.  As
a practical substitute, we use **cross-strategy span agreement** — the Jaccard
and edit-distance similarity between spans produced by two different strategies
for the same idiom — as a proxy for semantic stability.

The reasoning: if all three strategies independently produce similar span
phrasings, the concept is likely semantically clear and the model's renderings
are stable.  If strategies diverge widely, the concept is semantically ambiguous
or culturally opaque — a signal of potential semantic infidelity.

Analyses:
  19.1  Per-idiom semantic stability score — aggregate cross-strategy span agreement
  19.2  What predicts stability? — correlation with difficulty, coverage, char length
  19.3  Most stable and most unstable idioms — qualitative examples
  19.4  Stability by target language — does semantic clarity vary by translation target?

Outputs
-------
data/processed/semantic_consistency.csv
figures/semantic_consistency_distribution.png
figures/semantic_stability_features.png
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
from scipy.stats import spearmanr

from utils import STRATEGY_COLORS as COLORS, SOURCE_COLORS, RESOURCE_COLORS

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data …")
div  = pd.read_parquet(PROC / "divergence_scores.parquet")
diff = pd.read_parquet(PROC / "idiom_difficulty.parquet")
meta = pd.read_parquet(PROC / "idiom_metadata.parquet")
print(f"  Divergence scores: {len(div):,} rows, {div['idiom'].nunique():,} idioms")

# ── 19.1  Per-idiom semantic stability score ──────────────────────────────────
print("\n── 19.1  Per-idiom semantic stability score ──────────────────────────────")

# Cross-strategy edit distance (lower = more stable / semantically consistent)
# We define stability as the mean of the three pairwise edit distances,
# averaged across all target languages available for that idiom.
stability = (
    div.groupby(["idiom", "source_language"])[["edit_CA", "edit_CAu", "edit_AAu"]]
    .mean()
    .assign(edit_mean=lambda d: d[["edit_CA","edit_CAu","edit_AAu"]].mean(axis=1),
            stability=lambda d: 1 - d["edit_mean"])
    .reset_index()
)
print(f"  Stability scores computed for {len(stability):,} (idiom, source) pairs")
print(f"  Mean stability: {stability['stability'].mean():.3f} ± {stability['stability'].std():.3f}")
print(f"  Range: [{stability['stability'].min():.3f}, {stability['stability'].max():.3f}]")

# ── 19.2  What predicts stability? ────────────────────────────────────────────
print("\n── 19.2  Feature correlations with stability ─────────────────────────────")

feat = (
    stability
    .merge(diff[["idiom", "source_language", "difficulty"]], on=["idiom", "source_language"], how="left")
    .merge(meta[["idiom", "in_xinhua", "in_thuocl", "thuocl_freq", "def_len"]], on="idiom", how="left")
)
feat["char_len"]   = feat["idiom"].str.len()
feat["in_xinhua"]  = feat["in_xinhua"].fillna(False).astype(int)
feat["in_thuocl"]  = feat["in_thuocl"].fillna(False).astype(int)
feat["thuocl_freq"] = feat["thuocl_freq"].fillna(0)
feat["def_len"]    = feat["def_len"].fillna(0)

FEATURES = ["difficulty", "char_len", "in_xinhua", "in_thuocl", "thuocl_freq", "def_len"]
rho_rows = []
for f in FEATURES:
    vals = feat[["stability", f]].dropna()
    rho, p = spearmanr(vals["stability"], vals[f])
    rho_rows.append({"feature": f, "spearman_rho": rho, "p_value": p, "n": len(vals)})

rho_df = pd.DataFrame(rho_rows).sort_values("spearman_rho", key=abs, ascending=False)
print(rho_df.to_string(index=False))

# ── 19.3  Most stable and most unstable idioms ────────────────────────────────
print("\n── 19.3  Most stable and most unstable idioms ────────────────────────────")

print("\n  Top 15 most stable (semantically convergent):")
top_stable = feat.nlargest(15, "stability")[
    ["source_language","idiom","stability","difficulty","in_xinhua"]]
print(top_stable.to_string(index=False))

print("\n  Top 15 most unstable (semantically divergent):")
top_unstable = feat.nsmallest(15, "stability")[
    ["source_language","idiom","stability","difficulty","in_xinhua"]]
print(top_unstable.to_string(index=False))

# Source language breakdown
print("\n  Mean stability by source language:")
print(feat.groupby("source_language")["stability"].agg(["mean","std","count"]).to_string())

# Save
feat[["idiom","source_language","stability","edit_mean","edit_CA","edit_CAu","edit_AAu",
      "difficulty","in_xinhua","in_thuocl","char_len"]].to_csv(
    PROC / "semantic_consistency.csv", index=False)
print(f"\n  Saved → data/processed/semantic_consistency.csv")

# ── 19.4  Stability by target language ────────────────────────────────────────
print("\n── 19.4  Stability by target language ────────────────────────────────────")

# Load target_language_profile for resource info
tlp = pd.read_parquet(PROC / "target_language_profile.parquet").reset_index()
tlp.rename(columns={"index": "target_language"}, inplace=True)

stability_by_tgt = (
    div.groupby("target_language")[["edit_CA", "edit_CAu", "edit_AAu"]]
    .mean()
    .assign(edit_mean=lambda d: d.mean(axis=1),
            stability=lambda d: 1 - d["edit_mean"])
    .reset_index()
    .merge(tlp[["target_language","resource"]], on="target_language", how="left")
    .sort_values("stability", ascending=False)
)
print(stability_by_tgt[["target_language","resource","stability","edit_mean"]].to_string(index=False))

# ── Figures ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: distribution of stability by source language
for src, grp in feat.groupby("source_language"):
    axes[0].hist(grp["stability"].dropna(), bins=40, alpha=0.55,
                 label=src, color=SOURCE_COLORS[src], density=True)
    axes[0].axvline(grp["stability"].mean(), color=SOURCE_COLORS[src],
                    linestyle="--", lw=1.5)
axes[0].set_xlabel("Semantic stability score (1 − mean edit distance)")
axes[0].set_ylabel("Density")
axes[0].set_title("Distribution of Semantic Stability\nby Source Language",
                  fontweight="bold")
axes[0].legend()

# Right: stability vs difficulty scatter
sample = feat.dropna(subset=["stability","difficulty"]).sample(
    min(5000, len(feat)), random_state=0)
for src, grp in sample.groupby("source_language"):
    axes[1].scatter(grp["difficulty"], grp["stability"],
                    c=SOURCE_COLORS[src], alpha=0.25, s=12, label=src)
rho, _ = spearmanr(sample["difficulty"], sample["stability"])
axes[1].set_xlabel("Composite difficulty score")
axes[1].set_ylabel("Semantic stability (1 − mean cross-strategy edit)")
axes[1].set_title(f"Stability vs Difficulty\n(Spearman ρ = {rho:.3f})",
                  fontweight="bold")
axes[1].legend()

fig.tight_layout()
fig.savefig(FIG / "semantic_consistency_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/semantic_consistency_distribution.png")

# Fig: feature correlations bar + stability by target language
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

bar_colors = ["#C44E52" if r < 0 else "#4C72B0" for r in rho_df["spearman_rho"]]
axes[0].barh(rho_df["feature"], rho_df["spearman_rho"],
             color=bar_colors, alpha=0.85)
axes[0].axvline(0, color="grey", lw=1)
axes[0].set_xlabel("Spearman ρ with semantic stability")
axes[0].set_title("Feature Correlations with Semantic Stability",
                  fontweight="bold")
for i, (_, row) in enumerate(rho_df.iterrows()):
    sig = "***" if row["p_value"] < 0.001 else ("*" if row["p_value"] < 0.05 else "")
    offset = 0.005 if row["spearman_rho"] >= 0 else -0.005
    axes[0].text(row["spearman_rho"] + offset, i, sig, va="center", fontsize=9)

# Stability by target language
colors_tgt = [RESOURCE_COLORS[r] for r in stability_by_tgt["resource"]]
axes[1].barh(stability_by_tgt["target_language"],
             stability_by_tgt["stability"],
             color=colors_tgt, alpha=0.85)
axes[1].set_xlabel("Mean semantic stability")
axes[1].set_title("Semantic Stability by Target Language\n(blue=high-resource, orange=low-resource)",
                  fontweight="bold")
for i, v in enumerate(stability_by_tgt["stability"]):
    axes[1].text(v + 0.001, i, f"{v:.3f}", va="center", fontsize=8)

fig.tight_layout()
fig.savefig(FIG / "semantic_stability_features.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/semantic_stability_features.png")

print("\nDone.")
