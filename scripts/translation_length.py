"""
Translation Length & Expansion Ratio.

Outputs
-------
data/processed/translation_length_stats.csv  – per-strategy median length by target
                                                language; expansion ratio macrostats;
                                                Wilcoxon effect sizes.
figures/fig3_translation_length_violin.png
figures/fig4_length_by_target_language.png
figures/expansion_ratio.png
figures/wilcoxon_effects.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")


from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import wilcoxon

ROOT = Path(__file__).parent.parent
df   = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TRANS = ["translate_creatively", "translate_analogy", "translate_author"]
LABELS = ["Creatively", "Analogy", "Author"]
COLORS = ["#4C72B0", "#DD8452", "#55A868"]

# ── Expansion ratio ───────────────────────────────────────────────────────────
sent_len = df["sentence"].str.len().replace(0, np.nan)
for col, lbl in zip(TRANS, LABELS):
    df[f"exp_{lbl}"] = df[col].str.len() / sent_len

# Macro-average over idioms (one mean per unique idiom, then average those)
def macro_stat(series, idiom_col):
    return series.groupby(idiom_col).mean().mean()

print("Expansion ratio (macro-avg over idioms):")
for lbl in LABELS:
    vals = df[f"exp_{lbl}"].dropna()
    ma = macro_stat(vals, df.loc[vals.index, "idiom"])
    print(f"  {lbl:<14}  median={vals.median():.2f}  mean={vals.mean():.2f}  macro-mean={ma:.2f}")

# ── Fig 1a: violin of expansion ratio per strategy ───────────────────────────
sample = df.sample(50_000, random_state=0)
melted = pd.melt(
    sample[[f"exp_{l}" for l in LABELS]].rename(columns={f"exp_{l}": l for l in LABELS}),
    var_name="Strategy", value_name="Expansion ratio"
).dropna()
melted = melted[melted["Expansion ratio"] < melted["Expansion ratio"].quantile(0.99)]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.violinplot(data=melted, x="Strategy", y="Expansion ratio",
               hue="Strategy", palette=COLORS, cut=0, inner="quartile",
               legend=False, ax=axes[0])
axes[0].set_title("Expansion Ratio Distribution by Strategy", fontweight="bold")
axes[0].set_ylabel("len(translation) / len(sentence)")
for i, lbl in enumerate(LABELS):
    med = sample[f"exp_{lbl}"].dropna().median()
    axes[0].text(i, med + 0.15, f"med={med:.2f}", ha="center", fontsize=9)

# ── Fig 1b: median length per target language × strategy ─────────────────────
len_df = df[["target_language"] + TRANS].copy()
for col in TRANS:
    len_df[col] = len_df[col].str.len()
med_tgt = len_df.groupby("target_language")[TRANS].median()
med_tgt.columns = LABELS
med_tgt = med_tgt.sort_values("Creatively")
x = np.arange(len(med_tgt))
w = 0.26
for i, (lbl, color) in enumerate(zip(LABELS, COLORS)):
    axes[1].bar(x + i*w, med_tgt[lbl], w, label=lbl, color=color)
axes[1].set_xticks(x + w)
axes[1].set_xticklabels(med_tgt.index, rotation=30, ha="right")
axes[1].set_title("Median Translation Length\nby Target Language & Strategy", fontweight="bold")
axes[1].set_ylabel("Median character count")
axes[1].legend(title="Strategy")
fig.tight_layout()
fig.savefig(FIG / "expansion_ratio.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/expansion_ratio.png")

# ── Wilcoxon tests between strategy pairs per target language ─────────────────
print("\nWilcoxon tests (Creatively vs Analogy, Creatively vs Author) per target language:")
print(f"{'Language':<15} {'C vs A  p':>12} {'C vs Au p':>12} {'effect C-A':>12} {'effect C-Au':>12}")
rows = []
for lang, grp in df.groupby("target_language"):
    c  = grp["translate_creatively"].str.len().dropna()
    a  = grp["translate_analogy"].str.len().dropna()
    au = grp["translate_author"].str.len().dropna()
    idx = c.index.intersection(a.index).intersection(au.index)
    stat_ca,  p_ca  = wilcoxon(c[idx], a[idx],  alternative="less")
    stat_cau, p_cau = wilcoxon(c[idx], au[idx], alternative="less")
    n = len(idx)
    r_ca  = 1 - (2*stat_ca)  / (n*(n+1)/2)
    r_cau = 1 - (2*stat_cau) / (n*(n+1)/2)
    rows.append({"lang": lang, "p_CA": p_ca, "p_CAu": p_cau, "r_CA": r_ca, "r_CAu": r_cau})
    print(f"  {lang:<15} {p_ca:>12.2e} {p_cau:>12.2e} {r_ca:>12.4f} {r_cau:>12.4f}")

# ── Fig 1c: heatmap of effect sizes ──────────────────────────────────────────
wdf = pd.DataFrame(rows).set_index("lang")
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
for ax, col, title in [
    (axes[0], "r_CA",  "Effect size r\n(Creatively < Analogy)"),
    (axes[1], "r_CAu", "Effect size r\n(Creatively < Author)"),
]:
    vals = wdf[[col]].sort_values(col, ascending=False)
    sns.heatmap(vals, annot=True, fmt=".3f", cmap="Blues", vmin=0, vmax=1,
                linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.7})
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("")
fig.suptitle("Wilcoxon Effect Sizes — Translation Length\n(all p < 0.001)", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "wilcoxon_effects.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/wilcoxon_effects.png")

# ── Fig 3: translation length violin (all three strategies) ──────────────────
sample = df.sample(min(50_000, len(df)), random_state=42)
length_df = pd.DataFrame({
    label: sample[col].str.len()
    for col, label in zip(TRANS, LABELS)
})
melted_v = length_df.melt(var_name="Strategy", value_name="Length (chars)")

fig, ax = plt.subplots(figsize=(10, 5))
sns.violinplot(data=melted_v, x="Strategy", y="Length (chars)",
               palette=COLORS, cut=0, inner="quartile", ax=ax)
ax.set_title("Translation Length Distribution by Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Character count")
for i, label in enumerate(LABELS):
    med = length_df[label].median()
    ax.text(i, med + 20, f"med={med:.0f}", ha="center", va="bottom",
            fontsize=9, color="black")
fig.tight_layout()
fig.savefig(FIG / "fig3_translation_length_violin.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/fig3_translation_length_violin.png")

# ── Fig 4: median translation length by target language × strategy ────────────
med_by_lang = (
    df.groupby("target_language")[TRANS]
    .apply(lambda g: g.apply(lambda s: s.str.len().median()))
    .rename(columns=dict(zip(TRANS, LABELS)))
)
med_by_lang = med_by_lang.sort_values("Creatively")

fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(med_by_lang))
width = 0.26
for i, (label, color) in enumerate(zip(LABELS, COLORS)):
    ax.bar(x + i * width, med_by_lang[label], width, label=label, color=color)
ax.set_xticks(x + width)
ax.set_xticklabels(med_by_lang.index, rotation=30, ha="right")
ax.set_title("Median Translation Length by Target Language & Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Median character count")
ax.legend(title="Strategy")
fig.tight_layout()
fig.savefig(FIG / "fig4_length_by_target_language.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/fig4_length_by_target_language.png")

# ── Save processed output ──────────────────────────────────────────────────────
# Per-strategy expansion macro-stats
macro_rows = []
sent_len_for_stats = df["sentence"].str.len().replace(0, np.nan)
for col, lbl in zip(TRANS, LABELS):
    exp = df[col].str.len() / sent_len_for_stats
    vals = exp.dropna()
    macro_rows.append({
        "strategy": lbl,
        "expansion_median": float(vals.median()),
        "expansion_mean": float(vals.mean()),
        "expansion_macro_mean": float(vals.groupby(df.loc[vals.index, "idiom"]).mean().mean()),
    })
macro_df = pd.DataFrame(macro_rows)

# Median length by target language × strategy
med_long = med_by_lang.reset_index().melt(
    id_vars="target_language", var_name="strategy", value_name="median_chars"
)

# Wilcoxon effect sizes (already computed in wdf above)
wilcoxon_df = wdf.reset_index().rename(columns={"lang": "target_language"})

# Merge into one output
stats_out = med_long.merge(wilcoxon_df, on="target_language", how="left")
stats_out = stats_out.merge(
    macro_df[["strategy", "expansion_median", "expansion_mean", "expansion_macro_mean"]],
    on="strategy", how="left"
)
out_path = PROC / "translation_length_stats.csv"
stats_out.to_csv(out_path, index=False)
print(f"Saved → {out_path}")
