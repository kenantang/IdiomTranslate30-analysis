"""
Idiom-level difficulty composite.

Difficulty proxy (higher = harder to translate):
  1. Mean cross-strategy divergence (edit distance, from divergence_scores.parquet, 50k sample)
  2. Mean expansion ratio (computed fresh from raw data, macro-averaged over sentences)
  3. Within-idiom context sensitivity (mean CV of translation length, from context_sensitivity.parquet)
  4. Cross-target vocabulary overlap (mean within-family Jaccard, INVERTED — low overlap = hard)

All four components are min-max normalised per source language then averaged into a composite.

Correlates tested:
  - external dictionary coverage (in_xinhua, thuocl_freq from idiom_metadata.parquet)
  - cognate pair membership (in ZH-KO, ZH-JA, or KO-JA cognate lists)
  - idiom length (4-char vs non-4-char Chinese)
  - lexical diversity of spans (lexdiv_per_idiom.parquet)

Outputs:
  data/processed/idiom_difficulty.parquet
  figures/difficulty.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr, mannwhitneyu
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROC = ROOT / "data/processed"
FIG  = ROOT / "figures"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
LABELS = ["Creatively", "Analogy", "Author"]
LONG_THRESH = 500

print("Loading data…")
df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
for tc in TCOLS:
    df.loc[df[tc].str.len() > LONG_THRESH, tc] = np.nan

# ── Component 1: Cross-strategy edit distance (from 50k sample) ───────────
print("Component 1: cross-strategy divergence…")
div = pd.read_parquet(PROC / "divergence_scores.parquet")
# Use mean of the three pairwise edit distances
div["mean_edit"] = div[["edit_CA","edit_CAu","edit_AAu"]].mean(axis=1)
div_idiom = (div.groupby(["source_language","idiom"])["mean_edit"]
             .mean().reset_index()
             .rename(columns={"mean_edit":"div_mean_edit"}))

# ── Component 2: Expansion ratio (macro: mean over all rows per idiom) ─────
print("Component 2: expansion ratio…")
sent_len = df["sentence"].str.len().replace(0, np.nan)
for tc, lbl in zip(TCOLS, LABELS):
    df[f"exp_{lbl}"] = df[tc].str.len() / sent_len
exp_idiom = (df.groupby(["source_language","idiom"])
             [[f"exp_{l}" for l in LABELS]]
             .mean()
             .mean(axis=1)
             .reset_index()
             .rename(columns={0:"exp_mean"}))

# ── Component 3: Context sensitivity (CV, from context_sensitivity.parquet) ─────────
print("Component 3: context sensitivity…")
sens = pd.read_parquet(PROC / "context_sensitivity.parquet")
# Mean CV across strategies and target languages per idiom
cv_cols = [f"cv_{l}" for l in LABELS]
sens_idiom = (sens.groupby(["source_language","idiom"])[cv_cols]
              .mean()
              .mean(axis=1)
              .reset_index()
              .rename(columns={0:"mean_cv"}))

# ── Component 4: Cross-target Jaccard (within-family, INVERTED) ───────────
print("Component 4: cross-target overlap…")
xt = pd.read_parquet(PROC / "cross_target_overlap.parquet")
wf = xt[xt.relationship=="within-family"]
xt_idiom = (wf.groupby(["source_language","idiom"])["jaccard"]
            .mean()
            .reset_index()
            .rename(columns={"jaccard":"wf_jaccard"}))

# ── Merge all components ───────────────────────────────────────────────────
print("Merging components…")
base = df[["source_language","idiom"]].drop_duplicates()
comp = (base
        .merge(div_idiom,  on=["source_language","idiom"], how="left")
        .merge(exp_idiom,  on=["source_language","idiom"], how="left")
        .merge(sens_idiom, on=["source_language","idiom"], how="left")
        .merge(xt_idiom,   on=["source_language","idiom"], how="left"))

# Min-max normalise within each source language
def minmax(series):
    mn, mx = series.min(), series.max()
    return (series - mn) / (mx - mn) if mx > mn else pd.Series(0.5, index=series.index)

for src, grp_idx in comp.groupby("source_language").groups.items():
    grp = comp.loc[grp_idx]
    comp.loc[grp_idx, "n_div"]  = minmax(grp["div_mean_edit"])
    comp.loc[grp_idx, "n_exp"]  = minmax(grp["exp_mean"])
    comp.loc[grp_idx, "n_cv"]   = minmax(grp["mean_cv"])
    # Inverted: low within-family overlap = harder
    comp.loc[grp_idx, "n_xt"]   = 1 - minmax(grp["wf_jaccard"])

comp["difficulty"] = comp[["n_div","n_exp","n_cv","n_xt"]].mean(axis=1)

# ── Correlates ────────────────────────────────────────────────────────────
# Merge external metadata (Chinese only)
meta = pd.read_parquet(PROC / "idiom_metadata.parquet")
comp_zh = comp[comp.source_language=="Chinese"].merge(meta, on="idiom", how="left")

print("\n=== Spearman ρ: difficulty vs external metadata (Chinese) ===")
for col, label in [("thuocl_freq","THUOCL freq (rank)"),
                    ("def_len","Xinhua def length"),
                    ("exp_mean","Mean expansion ratio"),
                    ("mean_cv","Mean CV (context sens)")]:
    valid = comp_zh[[col,"difficulty"]].dropna()
    r, p = spearmanr(valid[col], valid["difficulty"])
    print(f"  {label:<30}  ρ={r:+.3f}  p={p:.2e}  n={len(valid):,}")

# Cognate membership
cognate_zh = set(pd.read_csv(PROC/"cjk_cognate_pairs.csv")["zh_idiom"])
cognate_ja = set(pd.read_csv(PROC/"zhja_cognate_pairs.csv")["zh_idiom"])
comp_zh["is_cognate_zhko"] = comp_zh["idiom"].isin(cognate_zh)
comp_zh["is_cognate_zhja"] = comp_zh["idiom"].isin(cognate_ja)

print("\n=== Difficulty: cognate vs non-cognate (Chinese) ===")
for flag, label in [("is_cognate_zhko","ZH-KO cognate"),
                     ("is_cognate_zhja","ZH-JA cognate")]:
    yes = comp_zh[comp_zh[flag]]["difficulty"].dropna()
    no  = comp_zh[~comp_zh[flag]]["difficulty"].dropna()
    stat, p = mannwhitneyu(yes, no, alternative="two-sided")
    print(f"  {label}: cognate μ={yes.mean():.3f}  non-cognate μ={no.mean():.3f}  p={p:.3e}")

# 4-char vs non-4-char (Chinese)
comp_zh["is_4char"] = comp_zh["idiom"].str.len() == 4
yes = comp_zh[comp_zh["is_4char"]]["difficulty"].dropna()
no  = comp_zh[~comp_zh["is_4char"]]["difficulty"].dropna()
stat, p = mannwhitneyu(yes, no, alternative="two-sided")
print(f"\n  4-char vs non-4-char: 4-char μ={yes.mean():.3f}  non-4 μ={no.mean():.3f}  p={p:.3e}")

# Lexical diversity (lexdiv_per_idiom.parquet)
lexdiv = pd.read_parquet(PROC / "lexdiv_per_idiom.parquet")
comp_all = comp.merge(lexdiv, on=["source_language","idiom"], how="left")
print("\n=== Spearman ρ: difficulty vs mean unique unigrams (all sources) ===")
for lbl in LABELS:
    valid = comp_all[["uniq_uni_"+lbl,"difficulty"]].dropna()
    r, p = spearmanr(valid["uniq_uni_"+lbl], valid["difficulty"])
    print(f"  {lbl:<14}  ρ={r:+.3f}  p={p:.2e}  n={len(valid):,}")

# Save
comp.to_parquet(PROC / "idiom_difficulty.parquet", index=False)
print(f"\nSaved {len(comp):,} idioms → data/processed/idiom_difficulty.parquet")
print("\n=== Difficulty distribution by source language ===")
print(comp.groupby("source_language")["difficulty"].describe().round(3).to_string())

# Top/bottom 10 hardest Chinese idioms (min coverage in div sample)
top10 = comp_zh.nlargest(10,"difficulty")[["idiom","difficulty","exp_mean","mean_cv","div_mean_edit"]]
bot10 = comp_zh.nsmallest(10,"difficulty")[["idiom","difficulty","exp_mean","mean_cv","div_mean_edit"]]
print("\n=== Top 10 hardest Chinese idioms ===")
print(top10.round(3).to_string(index=False))
print("\n=== Top 10 easiest Chinese idioms ===")
print(bot10.round(3).to_string(index=False))

# ── Figures ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(17, 10))

# F1: Difficulty distribution per source language
ax = axes[0, 0]
for src, color in zip(["Chinese","Japanese","Korean"],
                       ["#4C72B0","#DD8452","#55A868"]):
    comp[comp.source_language==src]["difficulty"].plot.kde(
        ax=ax, label=src, color=color, bw_method=0.15)
ax.set_title("Difficulty Score Distribution\nby Source Language", fontweight="bold")
ax.set_xlabel("Difficulty score (0=easy, 1=hard)")
ax.set_ylabel("Density"); ax.legend(fontsize=9)

# F2: Scatter difficulty vs expansion ratio (Chinese)
ax = axes[0, 1]
ax.scatter(comp_zh["exp_mean"], comp_zh["difficulty"], alpha=0.15, s=5, color="#4C72B0")
r, p = spearmanr(comp_zh[["exp_mean","difficulty"]].dropna()["exp_mean"],
                 comp_zh[["exp_mean","difficulty"]].dropna()["difficulty"])
ax.set_title(f"Difficulty vs Expansion Ratio\n(Chinese, ρ={r:.2f})", fontweight="bold")
ax.set_xlabel("Mean expansion ratio"); ax.set_ylabel("Difficulty score")

# F3: Difficulty by THUOCL quintile
ax = axes[0, 2]
valid_th = comp_zh[comp_zh["thuocl_freq"].notna()].copy()
valid_th["freq_quintile"] = pd.qcut(valid_th["thuocl_freq"], 5,
                                     labels=["Q1\n(rare)","Q2","Q3","Q4","Q5\n(common)"])
means = valid_th.groupby("freq_quintile", observed=True)["difficulty"].mean()
ax.bar(means.index, means.values, color="#4C72B0")
ax.set_title("Mean Difficulty by THUOCL\nFrequency Quintile (Chinese)", fontweight="bold")
ax.set_xlabel("Frequency quintile"); ax.set_ylabel("Mean difficulty score")

# F4: Cognate vs non-cognate difficulty (Chinese, violin)
ax = axes[1, 0]
cog_data = pd.concat([
    comp_zh[["difficulty","is_cognate_zhko"]].assign(
        Group=lambda d: d["is_cognate_zhko"].map({True:"ZH-KO\ncognate",False:"Non-cognate"})),
    comp_zh[["difficulty","is_cognate_zhja"]].assign(
        Group=lambda d: d["is_cognate_zhja"].map({True:"ZH-JA\ncognate",False:"Non-cognate"})),
])
sns.violinplot(data=cog_data, x="Group", y="difficulty",
               order=["ZH-KO\ncognate","ZH-JA\ncognate","Non-cognate"],
               palette={"ZH-KO\ncognate":"#4C72B0","ZH-JA\ncognate":"#DD8452",
                        "Non-cognate":"#AEB6BF"},
               inner="box", ax=ax)
ax.set_title("Difficulty: Cognate vs Non-Cognate\n(Chinese)", fontweight="bold")
ax.set_ylabel("Difficulty score"); ax.set_xlabel("")

# F5: Component correlation matrix (Chinese)
ax = axes[1, 1]
comp_cols = {"n_div":"Cross-strat\ndivergence","n_exp":"Expansion\nratio",
             "n_cv":"Context\nsensitivity","n_xt":"Cross-target\ndissimilarity"}
corr = comp_zh[list(comp_cols.keys())].rename(columns=comp_cols).corr(method="spearman")
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0,
            vmin=-1, vmax=1, linewidths=0.5, ax=ax)
ax.set_title("Component Intercorrelation\n(Spearman ρ, Chinese)", fontweight="bold")

# F6: Difficulty vs context sensitivity CV
ax = axes[1, 2]
for src, color in zip(["Chinese","Japanese","Korean"],
                       ["#4C72B0","#DD8452","#55A868"]):
    sub = comp[comp.source_language==src][["mean_cv","difficulty"]].dropna()
    ax.scatter(sub["mean_cv"], sub["difficulty"], alpha=0.15, s=4, color=color, label=src)
ax.set_title("Difficulty vs Context Sensitivity\n(mean CV across strategies)",
             fontweight="bold")
ax.set_xlabel("Mean CV of translation length")
ax.set_ylabel("Difficulty score"); ax.legend(fontsize=8)

fig.suptitle("Idiom-Level Difficulty Composite Score", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "difficulty.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/difficulty.png")
