"""
Part 17: Strategy Length Correlations per Target Language.

Part 3 reports global Pearson r between strategy translation lengths
(Creatively ↔ Analogy r = 0.462, etc.) but never breaks these down by target
language.  This script computes per-target correlations and tests whether the
strategy coupling is stronger in high-resource languages (where the model may
have more consistent patterns) vs low-resource languages.

Outputs
-------
data/processed/strategy_length_correlations.csv
figures/strategy_length_correlations.png
figures/strategy_corr_heatmap.png
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

from utils import STRATEGY_COLORS as COLORS, RESOURCE_COLORS, OUTLIER_PERCENTILE

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

LABELS     = ["Creatively", "Analogy", "Author"]
TRANS_COLS = ["translate_creatively", "translate_analogy", "translate_author"]
PAIRS      = [("Creatively", "Analogy"), ("Creatively", "Author"), ("Analogy", "Author")]

# ── Load and compute translation lengths ─────────────────────────────────────
print("Loading raw data …")
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
for col, label in zip(TRANS_COLS, LABELS):
    df[f"len_{label}"] = df[col].str.len()
print(f"  {len(df):,} rows loaded")

# ── Per-target-language correlations ──────────────────────────────────────────
print("\n── Per-target-language correlations ──────────────────────────────────────")

# Load resource-level info
tlp = pd.read_parquet(PROC / "target_language_profile.parquet").reset_index()
tlp.rename(columns={"index": "target_language"}, inplace=True)

records = []
for lang, grp in df.groupby("target_language"):
    sub = grp[[f"len_{l}" for l in LABELS]].dropna()
    # cap outliers
    cap = sub.quantile(OUTLIER_PERCENTILE)
    sub = sub[(sub <= cap).all(axis=1)]
    row = {"target_language": lang}
    for a, b in PAIRS:
        r, p = pearsonr(sub[f"len_{a}"], sub[f"len_{b}"])
        row[f"r_{a[:2]}_{b[:2]}"] = r  # e.g. r_Cr_An
        row[f"p_{a[:2]}_{b[:2]}"] = p
    records.append(row)

corr_df = pd.DataFrame(records).merge(
    tlp[["target_language", "resource"]], on="target_language", how="left"
)

# Rename for readability
col_rename = {"r_Cr_An": "r_C_A", "r_Cr_Au": "r_C_Au", "r_An_Au": "r_A_Au",
              "p_Cr_An": "p_C_A", "p_Cr_Au": "p_C_Au", "p_An_Au": "p_A_Au"}
corr_df.rename(columns=col_rename, inplace=True)
corr_df.to_csv(PROC / "strategy_length_correlations.csv", index=False)

print("\n  Per-target Pearson r (translation length):")
print(corr_df[["target_language", "resource", "r_C_A", "r_C_Au", "r_A_Au"]].to_string(index=False))

# Group by resource level
print("\n  Mean r by resource level:")
print(corr_df.groupby("resource")[["r_C_A", "r_C_Au", "r_A_Au"]].mean().to_string())

# Global baseline (all data)
global_r = {}
all_sub = df[[f"len_{l}" for l in LABELS]].dropna()
for a, b in PAIRS:
    r, _ = pearsonr(all_sub[f"len_{a}"].sample(50000, random_state=0),
                    all_sub[f"len_{b}"].sample(50000, random_state=0))
    global_r[f"{a[:2]}–{b[:2]}"] = r
print("\n  Global baseline r (50k sample):", global_r)

# ── Fig: heatmap of r values per target ──────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: heatmap
hm = corr_df.set_index("target_language")[["r_C_A", "r_C_Au", "r_A_Au"]]
hm.columns = ["C↔A", "C↔Au", "A↔Au"]
order = hm.mean(axis=1).sort_values(ascending=False).index
sns.heatmap(hm.loc[order], annot=True, fmt=".3f", cmap="YlGnBu",
            vmin=0.3, vmax=0.9, linewidths=0.4,
            cbar_kws={"label": "Pearson r"}, ax=axes[0])
axes[0].set_title("Cross-Strategy Translation Length Correlation\nby Target Language",
                  fontweight="bold")
axes[0].set_xlabel("Strategy pair")

# Right: r_C_A scatter by resource level
for res, grp in corr_df.groupby("resource"):
    axes[1].scatter(grp["r_C_A"], grp["r_A_Au"],
                    c=RESOURCE_COLORS[res], s=80, label=res, alpha=0.85)
    for _, row in grp.iterrows():
        axes[1].annotate(row["target_language"],
                         (row["r_C_A"], row["r_A_Au"]),
                         textcoords="offset points", xytext=(5, 3), fontsize=8)
axes[1].axhline(np.mean([r for r in corr_df["r_A_Au"]]), color="grey",
                linestyle="--", lw=1, alpha=0.5, label="Mean A↔Au")
axes[1].axvline(np.mean([r for r in corr_df["r_C_A"]]), color="grey",
                linestyle=":", lw=1, alpha=0.5, label="Mean C↔A")
axes[1].set_xlabel("r(Creatively ↔ Analogy)")
axes[1].set_ylabel("r(Analogy ↔ Author)")
axes[1].set_title("Strategy Coupling by Resource Level",
                  fontweight="bold")
axes[1].legend()

fig.tight_layout()
fig.savefig(FIG / "strategy_length_correlations.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\n  Saved → figures/strategy_length_correlations.png")

# ── Fig: violin of per-strategy length distributions coloured by target ──────
fig, ax = plt.subplots(figsize=(13, 5))
sample = df.sample(30_000, random_state=0)
long = pd.melt(
    sample[["target_language"] + [f"len_{l}" for l in LABELS]].rename(
        columns={f"len_{l}": l for l in LABELS}),
    id_vars="target_language", var_name="Strategy", value_name="Length"
).dropna()
long = long[long["Length"] < long["Length"].quantile(OUTLIER_PERCENTILE)]
order_tgt = (long.groupby("target_language")["Length"].median()
             .sort_values(ascending=False).index)
palette = sns.color_palette("tab10", n_colors=len(order_tgt))
sns.boxplot(data=long, x="Strategy", y="Length", hue="target_language",
            hue_order=order_tgt, palette=palette,
            flierprops=dict(marker=".", alpha=0.2, markersize=1), ax=ax)
ax.set_title("Translation Length by Strategy & Target Language\n(30k-row sample)",
             fontweight="bold")
ax.set_ylabel("Translation length (chars)")
ax.legend(title="Target", bbox_to_anchor=(1.01, 1), loc="upper left", fontsize=8)
fig.tight_layout()
fig.savefig(FIG / "strategy_corr_heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/strategy_corr_heatmap.png")

print("\nDone.")
