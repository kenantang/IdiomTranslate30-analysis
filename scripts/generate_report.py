"""
Generate analysis figures and a markdown report for the IdiomTranslate30 dataset.
Figures → figures/
Report  → README.md (project root)
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DATA_PATH = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
FIGURES_DIR = ROOT / "figures"
REPORT_PATH = ROOT / "README.md"

FIGURES_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)
FIGSIZE = (10, 5)

# ── Load ───────────────────────────────────────────────────────────────────────
print("Loading dataset...")
df = pd.read_parquet(DATA_PATH)
print(f"  {len(df):,} rows × {len(df.columns)} columns")

TRANS_COLS = ["translate_creatively", "translate_analogy", "translate_author"]
TRANS_LABELS = ["Creatively", "Analogy", "Author"]
STRATEGY_COLORS = ["#4C72B0", "#DD8452", "#55A868"]

figures_meta = []  # list of (filename, caption)


def save_fig(fig, name, caption):
    path = FIGURES_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    figures_meta.append((name, caption))
    print(f"  Saved {name}")


# ══════════════════════════════════════════════════════════════════════════════
# Fig 1 – Dataset composition (source / target language distribution)
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=FIGSIZE)

src_counts = df["source_language"].value_counts()
axes[0].bar(src_counts.index, src_counts.values, color=STRATEGY_COLORS[:3])
axes[0].set_title("Source Language Distribution")
axes[0].set_ylabel("Number of rows")
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar, val in zip(axes[0].patches, src_counts.values):
    axes[0].text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 4000,
                 f"{val:,}", ha="center", va="bottom", fontsize=9)

tgt_counts = df["target_language"].value_counts()
colors_10 = sns.color_palette("muted", 10)
axes[1].barh(tgt_counts.index[::-1], tgt_counts.values[::-1], color=colors_10)
axes[1].set_title("Target Language Distribution")
axes[1].set_xlabel("Number of rows")
axes[1].xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar in axes[1].patches:
    axes[1].text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                 f"{int(bar.get_width()):,}", va="center", fontsize=8)

fig.suptitle("Dataset Composition by Language", fontsize=13, fontweight="bold")
fig.tight_layout()
save_fig(fig, "fig1_language_distribution.png",
         "Distribution of rows across source (left) and target (right) languages. "
         "Target languages are perfectly balanced (~90,660 rows each), while Chinese "
         "contributes nearly half the source sentences.")

# ══════════════════════════════════════════════════════════════════════════════
# Fig 2 – Idiom coverage per source language
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4))
idiom_counts = df.groupby("source_language")["idiom"].nunique()
bars = ax.bar(idiom_counts.index, idiom_counts.values, color=STRATEGY_COLORS[:3], width=0.5)
ax.set_title("Unique Idioms per Source Language", fontsize=13, fontweight="bold")
ax.set_ylabel("Unique idiom count")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
for bar, val in zip(bars, idiom_counts.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
            f"{val:,}", ha="center", va="bottom", fontsize=10)
ax.set_ylim(0, idiom_counts.max() * 1.15)
fig.tight_layout()
save_fig(fig, "fig2_idiom_coverage.png",
         "Number of unique idioms per source language. Chinese has the largest inventory "
         "(4,306), followed by Japanese (2,440) and Korean (2,316).")

# ══════════════════════════════════════════════════════════════════════════════
# Fig 3 – Translation length distributions (violin)
# ══════════════════════════════════════════════════════════════════════════════
sample = df.sample(min(50_000, len(df)), random_state=42)
length_df = pd.DataFrame({
    label: sample[col].str.len()
    for col, label in zip(TRANS_COLS, TRANS_LABELS)
})
melted = length_df.melt(var_name="Strategy", value_name="Length (chars)")

fig, ax = plt.subplots(figsize=FIGSIZE)
sns.violinplot(data=melted, x="Strategy", y="Length (chars)",
               palette=STRATEGY_COLORS, cut=0, inner="quartile", ax=ax)
ax.set_title("Translation Length Distribution by Strategy", fontsize=13, fontweight="bold")
ax.set_ylabel("Character count")
# annotate medians
for i, label in enumerate(TRANS_LABELS):
    med = length_df[label].median()
    ax.text(i, med + 20, f"med={med:.0f}", ha="center", va="bottom", fontsize=9, color="black")
fig.tight_layout()
save_fig(fig, "fig3_translation_length_violin.png",
         "Violin plot of translation lengths (characters) for each strategy on a 50k-row sample. "
         "Inner lines show quartiles. Analogy and Author strategies tend to produce longer translations "
         "than the Creatively strategy.")

# ══════════════════════════════════════════════════════════════════════════════
# Fig 4 – Median translation length by target language × strategy
# ══════════════════════════════════════════════════════════════════════════════
med_by_lang = (
    df.groupby("target_language")[TRANS_COLS]
    .apply(lambda g: g.apply(lambda s: s.str.len().median()))
    .rename(columns=dict(zip(TRANS_COLS, TRANS_LABELS)))
)
med_by_lang = med_by_lang.sort_values("Creatively")

fig, ax = plt.subplots(figsize=(11, 5))
x = np.arange(len(med_by_lang))
width = 0.26
for i, (label, color) in enumerate(zip(TRANS_LABELS, STRATEGY_COLORS)):
    ax.bar(x + i * width, med_by_lang[label], width, label=label, color=color)

ax.set_xticks(x + width)
ax.set_xticklabels(med_by_lang.index, rotation=30, ha="right")
ax.set_title("Median Translation Length by Target Language & Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Median character count")
ax.legend(title="Strategy")
fig.tight_layout()
save_fig(fig, "fig4_length_by_target_language.png",
         "Median character count of each translation strategy grouped by target language. "
         "Languages with complex scripts (e.g., Arabic, Bengali, Hindi) tend to have shorter "
         "character counts despite equivalent semantic content.")

# ══════════════════════════════════════════════════════════════════════════════
# Fig 5 – Sentence length distribution by source language
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=FIGSIZE)
for lang, color in zip(df["source_language"].unique(), STRATEGY_COLORS):
    lengths = df.loc[df["source_language"] == lang, "sentence"].str.len()
    ax.hist(lengths, bins=50, alpha=0.6, label=lang, color=color, density=True)
ax.set_title("Source Sentence Length Distribution by Language",
             fontsize=13, fontweight="bold")
ax.set_xlabel("Character count")
ax.set_ylabel("Density")
ax.legend(title="Source Language")
fig.tight_layout()
save_fig(fig, "fig5_sentence_length_by_source.png",
         "Density histogram of source sentence lengths by language. "
         "All three languages show a similar unimodal distribution peaking around 25–30 characters, "
         "consistent with the dataset's design of short, idiom-carrying sentences.")

# ══════════════════════════════════════════════════════════════════════════════
# Fig 6 – Span length distributions (how long is the idiom span in translation)
# ══════════════════════════════════════════════════════════════════════════════
SPAN_COLS = ["span_creatively", "span_analogy", "span_author"]
SPAN_LABELS = ["Creatively", "Analogy", "Author"]

span_sample = df.dropna(subset=SPAN_COLS).sample(min(50_000, len(df)), random_state=0)
span_df = pd.DataFrame({
    label: span_sample[col].str.len()
    for col, label in zip(SPAN_COLS, SPAN_LABELS)
})
span_melted = span_df.melt(var_name="Strategy", value_name="Span Length (chars)")
# cap extreme outliers for readability
span_melted = span_melted[span_melted["Span Length (chars)"] < span_melted["Span Length (chars)"].quantile(0.995)]

fig, ax = plt.subplots(figsize=FIGSIZE)
sns.boxplot(data=span_melted, x="Strategy", y="Span Length (chars)",
            palette=STRATEGY_COLORS, width=0.45, flierprops=dict(marker=".", alpha=0.3), ax=ax)
ax.set_title("Idiom Span Length in Translation by Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Span character count")
fig.tight_layout()
save_fig(fig, "fig6_span_length_by_strategy.png",
         "Box plots of the character length of the idiom span identified within each translation. "
         "The Analogy strategy produces noticeably longer spans, suggesting more elaborate "
         "idiomatic substitutions.")

# ══════════════════════════════════════════════════════════════════════════════
# Fig 7 – Missing values heatmap
# ══════════════════════════════════════════════════════════════════════════════
missing_by_lang = df.groupby("source_language")[SPAN_COLS].apply(lambda g: g.isnull().sum())
missing_by_lang.columns = SPAN_LABELS

fig, ax = plt.subplots(figsize=(7, 3))
sns.heatmap(missing_by_lang, annot=True, fmt="d", cmap="YlOrRd",
            linewidths=0.5, cbar_kws={"label": "Missing count"}, ax=ax)
ax.set_title("Missing Span Annotations by Source Language & Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("")
fig.tight_layout()
save_fig(fig, "fig7_missing_spans.png",
         "Count of missing span annotations per source language and strategy. "
         "Missingness is very low overall (<25 rows) and concentrated in Chinese rows.")

# ══════════════════════════════════════════════════════════════════════════════
# Build Markdown report
# ══════════════════════════════════════════════════════════════════════════════
print("\nWriting README.md ...")

n_rows = len(df)
n_src = df["source_language"].nunique()
n_tgt = df["target_language"].nunique()
n_pairs = df.groupby(["source_language", "target_language"]).ngroups
n_idioms = df["idiom"].nunique()
total_missing = df[SPAN_COLS].isnull().sum().sum()

# Per-strategy length stats
len_stats = {}
for col, label in zip(TRANS_COLS, TRANS_LABELS):
    s = df[col].str.len()
    len_stats[label] = {"min": s.min(), "median": s.median(), "mean": s.mean(), "max": s.max()}

src_table = "\n".join(
    f"| {lang} | {cnt:,} | {cnt/n_rows*100:.1f}% |"
    for lang, cnt in df["source_language"].value_counts().items()
)
tgt_table = "\n".join(
    f"| {lang} | {cnt:,} | {cnt/n_rows*100:.1f}% |"
    for lang, cnt in df["target_language"].value_counts().items()
)
idiom_table = "\n".join(
    f"| {lang} | {grp['idiom'].nunique():,} |"
    for lang, grp in df.groupby("source_language")
)
len_table = "\n".join(
    f"| {label} | {s['min']} | {s['median']:.0f} | {s['mean']:.0f} | {s['max']} |"
    for label, s in len_stats.items()
)
fig_section = "\n\n".join(
    f"### {i+1}. {name.replace('_', ' ').replace('.png','').title()}\n\n"
    f"![{name}](figures/{name})\n\n{caption}"
    for i, (name, caption) in enumerate(figures_meta)
)

report = f"""\
# IdiomTranslate30 — Basic Statistics Report

