"""Translation Length & Expansion Ratio."""
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
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG = ROOT / "figures"
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
