"""Classify span-not-in-translation errors."""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")

PAIRS  = [("translate_creatively","span_creatively"),
          ("translate_analogy",   "span_analogy"),
          ("translate_author",    "span_author")]
LABELS = ["Creatively", "Analogy", "Author"]

def classify_mismatch(trans, span):
    """Return error category for a span not contained in translation."""
    if pd.isna(span) or pd.isna(trans):
        return "missing"
    span, trans = str(span), str(trans)
    if span in trans:
        return "ok"                              # should not happen here
    if span.strip() in trans:
        return "leading/trailing whitespace"
    if span.lower() in trans.lower():
        return "case mismatch"
    # Remove punctuation from both and test
    def strip_punct(s):
        return "".join(c for c in s if not unicodedata.category(c).startswith("P"))
    if strip_punct(span) in strip_punct(trans):
        return "punctuation difference"
    # Check if span is near-substring (first/last char differs)
    if len(span) > 2 and (span[1:] in trans or span[:-1] in trans):
        return "off-by-one boundary"
    # Shared word check
    span_words = set(span.lower().split())
    trans_words = set(trans.lower().split())
    if span_words & trans_words:
        return "partial word overlap"
    return "no overlap"

records = []
for (tc, sc), label in zip(PAIRS, LABELS):
    mask_valid = df[sc].notna() & (df[sc].str.strip().str.len() > 0)
    contained  = pd.Series(False, index=df.index)
    contained[mask_valid] = [
        s in t for s, t in zip(df.loc[mask_valid, sc], df.loc[mask_valid, tc])
    ]
    flagged = df[mask_valid & ~contained]
    print(f"{label}: {len(flagged):,} span-not-in-trans rows")
    cats = [classify_mismatch(t, s) for t, s in
            zip(flagged[tc].values, flagged[sc].values)]
    vc = pd.Series(cats).value_counts()
    for cat, n in vc.items():
        records.append({"strategy": label, "category": cat, "count": int(n)})
    print(vc.to_string())
    print()

err_df = pd.DataFrame(records)
pivot  = err_df.pivot_table(index="category", columns="strategy",
                             values="count", fill_value=0)
print("Summary table:")
print(pivot.to_string())

# Figure
fig, ax = plt.subplots(figsize=(10, 5))
pivot.plot(kind="bar", ax=ax, color=["#4C72B0","#DD8452","#55A868"], width=0.7)
ax.set_title("Span-Not-in-Translation Error Classification", fontweight="bold")
ax.set_ylabel("Number of rows")
ax.set_xlabel("")
ax.tick_params(axis="x", rotation=30)
ax.legend(title="Strategy")
fig.tight_layout()
fig.savefig(FIG / "span_error_types.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/span_error_types.png")

# Save to CSV for inspection
err_df.to_csv(ROOT / "data/audit/span_error_classification.csv", index=False)
print("Saved → data/audit/span_error_classification.csv")