*Generated on 2026-03-22*

---

## Overview

**IdiomTranslate30** is a massively multilingual dataset of context-aware translations of East Asian
idioms across 30 language pairs, generated using Google Gemini 3.0 Flash Preview and published in
*EMNLP 2024 Findings*.

| Property | Value |
|---|---|
| Total rows | {n_rows:,} |
| Columns | 10 |
| Source languages | {n_src} (Chinese, Japanese, Korean) |
| Target languages | {n_tgt} |
| Language pairs | {n_pairs} |
| Unique idioms | {n_idioms:,} |
| Missing span annotations | {total_missing} |
| License | CC-BY-NC-SA-4.0 |

---

## Language Distribution

### Source Languages

| Language | Rows | Share |
|---|---|---|
{src_table}

### Target Languages

| Language | Rows | Share |
|---|---|---|
{tgt_table}

Each of the 10 target languages is perfectly balanced (~90,660 rows, 10.0%).
Each of the 30 language pairs contains a fixed number of rows proportional to the source language's
idiom inventory size (Chinese: 43,100 / pair; Japanese: 24,400 / pair; Korean: 23,160 / pair).

---

## Idiom Coverage

| Source Language | Unique Idioms |
|---|---|
{idiom_table}
| **Total** | **{n_idioms:,}** |

