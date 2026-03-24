"""
Cross-target language word overlap for the same idiom.

For each (idiom, strategy):
  - Aggregate the vocabulary used across all 10 sentences per target language
    → word_set[lang] = union of word sets from all 10 translations
  - Compute pairwise Jaccard between all C(10,2)=45 language pairs
  - Classify pairs as within-family vs between-family

Language families (among IT30's 10 targets):
  Germanic  : English, German
  Romance   : French, Spanish, Italian
  South_Asian: Bengali, Hindi
  Semitic   : Arabic
  Slavic    : Russian
  Bantu     : Swahili

Within-family pairs: (English,German), (French,Spanish), (French,Italian),
                     (Spanish,Italian), (Bengali,Hindi)
All others: between-family.

Outputs:
  data/processed/cross_target_overlap.parquet   (per-idiom pair-level)
  data/processed/cross_target_summary.csv       (mean Jaccard by family relationship)
  figures/cross_target_overlap.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROC = ROOT / "data/processed"
FIG  = ROOT / "figures"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
LABELS = ["Creatively", "Analogy", "Author"]
LONG_THRESH = 500

FAMILIES = {
    "English":  "Germanic",
    "German":   "Germanic",
    "French":   "Romance",
    "Spanish":  "Romance",
    "Italian":  "Romance",
    "Bengali":  "South Asian",
    "Hindi":    "South Asian",
    "Arabic":   "Semitic",
    "Russian":  "Slavic",
    "Swahili":  "Bantu",
}
TARGETS = list(FAMILIES.keys())

print("Loading data…")
df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
for tc in TCOLS:
    df.loc[df[tc].str.len() > LONG_THRESH, tc] = np.nan

# ── Build vocabulary per (idiom, target, strategy) ─────────────────────────
print("Building word sets…")
# Aggregate words across all 10 sentences per (idiom, target_language)
def agg_words(series):
    words = set()
    for t in series.dropna():
        words.update(str(t).lower().split())
    return words

# Work strategy by strategy to keep memory manageable
all_records = []

for tc, lbl in zip(TCOLS, LABELS):
    print(f"  Processing {lbl}…")
    sub = df[["source_language","idiom","target_language", tc]].copy()
    # Build word sets grouped by (idiom, target_language)
    word_sets = (sub.groupby(["source_language","idiom","target_language"])[tc]
                 .apply(agg_words))
    # Pivot: index=(src,idiom), columns=target_language
    word_sets = word_sets.unstack(level="target_language")  # shape: (n_idioms, 10)

    for (src, idiom), row in word_sets.iterrows():
        # row is a Series indexed by target language, values = word sets (or NaN)
        valid_langs = [l for l in TARGETS if l in row.index and isinstance(row[l], set)]
        if len(valid_langs) < 2:
            continue
        for la, lb in combinations(valid_langs, 2):
            wa, wb = row[la], row[lb]
            union = wa | wb
            jacc  = len(wa & wb) / len(union) if union else 0.0
            fa, fb = FAMILIES[la], FAMILIES[lb]
            rel = "within-family" if fa == fb else "between-family"
            all_records.append({
                "source_language": src, "idiom": idiom,
                "lang_A": la, "lang_B": lb,
                "family_A": fa, "family_B": fb,
                "relationship": rel,
                "jaccard": jacc,
                "strategy": lbl,
            })

overlap = pd.DataFrame(all_records)
overlap.to_parquet(PROC / "cross_target_overlap.parquet", index=False)
print(f"Saved {len(overlap):,} pair-level rows → data/processed/cross_target_overlap.parquet")

# ── Summary ────────────────────────────────────────────────────────────────
print("\n=== Mean Jaccard by relationship × strategy ===")
summary = (overlap.groupby(["strategy","relationship"])["jaccard"]
           .agg(["mean","median","std","count"]).round(4))
print(summary.to_string())
summary.to_csv(PROC / "cross_target_summary.csv")

print("\n=== Mean Jaccard by language pair (Creatively) ===")
sub_c = overlap[overlap.strategy=="Creatively"]
pair_mean = (sub_c.groupby(["lang_A","lang_B"])["jaccard"].mean()
             .sort_values(ascending=False))
print(pair_mean.head(15).round(4).to_string())

print("\n=== Mean Jaccard by source language × relationship (Creatively) ===")
print(sub_c.groupby(["source_language","relationship"])["jaccard"]
      .mean().round(4).to_string())

# ── Figures ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(17, 10))

# F1–F3: Within vs between-family Jaccard per strategy
for ax, lbl in zip(axes[0], LABELS):
    sub = overlap[overlap.strategy==lbl]
    sns.boxplot(data=sub, x="relationship", y="jaccard",
                order=["within-family","between-family"],
                palette={"within-family":"#4C72B0","between-family":"#AEB6BF"},
                flierprops=dict(marker=".", alpha=0.05), ax=ax)
    wf = sub[sub.relationship=="within-family"]["jaccard"].mean()
    bf = sub[sub.relationship=="between-family"]["jaccard"].mean()
    ax.set_title(f"Jaccard by Language Relationship\n({lbl})", fontweight="bold")
    ax.set_ylabel("Jaccard word overlap"); ax.set_xlabel("")
    ax.text(0, ax.get_ylim()[1]*0.92, f"μ={wf:.3f}", ha="center", fontsize=9,
            color="#4C72B0", fontweight="bold")
    ax.text(1, ax.get_ylim()[1]*0.92, f"μ={bf:.3f}", ha="center", fontsize=9,
            color="#555", fontweight="bold")

# F4: Heatmap of mean Jaccard between all target language pairs (Creatively)
ax = axes[1, 0]
mat = pd.DataFrame(index=TARGETS, columns=TARGETS, dtype=float)
for la, lb in combinations(TARGETS, 2):
    sel = sub_c[(sub_c.lang_A==la) & (sub_c.lang_B==lb)]
    if sel.empty:
        sel = sub_c[(sub_c.lang_A==lb) & (sub_c.lang_B==la)]
    v = sel["jaccard"].mean() if not sel.empty else np.nan
    mat.loc[la, lb] = v
    mat.loc[lb, la] = v
np.fill_diagonal(mat.values, 1.0)
sns.heatmap(mat.astype(float), annot=True, fmt=".3f", cmap="YlOrRd",
            vmin=0, vmax=0.3, linewidths=0.4,
            cbar_kws={"label":"Mean Jaccard"}, ax=ax)
ax.set_title("Cross-Target Jaccard Heatmap\n(Creatively)", fontweight="bold")

# F5: Top/bottom language pairs by Jaccard
ax = axes[1, 1]
top10 = pair_mean.head(10)
bot10 = pair_mean.tail(10).sort_values()
labels_bar = [f"{a}–{b}" for a,b in top10.index] + [f"{a}–{b}" for a,b in bot10.index]
values_bar  = list(top10.values) + list(bot10.values)
colors_bar  = ["#4C72B0"]*10 + ["#DD8452"]*10
y = range(len(labels_bar))
ax.barh(list(y), values_bar, color=colors_bar)
ax.set_yticks(list(y)); ax.set_yticklabels(labels_bar, fontsize=8)
ax.set_title("Top & Bottom 10 Language Pairs\nBy Jaccard (Creatively)", fontweight="bold")
ax.set_xlabel("Mean Jaccard")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#4C72B0",label="Top 10"),
                   Patch(color="#DD8452",label="Bottom 10")], fontsize=8)

# F6: Within-family Jaccard by family group across strategies
ax = axes[1, 2]
wf_family = (overlap[overlap.relationship=="within-family"]
             .groupby(["family_A","strategy"])["jaccard"].mean().unstack())
# Only families with within-family pairs: Germanic, Romance, South Asian
wf_family = wf_family.loc[["Germanic","Romance","South Asian"]]
wf_family[LABELS].plot(kind="bar", ax=ax,
    color=["#4C72B0","#DD8452","#55A868"], width=0.65)
ax.set_title("Within-Family Jaccard\nby Language Family & Strategy", fontweight="bold")
ax.set_ylabel("Mean Jaccard"); ax.tick_params(axis="x", rotation=0)
ax.legend(title="Strategy", fontsize=8)

fig.suptitle("Cross-Target Language Word Overlap for the Same Idiom",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "cross_target_overlap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/cross_target_overlap.png")
