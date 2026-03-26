"""
Data Quality Audit.

Outputs
-------
data/audit/anomalies.csv              – every flagged row with flag columns
data/processed/span_audit_summary.csv – per-check × per-strategy flag rates
figures/fig7_missing_spans.png
figures/flag_rates.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")


import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

ROOT      = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
AUDIT_DIR = ROOT / "data" / "audit"
FIG_DIR   = ROOT / "figures"
PROC      = ROOT / "data" / "processed"
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
PROC.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

print("Loading data...")
df = pd.read_parquet(DATA_PATH)

PAIRS = [
    ("translate_creatively", "span_creatively"),
    ("translate_analogy",    "span_analogy"),
    ("translate_author",     "span_author"),
]
LABELS = ["Creatively", "Analogy", "Author"]
COLORS = ["#4C72B0", "#DD8452", "#55A868"]

flags = pd.DataFrame(index=df.index)

for (tcol, scol), label in zip(PAIRS, LABELS):
    t = df[tcol].fillna("")
    s = df[scol].fillna("")
    flags[f"missing_span_{label}"]      = df[scol].isnull()
    flags[f"empty_span_{label}"]        = (~df[scol].isnull()) & (s.str.strip().str.len() == 0)
    flags[f"span_not_in_trans_{label}"] = (~df[scol].isnull()) & (s.str.strip().str.len() > 0) & \
                                          (~df.apply(lambda r: r[scol] in r[tcol]
                                                     if pd.notna(r[scol]) else False, axis=1))
    flags[f"span_longer_{label}"]       = s.str.len() > t.str.len()
    flags[f"span_equals_idiom_{label}"] = s == df["idiom"]
    flags[f"degenerate_trans_{label}"]  = df[tcol] == df["sentence"]
    flags[f"short_trans_{label}"]       = t.str.len() < 10

# span_not_in_trans is slow row-by-row; redo with vectorized string contains
print("  Running span-containment check (vectorised)...")
for (tcol, scol), label in zip(PAIRS, LABELS):
    mask_valid = df[scol].notna() & (df[scol].str.strip().str.len() > 0)
    contained  = pd.Series(False, index=df.index)
    contained[mask_valid] = [
        span in trans
        for span, trans in zip(df.loc[mask_valid, scol], df.loc[mask_valid, tcol])
    ]
    flags[f"span_not_in_trans_{label}"] = mask_valid & ~contained

# ── Summary table ─────────────────────────────────────────────────────────────
checks = [
    "missing_span", "empty_span", "span_not_in_trans",
    "span_longer", "span_equals_idiom", "degenerate_trans", "short_trans",
]
records = []
for check in checks:
    for label in LABELS:
        col = f"{check}_{label}"
        if col in flags.columns:
            n = flags[col].sum()
            records.append({"check": check, "strategy": label,
                            "n_flagged": int(n), "pct": n / len(df) * 100})

summary = pd.DataFrame(records)
print("\nFlag summary:")
print(summary.to_string(index=False))

# ── Save anomalies CSV ────────────────────────────────────────────────────────
any_flag = flags.any(axis=1)
anomalies = df[any_flag].copy()
flag_cols  = flags[any_flag]
anomalies = pd.concat([anomalies, flag_cols], axis=1)
anomalies.to_csv(AUDIT_DIR / "anomalies.csv", index=False)
print(f"\nAnomalous rows: {any_flag.sum():,} ({any_flag.mean()*100:.2f}%)")
print(f"Saved → data/audit/anomalies.csv")

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: flag rates per check × strategy
pivot = summary.pivot(index="check", columns="strategy", values="pct")
pivot = pivot.loc[["span_not_in_trans", "span_equals_idiom", "span_longer",
                   "missing_span", "empty_span", "degenerate_trans", "short_trans"]]
pivot.plot(kind="bar", ax=axes[0], color=COLORS, width=0.7)
axes[0].set_title("Flag Rate (%) by Check & Strategy", fontweight="bold")
axes[0].set_ylabel("% of rows flagged")
axes[0].set_xlabel("")
axes[0].tick_params(axis="x", rotation=30)
axes[0].legend(title="Strategy")
for bar in axes[0].patches:
    if bar.get_height() > 0.001:
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
                     f"{bar.get_height():.2f}%", ha="center", va="bottom", fontsize=7)

# Right: span-not-in-translation broken down by source language
for (tcol, scol), label, color in zip(PAIRS, LABELS, COLORS):
    pass  # computed above

sni_by_lang = {}
for label in LABELS:
    col = f"span_not_in_trans_{label}"
    sni_by_lang[label] = df.groupby("source_language").apply(
        lambda g, c=col: flags.loc[g.index, c].mean() * 100
    )
sni_df = pd.DataFrame(sni_by_lang)
sni_df.plot(kind="bar", ax=axes[1], color=COLORS, width=0.6)
axes[1].set_title("Span-Not-in-Translation Rate\nby Source Language & Strategy", fontweight="bold")
axes[1].set_ylabel("% of rows")
axes[1].set_xlabel("")
axes[1].tick_params(axis="x", rotation=0)
axes[1].legend(title="Strategy")

fig.tight_layout()
fig.savefig(FIG_DIR / "flag_rates.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/flag_rates.png")

# ── Fig 7: missing spans heatmap (from generate_report) ───────────────────────
SPAN_COLS   = ["span_creatively", "span_analogy", "span_author"]
missing_by_lang = df.groupby("source_language")[SPAN_COLS].apply(
    lambda g: g.isnull().sum()
)
missing_by_lang.columns = LABELS

fig, ax = plt.subplots(figsize=(7, 3))
sns.heatmap(missing_by_lang, annot=True, fmt="d", cmap="YlOrRd",
            linewidths=0.5, cbar_kws={"label": "Missing count"}, ax=ax)
ax.set_title("Missing Span Annotations by Source Language & Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("")
fig.tight_layout()
fig.savefig(FIG_DIR / "fig7_missing_spans.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/fig7_missing_spans.png")

# ── Save processed summary ─────────────────────────────────────────────────────
summary_path = PROC / "span_audit_summary.csv"
summary.to_csv(summary_path, index=False)
print(f"Saved → {summary_path}")