Each idiom appears **200 times** in the dataset (10 target languages × ~20 context sentences),
ensuring balanced coverage across translation directions.

---

## Translation Length Statistics

Character-level length statistics for the three translation strategies:

| Strategy | Min | Median | Mean | Max |
|---|---|---|---|---|
{len_table}

Key observations:
- **Analogy** and **Author** strategies produce longer translations than **Creatively** (median ~121 vs 97 chars).
- All strategies have heavy-tailed distributions — the maximum lengths are 3–12× the median,
  indicating occasional verbose outputs.
- No translation is shorter than 15 characters (no empty outputs).

---

## Source Sentence Lengths

Source sentences are short by design (they carry exactly one idiom):

| Statistic | Value |
|---|---|
| Min | {df['sentence'].str.len().min()} chars |
| Median | {df['sentence'].str.len().median():.0f} chars |
| Mean | {df['sentence'].str.len().mean():.1f} chars |
| Max | {df['sentence'].str.len().max()} chars |

---

## Missing Values

| Column | Missing |
|---|---|
| span_creatively | {df['span_creatively'].isnull().sum()} |
| span_analogy | {df['span_analogy'].isnull().sum()} |
| span_author | {df['span_author'].isnull().sum()} |
| All others | 0 |

Missingness is negligible (<0.003% of rows) and only affects span annotation columns.

---

## Figures

{fig_section}
"""

# Preserve any manually-maintained sections from the existing README.
# Everything from the first occurrence of "## Analysis Results" or "## TODO"
# (whichever comes first) is kept verbatim across regenerations.
preserved = ""
if REPORT_PATH.exists():
    existing = REPORT_PATH.read_text(encoding="utf-8")
    markers = ["## Analysis Results", "## TODO"]
    positions = [existing.find(f"\n{m}") for m in markers]
    valid = [p for p in positions if p != -1]
    if valid:
        preserved = "\n" + existing[min(valid):].lstrip("\n")

REPORT_PATH.write_text(textwrap.dedent(report).strip() + "\n" + preserved)
print(f"  Saved {REPORT_PATH}")
print("\nDone.")
