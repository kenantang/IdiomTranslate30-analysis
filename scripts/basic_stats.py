"""
Basic statistics for the IdiomTranslate30 dataset.

Outputs
-------
data/processed/basic_stats.json  – row counts, language distributions, idiom counts,
                                    translation length stats, missing values, doubled
                                    idioms, and long-translation inventory.
figures/fig1_language_distribution.png
figures/fig2_idiom_coverage.png
figures/fig5_sentence_length_by_source.png
"""
import json
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path

ROOT      = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
PROC      = ROOT / "data" / "processed"
FIG       = ROOT / "figures"
PROC.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
STRATEGY_COLORS = ["#4C72B0", "#DD8452", "#55A868"]
TRANS_COLS      = ["translate_creatively", "translate_analogy", "translate_author"]
TRANS_LABELS    = ["Creatively", "Analogy", "Author"]
LONG_THRESH     = 500


def main():
    print("Loading dataset...")
    df = pd.read_parquet(DATA_PATH)
    n_rows = len(df)
    print(f"  {n_rows:,} rows × {len(df.columns)} columns")

    # ── Shape ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}\nSHAPE\n{'='*60}")
    print(f"Rows:    {n_rows:,}")
    print(f"Columns: {len(df.columns)}")

    # ── Columns & dtypes ───────────────────────────────────────────────────────
    print(f"\n{'='*60}\nCOLUMNS & DTYPES\n{'='*60}")
    print(df.dtypes.to_string())

    # ── Missing values ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}\nMISSING VALUES\n{'='*60}")
    missing = df.isnull().sum()
    if missing.any():
        print(missing[missing > 0].to_string())
    else:
        print("No missing values.")

    # ── Language distributions ─────────────────────────────────────────────────
    print(f"\n{'='*60}\nSOURCE LANGUAGE DISTRIBUTION\n{'='*60}")
    src_counts = df["source_language"].value_counts()
    for lang, count in src_counts.items():
        print(f"  {lang:<20} {count:>10,}  ({count/n_rows*100:.1f}%)")

    print(f"\n{'='*60}\nTARGET LANGUAGE DISTRIBUTION\n{'='*60}")
    tgt_counts = df["target_language"].value_counts()
    for lang, count in tgt_counts.items():
        print(f"  {lang:<20} {count:>10,}  ({count/n_rows*100:.1f}%)")

    # ── Language pair counts ───────────────────────────────────────────────────
    print(f"\n{'='*60}\nLANGUAGE PAIR COUNTS (src → tgt)\n{'='*60}")
    pair_counts = (
        df.groupby(["source_language", "target_language"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    for _, row in pair_counts.iterrows():
        print(f"  {row['source_language']:<15} → {row['target_language']:<15} {row['count']:>10,}")

    # ── Unique idioms ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}\nIDIOMS\n{'='*60}")
    n_idioms = df["idiom"].nunique()
    print(f"Total unique idioms: {n_idioms:,}")
    idiom_per_src = {}
    for lang, grp in df.groupby("source_language"):
        c = grp["idiom"].nunique()
        idiom_per_src[lang] = c
        print(f"  {lang:<20} {c:>6,}")

    # ── Translation length stats ────────────────────────────────────────────────
    text_cols = ["sentence"] + TRANS_COLS
    print(f"\n{'='*60}\nTEXT LENGTH STATISTICS (characters)\n{'='*60}")
    len_stats = {}
    for col in text_cols:
        lengths = df[col].str.len()
        stats = {
            "min": int(lengths.min()),
            "p25": float(lengths.quantile(0.25)),
            "median": float(lengths.median()),
            "mean": float(lengths.mean()),
            "p75": float(lengths.quantile(0.75)),
            "p95": float(lengths.quantile(0.95)),
            "max": int(lengths.max()),
        }
        len_stats[col] = stats
        print(f"\n  {col}")
        print(f"    min={stats['min']:>6}  p25={stats['p25']:>7.1f}"
              f"  median={stats['median']:>7.1f}  mean={stats['mean']:>7.1f}"
              f"  p75={stats['p75']:>7.1f}  p95={stats['p95']:>8.1f}  max={stats['max']:>7}")

    # ── Short translations ─────────────────────────────────────────────────────
    print(f"\n{'='*60}\nEMPTY OR VERY SHORT TRANSLATIONS (len < 5)\n{'='*60}")
    for col in TRANS_COLS:
        short = int((df[col].str.len() < 5).sum())
        print(f"  {col:<30} {short:>8,}  ({short/n_rows*100:.3f}%)")

    # ── Doubled idioms ─────────────────────────────────────────────────────────
    grp_sizes = df.groupby(["source_language", "idiom", "target_language"]).size()
    doubled_idioms = sorted(
        grp_sizes[grp_sizes == 20].reset_index()["idiom"].unique().tolist()
    )
    print(f"\n{'='*60}\nDOUBLED IDIOMS (20 sentences instead of 10)\n{'='*60}")
    for idiom in doubled_idioms:
        print(f"  {idiom}")

    # ── Long translations ──────────────────────────────────────────────────────
    long_rows = []
    for col, label in zip(TRANS_COLS, TRANS_LABELS):
        mask = df[col].str.len() > LONG_THRESH
        for _, r in df[mask].iterrows():
            long_rows.append({
                "strategy": label,
                "idiom": r["idiom"],
                "source_language": r["source_language"],
                "target_language": r["target_language"],
                "length": int(len(str(r[col]))),
            })
    n_long = {lbl: int((df[col].str.len() > LONG_THRESH).sum())
              for col, lbl in zip(TRANS_COLS, TRANS_LABELS)}
    print(f"\n{'='*60}\nLONG TRANSLATIONS (> {LONG_THRESH} chars)\n{'='*60}")
    for lbl, n in n_long.items():
        print(f"  {lbl:<14} {n}")

    # ── Sample rows ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}\nSAMPLE ROWS (2 random rows)\n{'='*60}")
    for i, (_, row) in enumerate(df.sample(2, random_state=42).iterrows(), 1):
        print(f"\n--- Sample {i} ---")
        for col in df.columns:
            val = str(row[col])
            if len(val) > 200:
                val = val[:200] + "..."
            print(f"  {col}: {val}")

    # ── Save processed output ──────────────────────────────────────────────────
    out = {
        "n_rows": n_rows,
        "n_columns": len(df.columns),
        "n_unique_idioms": n_idioms,
        "total_missing_spans": int(df[["span_creatively", "span_analogy", "span_author"]].isnull().sum().sum()),
        "source_language_counts": {k: int(v) for k, v in src_counts.items()},
        "target_language_counts": {k: int(v) for k, v in tgt_counts.items()},
        "idioms_per_source_language": idiom_per_src,
        "length_stats": len_stats,
        "long_translation_threshold": LONG_THRESH,
        "long_translation_counts": n_long,
        "long_translation_rows": long_rows,
        "doubled_idioms": doubled_idioms,
    }
    out_path = PROC / "basic_stats.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\nSaved → {out_path}")

    # ── Fig 1: language distribution (source + target) ─────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))

    axes[0].bar(src_counts.index, src_counts.values, color=STRATEGY_COLORS[:3])
    axes[0].set_title("Source Language Distribution")
    axes[0].set_ylabel("Number of rows")
    axes[0].yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    for bar, val in zip(axes[0].patches, src_counts.values):
        axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 4000,
                     f"{val:,}", ha="center", va="bottom", fontsize=9)

    colors_10 = sns.color_palette("muted", 10)
    axes[1].barh(tgt_counts.index[::-1], tgt_counts.values[::-1], color=colors_10)
    axes[1].set_title("Target Language Distribution")
    axes[1].set_xlabel("Number of rows")
    axes[1].xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    for bar in axes[1].patches:
        axes[1].text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                     f"{int(bar.get_width()):,}", va="center", fontsize=8)

    fig.suptitle("Dataset Composition by Language", fontsize=13, fontweight="bold")
    fig.tight_layout()
    fig.savefig(FIG / "fig1_language_distribution.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved → figures/fig1_language_distribution.png")

    # ── Fig 2: idiom coverage per source language ──────────────────────────────
    idiom_counts = df.groupby("source_language")["idiom"].nunique()
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(idiom_counts.index, idiom_counts.values,
                  color=STRATEGY_COLORS[:3], width=0.5)
    ax.set_title("Unique Idioms per Source Language", fontsize=13, fontweight="bold")
    ax.set_ylabel("Unique idiom count")
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    for bar, val in zip(bars, idiom_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                f"{val:,}", ha="center", va="bottom", fontsize=10)
    ax.set_ylim(0, idiom_counts.max() * 1.15)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_idiom_coverage.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved → figures/fig2_idiom_coverage.png")

    # ── Fig 5: sentence length distribution by source language ────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    for lang, color in zip(df["source_language"].unique(), STRATEGY_COLORS):
        lengths = df.loc[df["source_language"] == lang, "sentence"].str.len()
        ax.hist(lengths, bins=50, alpha=0.6, label=lang, color=color, density=True)
    ax.set_title("Source Sentence Length Distribution by Language",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Character count")
    ax.set_ylabel("Density")
    ax.legend(title="Source Language")
    fig.tight_layout()
    fig.savefig(FIG / "fig5_sentence_length_by_source.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved → figures/fig5_sentence_length_by_source.png")


if __name__ == "__main__":
    main()
