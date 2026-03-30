"""
Part 12: Pairwise & Stratified Analysis.

Addresses three complementary stratification gaps:
  12.1  Error rates by source × target language pair (90 cells: 3 src × 10 tgt × 3 strategy)
  12.2  Script-family effects on span properties (Latin / Cyrillic / Arabic / Indic / Bantu)
  12.3  Strategy consistency across source languages (does Creatively behave the same
        regardless of whether the source idiom is Chinese, Japanese, or Korean?)

Outputs
-------
data/processed/pairwise_error_rates.csv      – error rate per (source, target, strategy)
data/processed/script_family_stats.csv       – span ratio & error rate aggregated by script family
data/processed/strategy_source_consistency.csv – mean ± std of expansion ratio per
                                                  (strategy, target, source)
figures/pairwise_error_heatmap.png
figures/script_family_stats.png
figures/strategy_source_consistency.png
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
from scipy.stats import f_oneway

from utils import STRATEGY_COLORS as COLORS, SOURCE_COLORS, OUTLIER_PERCENTILE

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ── Script-family mapping ─────────────────────────────────────────────────────
SCRIPT_FAMILY = {
    "English": "Latin",
    "French":  "Latin",
    "German":  "Latin",
    "Spanish": "Latin",
    "Italian": "Latin",
    "Swahili": "Latin",
    "Russian": "Cyrillic",
    "Arabic":  "Arabic",
    "Bengali": "Indic",
    "Hindi":   "Indic",
}

STRATEGY_COLS = [
    ("translate_creatively", "span_creatively", "Creatively"),
    ("translate_analogy",    "span_analogy",    "Analogy"),
    ("translate_author",     "span_author",     "Author"),
]

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading raw data …")
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
print(f"  {len(df):,} rows loaded")

# ── 12.1  Error rates by (source, target, strategy) ──────────────────────────
print("\n── 12.1  Pairwise error rates ──────────────────────────────────────────")

records = []
for tcol, scol, label in STRATEGY_COLS:
    t = df[tcol].fillna("").astype(str)
    s = df[scol].fillna("").astype(str)
    err = pd.Series([sp not in tr for sp, tr in zip(s, t)], index=df.index)
    tmp = df[["source_language", "target_language"]].copy()
    tmp["strategy"] = label
    tmp["error"] = err
    records.append(tmp)

err_df = pd.concat(records, ignore_index=True)
pair_rates = (
    err_df.groupby(["source_language", "target_language", "strategy"])["error"]
    .agg(error_rate="mean", n="count")
    .reset_index()
)
pair_rates["error_pct"] = pair_rates["error_rate"] * 100
pair_rates.to_csv(PROC / "pairwise_error_rates.csv", index=False)
print(f"  Saved → data/processed/pairwise_error_rates.csv  ({len(pair_rates)} rows)")

# Overall per-source stats
for src in ["Chinese", "Japanese", "Korean"]:
    sub = pair_rates[pair_rates["source_language"] == src]
    print(f"  {src:10s}  mean error {sub['error_pct'].mean():.2f}%  "
          f"range [{sub['error_pct'].min():.2f}–{sub['error_pct'].max():.2f}%]")

# ── Fig: pairwise error heatmap (one panel per source language) ───────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharey=False)
for ax, src in zip(axes, ["Chinese", "Japanese", "Korean"]):
    pivot = (
        pair_rates[pair_rates["source_language"] == src]
        .pivot_table(index="target_language", columns="strategy",
                     values="error_pct", aggfunc="mean")
        [["Creatively", "Analogy", "Author"]]
    )
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlOrRd",
                vmin=0, vmax=12, linewidths=0.4,
                cbar_kws={"label": "Error rate (%)"}, ax=ax)
    ax.set_title(f"Source: {src}", fontweight="bold")
    ax.set_xlabel("Strategy")
    ax.set_ylabel("Target language" if ax is axes[0] else "")
fig.suptitle("Span Containment Error Rate (%) by Source–Target Pair",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "pairwise_error_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/pairwise_error_heatmap.png")

# ── 12.2  Script-family effects ───────────────────────────────────────────────
print("\n── 12.2  Script-family effects ─────────────────────────────────────────")

df["script_family"] = df["target_language"].map(SCRIPT_FAMILY)

# Compute span ratio per strategy
for tcol, scol, label in STRATEGY_COLS:
    tl = df[tcol].str.len().replace(0, np.nan)
    sl = df[scol].str.len()
    df[f"span_ratio_{label}"] = sl / tl
    df[f"trans_len_{label}"]  = tl

sf_stats_rows = []
for family, grp in df.groupby("script_family"):
    row = {"script_family": family, "n_rows": len(grp)}
    for _, _, label in STRATEGY_COLS:
        row[f"span_ratio_med_{label}"] = grp[f"span_ratio_{label}"].median()
        row[f"trans_len_med_{label}"]  = grp[f"trans_len_{label}"].median()
    # error rate from pair_rates
    targets = grp["target_language"].unique()
    sub = pair_rates[pair_rates["target_language"].isin(targets)]
    row["error_pct_mean"] = sub["error_pct"].mean()
    sf_stats_rows.append(row)

sf_stats = pd.DataFrame(sf_stats_rows).sort_values("script_family")
sf_stats.to_csv(PROC / "script_family_stats.csv", index=False)
print(sf_stats[["script_family", "n_rows", "span_ratio_med_Creatively",
                "trans_len_med_Creatively", "error_pct_mean"]].to_string(index=False))
print("  Saved → data/processed/script_family_stats.csv")

# ── Fig: script family span ratio + error rate ────────────────────────────────
families = sf_stats["script_family"].tolist()
x = np.arange(len(families))
width = 0.25

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: median span ratio per strategy
for i, (_, _, label) in enumerate(STRATEGY_COLS):
    axes[0].bar(x + i * width,
                sf_stats[f"span_ratio_med_{label}"],
                width, label=label, color=COLORS[i], alpha=0.85)
axes[0].set_xticks(x + width)
axes[0].set_xticklabels(families, rotation=15, ha="right")
axes[0].set_ylabel("Median span / translation ratio")
axes[0].set_title("Span Ratio by Script Family & Strategy", fontweight="bold")
axes[0].legend()
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.2f}"))

# Right: mean error rate per script family
bar_colors = {"Latin": "#4C72B0", "Cyrillic": "#DD8452",
              "Arabic": "#55A868", "Indic": "#C44E52"}
axes[1].bar(families,
            sf_stats["error_pct_mean"],
            color=[bar_colors.get(f, "#AEB6BF") for f in families],
            alpha=0.85)
axes[1].set_ylabel("Mean error rate (%)")
axes[1].set_title("Span Error Rate by Script Family", fontweight="bold")
axes[1].set_xticklabels(families, rotation=15, ha="right")
for i, v in enumerate(sf_stats["error_pct_mean"]):
    axes[1].text(i, v + 0.05, f"{v:.1f}%", ha="center", fontsize=9)

fig.tight_layout()
fig.savefig(FIG / "script_family_stats.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/script_family_stats.png")

# ── 12.3  Strategy consistency across source languages ────────────────────────
print("\n── 12.3  Strategy consistency across source languages ──────────────────")

consistency_rows = []
for tgt, grp in df.groupby("target_language"):
    for _, _, label in STRATEGY_COLS:
        col = f"trans_len_{label}"
        for src, sgrp in grp.groupby("source_language"):
            med = sgrp[col].dropna().median()
            std = sgrp[col].dropna().std()
            consistency_rows.append({
                "target_language": tgt,
                "strategy": label,
                "source_language": src,
                "median_len": med,
                "std_len": std,
            })

cons_df = pd.DataFrame(consistency_rows)
cons_df.to_csv(PROC / "strategy_source_consistency.csv", index=False)
print(f"  Saved → data/processed/strategy_source_consistency.csv  ({len(cons_df)} rows)")

# ANOVA: does source language significantly affect translation length per strategy?
print("\n  One-way ANOVA (source language effect on translation length):")
for _, _, label in STRATEGY_COLS:
    col = f"trans_len_{label}"
    groups = [df[df["source_language"] == s][col].dropna().sample(
                  min(10000, len(df[df["source_language"] == s])), random_state=0)
              for s in ["Chinese", "Japanese", "Korean"]]
    F, p = f_oneway(*groups)
    print(f"  {label:<14}  F={F:.1f}  p={p:.2e}")

# ── Fig: strategy consistency across source languages ─────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=False)
for ax, (_, _, label) in zip(axes, STRATEGY_COLS):
    pivot = cons_df[cons_df["strategy"] == label].pivot(
        index="target_language", columns="source_language", values="median_len"
    )[["Chinese", "Japanese", "Korean"]]
    order = pivot.mean(axis=1).sort_values().index
    pivot = pivot.loc[order]
    pivot.plot(kind="barh", ax=ax,
               color=[SOURCE_COLORS["Chinese"], SOURCE_COLORS["Japanese"],
                      SOURCE_COLORS["Korean"]],
               alpha=0.85, width=0.7)
    ax.set_title(f"Strategy: {label}", fontweight="bold")
    ax.set_xlabel("Median translation length (chars)")
    ax.set_ylabel("Target language" if ax is axes[0] else "")
    ax.legend(title="Source")
fig.suptitle("Translation Length by Source Language — Strategy Consistency",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "strategy_source_consistency.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/strategy_source_consistency.png")

print("\nDone.")
