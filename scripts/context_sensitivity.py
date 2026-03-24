"""
Context sensitivity and span reuse within idiom.

For each (idiom, target_language, strategy):
  - CV of translation length across the 10 context sentences
  - Mean pairwise Jaccard between the 10 translations (word-level)
  - Number of unique spans / total spans (span reuse rate)

High CV / high Jaccard-diversity → model uses context.
Low CV / low Jaccard-diversity  → model ignores context, fixed rendering.

Outputs:
  data/processed/context_sensitivity.parquet
  figures/context_sensitivity.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).parent.parent
PROC = ROOT / "data/processed"
FIG  = ROOT / "figures"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
SCOLS  = ["span_creatively",      "span_analogy",      "span_author"]
LABELS = ["Creatively", "Analogy", "Author"]
LONG_THRESH = 500   # preprocessing: exclude pathologically long translations

print("Loading data…")
df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")

# Apply per-strategy length filter
for tc in TCOLS:
    mask = df[tc].str.len() > LONG_THRESH
    df.loc[mask, tc] = np.nan

# ── Compute per-group metrics ──────────────────────────────────────────────
def mean_pairwise_jaccard(texts):
    """Mean Jaccard over all C(n,2) pairs of word sets."""
    word_sets = [set(str(t).lower().split()) for t in texts if pd.notna(t)]
    if len(word_sets) < 2:
        return np.nan
    scores = []
    for a, b in combinations(word_sets, 2):
        u = a | b
        scores.append(len(a & b) / len(u) if u else 0.0)
    return float(np.mean(scores))

def span_unique_frac(spans):
    """Fraction of unique span values (1 = all same, high = all different)."""
    valid = [str(s) for s in spans if pd.notna(s) and str(s).strip()]
    if not valid:
        return np.nan
    return len(set(valid)) / len(valid)

print("Computing group-level metrics…")
records = []
groups = df.groupby(["source_language", "idiom", "target_language"])
n_groups = len(groups)
for i, ((src, idiom, tgt), grp) in enumerate(groups):
    if i % 10000 == 0:
        print(f"  {i:,}/{n_groups:,}")
    rec = {"source_language": src, "idiom": idiom, "target_language": tgt,
           "n_sentences": len(grp)}
    for tc, sc, lbl in zip(TCOLS, SCOLS, LABELS):
        lens = grp[tc].str.len().dropna()
        rec[f"cv_{lbl}"]          = (lens.std() / lens.mean()) if lens.mean() > 0 and len(lens) > 1 else np.nan
        rec[f"jaccard_div_{lbl}"] = mean_pairwise_jaccard(grp[tc].dropna().tolist())
        rec[f"span_uniq_{lbl}"]   = span_unique_frac(grp[sc].tolist())
    records.append(rec)

sens = pd.DataFrame(records)
sens.to_parquet(PROC / "context_sensitivity.parquet", index=False)
print(f"Saved {len(sens):,} group rows → data/processed/context_sensitivity.parquet")

# ── Summary statistics ─────────────────────────────────────────────────────
print("\n=== CV of translation length (proxy: context sensitivity) ===")
for lbl in LABELS:
    col = f"cv_{lbl}"
    v   = sens[col].dropna()
    print(f"  {lbl:<14}  mean={v.mean():.4f}  median={v.median():.4f}  "
          f"p25={v.quantile(.25):.4f}  p75={v.quantile(.75):.4f}")
    # Fraction with CV=0 (perfectly fixed length)
    print(f"               CV=0: {(v==0).mean()*100:.1f}%   "
          f"CV>0.1: {(v>0.1).mean()*100:.1f}%")

print("\n=== Mean pairwise Jaccard diversity (high = more varied wording) ===")
for lbl in LABELS:
    col = f"jaccard_div_{lbl}"
    v   = sens[col].dropna()
    print(f"  {lbl:<14}  mean={v.mean():.4f}  median={v.median():.4f}")

print("\n=== Span uniqueness fraction ===")
for lbl in LABELS:
    col = f"span_uniq_{lbl}"
    v   = sens[col].dropna()
    fully_converged = (v <= 1/10 + 1e-9).mean() * 100
    all_diff        = (v >= 1.0).mean() * 100
    print(f"  {lbl:<14}  mean={v.mean():.3f}  "
          f"fully-converged (1 unique span): {fully_converged:.1f}%  "
          f"all-different: {all_diff:.1f}%")

# Cross-source comparison: does source language affect sensitivity?
print("\n=== CV by source language (Creatively) ===")
print(sens.groupby("source_language")["cv_Creatively"].mean().round(4).to_string())

# ── Figures ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(17, 10))

# Row 0: CV distributions
for ax, lbl in zip(axes[0], LABELS):
    data = {src: sens[sens.source_language==src][f"cv_{lbl}"].dropna()
            for src in ["Chinese","Japanese","Korean"]}
    ax.hist(data["Chinese"],  bins=60, alpha=0.55, color="#4C72B0", label="Chinese",  density=True)
    ax.hist(data["Japanese"], bins=60, alpha=0.55, color="#DD8452", label="Japanese", density=True)
    ax.hist(data["Korean"],   bins=60, alpha=0.55, color="#55A868", label="Korean",   density=True)
    ax.set_xlim(0, 0.5)
    ax.set_title(f"CV of Translation Length\n({lbl})", fontweight="bold")
    ax.set_xlabel("CV"); ax.set_ylabel("Density")
    ax.legend(fontsize=8)

# Row 1: Span reuse
ax_span = axes[1, 0]
for lbl, color in zip(LABELS, ["#4C72B0","#DD8452","#55A868"]):
    v = sens[f"span_uniq_{lbl}"].dropna()
    ax_span.hist(v, bins=20, alpha=0.55, color=color, label=lbl, density=True)
ax_span.set_title("Span Uniqueness Fraction\n(1/10 = all same, 1.0 = all different)", fontweight="bold")
ax_span.set_xlabel("Unique spans / total spans"); ax_span.set_ylabel("Density")
ax_span.legend(fontsize=8)

# Row 1 middle: Jaccard diversity by strategy (box)
ax_jacc = axes[1, 1]
jacc_data = pd.concat([
    sens[f"jaccard_div_{lbl}"].rename(lbl) for lbl in LABELS
], axis=1).melt(var_name="Strategy", value_name="Jaccard diversity")
sns.boxplot(data=jacc_data, x="Strategy", y="Jaccard diversity",
            palette={"Creatively":"#4C72B0","Analogy":"#DD8452","Author":"#55A868"},
            flierprops=dict(marker=".", alpha=0.1), ax=ax_jacc)
ax_jacc.set_title("Mean Pairwise Jaccard Diversity\nAcross 10 Context Sentences", fontweight="bold")
ax_jacc.set_xlabel("")

# Row 1 right: CV vs Jaccard scatter (Creatively, sample)
ax_sc = axes[1, 2]
sample = sens[["cv_Creatively","jaccard_div_Creatively","source_language"]].dropna().sample(
    min(5000, len(sens)), random_state=42)
for src, color in zip(["Chinese","Japanese","Korean"], ["#4C72B0","#DD8452","#55A868"]):
    sub = sample[sample.source_language==src]
    ax_sc.scatter(sub["cv_Creatively"], sub["jaccard_div_Creatively"],
                  alpha=0.15, s=4, color=color, label=src)
ax_sc.set_title("CV vs Jaccard Diversity\n(Creatively, sample)", fontweight="bold")
ax_sc.set_xlabel("CV of translation length")
ax_sc.set_ylabel("Mean pairwise Jaccard diversity")
ax_sc.legend(fontsize=8)

fig.suptitle("Context Sensitivity & Span Reuse Across 10 Context Sentences",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "context_sensitivity.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/context_sensitivity.png")
