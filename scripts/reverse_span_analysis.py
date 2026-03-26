"""
Reverse span analysis: for each target language, which spans are reused
across the most source idioms? How many idioms does each span absorb?

Output: data/processed/span_attractor_counts.parquet
        data/processed/span_top_attractors.csv
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

from utils import normalize_span

ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
OUT_PARQUET = ROOT / "data" / "processed" / "span_attractor_counts.parquet"
OUT_CSV     = ROOT / "data" / "processed" / "span_top_attractors.csv"

df = pd.read_parquet(DATA_PATH)

# Melt span columns to long format
rows = []
for strat, scol in [("Creatively", "span_creatively"),
                    ("Analogy",    "span_analogy"),
                    ("Author",     "span_author")]:
    sub = df[["source_language", "target_language", "idiom", scol]].copy()
    sub.columns = ["source_language", "target_language", "idiom", "span"]
    sub["strategy"] = strat
    rows.append(sub)
long = pd.concat(rows, ignore_index=True)
long = long.dropna(subset=["span"])
long = long[long["span"].str.strip() != ""]

# NFC-normalize then lowercase for matching (H8)
long["span_norm"] = long["span"].apply(normalize_span)

# Per (target_language, span_norm): count distinct idioms and raw occurrences
agg = (long.groupby(["target_language", "span_norm"])
       .agg(
           n_idioms    = ("idiom", "nunique"),
           n_uses      = ("idiom", "count"),
           n_creatively = ("strategy", lambda s: (s == "Creatively").sum()),
           n_analogy    = ("strategy", lambda s: (s == "Analogy").sum()),
           n_author     = ("strategy", lambda s: (s == "Author").sum()),
       )
       .reset_index()
       .sort_values(["target_language", "n_idioms"], ascending=[True, False]))

agg.to_parquet(OUT_PARQUET, index=False)
print(f"Saved → {OUT_PARQUET}")

# Top 10 attractors per language
top = (agg.groupby("target_language")
       .apply(lambda g: g.nlargest(10, "n_idioms"))
       .reset_index(drop=True))
top.to_csv(OUT_CSV, index=False)
print(f"Saved → {OUT_CSV}")

# Print summary
print("\n=== Attractor summary ===")
print(f"{'Language':<10} {'>10 idioms':>12} {'>5 idioms':>10} {'max':>6}  top span")
for lang in ["English","French","Spanish","German","Italian","Russian",
             "Arabic","Hindi","Bengali","Swahili"]:
    sub = agg[agg["target_language"] == lang]
    n_gt10 = (sub["n_idioms"] >= 10).sum()
    n_gt5  = (sub["n_idioms"] >= 5).sum()
    top1   = sub.iloc[0]
    print(f"{lang:<10} {n_gt10:>12} {n_gt5:>10} {top1['n_idioms']:>6}  '{top1['span_norm']}'"
          f" ({top1['n_uses']} uses)")
