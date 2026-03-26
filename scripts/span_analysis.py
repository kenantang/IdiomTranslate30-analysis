"""
Span Length & Idiom Footprint Analysis.

Outputs
-------
data/processed/span_length_stats.csv  – per-strategy span ratio medians,
                                         cross-strategy Pearson correlations,
                                         and per-target-language Analogy span medians.
figures/fig6_span_length_by_strategy.png
figures/span_ratio.png
figures/span_vs_idiom_length.png
figures/span_correlation.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")


from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import pearsonr

ROOT = Path(__file__).parent.parent
df   = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

PAIRS  = [("translate_creatively","span_creatively"),
          ("translate_analogy",   "span_analogy"),
          ("translate_author",    "span_author")]
LABELS = ["Creatively", "Analogy", "Author"]
COLORS = ["#4C72B0", "#DD8452", "#55A868"]

idiom_len = df["idiom"].str.len()

for (tc, sc), lbl in zip(PAIRS, LABELS):
    tl = df[tc].str.len()
    sl = df[sc].str.len()
    df[f"span_len_{lbl}"]   = sl
    df[f"trans_len_{lbl}"]  = tl
    df[f"span_ratio_{lbl}"] = sl / tl.replace(0, np.nan)

# ── Fig 2a: violin — span-to-translation ratio per strategy ──────────────────
sample = df.sample(50_000, random_state=1)
ratio_data = pd.melt(
    sample[[f"span_ratio_{l}" for l in LABELS]].rename(
        columns={f"span_ratio_{l}": l for l in LABELS}),
    var_name="Strategy", value_name="Span / Translation ratio"
).dropna()
ratio_data = ratio_data[ratio_data["Span / Translation ratio"] <= 1.0]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.violinplot(data=ratio_data, x="Strategy", y="Span / Translation ratio",
               hue="Strategy", palette=COLORS, cut=0, inner="quartile",
               legend=False, ax=axes[0])
axes[0].set_title("Span / Translation Ratio by Strategy", fontweight="bold")
axes[0].set_ylabel("len(span) / len(translation)")
for i, lbl in enumerate(LABELS):
    med = sample[f"span_ratio_{lbl}"].dropna().median()
    axes[0].text(i, med + 0.015, f"med={med:.2f}", ha="center", fontsize=9)

# Right: span length box per target language (Analogy, as longest)
span_lang = df[["target_language", "span_len_Analogy"]].dropna()
order = span_lang.groupby("target_language")["span_len_Analogy"].median().sort_values().index
sns.boxplot(data=span_lang, x="span_len_Analogy", y="target_language",
            order=order, color=COLORS[1],
            flierprops=dict(marker=".", alpha=0.2, markersize=2), ax=axes[1])
axes[1].set_title("Span Length Distribution\nby Target Language (Analogy)", fontweight="bold")
axes[1].set_xlabel("Span character count")
axes[1].set_ylabel("")
axes[1].set_xlim(0, 250)
fig.tight_layout()
fig.savefig(FIG / "span_ratio.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/span_ratio.png")

# ── Fig 2b: idiom length vs span length scatter (sampled) ────────────────────
s = df.sample(10_000, random_state=2)[["idiom", "span_len_Creatively",
                                        "span_len_Analogy", "span_len_Author"]].dropna()
idiom_l = s["idiom"].str.len()

fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=False)
for ax, lbl, color in zip(axes, LABELS, COLORS):
    col = f"span_len_{lbl}"
    ax.scatter(idiom_l, s[col], alpha=0.15, s=5, color=color)
    # regression line
    m, b = np.polyfit(idiom_l, s[col].fillna(0), 1)
    xs = np.array([idiom_l.min(), idiom_l.max()])
    ax.plot(xs, m*xs + b, color="black", lw=1.5)
    r, p = pearsonr(idiom_l, s[col].fillna(0))
    ax.set_title(f"{lbl}\nr={r:.3f}, p={p:.2e}", fontweight="bold")
    ax.set_xlabel("Source idiom length (chars)")
    ax.set_ylabel("Span length (chars)" if ax is axes[0] else "")
    ax.set_ylim(0, 400)
fig.suptitle("Source Idiom Length vs Span Length in Translation", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "span_vs_idiom_length.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/span_vs_idiom_length.png")

# ── Fig 2c: 3×3 cross-strategy span correlation heatmap ──────────────────────
# Per target language
corr_records = []
for lang, grp in df.groupby("target_language"):
    sub = grp[["span_len_Creatively","span_len_Analogy","span_len_Author"]].dropna()
    corr_matrix = sub.corr()
    corr_records.append({"lang": lang, "C-A": corr_matrix.iloc[0,1],
                         "C-Au": corr_matrix.iloc[0,2], "A-Au": corr_matrix.iloc[1,2]})
corr_df = pd.DataFrame(corr_records).set_index("lang")

fig, ax = plt.subplots(figsize=(7, 4))
sns.heatmap(corr_df, annot=True, fmt=".3f", cmap="YlGnBu",
            vmin=0, vmax=1, linewidths=0.5, ax=ax,
            cbar_kws={"label": "Pearson r"})
ax.set_title("Cross-Strategy Span Length Correlation\nby Target Language", fontweight="bold")
ax.set_xlabel("Strategy pair")
fig.tight_layout()
fig.savefig(FIG / "span_correlation.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/span_correlation.png")

# Print summary stats
print("\nSpan-to-translation ratio medians:")
for lbl in LABELS:
    print(f"  {lbl:<14} {df[f'span_ratio_{lbl}'].dropna().median():.3f}")
print("\nCross-strategy correlation (mean over target languages):")
print(corr_df.mean().to_string())

# ── Fig 6: span length box per strategy (from generate_report) ────────────────
SPAN_COLS   = ["span_creatively", "span_analogy", "span_author"]
span_sample = df.dropna(subset=SPAN_COLS).sample(min(50_000, len(df)), random_state=0)
span_df = pd.DataFrame({
    label: span_sample[col].str.len()
    for col, label in zip(SPAN_COLS, LABELS)
})
span_melted = span_df.melt(var_name="Strategy", value_name="Span Length (chars)")
span_melted = span_melted[
    span_melted["Span Length (chars)"] <
    span_melted["Span Length (chars)"].quantile(0.995)
]
fig, ax = plt.subplots(figsize=(10, 5))
sns.boxplot(data=span_melted, x="Strategy", y="Span Length (chars)",
            palette=COLORS, width=0.45,
            flierprops=dict(marker=".", alpha=0.3), ax=ax)
ax.set_title("Idiom Span Length in Translation by Strategy",
             fontsize=13, fontweight="bold")
ax.set_ylabel("Span character count")
fig.tight_layout()
fig.savefig(FIG / "fig6_span_length_by_strategy.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/fig6_span_length_by_strategy.png")

# ── Save processed output ──────────────────────────────────────────────────────
ratio_summary = pd.DataFrame({
    "strategy": LABELS,
    "span_ratio_median": [df[f"span_ratio_{lbl}"].dropna().median() for lbl in LABELS],
    "span_len_median": [df[f"span_len_{lbl}"].dropna().median() for lbl in LABELS],
})

corr_summary = corr_df.reset_index().rename(columns={"lang": "target_language"})

analogy_by_lang = (
    df[["target_language", "span_len_Analogy"]]
    .dropna()
    .groupby("target_language")["span_len_Analogy"]
    .median()
    .reset_index()
    .rename(columns={"span_len_Analogy": "analogy_span_median"})
)

out = ratio_summary.merge(
    corr_summary.rename(columns={"C-A": "corr_CA", "C-Au": "corr_CAu", "A-Au": "corr_AAu"})
    .assign(strategy="Analogy")[["corr_CA", "corr_CAu", "corr_AAu"]].mean()
    .to_frame().T,
    how="cross"
).merge(analogy_by_lang, how="cross")

# Keep it flat: just save each component as its own file
ratio_summary.to_csv(PROC / "span_length_stats.csv", index=False)
corr_summary.to_csv(PROC / "span_correlation_stats.csv", index=False)
analogy_by_lang.to_csv(PROC / "span_analogy_by_language.csv", index=False)
print(f"Saved → data/processed/span_length_stats.csv")
print(f"Saved → data/processed/span_correlation_stats.csv")
print(f"Saved → data/processed/span_analogy_by_language.csv")
