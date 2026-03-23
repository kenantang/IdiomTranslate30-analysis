"""
Basic statistics for the IdiomTranslate30 dataset.
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "raw" / "IdiomTranslate30.parquet"

def main():
    print("Loading dataset...")
    df = pd.read_parquet(DATA_PATH)

    # ── Shape ──────────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SHAPE")
    print(f"{'='*60}")
    print(f"Rows:    {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    # ── Columns & dtypes ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("COLUMNS & DTYPES")
    print(f"{'='*60}")
    print(df.dtypes.to_string())

    # ── Missing values ─────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("MISSING VALUES")
    print(f"{'='*60}")
    missing = df.isnull().sum()
    if missing.any():
        print(missing[missing > 0].to_string())
    else:
        print("No missing values.")

    # ── Language pair distribution ─────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SOURCE LANGUAGE DISTRIBUTION")
    print(f"{'='*60}")
    src_counts = df["source_language"].value_counts()
    for lang, count in src_counts.items():
        print(f"  {lang:<20} {count:>10,}  ({count/len(df)*100:.1f}%)")

    print(f"\n{'='*60}")
    print("TARGET LANGUAGE DISTRIBUTION")
    print(f"{'='*60}")
    tgt_counts = df["target_language"].value_counts()
    for lang, count in tgt_counts.items():
        print(f"  {lang:<20} {count:>10,}  ({count/len(df)*100:.1f}%)")

    # ── Language pair counts ───────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("LANGUAGE PAIR COUNTS (src → tgt)")
    print(f"{'='*60}")
    pair_counts = df.groupby(["source_language", "target_language"]).size().reset_index(name="count")
    pair_counts = pair_counts.sort_values("count", ascending=False)
    for _, row in pair_counts.iterrows():
        print(f"  {row['source_language']:<15} → {row['target_language']:<15} {row['count']:>10,}")

    # ── Unique idioms ──────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("IDIOMS")
    print(f"{'='*60}")
    total_unique = df["idiom"].nunique()
    print(f"Total unique idioms: {total_unique:,}")

    print("\nUnique idioms per source language:")
    for lang, grp in df.groupby("source_language"):
        print(f"  {lang:<20} {grp['idiom'].nunique():>6,}")

    print("\nTop 10 most frequent idioms (across all language pairs):")
    top_idioms = df["idiom"].value_counts().head(10)
    for idiom, count in top_idioms.items():
        print(f"  {idiom:<20} {count:>8,}")

    # ── Sentence / translation length stats ────────────────────────────────────
    text_cols = [
        "sentence",
        "translate_creatively",
        "translate_analogy",
        "translate_author",
    ]
    print(f"\n{'='*60}")
    print("TEXT LENGTH STATISTICS (characters)")
    print(f"{'='*60}")
    for col in text_cols:
        lengths = df[col].str.len()
        print(f"\n  {col}")
        print(f"    min={lengths.min():>6}  p25={lengths.quantile(0.25):>7.1f}"
              f"  median={lengths.median():>7.1f}  mean={lengths.mean():>7.1f}"
              f"  p75={lengths.quantile(0.75):>7.1f}  p95={lengths.quantile(0.95):>8.1f}"
              f"  max={lengths.max():>7}")

    # ── Empty / very short translations ───────────────────────────────────────
    print(f"\n{'='*60}")
    print("EMPTY OR VERY SHORT TRANSLATIONS (len < 5)")
    print(f"{'='*60}")
    for col in ["translate_creatively", "translate_analogy", "translate_author"]:
        short = (df[col].str.len() < 5).sum()
        print(f"  {col:<30} {short:>8,}  ({short/len(df)*100:.3f}%)")

    # ── Sample rows ────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SAMPLE ROWS (2 random rows)")
    print(f"{'='*60}")
    sample = df.sample(2, random_state=42)
    for i, (_, row) in enumerate(sample.iterrows(), 1):
        print(f"\n--- Sample {i} ---")
        for col in df.columns:
            val = str(row[col])
            if len(val) > 200:
                val = val[:200] + "..."
            print(f"  {col}: {val}")


if __name__ == "__main__":
    main()
