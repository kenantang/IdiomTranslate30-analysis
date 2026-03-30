"""
Part 13: Extended Cognate Analysis.

Extends the pairwise ZH–KO / ZH–JA / JA–KO cognate work with two new analyses:
  13.1  Three-way cognate detection — idioms with cognate links across all three
        source languages simultaneously (ZH–JA and ZH–KO and JA–KO).
  13.2  Low-divergence cognate pair ranking — which ZH–KO pairs produce the most
        similar translations across all 10 target languages, and what properties
        do they share?

Outputs
-------
data/processed/triple_cognates.csv            – three-way cognate triples with match types
data/processed/cognate_divergence_ranking.csv – ZH–KO pairs ranked by mean edit distance
figures/triple_cognate_overlap.png
figures/cognate_divergence_distribution.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from utils import STRATEGY_COLORS as COLORS, SOURCE_COLORS, COGNATE_COLORS

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ── Load cognate pair tables ───────────────────────────────────────────────────
zhko = pd.read_csv(PROC / "cjk_cognate_pairs.csv")     # zh_idiom, ko_idiom, match_type
zhja = pd.read_csv(PROC / "zhja_cognate_pairs.csv")     # zh_idiom, ja_idiom, match_type
koja = pd.read_csv(PROC / "koja_cognate_pairs.csv")     # ja_idiom, ko_idiom, match_type

print(f"ZH–KO pairs : {len(zhko):,}  ({(zhko.match_type=='exact_4/4').sum()} exact)")
print(f"ZH–JA pairs : {len(zhja):,}  ({(zhja.match_type=='exact_4/4').sum()} exact)")
print(f"JA–KO pairs : {len(koja):,}  ({(koja.match_type=='exact_4/4').sum()} exact)")

# ── 13.1  Three-way cognate detection ─────────────────────────────────────────
print("\n── 13.1  Three-way cognate detection ────────────────────────────────────")

# Step 1: find ZH idioms that have both a JA and a KO cognate
zh_in_zhko = set(zhko["zh_idiom"])
zh_in_zhja = set(zhja["zh_idiom"])
zh_both    = zh_in_zhko & zh_in_zhja

# Step 2: for each such ZH idiom, get its JA cognate(s) and check if that JA
# idiom also has a KO cognate in koja
triples = []
for zh in sorted(zh_both):
    ja_rows = zhja[zhja["zh_idiom"] == zh]
    ko_rows = zhko[zhko["zh_idiom"] == zh]
    for _, jrow in ja_rows.iterrows():
        ja = jrow["ja_idiom"]
        koja_match = koja[koja["ja_idiom"] == ja]
        if koja_match.empty:
            continue
        for _, krow in ko_rows.iterrows():
            ko = krow["ko_idiom"]
            koja_direct = koja_match[koja_match["ko_idiom"] == ko]
            if not koja_direct.empty:
                triples.append({
                    "zh_idiom":    zh,
                    "ja_idiom":    ja,
                    "ko_idiom":    ko,
                    "zhja_match":  jrow["match_type"],
                    "zhko_match":  krow["match_type"],
                    "koja_match":  koja_direct.iloc[0]["match_type"],
                    "all_exact":   (jrow["match_type"] == "exact_4/4" and
                                   krow["match_type"] == "exact_4/4" and
                                   koja_direct.iloc[0]["match_type"] == "exact_4/4"),
                })

triples_df = pd.DataFrame(triples)
triples_df.to_csv(PROC / "triple_cognates.csv", index=False)

n_triples  = len(triples_df)
n_exact3   = triples_df["all_exact"].sum() if not triples_df.empty else 0
print(f"  Three-way cognate triples : {n_triples}")
print(f"  All-exact triples         : {n_exact3}")
if not triples_df.empty:
    print(f"\n  Sample triples:")
    print(triples_df.head(10)[["zh_idiom","ja_idiom","ko_idiom","zhja_match","zhko_match"]].to_string(index=False))
print(f"  Saved → data/processed/triple_cognates.csv")

# ── Fig: Venn-style overlap diagram ───────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: try venn3, fall back to bar chart
labels = ["ZH–KO only", "ZH–JA only", "ZH in both\n(no triple link)",
          "Three-way triples"]
vals = [
    len(zh_in_zhko - zh_in_zhja),
    len(zh_in_zhja - zh_in_zhko),
    len(zh_both) - n_triples,
    n_triples,
]
axes[0].bar(labels, vals,
            color=[SOURCE_COLORS["Korean"], SOURCE_COLORS["Japanese"],
                   "#8172B2", "#C44E52"],
            alpha=0.85)
axes[0].set_ylabel("Number of ZH idioms")
axes[0].set_title("ZH Idiom Overlap Across Pairwise Cognate Sets",
                  fontweight="bold")
for i, v in enumerate(vals):
    axes[0].text(i, v + 0.5, str(v), ha="center", fontsize=10)

# Right: match-type breakdown for triples
if not triples_df.empty:
    match_counts = triples_df.groupby(["zhja_match", "zhko_match"]).size().reset_index(name="count")
    axes[1].barh(
        [f"{r.zhja_match} / {r.zhko_match}" for _, r in match_counts.iterrows()],
        match_counts["count"],
        color=["#4C72B0" if "exact" in str(r.zhja_match) else "#DD8452"
               for _, r in match_counts.iterrows()],
        alpha=0.85,
    )
    axes[1].set_xlabel("Number of triples")
    axes[1].set_title("Match Type Distribution in Three-way Triples\n(ZH–JA / ZH–KO)",
                      fontweight="bold")
else:
    axes[1].text(0.5, 0.5, "No triples found", ha="center", va="center",
                 transform=axes[1].transAxes, fontsize=14)
    axes[1].set_title("Three-way Triples: Match Types", fontweight="bold")

fig.tight_layout()
fig.savefig(FIG / "triple_cognate_overlap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/triple_cognate_overlap.png")

# ── 13.2  Low-divergence cognate pair ranking ─────────────────────────────────
print("\n── 13.2  Low-divergence cognate pair ranking ─────────────────────────────")

div = pd.read_parquet(PROC / "divergence_scores.parquet")
# div columns: idiom, source_language, target_language, div_CA_ng1, div_CAu_ng1,
#              div_AAu_ng1, edit_CA, edit_CAu, edit_AAu

# For each (idiom, source_language), compute mean edit distance across all targets
div_mean = (
    div.groupby(["idiom", "source_language"])[["edit_CA", "edit_CAu", "edit_AAu"]]
    .mean()
    .assign(edit_mean=lambda d: d[["edit_CA","edit_CAu","edit_AAu"]].mean(axis=1))
    .reset_index()
)

# Merge ZH–KO pairs with divergence for both ZH and KO idioms
zhko_div = (
    zhko
    .merge(div_mean[div_mean["source_language"] == "Chinese"]
               .rename(columns={"idiom": "zh_idiom", "edit_mean": "edit_zh"}),
           on="zh_idiom", how="inner")
    .merge(div_mean[div_mean["source_language"] == "Korean"]
               .rename(columns={"idiom": "ko_idiom", "edit_mean": "edit_ko"}),
           on="ko_idiom", how="inner")
)
zhko_div["edit_pair_mean"] = (zhko_div["edit_zh"] + zhko_div["edit_ko"]) / 2
zhko_div_sorted = zhko_div.sort_values("edit_pair_mean").reset_index(drop=True)

# Save full ranking
save_cols = ["zh_idiom", "ko_idiom", "match_type", "edit_zh", "edit_ko", "edit_pair_mean"]
zhko_div_sorted[save_cols].to_csv(PROC / "cognate_divergence_ranking.csv", index=False)
print(f"  Total ZH–KO pairs with divergence data: {len(zhko_div_sorted)}")
print(f"\n  10 lowest-divergence pairs (most convergent translations):")
print(zhko_div_sorted.head(10)[save_cols].to_string(index=False))
print(f"\n  10 highest-divergence pairs:")
print(zhko_div_sorted.tail(10)[save_cols].to_string(index=False))
print(f"  Saved → data/processed/cognate_divergence_ranking.csv")

# Also compute for triples if they exist
if not triples_df.empty:
    triple_div = (
        triples_df
        .merge(div_mean[div_mean["source_language"] == "Chinese"]
                   .rename(columns={"idiom":"zh_idiom","edit_mean":"edit_zh"}),
               on="zh_idiom", how="left")
        .merge(div_mean[div_mean["source_language"] == "Japanese"]
                   .rename(columns={"idiom":"ja_idiom","edit_mean":"edit_ja"}),
               on="ja_idiom", how="left")
        .merge(div_mean[div_mean["source_language"] == "Korean"]
                   .rename(columns={"idiom":"ko_idiom","edit_mean":"edit_ko"}),
               on="ko_idiom", how="left")
    )
    triple_div["edit_triple_mean"] = triple_div[["edit_zh","edit_ja","edit_ko"]].mean(axis=1)
    print(f"\n  Mean edit distance in triples: {triple_div['edit_triple_mean'].mean():.3f}")
    print(f"  vs all ZH–KO pairs:            {zhko_div['edit_pair_mean'].mean():.3f}")

# ── Fig: divergence distribution ─────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: histogram of pair-level divergence
axes[0].hist(zhko_div_sorted["edit_pair_mean"].dropna(), bins=30,
             color="#4C72B0", alpha=0.8, edgecolor="white")
axes[0].axvline(zhko_div_sorted["edit_pair_mean"].median(), color="#C44E52",
                linestyle="--", lw=1.5, label=f"Median={zhko_div_sorted['edit_pair_mean'].median():.2f}")
axes[0].set_xlabel("Mean edit distance (averaged across ZH and KO)")
axes[0].set_ylabel("Number of ZH–KO cognate pairs")
axes[0].set_title("Distribution of Translation Divergence\nacross ZH–KO Cognate Pairs",
                  fontweight="bold")
axes[0].legend()

# Right: scatter ZH divergence vs KO divergence, coloured by match type
colors_map = {"exact_4/4": "#4C72B0", "near_3/4": "#DD8452"}
for mtype, grp in zhko_div_sorted.groupby("match_type"):
    axes[1].scatter(grp["edit_zh"], grp["edit_ko"],
                    c=colors_map.get(mtype, "#AEB6BF"),
                    alpha=0.5, s=25, label=mtype)
axes[1].plot([0.3, 0.9], [0.3, 0.9], "k--", lw=1, alpha=0.4, label="y=x")
axes[1].set_xlabel("ZH translation divergence (mean edit)")
axes[1].set_ylabel("KO translation divergence (mean edit)")
axes[1].set_title("Per-Pair Divergence: ZH vs KO Source\nColoured by Match Type",
                  fontweight="bold")
axes[1].legend()

fig.tight_layout()
fig.savefig(FIG / "cognate_divergence_distribution.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/cognate_divergence_distribution.png")

print("\nDone.")
