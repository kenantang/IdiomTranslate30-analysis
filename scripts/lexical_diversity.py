"""Lexical Diversity Analysis."""
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

ROOT = Path(__file__).parent.parent
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG = ROOT / "figures"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TRANS_COLS  = ["translate_creatively", "translate_analogy", "translate_author"]
SPAN_COLS   = ["span_creatively",      "span_analogy",      "span_author"]
LABELS      = ["Creatively", "Analogy", "Author"]
COLORS      = ["#4C72B0", "#DD8452", "#55A868"]

# ── TTR (word-level) ──────────────────────────────────────────────────────────
def ttr(text):
    words = str(text).lower().split()
    return len(set(words)) / len(words) if words else np.nan

print("Computing TTR…")
for col, lbl in zip(TRANS_COLS, LABELS):
    df[f"ttr_{lbl}"] = df[col].apply(ttr)

print("TTR medians:")
for lbl in LABELS:
    print(f"  {lbl:<14} {df[f'ttr_{lbl}'].median():.3f}")

# ── Unique unigrams in spans per idiom (across 10 target languages) ───────────
print("\nComputing unique unigrams in spans per idiom…")
uniq_rows = []
for (src, idiom), grp in df.groupby(["source_language","idiom"]):
    row = {"source_language": src, "idiom": idiom}
    for sc, lbl in zip(SPAN_COLS, LABELS):
        spans = grp[sc].dropna().tolist()
        all_words = " ".join(spans).lower().split()
        row[f"uniq_uni_{lbl}"] = len(set(all_words))
    uniq_rows.append(row)
uniq_df = pd.DataFrame(uniq_rows)

print("\nMean unique unigrams in spans per idiom:")
for lbl in LABELS:
    print(f"  {lbl:<14} {uniq_df[f'uniq_uni_{lbl}'].mean():.1f}")

# ── Fig 7a: unique unigrams distribution per strategy ────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
melt_uniq = pd.melt(
    uniq_df[[f"uniq_uni_{l}" for l in LABELS]].rename(
        columns={f"uniq_uni_{l}": l for l in LABELS}),
    var_name="Strategy", value_name="Unique unigrams in spans"
)
sns.violinplot(data=melt_uniq, x="Strategy", y="Unique unigrams in spans",
               hue="Strategy", palette=COLORS, cut=0, inner="quartile",
               legend=False, ax=axes[0])
axes[0].set_title("Unique Unigrams in Spans\nper Idiom (across 10 target langs)", fontweight="bold")
for i, lbl in enumerate(LABELS):
    med = uniq_df[f"uniq_uni_{lbl}"].median()
    axes[0].text(i, med+1, f"med={med:.0f}", ha="center", fontsize=9)

# ── Fig 7b: TTR by target language ───────────────────────────────────────────
ttr_lang = df.groupby("target_language")[[f"ttr_{l}" for l in LABELS]].mean()
ttr_lang.columns = LABELS
ttr_lang = ttr_lang.sort_values("Creatively")
x = np.arange(len(ttr_lang))
w = 0.26
for i, (lbl, color) in enumerate(zip(LABELS, COLORS)):
    axes[1].bar(x + i*w, ttr_lang[lbl], w, label=lbl, color=color)
axes[1].set_xticks(x + w)
axes[1].set_xticklabels(ttr_lang.index, rotation=30, ha="right")
axes[1].set_title("Mean TTR by Target Language & Strategy", fontweight="bold")
axes[1].set_ylabel("Type-token ratio")
axes[1].legend(title="Strategy")
fig.tight_layout()
fig.savefig(FIG / "unique_unigrams.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/unique_unigrams.png")

# ── Fig 7c: Span TTR vs full translation TTR scatter ────────────────────────
def span_ttr(text):
    words = str(text).lower().split()
    return len(set(words)) / len(words) if words else np.nan

sample = df.sample(20_000, random_state=7)
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, (tc, sc), lbl, color in zip(axes, zip(TRANS_COLS, SPAN_COLS), LABELS, COLORS):
    trans_ttr = sample[tc].apply(ttr)
    sp_ttr    = sample[sc].apply(span_ttr)
    valid = trans_ttr.notna() & sp_ttr.notna()
    ax.scatter(trans_ttr[valid], sp_ttr[valid], alpha=0.1, s=4, color=color)
    r, p = spearmanr(trans_ttr[valid], sp_ttr[valid])
    ax.set_title(f"{lbl}\nSpearman ρ={r:.3f}", fontweight="bold")
    ax.set_xlabel("Full translation TTR")
    ax.set_ylabel("Span TTR" if ax is axes[0] else "")
fig.suptitle("Span TTR vs Full Translation TTR", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "ttr_by_language.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/ttr_by_language.png")

# Save unique-unigrams per idiom for use by the difficulty script
uniq_df.to_parquet(ROOT / "data" / "processed" / "lexdiv_per_idiom.parquet", index=False)
print("Saved → data/processed/lexdiv_per_idiom.parquet")
