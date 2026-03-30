"""
Part 15: Context Complexity, Difficulty Prediction & Typological Span Analysis.

Three linked analyses that quantify relationships between input properties,
translation behaviour, and target-language structure:
  15.1  Sentence complexity → output consistency — does source sentence length
        predict within-cell translation CV?
  15.2  Difficulty prediction model — which idiom-level features (frequency,
        character count, dictionary coverage) best predict the composite
        difficulty score?  Spearman correlations + OLS regression.
  15.3  Span position × linguistic typology — do word order (SVO/SOV/VSO) and
        morphological complexity predict where in the translation the idiom
        rendering appears?

Outputs
-------
data/processed/sentence_complexity_corr.csv
data/processed/difficulty_feature_importance.csv
data/processed/typology_span_stats.csv
figures/sentence_complexity_cv.png
figures/difficulty_regression.png
figures/typology_span_heatmap.png
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

LABELS = ["Creatively", "Analogy", "Author"]

# ── Linguistic typology annotations ──────────────────────────────────────────
TYPOLOGY = pd.DataFrame([
    {"target_language": "English",  "script": "Latin",    "word_order": "SVO", "morphology": "low",    "resource": "high"},
    {"target_language": "French",   "script": "Latin",    "word_order": "SVO", "morphology": "low",    "resource": "high"},
    {"target_language": "German",   "script": "Latin",    "word_order": "SVO", "morphology": "medium", "resource": "high"},
    {"target_language": "Spanish",  "script": "Latin",    "word_order": "SVO", "morphology": "low",    "resource": "high"},
    {"target_language": "Italian",  "script": "Latin",    "word_order": "SVO", "morphology": "low",    "resource": "high"},
    {"target_language": "Russian",  "script": "Cyrillic", "word_order": "SVO", "morphology": "high",   "resource": "high"},
    {"target_language": "Arabic",   "script": "Arabic",   "word_order": "VSO", "morphology": "high",   "resource": "low"},
    {"target_language": "Bengali",  "script": "Indic",    "word_order": "SOV", "morphology": "medium", "resource": "low"},
    {"target_language": "Hindi",    "script": "Indic",    "word_order": "SOV", "morphology": "medium", "resource": "low"},
    {"target_language": "Swahili",  "script": "Latin",    "word_order": "SVO", "morphology": "high",   "resource": "low"},
])

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading data …")
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
cs = pd.read_parquet(PROC / "context_sensitivity.parquet")
diff = pd.read_parquet(PROC / "idiom_difficulty.parquet")
meta = pd.read_parquet(PROC / "idiom_metadata.parquet")
span_pos = pd.read_parquet(PROC / "span_positions.parquet")
print(f"  Raw: {len(df):,} rows | CS: {len(cs):,} | Diff: {len(diff):,}")

# ── 15.1  Sentence complexity → output consistency ────────────────────────────
print("\n── 15.1  Sentence complexity → output consistency ───────────────────────")

# Source sentence length per (source_language, idiom) — averaged across all 10 sentences
sent_len = (
    df.groupby(["source_language", "idiom"])["sentence"]
    .apply(lambda s: s.str.len().mean())
    .reset_index(name="mean_sentence_len")
)
# Word count
df["sentence_wc"] = df["sentence"].str.split().str.len()
sent_wc = (
    df.groupby(["source_language", "idiom"])["sentence_wc"]
    .mean()
    .reset_index(name="mean_sentence_wc")
)

# Merge with context sensitivity
cs_merged = cs.merge(sent_len, on=["source_language", "idiom"], how="inner")
cs_merged = cs_merged.merge(sent_wc, on=["source_language", "idiom"], how="inner")

corr_rows = []
for src, grp in cs_merged.groupby("source_language"):
    for tgt, tgrp in grp.groupby("target_language"):
        for label in LABELS:
            cv_col = f"cv_{label}"
            vals = tgrp[[cv_col, "mean_sentence_len", "mean_sentence_wc"]].dropna()
            if len(vals) < 20:
                continue
            r_len, p_len = spearmanr(vals["mean_sentence_len"], vals[cv_col])
            r_wc,  p_wc  = spearmanr(vals["mean_sentence_wc"],  vals[cv_col])
            corr_rows.append({
                "source_language":  src,
                "target_language":  tgt,
                "strategy":         label,
                "rho_sent_len":     r_len,
                "p_sent_len":       p_len,
                "rho_sent_wc":      r_wc,
                "p_sent_wc":        p_wc,
                "n":                len(vals),
            })

corr_df = pd.DataFrame(corr_rows)
corr_df.to_csv(PROC / "sentence_complexity_corr.csv", index=False)
print(f"  Saved → data/processed/sentence_complexity_corr.csv  ({len(corr_df)} rows)")

print("\n  Mean Spearman ρ (sentence length → CV) by strategy:")
agg = corr_df.groupby("strategy")[["rho_sent_len", "rho_sent_wc"]].mean()
print(agg.to_string())

sig_frac = (corr_df["p_sent_len"] < 0.05).mean()
print(f"\n  Fraction of (src×tgt×strategy) cells with p<0.05 : {sig_frac:.1%}")

# ── Fig: sentence complexity → CV ────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: heatmap of mean rho by (source, strategy)
hm_data = (
    corr_df.groupby(["source_language", "strategy"])["rho_sent_len"]
    .mean()
    .unstack("strategy")[LABELS]
)
sns.heatmap(hm_data, annot=True, fmt=".3f", cmap="RdBu_r",
            center=0, vmin=-0.3, vmax=0.3,
            linewidths=0.5, cbar_kws={"label": "Spearman ρ"}, ax=axes[0])
axes[0].set_title("Correlation: Source Sentence Length → CV\nby Source Language & Strategy",
                  fontweight="bold")

# Right: scatter (mean rho per target language)
agg_tgt = corr_df.groupby("target_language")["rho_sent_len"].mean().reset_index()
agg_tgt = agg_tgt.merge(TYPOLOGY[["target_language", "resource"]], on="target_language")
colors_r = {"high": RESOURCE_COLORS["high"], "low": RESOURCE_COLORS["low"]}
for _, row in agg_tgt.iterrows():
    axes[1].scatter(0, row["rho_sent_len"],
                    color=colors_r[row["resource"]], s=80, alpha=0.8)
    axes[1].annotate(row["target_language"],
                     (0, row["rho_sent_len"]),
                     textcoords="offset points", xytext=(8, 0), fontsize=9)
axes[1].axhline(0, color="grey", linestyle="--", lw=1)
axes[1].set_xlim(-0.3, 0.5)
axes[1].set_yticks(agg_tgt["rho_sent_len"].round(3))
axes[1].set_ylabel("Mean Spearman ρ (all strategies)")
axes[1].set_title("Sentence Length → CV Correlation\nby Target Language",
                  fontweight="bold")
from matplotlib.lines import Line2D
legend_els = [Line2D([0], [0], marker="o", color="w",
                     markerfacecolor=colors_r["high"], label="High-resource"),
              Line2D([0], [0], marker="o", color="w",
                     markerfacecolor=colors_r["low"], label="Low-resource")]
axes[1].legend(handles=legend_els)

fig.tight_layout()
fig.savefig(FIG / "sentence_complexity_cv.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/sentence_complexity_cv.png")

# ── 15.2  Difficulty prediction model ─────────────────────────────────────────
print("\n── 15.2  Difficulty prediction model ──────────────────────────────────────")

# Build feature matrix
feat = (
    diff[["source_language", "idiom", "difficulty"]]
    .merge(meta, on="idiom", how="left")
)
feat["char_len"]   = feat["idiom"].str.len()
feat["is_4char"]   = (feat["char_len"] == 4).astype(int)
feat["in_xinhua"]  = feat["in_xinhua"].fillna(False).astype(int)
feat["in_thuocl"]  = feat["in_thuocl"].fillna(False).astype(int)
feat["thuocl_freq"] = feat["thuocl_freq"].fillna(0)
feat["def_len"]    = feat["def_len"].fillna(0)
feat["src_zh"]     = (feat["source_language"] == "Chinese").astype(int)
feat["src_ja"]     = (feat["source_language"] == "Japanese").astype(int)
# Korean is the reference category

feat = feat.dropna(subset=["difficulty"])
print(f"  Feature matrix: {len(feat)} rows")

FEATURES = ["char_len", "is_4char", "in_xinhua", "in_thuocl",
            "thuocl_freq", "def_len", "src_zh", "src_ja"]

# Spearman correlations
rho_rows = []
for f in FEATURES:
    vals = feat[["difficulty", f]].dropna()
    rho, p = spearmanr(vals["difficulty"], vals[f])
    rho_rows.append({"feature": f, "spearman_rho": rho, "p_value": p, "n": len(vals)})
rho_df = pd.DataFrame(rho_rows).sort_values("spearman_rho", key=abs, ascending=False)
print("\n  Spearman correlations with difficulty:")
print(rho_df.to_string(index=False))

# OLS regression (numpy lstsq)
X_df = feat[FEATURES].fillna(0)
y    = feat["difficulty"].values
X    = np.column_stack([np.ones(len(X_df)), X_df.values])
coef, residuals, _, _ = np.linalg.lstsq(X, y, rcond=None)
y_hat = X @ coef
ss_res = ((y - y_hat)**2).sum()
ss_tot = ((y - y.mean())**2).sum()
r2 = 1 - ss_res / ss_tot
print(f"\n  OLS R² = {r2:.4f}")

feat_importance = pd.DataFrame({
    "feature":     ["intercept"] + FEATURES,
    "coefficient": coef,
})
feat_importance["abs_coef"] = feat_importance["coefficient"].abs()
feat_importance = feat_importance.merge(
    rho_df[["feature","spearman_rho","p_value"]], on="feature", how="left")
feat_importance.to_csv(PROC / "difficulty_feature_importance.csv", index=False)
print(f"  Saved → data/processed/difficulty_feature_importance.csv")

# ── Fig: difficulty regression ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: feature importance (Spearman rho bar chart)
plot_feats = rho_df.copy()
bar_colors = ["#C44E52" if r < 0 else "#4C72B0" for r in plot_feats["spearman_rho"]]
axes[0].barh(plot_feats["feature"], plot_feats["spearman_rho"],
             color=bar_colors, alpha=0.85)
axes[0].axvline(0, color="grey", lw=1)
axes[0].set_xlabel("Spearman ρ with difficulty score")
axes[0].set_title(f"Feature Correlations with Idiom Difficulty\n(OLS R²={r2:.3f})",
                  fontweight="bold")
for i, (_, row) in enumerate(plot_feats.iterrows()):
    sig = "*" if row["p_value"] < 0.05 else ""
    axes[0].text(row["spearman_rho"] + (0.005 if row["spearman_rho"] >= 0 else -0.005),
                 i, sig, va="center", fontsize=10)

# Right: scatter — predicted vs actual difficulty (sampled)
sample = feat.sample(min(5000, len(feat)), random_state=42)
X_s = np.column_stack([np.ones(len(sample)), sample[FEATURES].fillna(0).values])
y_hat_s = X_s @ coef
axes[1].scatter(y_hat_s, sample["difficulty"], alpha=0.15, s=8, color="#4C72B0")
lims = [min(y_hat_s.min(), sample["difficulty"].min()),
        max(y_hat_s.max(), sample["difficulty"].max())]
axes[1].plot(lims, lims, "r--", lw=1.5, label="y=x (perfect)")
axes[1].set_xlabel("Predicted difficulty")
axes[1].set_ylabel("Actual difficulty")
axes[1].set_title("OLS Predicted vs Actual Difficulty\n(5,000-point sample)", fontweight="bold")
axes[1].legend()

fig.tight_layout()
fig.savefig(FIG / "difficulty_regression.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/difficulty_regression.png")

# ── 15.3  Span position × linguistic typology ─────────────────────────────────
print("\n── 15.3  Span position × linguistic typology ─────────────────────────────")

sp_typed = span_pos.merge(TYPOLOGY, on="target_language", how="left")

# Median rel_start by typological category
by_word_order = (
    sp_typed.groupby(["word_order", "strategy"])["rel_start"]
    .agg(median="median", mean="mean", n="count")
    .reset_index()
)
by_morphology = (
    sp_typed.groupby(["morphology", "strategy"])["rel_start"]
    .agg(median="median", mean="mean", n="count")
    .reset_index()
)
by_script = (
    sp_typed.groupby(["script", "strategy"])["rel_start"]
    .agg(median="median", mean="mean", n="count")
    .reset_index()
)

print("\n  Median span position (rel_start) by word order:")
print(by_word_order.pivot_table(index="word_order", columns="strategy",
                                 values="median").to_string())
print("\n  Median span position by morphological complexity:")
print(by_morphology.pivot_table(index="morphology", columns="strategy",
                                 values="median").to_string())
print("\n  Median span position by script family:")
print(by_script.pivot_table(index="script", columns="strategy",
                              values="median").to_string())

# Save
typology_stats = sp_typed.groupby(
    ["target_language", "word_order", "morphology", "script", "resource", "strategy"]
)["rel_start"].agg(median_rel_start="median", mean_rel_start="mean").reset_index()
typology_stats.to_csv(PROC / "typology_span_stats.csv", index=False)
print(f"  Saved → data/processed/typology_span_stats.csv")

# Spearman correlation between span position and morphological complexity
morph_order = {"low": 0, "medium": 1, "high": 2}
sp_typed["morph_num"] = sp_typed["morphology"].map(morph_order)
rho_morph, p_morph = spearmanr(
    sp_typed["morph_num"].dropna(),
    sp_typed.loc[sp_typed["morph_num"].notna(), "rel_start"])
print(f"\n  Spearman ρ (morphology → rel_start): {rho_morph:.4f}, p={p_morph:.2e}")

# ── Fig: typology heatmap ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

for ax, groupby_col, title in zip(
        axes,
        ["word_order", "morphology", "script"],
        ["Word Order", "Morphological Complexity", "Script Family"]):
    pivot = sp_typed.groupby([groupby_col, "strategy"])["rel_start"].median().unstack("strategy")
    pivot = pivot[LABELS]  # ensure column order
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap="YlGnBu",
                vmin=0.4, vmax=0.7, linewidths=0.5,
                cbar_kws={"label": "Median rel. position"}, ax=ax)
    ax.set_title(f"Span Position by {title}", fontweight="bold")
    ax.set_xlabel("Strategy")
    ax.set_ylabel(title if ax is axes[0] else "")

fig.suptitle("Median Idiom Span Position in Translation by Linguistic Typology",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "typology_span_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/typology_span_heatmap.png")

print("\nDone.")
