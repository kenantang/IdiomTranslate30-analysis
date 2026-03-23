"""Module 3 — Strategy Divergence via N-gram & Edit Distance Analysis."""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")


from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from rapidfuzz.distance import Levenshtein

ROOT = Path(__file__).parent.parent
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TRANS  = ["translate_creatively", "translate_analogy", "translate_author"]
LABELS = ["Creatively", "Analogy", "Author"]
COLORS = ["#4C72B0", "#DD8452", "#55A868"]

sample = df.sample(50_000, random_state=3).dropna(subset=TRANS).reset_index(drop=True)

# ── N-gram divergence (word-level unigrams) ───────────────────────────────────
def ngram_div(text_a, text_b, n=1):
    """Fraction of n-grams in text_a not present in text_b."""
    def ngrams(t, n):
        words = t.lower().split()
        return set(zip(*[words[i:] for i in range(n)])) if len(words) >= n else set()
    a = ngrams(text_a, n)
    if not a:
        return np.nan
    return len(a - ngrams(text_b, n)) / len(a)

print("Computing n-gram divergence (50k sample)…")
for n in [1, 2]:
    tag = f"ng{n}"
    sample[f"div_CA_{tag}"]  = [ngram_div(a, b, n) for a, b in
                                 zip(sample["translate_creatively"], sample["translate_analogy"])]
    sample[f"div_CAu_{tag}"] = [ngram_div(a, b, n) for a, b in
                                 zip(sample["translate_creatively"], sample["translate_author"])]
    sample[f"div_AAu_{tag}"] = [ngram_div(a, b, n) for a, b in
                                 zip(sample["translate_analogy"],    sample["translate_author"])]

# ── Normalised edit distance ──────────────────────────────────────────────────
print("Computing edit distances…")
def norm_edit(a, b):
    max_len = max(len(a), len(b))
    if max_len == 0:
        return 0.0
    return Levenshtein.distance(a, b) / max_len

sample["edit_CA"]  = [norm_edit(a, b) for a, b in
                      zip(sample["translate_creatively"], sample["translate_analogy"])]
sample["edit_CAu"] = [norm_edit(a, b) for a, b in
                      zip(sample["translate_creatively"], sample["translate_author"])]
sample["edit_AAu"] = [norm_edit(a, b) for a, b in
                      zip(sample["translate_analogy"],    sample["translate_author"])]

# ── Print summary ─────────────────────────────────────────────────────────────
print("\nMean unigram divergence (fraction of A's unigrams absent from B):")
for pair, col in [("C→A","div_CA_ng1"), ("C→Au","div_CAu_ng1"), ("A→Au","div_AAu_ng1")]:
    print(f"  {pair}: {sample[col].mean():.3f}")
print("\nMean normalised edit distance:")
for pair, col in [("C↔A","edit_CA"), ("C↔Au","edit_CAu"), ("A↔Au","edit_AAu")]:
    print(f"  {pair}: {sample[col].mean():.3f}")

# ── Fig 3a: divergence heatmap per target language ───────────────────────────
rows = []
for lang, grp in sample.groupby("target_language"):
    rows.append({"lang": lang,
                 "C vs A":  grp["div_CA_ng1"].mean(),
                 "C vs Au": grp["div_CAu_ng1"].mean(),
                 "A vs Au": grp["div_AAu_ng1"].mean()})
heat = pd.DataFrame(rows).set_index("lang")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.heatmap(heat, annot=True, fmt=".3f", cmap="OrRd", linewidths=0.5,
            vmin=0, vmax=heat.values.max()*1.1,
            cbar_kws={"label": "Unigram divergence"}, ax=axes[0])
axes[0].set_title("Mean Unigram Divergence\nby Target Language", fontweight="bold")
axes[0].set_xlabel("")

# ── Fig 3b: edit distance distribution ───────────────────────────────────────
edit_melt = pd.melt(
    sample[["edit_CA","edit_CAu","edit_AAu"]].rename(
        columns={"edit_CA":"C↔A","edit_CAu":"C↔Au","edit_AAu":"A↔Au"}),
    var_name="Pair", value_name="Norm. edit distance"
)
sns.violinplot(data=edit_melt, x="Pair", y="Norm. edit distance",
               hue="Pair", palette=["#4C72B0","#DD8452","#55A868"],
               cut=0, inner="quartile", legend=False, ax=axes[1])
axes[1].set_title("Normalised Edit Distance\nbetween Strategy Pairs", fontweight="bold")
for i, (pair, col) in enumerate([("C↔A","edit_CA"),("C↔Au","edit_CAu"),("A↔Au","edit_AAu")]):
    med = sample[col].median()
    axes[1].text(i, med+0.01, f"med={med:.2f}", ha="center", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "module3_ngram_divergence_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/module3_ngram_divergence_heatmap.png")

# ── Fig 3c: edit distance distribution figure ────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))
edit_melt2 = edit_melt[edit_melt["Norm. edit distance"] <= 1.0]
sns.boxplot(data=edit_melt2, x="Pair", y="Norm. edit distance",
            hue="Pair", palette=["#4C72B0","#DD8452","#55A868"],
            width=0.45, flierprops=dict(marker=".", alpha=0.3), legend=False, ax=ax)
ax.set_title("Normalised Edit Distance between Translation Strategies", fontweight="bold")
ax.set_ylabel("Normalised Levenshtein distance")
fig.tight_layout()
fig.savefig(FIG / "module3_edit_distance_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/module3_edit_distance_distribution.png")

# ── Top/bottom idioms by divergence ──────────────────────────────────────────
idiom_div = sample.groupby("idiom")["div_CA_ng1"].mean().dropna()
print("\nTop 10 most divergent idioms (C vs A):")
print(idiom_div.nlargest(10).to_string())
print("\nTop 10 least divergent idioms (C vs A):")
print(idiom_div.nsmallest(10).to_string())

# Save per-row divergence scores for use in Module 8
sample[["idiom","source_language","target_language",
        "div_CA_ng1","div_CAu_ng1","div_AAu_ng1","edit_CA","edit_CAu","edit_AAu"]]\
    .to_parquet(PROC / "divergence_scores.parquet", index=False)
print("Saved → data/processed/divergence_scores.parquet")
