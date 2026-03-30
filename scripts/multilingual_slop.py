"""
Part 16: Multilingual Template Analysis.

The slop/template analysis in Part 9 & 10 covers only English Analogy translations
using 8 hard-coded regex patterns.  This script extends template detection to all
10 target languages using a data-driven, language-agnostic approach:

  16.1  Over-represented Analogy bigrams — for each target language, identify
        word bigrams that appear at ≥2× the rate in Analogy vs Creatively spans.
        These are the language-specific "slop signals".
  16.2  Template rate per language — fraction of Analogy spans that contain at
        least one over-represented bigram (i.e. are "template-touched").
  16.3  Cross-language template convergence — do certain concepts (body+soul,
        light+shadow, wave+ocean) recur across languages as translation-of-
        translation artefacts?

Outputs
-------
data/processed/multilingual_template_scores.csv  – per (language, source) template rate
data/processed/multilingual_top_ngrams.csv        – top over-represented bigrams per language
figures/multilingual_template_heatmap.png
figures/multilingual_template_rates.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from utils import STRATEGY_COLORS as COLORS, SOURCE_COLORS, normalize_span

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# Minimum bigram count to be considered a candidate template
MIN_COUNT   = 30
# Minimum Analogy/Creatively frequency ratio to flag a bigram as over-represented
RATIO_THRESH = 2.5

# Latin-script languages (where word bigrams are meaningful)
LATIN_LANGS = {"English", "French", "German", "Spanish", "Italian", "Swahili"}

# ── Load data ─────────────────────────────────────────────────────────────────
print("Loading raw data …")
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
print(f"  {len(df):,} rows loaded")

# ── Helper: extract word bigrams from a span string ───────────────────────────
def _bigrams(text: str) -> list[str]:
    """Return word bigrams from *text*, lowercased."""
    tokens = re.sub(r"[^\w\s]", " ", str(text).lower()).split()
    return [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]

# ── 16.1 & 16.2  Over-represented Analogy bigrams + template rate ─────────────
print("\n── 16.1  Over-represented Analogy bigrams ───────────────────────────────")

ngram_records  = []
score_records  = []

for lang, grp in df.groupby("target_language"):
    # Normalise spans
    ana_spans  = grp["span_analogy"].dropna().apply(normalize_span).tolist()
    cre_spans  = grp["span_creatively"].dropna().apply(normalize_span).tolist()

    if lang not in LATIN_LANGS:
        # For non-Latin scripts, use character bigrams on the span itself
        ana_tok  = [s[i:i+2] for s in ana_spans for i in range(len(s)-1) if s.strip()]
        cre_tok  = [s[i:i+2] for s in cre_spans for i in range(len(s)-1) if s.strip()]
    else:
        ana_tok  = [bg for s in ana_spans  for bg in _bigrams(s)]
        cre_tok  = [bg for s in cre_spans  for bg in _bigrams(s)]

    ana_counter = Counter(ana_tok)
    cre_counter = Counter(cre_tok)

    total_ana = max(len(ana_tok), 1)
    total_cre = max(len(cre_tok), 1)

    # Find over-represented Analogy bigrams
    over = []
    for bg, cnt in ana_counter.items():
        if cnt < MIN_COUNT:
            continue
        cre_cnt = cre_counter.get(bg, 0)
        ana_freq = cnt / total_ana
        cre_freq = (cre_cnt + 1) / total_cre  # Laplace smoothing
        ratio = ana_freq / cre_freq
        if ratio >= RATIO_THRESH:
            over.append((bg, cnt, cre_cnt, ana_freq, ratio))

    over.sort(key=lambda x: -x[4])  # sort by ratio

    # Record top bigrams
    for rank, (bg, cnt, cre_cnt, freq, ratio) in enumerate(over[:20], 1):
        ngram_records.append({
            "target_language": lang,
            "rank":            rank,
            "bigram":          bg,
            "analogy_count":   cnt,
            "creatively_count": cre_cnt,
            "analogy_freq":    freq,
            "ratio":           ratio,
        })

    # Template rate = fraction of Analogy spans containing ≥1 over-represented bigram
    top_bgs = {bg for bg, *_ in over[:50]}
    if top_bgs:
        if lang not in LATIN_LANGS:
            hit = sum(
                any(s[i:i+2] in top_bgs for i in range(len(s)-1))
                for s in ana_spans if s.strip()
            )
        else:
            hit = sum(
                any(bg in top_bgs for bg in _bigrams(s))
                for s in ana_spans if s.strip()
            )
        template_rate = hit / max(len(ana_spans), 1)
    else:
        template_rate = 0.0

    # Per-source breakdown
    for src, sgrp in grp.groupby("source_language"):
        sa = sgrp["span_analogy"].dropna().apply(normalize_span).tolist()
        if top_bgs and sa:
            if lang not in LATIN_LANGS:
                h = sum(
                    any(s[i:i+2] in top_bgs for i in range(len(s)-1))
                    for s in sa if s.strip()
                )
            else:
                h = sum(any(bg in top_bgs for bg in _bigrams(s)) for s in sa if s.strip())
            src_rate = h / max(len(sa), 1)
        else:
            src_rate = 0.0
        score_records.append({
            "target_language": lang,
            "source_language": src,
            "n_analogy_spans": len(sa),
            "n_top_bigrams":   len(top_bgs),
            "template_rate":   src_rate,
            "template_rate_overall": template_rate,
        })

    n_bgs = len(top_bgs)
    print(f"  {lang:<10}  {n_bgs:3d} over-represented bigrams  "
          f"template rate={template_rate:.1%}  "
          f"top bigram: {over[0][0]!r} (ratio={over[0][4]:.1f}×)" if over else
          f"  {lang:<10}  0 over-represented bigrams")

ngram_df  = pd.DataFrame(ngram_records)
scores_df = pd.DataFrame(score_records)
ngram_df.to_csv(PROC / "multilingual_top_ngrams.csv", index=False)
scores_df.to_csv(PROC / "multilingual_template_scores.csv", index=False)
print(f"\n  Saved → data/processed/multilingual_top_ngrams.csv  ({len(ngram_df)} rows)")
print(f"  Saved → data/processed/multilingual_template_scores.csv  ({len(scores_df)} rows)")

# ── 16.3  Cross-language template convergence ──────────────────────────────────
print("\n── 16.3  Cross-language convergence check (Latin-script only) ───────────")

# For Latin-script languages, find bigrams that are in the top-50 over-represented
# list in 3+ languages simultaneously
lat_top = (
    ngram_df[ngram_df["target_language"].isin(LATIN_LANGS)]
    .groupby("bigram")["target_language"]
    .nunique()
    .reset_index(name="n_languages")
    .query("n_languages >= 3")
    .sort_values("n_languages", ascending=False)
)
print(f"\n  Bigrams over-represented in 3+ Latin-script languages:")
print(lat_top.head(20).to_string(index=False))

# ── Fig: template rate heatmap (target × source) ─────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: heatmap
pivot = scores_df.pivot_table(
    index="target_language", columns="source_language", values="template_rate"
)[["Chinese", "Japanese", "Korean"]]
tgt_order = pivot.mean(axis=1).sort_values(ascending=False).index
pivot = pivot.loc[tgt_order]

sns.heatmap(pivot, annot=True, fmt=".1%", cmap="YlOrRd",
            vmin=0, vmax=pivot.values.max() * 1.05,
            linewidths=0.4, cbar_kws={"label": "Template rate"}, ax=axes[0])
axes[0].set_title("Analogy Template Rate by\nTarget × Source Language",
                  fontweight="bold")
axes[0].set_xlabel("Source language")
axes[0].set_ylabel("Target language")

# Right: overall template rate per target, sorted
overall = scores_df.groupby("target_language")["template_rate_overall"].first().sort_values(ascending=False)
bar_colors = ["#4C72B0" if lang in LATIN_LANGS else "#DD8452"
              for lang in overall.index]
axes[1].barh(overall.index, overall.values * 100, color=bar_colors, alpha=0.85)
axes[1].set_xlabel("Template rate (%)")
axes[1].set_title("Overall Analogy Template Rate by Target Language\n"
                  "(blue=Latin-script, orange=non-Latin-script)",
                  fontweight="bold")
for i, v in enumerate(overall.values):
    axes[1].text(v * 100 + 0.1, i, f"{v:.1%}", va="center", fontsize=9)

fig.tight_layout()
fig.savefig(FIG / "multilingual_template_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\n  Saved → figures/multilingual_template_heatmap.png")

# ── Fig: top bigrams per language ─────────────────────────────────────────────
latin_ngrams = ngram_df[ngram_df["target_language"].isin(LATIN_LANGS)]
top5_per_lang = (
    latin_ngrams.groupby("target_language")
    .apply(lambda g: g.nlargest(5, "ratio"))
    .reset_index(drop=True)
)
n_langs = top5_per_lang["target_language"].nunique()
fig, axes = plt.subplots(1, n_langs, figsize=(3 * n_langs, 5), sharey=False)
if n_langs == 1:
    axes = [axes]
for ax, (lang, grp) in zip(axes, top5_per_lang.groupby("target_language")):
    grp = grp.sort_values("ratio")
    ax.barh(grp["bigram"], grp["ratio"], color="#4C72B0", alpha=0.85)
    ax.set_title(lang, fontweight="bold")
    ax.set_xlabel("Analogy/Creatively ratio")
    ax.set_ylabel("Bigram" if ax is axes[0] else "")
fig.suptitle("Top 5 Over-represented Analogy Bigrams per Latin-Script Target Language",
             fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "multilingual_template_rates.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/multilingual_template_rates.png")

print("\nDone.")
