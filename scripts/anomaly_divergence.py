"""
Part 14: Anomaly Characterisation & Divergence Baseline.

Two complementary analyses that address data quality and interpretation gaps:
  14.1  Zero-sentence anomaly characterisation — the 300 rows with empty source
        sentences (3 Chinese idioms) are described in passing throughout the docs
        but never systematically analysed.  This script characterises their
        translation properties and recommends a filtering policy.
  14.2  Within-cell vs between-cell divergence baseline — context sensitivity
        (within-cell CV) is reported but never compared against the between-idiom
        baseline, making it impossible to judge whether the measured variation is
        large or small.

Outputs
-------
data/processed/zero_sentence_summary.csv
data/processed/divergence_baseline.csv
figures/zero_sentence_analysis.png
figures/within_vs_between_divergence.png
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
from scipy.stats import mannwhitneyu, ks_2samp

from utils import STRATEGY_COLORS as COLORS, OUTLIER_PERCENTILE

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

LABELS    = ["Creatively", "Analogy", "Author"]
TRANS_COLS = ["translate_creatively", "translate_analogy", "translate_author"]
SPAN_COLS  = ["span_creatively",      "span_analogy",      "span_author"]

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading raw data …")
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
print(f"  {len(df):,} rows loaded")

# ── 14.1  Zero-sentence anomaly characterisation ──────────────────────────────
print("\n── 14.1  Zero-sentence anomaly characterisation ──────────────────────────")

df["sentence_len"] = df["sentence"].fillna("").str.len()
zero_mask  = df["sentence_len"] == 0
normal_mask = ~zero_mask

print(f"  Zero-sentence rows : {zero_mask.sum():,} ({100*zero_mask.mean():.3f}%)")
print(f"  Affected idioms    : {df[zero_mask]['idiom'].nunique()}")
print(f"  Affected source    : {df[zero_mask]['source_language'].unique()}")
print(f"  Idioms             : {sorted(df[zero_mask]['idiom'].unique())}")

# Per-strategy translation length comparison
zero_records = []
for tcol, scol, label in zip(TRANS_COLS, SPAN_COLS, LABELS):
    t_z = df[zero_mask][tcol].str.len().dropna()
    t_n = df[normal_mask][tcol].str.len().dropna()
    s_z = df[zero_mask][scol].str.len().dropna()
    s_n = df[normal_mask][scol].str.len().dropna()

    # Containment error rate
    err_z = pd.Series([sp not in tr for sp, tr in zip(
        df[zero_mask][scol].fillna("").astype(str),
        df[zero_mask][tcol].fillna("").astype(str))])
    err_n = pd.Series([sp not in tr for sp, tr in zip(
        df[normal_mask][scol].fillna("").astype(str),
        df[normal_mask][tcol].fillna("").astype(str))])

    stat, p = mannwhitneyu(t_z.sample(min(300, len(t_z)), random_state=0),
                           t_n.sample(min(3000, len(t_n)), random_state=0),
                           alternative="two-sided")

    zero_records.append({
        "strategy":          label,
        "zero_trans_median": t_z.median(),
        "norm_trans_median": t_n.median(),
        "zero_span_median":  s_z.median(),
        "norm_span_median":  s_n.median(),
        "zero_error_pct":    err_z.mean() * 100,
        "norm_error_pct":    err_n.mean() * 100,
        "mannwhitney_p":     p,
    })
    print(f"  {label:<14} trans_len  zero={t_z.median():.0f}  normal={t_n.median():.0f}"
          f"  p={p:.3e}")

zero_summary = pd.DataFrame(zero_records)
zero_summary.to_csv(PROC / "zero_sentence_summary.csv", index=False)
print(f"  Saved → data/processed/zero_sentence_summary.csv")

# ── Fig: zero-sentence analysis ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Translation length comparison
x = np.arange(len(LABELS))
width = 0.35
axes[0].bar(x - width/2, zero_summary["zero_trans_median"],
            width, label="Zero-sentence", color="#C44E52", alpha=0.85)
axes[0].bar(x + width/2, zero_summary["norm_trans_median"],
            width, label="Normal", color="#4C72B0", alpha=0.85)
axes[0].set_xticks(x); axes[0].set_xticklabels(LABELS)
axes[0].set_ylabel("Median translation length (chars)")
axes[0].set_title("Translation Length:\nZero-Sentence vs Normal Rows", fontweight="bold")
axes[0].legend()

# Span length comparison
axes[1].bar(x - width/2, zero_summary["zero_span_median"],
            width, label="Zero-sentence", color="#C44E52", alpha=0.85)
axes[1].bar(x + width/2, zero_summary["norm_span_median"],
            width, label="Normal", color="#4C72B0", alpha=0.85)
axes[1].set_xticks(x); axes[1].set_xticklabels(LABELS)
axes[1].set_ylabel("Median span length (chars)")
axes[1].set_title("Span Length:\nZero-Sentence vs Normal Rows", fontweight="bold")
axes[1].legend()

# Error rate comparison
axes[2].bar(x - width/2, zero_summary["zero_error_pct"],
            width, label="Zero-sentence", color="#C44E52", alpha=0.85)
axes[2].bar(x + width/2, zero_summary["norm_error_pct"],
            width, label="Normal", color="#4C72B0", alpha=0.85)
axes[2].set_xticks(x); axes[2].set_xticklabels(LABELS)
axes[2].set_ylabel("Span error rate (%)")
axes[2].set_title("Span Containment Error:\nZero-Sentence vs Normal Rows", fontweight="bold")
axes[2].legend()

fig.suptitle("Zero-Sentence Row Anomaly Characterisation", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "zero_sentence_analysis.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/zero_sentence_analysis.png")

# ── 14.2  Within-cell vs between-cell divergence baseline ─────────────────────
print("\n── 14.2  Within-cell vs between-cell divergence baseline ─────────────────")

cs = pd.read_parquet(PROC / "context_sensitivity.parquet")
# Columns: source_language, idiom, target_language, n_sentences,
#          cv_Creatively, jaccard_div_Creatively, span_uniq_Creatively, …

cv_cols   = ["cv_Creatively",   "cv_Analogy",   "cv_Author"]
jac_cols  = ["jaccard_div_Creatively", "jaccard_div_Analogy", "jaccard_div_Author"]
uniq_cols = ["span_uniq_Creatively",   "span_uniq_Analogy",   "span_uniq_Author"]

# Within-cell = the per-cell CV values already in context_sensitivity
# Between-cell = for each (target, strategy), draw two random DIFFERENT idioms
#                and compare how different their CVs are from each other.
#                Operationally: std of CV across all idioms per (target, strategy)
#                represents between-idiom variation in translation consistency.

baseline_rows = []
for tgt, grp in cs.groupby("target_language"):
    for cv_col, jac_col, uniq_col, label in zip(cv_cols, jac_cols, uniq_cols, LABELS):
        within_cv  = grp[cv_col].dropna()
        within_jac = grp[jac_col].dropna()
        # Between-cell: randomly shuffle idioms and compare CV pairs
        # (we measure std across idioms as the between-cell spread)
        between_cv_std  = grp.groupby("source_language")[cv_col].std().mean()
        between_jac_std = grp.groupby("source_language")[jac_col].std().mean()

        baseline_rows.append({
            "target_language":   tgt,
            "strategy":          label,
            "within_cv_mean":    within_cv.mean(),
            "within_cv_median":  within_cv.median(),
            "within_jac_mean":   within_jac.mean(),
            "between_cv_std":    between_cv_std,
            "between_jac_std":   between_jac_std,
            # ratio: how large is within vs between?
            "cv_within_to_between": within_cv.mean() / between_cv_std if between_cv_std > 0 else np.nan,
        })

baseline_df = pd.DataFrame(baseline_rows)
baseline_df.to_csv(PROC / "divergence_baseline.csv", index=False)
print(f"  Saved → data/processed/divergence_baseline.csv  ({len(baseline_df)} rows)")

print("\n  Mean within-cell CV vs between-cell CV std by strategy:")
agg = baseline_df.groupby("strategy")[["within_cv_mean", "between_cv_std",
                                        "cv_within_to_between"]].mean()
print(agg.to_string())

# Formal comparison: are within-cell CV distributions different across target languages?
print("\n  KS test (Creatively CV): highest vs lowest within-cell targets")
cv_by_tgt = {tgt: grp["cv_Creatively"].dropna().values
             for tgt, grp in cs.groupby("target_language")}
sorted_tgts = sorted(cv_by_tgt, key=lambda t: np.median(cv_by_tgt[t]))
lo, hi = sorted_tgts[0], sorted_tgts[-1]
ks_stat, ks_p = ks_2samp(cv_by_tgt[lo], cv_by_tgt[hi])
print(f"  {lo} (lowest CV median) vs {hi} (highest): KS={ks_stat:.3f}, p={ks_p:.2e}")

# ── Fig: within vs between divergence ────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: violin of within-cell CV by strategy
cv_long = pd.melt(
    cs[["cv_Creatively", "cv_Analogy", "cv_Author"]].rename(
        columns={f"cv_{l}": l for l in LABELS}),
    var_name="Strategy", value_name="Within-cell CV"
).dropna()
cv_long = cv_long[cv_long["Within-cell CV"] < cv_long["Within-cell CV"].quantile(OUTLIER_PERCENTILE)]

sns.violinplot(data=cv_long, x="Strategy", y="Within-cell CV",
               hue="Strategy", palette={l: c for l, c in zip(LABELS, COLORS)},
               cut=0, inner="quartile", legend=False, ax=axes[0])
axes[0].set_title("Within-cell CV Distribution by Strategy\n(10 sentences per idiom–target cell)",
                  fontweight="bold")
axes[0].set_ylabel("Coefficient of Variation (CV)")

# Right: within vs between — scatter per target language
agg_tgt = baseline_df.groupby("target_language")[
    ["within_cv_mean", "between_cv_std"]].mean().reset_index()
for i, row in agg_tgt.iterrows():
    axes[1].scatter(row["within_cv_mean"], row["between_cv_std"],
                    s=80, color="#4C72B0", alpha=0.8)
    axes[1].annotate(row["target_language"],
                     (row["within_cv_mean"], row["between_cv_std"]),
                     textcoords="offset points", xytext=(5, 3), fontsize=8)
# diagonal reference line
lims = [min(agg_tgt["within_cv_mean"].min(), agg_tgt["between_cv_std"].min()) * 0.9,
        max(agg_tgt["within_cv_mean"].max(), agg_tgt["between_cv_std"].max()) * 1.05]
axes[1].plot(lims, lims, "k--", lw=1, alpha=0.4, label="y=x")
axes[1].set_xlabel("Mean within-cell CV")
axes[1].set_ylabel("Between-idiom CV std")
axes[1].set_title("Within-Cell vs Between-Cell Divergence\nby Target Language (all strategies)",
                  fontweight="bold")
axes[1].legend()

fig.tight_layout()
fig.savefig(FIG / "within_vs_between_divergence.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/within_vs_between_divergence.png")

print("\nDone.")
