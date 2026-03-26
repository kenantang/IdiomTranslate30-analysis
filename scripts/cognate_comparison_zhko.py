"""
Quantitative comparison of sentences and translations for cognate idiom pairs.

For each cognate pair (ZH idiom ↔ KO idiom sharing the same Hanja origin), rows are
joined by target_language, then compared on:
  - Source sentence length
  - Translation length (all 3 strategies)
  - Expansion ratio
  - Span length and span/translation ratio
  - N-gram divergence between ZH-sourced and KO-sourced translations
  - Normalised edit distance between ZH and KO translations

Results are broken down by: (a) exact vs near-3 cognates, (b) target language resource
level, (c) translation strategy.
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import wilcoxon, mannwhitneyu, spearmanr

from utils import word_jaccard, normalized_levenshtein, HIGH_RESOURCE_LANGS, STRATEGY_COLORS as COLORS

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data/processed"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
SCOLS  = ["span_creatively",      "span_analogy",      "span_author"]
LABELS = ["Creatively", "Analogy", "Author"]
HIGH_RES = HIGH_RESOURCE_LANGS   # H27: imported from utils

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data…")
df  = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
cog = pd.read_csv(PROC / "cjk_cognate_pairs.csv")

zh_df = df[df["source_language"] == "Chinese"].copy()
ko_df = df[df["source_language"] == "Korean"].copy()

# ── Build aligned pair table ──────────────────────────────────────────────────
# For each cognate pair × target_language, merge ZH and KO rows.
# Multiple sentences per (idiom, target_language) → keep all; will aggregate later.
print("Building aligned pair table…")
records = []
for _, cog_row in cog.iterrows():
    zh_grp = zh_df[zh_df["idiom"] == cog_row["zh_idiom"]]
    ko_grp = ko_df[ko_df["idiom"] == cog_row["ko_idiom"]]
    for tgt_lang in zh_grp["target_language"].unique():
        zh_sub = zh_grp[zh_grp["target_language"] == tgt_lang]
        ko_sub = ko_grp[ko_grp["target_language"] == tgt_lang]
        if zh_sub.empty or ko_sub.empty:
            continue
        # Take means over all sentences for this (idiom, target_lang)
        row = {
            "zh_idiom":   cog_row["zh_idiom"],
            "ko_idiom":   cog_row["ko_idiom"],
            "match_type": cog_row["match_type"],
            "target_language": tgt_lang,
            "resource":   "high" if tgt_lang in HIGH_RES else "low",
            # sentence lengths
            "zh_sent_len": zh_sub["sentence"].str.len().mean(),
            "ko_sent_len": ko_sub["sentence"].str.len().mean(),
        }
        for tc, sc, lbl in zip(TCOLS, SCOLS, LABELS):
            row[f"zh_tlen_{lbl}"] = zh_sub[tc].str.len().mean()
            row[f"ko_tlen_{lbl}"] = ko_sub[tc].str.len().mean()
            row[f"zh_slen_{lbl}"] = zh_sub[sc].str.len().mean()
            row[f"ko_slen_{lbl}"] = ko_sub[sc].str.len().mean()
        records.append(row)

pairs = pd.DataFrame(records)
print(f"  Aligned rows: {len(pairs):,}  "
      f"(exact: {(pairs['match_type']=='exact_4/4').sum():,}, "
      f"near-3: {(pairs['match_type']=='near_3/4').sum():,})")

# Derived columns
sent_diff_mean = {}
for lbl in LABELS:
    pairs[f"tlen_diff_{lbl}"] = pairs[f"zh_tlen_{lbl}"] - pairs[f"ko_tlen_{lbl}"]
    pairs[f"slen_diff_{lbl}"] = pairs[f"zh_slen_{lbl}"] - pairs[f"ko_slen_{lbl}"]
pairs["sent_len_diff"] = pairs["zh_sent_len"] - pairs["ko_sent_len"]

# ── 1. Sentence length comparison ─────────────────────────────────────────────
print("\n=== Sentence length (source) ===")
print(f"  ZH  mean: {pairs['zh_sent_len'].mean():.1f}  median: {pairs['zh_sent_len'].median():.1f}")
print(f"  KO  mean: {pairs['ko_sent_len'].mean():.1f}  median: {pairs['ko_sent_len'].median():.1f}")
print(f"  Diff (ZH-KO) mean: {pairs['sent_len_diff'].mean():.2f}")
stat, p = wilcoxon(pairs["zh_sent_len"].dropna(), pairs["ko_sent_len"].dropna(),
                   zero_method="wilcox")
print(f"  Wilcoxon p: {p:.2e}")

# ── 2. Translation length comparison ─────────────────────────────────────────
print("\n=== Translation length: ZH vs KO (per strategy) ===")
for lbl in LABELS:
    zh_col, ko_col = f"zh_tlen_{lbl}", f"ko_tlen_{lbl}"
    valid = pairs[[zh_col, ko_col]].dropna()
    stat, p = wilcoxon(valid[zh_col], valid[ko_col], zero_method="wilcox")
    print(f"  {lbl:<14}  ZH={valid[zh_col].mean():.1f}  KO={valid[ko_col].mean():.1f}  "
          f"diff={valid[zh_col].mean()-valid[ko_col].mean():+.1f}  p={p:.2e}")

# Exact vs near-3
print("\n  By match type (Creatively):")
for mt, grp in pairs.groupby("match_type"):
    valid = grp[["zh_tlen_Creatively","ko_tlen_Creatively"]].dropna()
    diff = (valid["zh_tlen_Creatively"] - valid["ko_tlen_Creatively"]).mean()
    print(f"    {mt:<12}  diff ZH-KO = {diff:+.1f}")

# ── 3. Span length comparison ─────────────────────────────────────────────────
print("\n=== Span length: ZH vs KO (per strategy) ===")
for lbl in LABELS:
    zh_col, ko_col = f"zh_slen_{lbl}", f"ko_slen_{lbl}"
    valid = pairs[[zh_col, ko_col]].dropna()
    stat, p = wilcoxon(valid[zh_col], valid[ko_col], zero_method="wilcox")
    print(f"  {lbl:<14}  ZH={valid[zh_col].mean():.1f}  KO={valid[ko_col].mean():.1f}  "
          f"diff={valid[zh_col].mean()-valid[ko_col].mean():+.1f}  p={p:.2e}")

# ── 4. Cross-source translation divergence (n-gram + edit distance) ───────────
# For each (zh_idiom, ko_idiom, target_lang): average over all 10×10 sentence
# pairs so every sentence contributes equally to the divergence estimate.
print("\n=== Cross-source translation divergence ===")
sample_records = []
for (zh_id, ko_id, mt), grp_cog in cog.groupby(["zh_idiom","ko_idiom","match_type"]):
    zh_rows = zh_df[zh_df["idiom"]==zh_id]
    ko_rows = ko_df[ko_df["idiom"]==ko_id]
    for tgt in zh_rows["target_language"].unique():
        zh_sub = zh_rows[zh_rows["target_language"]==tgt]
        ko_sub = ko_rows[ko_rows["target_language"]==tgt]
        if zh_sub.empty or ko_sub.empty:
            continue
        rec = {"match_type": mt, "target_language": tgt,
               "resource": "high" if tgt in HIGH_RES else "low"}
        for tc, lbl in zip(TCOLS, LABELS):
            edits, jaccards = [], []
            for _, zh_r in zh_sub.iterrows():
                for _, ko_r in ko_sub.iterrows():
                    a, b = str(zh_r[tc]), str(ko_r[tc])
                    edits.append(normalized_levenshtein(a, b))    # H18
                    jaccards.append(word_jaccard(a, b))           # H17
            rec[f"edit_{lbl}"]    = float(np.mean(edits))
            rec[f"jaccard_{lbl}"] = float(np.mean(jaccards))
        sample_records.append(rec)

div_df = pd.DataFrame(sample_records)
print(f"  Divergence rows: {len(div_df):,}")
print("\n  Mean normalised edit distance (ZH vs KO translation of same underlying idiom):")
for lbl in LABELS:
    print(f"  {lbl:<14}  edit={div_df[f'edit_{lbl}'].mean():.3f}  "
          f"jaccard={div_df[f'jaccard_{lbl}'].mean():.3f}")

print("\n  By match type (Creatively):")
for mt, g in div_df.groupby("match_type"):
    print(f"    {mt:<12}  edit={g['edit_Creatively'].mean():.3f}  "
          f"jaccard={g['jaccard_Creatively'].mean():.3f}")

print("\n  By resource level (Creatively):")
for res, g in div_df.groupby("resource"):
    print(f"    {res:<6}  edit={g['edit_Creatively'].mean():.3f}  "
          f"jaccard={g['jaccard_Creatively'].mean():.3f}")

# ── 5. Correlation: tlen_diff ~ sent_len_diff ─────────────────────────────────
print("\n=== Spearman ρ: sentence length diff vs translation length diff ===")
for lbl in LABELS:
    valid = pairs[["sent_len_diff", f"tlen_diff_{lbl}"]].dropna()
    r, p = spearmanr(valid["sent_len_diff"], valid[f"tlen_diff_{lbl}"])
    print(f"  {lbl:<14}  ρ={r:.3f}  p={p:.2e}")

# ── Figures ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# F1: Sentence length ZH vs KO (violin)
ax = axes[0, 0]
sl_melt = pd.melt(
    pairs[["match_type","zh_sent_len","ko_sent_len"]],
    id_vars=["match_type"], var_name="lang", value_name="Sentence length (chars)"
)
sl_melt["lang"] = sl_melt["lang"].map({"zh_sent_len":"Chinese","ko_sent_len":"Korean"})
sns.violinplot(data=sl_melt, x="lang", y="Sentence length (chars)",
               hue="match_type", split=True, inner="quartile",
               palette={"exact_4/4":"#4C72B0","near_3/4":"#DD8452"}, ax=ax)
ax.set_title("Source Sentence Length:\nCognate Chinese vs Korean", fontweight="bold")
ax.set_xlabel("")
ax.legend(title="Match type", fontsize=8)

# F2: Translation length diff by strategy (box)
ax = axes[0, 1]
tl_diff = pd.melt(
    pairs[["match_type"] + [f"tlen_diff_{l}" for l in LABELS]].rename(
        columns={f"tlen_diff_{l}": l for l in LABELS}),
    id_vars=["match_type"], var_name="Strategy", value_name="ZH - KO length (chars)"
).dropna()
sns.boxplot(data=tl_diff, x="Strategy", y="ZH - KO length (chars)",
            hue="match_type", palette={"exact_4/4":"#4C72B0","near_3/4":"#DD8452"},
            flierprops=dict(marker=".", alpha=0.2), ax=ax)
ax.axhline(0, ls="--", color="red", lw=1)
ax.set_title("Translation Length Difference\n(ZH − KO) by Strategy", fontweight="bold")
ax.legend(title="Match type", fontsize=8)

# F3: Span length diff by strategy (box)
ax = axes[0, 2]
sl_diff = pd.melt(
    pairs[["match_type"] + [f"slen_diff_{l}" for l in LABELS]].rename(
        columns={f"slen_diff_{l}": l for l in LABELS}),
    id_vars=["match_type"], var_name="Strategy", value_name="ZH - KO span (chars)"
).dropna()
sns.boxplot(data=sl_diff, x="Strategy", y="ZH - KO span (chars)",
            hue="match_type", palette={"exact_4/4":"#4C72B0","near_3/4":"#DD8452"},
            flierprops=dict(marker=".", alpha=0.2), ax=ax)
ax.axhline(0, ls="--", color="red", lw=1)
ax.set_title("Span Length Difference\n(ZH − KO) by Strategy", fontweight="bold")
ax.legend(title="Match type", fontsize=8)

# F4: Edit distance by target language
ax = axes[1, 0]
edit_lang = div_df.groupby("target_language")[
    [f"edit_{l}" for l in LABELS]].mean().rename(columns={f"edit_{l}":l for l in LABELS})
edit_lang = edit_lang.sort_values("Creatively")
x = np.arange(len(edit_lang)); w = 0.26
for i, (lbl, color) in enumerate(zip(LABELS, COLORS)):
    ax.bar(x + i*w, edit_lang[lbl], w, label=lbl, color=color)
ax.set_xticks(x + w)
ax.set_xticklabels(edit_lang.index, rotation=30, ha="right")
ax.set_title("ZH–KO Translation Edit Distance\nby Target Language", fontweight="bold")
ax.set_ylabel("Mean normalised edit distance")
ax.legend(title="Strategy", fontsize=8)

# F5: Edit distance by match type × strategy (violin)
ax = axes[1, 1]
edit_melt = pd.melt(
    div_df[["match_type"] + [f"edit_{l}" for l in LABELS]].rename(
        columns={f"edit_{l}": l for l in LABELS}),
    id_vars=["match_type"], var_name="Strategy", value_name="Normalised edit distance"
).dropna()
sns.boxplot(data=edit_melt, x="Strategy", y="Normalised edit distance",
            hue="match_type", palette={"exact_4/4":"#4C72B0","near_3/4":"#DD8452"},
            flierprops=dict(marker=".", alpha=0.2), ax=ax)
ax.set_title("ZH–KO Translation Divergence\nby Match Type & Strategy", fontweight="bold")
ax.legend(title="Match type", fontsize=8)

# F6: Scatter — ZH tlen vs KO tlen (Creatively, exact cognates)
ax = axes[1, 2]
exact = pairs[pairs["match_type"]=="exact_4/4"].dropna(
    subset=["zh_tlen_Creatively","ko_tlen_Creatively"])
near3 = pairs[pairs["match_type"]=="near_3/4"].dropna(
    subset=["zh_tlen_Creatively","ko_tlen_Creatively"])
ax.scatter(exact["zh_tlen_Creatively"], exact["ko_tlen_Creatively"],
           alpha=0.3, s=8, color="#4C72B0", label="Exact (4/4)")
ax.scatter(near3["zh_tlen_Creatively"],  near3["ko_tlen_Creatively"],
           alpha=0.2, s=6, color="#DD8452", label="Near-3")
lim = max(pairs[["zh_tlen_Creatively","ko_tlen_Creatively"]].max()) * 1.05
ax.plot([0, lim], [0, lim], "k--", lw=0.8, label="ZH = KO")
ax.set_xlim(0, lim); ax.set_ylim(0, lim)
ax.set_title("Translation Length:\nChinese vs Korean (Creatively)", fontweight="bold")
ax.set_xlabel("ZH translation length (chars)")
ax.set_ylabel("KO translation length (chars)")
r, _ = spearmanr(exact["zh_tlen_Creatively"], exact["ko_tlen_Creatively"])
ax.text(0.05, 0.95, f"ρ={r:.3f} (exact)", transform=ax.transAxes, va="top", fontsize=9)
ax.legend(fontsize=8)

fig.suptitle("Cognate Pair Comparison: Chinese vs Korean Source Idioms",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "cognate_comparison_zhko.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/cognate_comparison_zhko.png")

# ── Fig 2: Jaccard similarity heatmap by target language × strategy ───────────
fig, ax = plt.subplots(figsize=(9, 5))
jacc_pivot = div_df.groupby("target_language")[
    [f"jaccard_{l}" for l in LABELS]].mean().rename(
    columns={f"jaccard_{l}": l for l in LABELS})
jacc_pivot = jacc_pivot.sort_values("Creatively")
sns.heatmap(jacc_pivot, annot=True, fmt=".3f", cmap="YlGnBu",
            vmin=0, vmax=1, linewidths=0.4,
            cbar_kws={"label": "Jaccard similarity (word-level)"}, ax=ax)
ax.set_title("ZH–KO Translation Word Overlap (Jaccard)\nby Target Language & Strategy",
             fontweight="bold")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(FIG / "jaccard_heatmap_zhko.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/jaccard_heatmap_zhko.png")

# ── Save table ────────────────────────────────────────────────────────────────
summary = pd.DataFrame({
    "Strategy": LABELS,
    "ZH_tlen_mean": [pairs[f"zh_tlen_{l}"].mean() for l in LABELS],
    "KO_tlen_mean": [pairs[f"ko_tlen_{l}"].mean() for l in LABELS],
    "tlen_diff_mean": [pairs[f"tlen_diff_{l}"].mean() for l in LABELS],
    "ZH_slen_mean": [pairs[f"zh_slen_{l}"].mean() for l in LABELS],
    "KO_slen_mean": [pairs[f"ko_slen_{l}"].mean() for l in LABELS],
    "edit_dist_mean": [div_df[f"edit_{l}"].mean() for l in LABELS],
    "jaccard_mean":   [div_df[f"jaccard_{l}"].mean() for l in LABELS],
})
print("\n=== Summary table ===")
print(summary.round(3).to_string(index=False))
summary.to_csv(PROC / "cognate_comparison_summary.csv", index=False)
print("Saved → data/processed/cognate_comparison_summary.csv")
