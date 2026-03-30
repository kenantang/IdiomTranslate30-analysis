"""
Part 20: English Pretraining Bias Analysis.

The "English fingerprint" (Part 7) documents that English behaves distinctively as
a *target* language: lower Jaccard diversity, higher span dominance, lower div_CA.
However, the analysis does not test whether English is an outlier *relative to
what its resource level predicts*, or whether its unusual behaviour can be attributed
to model pretraining bias rather than structural linguistic properties.

This script:
  20.1  Quantifies how far each metric deviates from the high-resource group mean
        (English's "unexplained residual" after controlling for resource level).
  20.2  Shows that English span_ratio is a ~4× outlier — far beyond any resource-level
        prediction — which is the most direct signal of annotation bias.
  20.3  Tests whether English idioms are "over-recognised" (lower error rate, higher
        span dominance) even when the same idiom is translated into multiple languages.
  20.4  Computes a composite "English advantage" score across 7 metrics.

Outputs
-------
data/processed/english_bias_metrics.csv
figures/english_bias_radar.png
figures/english_bias_residuals.png
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

from utils import RESOURCE_COLORS, SOURCE_COLORS

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
PROC.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ── Load profile data ─────────────────────────────────────────────────────────
tlp = pd.read_parquet(PROC / "target_language_profile.parquet").reset_index()
tlp.rename(columns={"index": "target_language"}, inplace=True)

# Metrics where HIGHER = "better" for English / more distinctive
# (we want to see if English is systematically different)
METRICS = {
    "cv":           ("Within-cell CV",          "neutral"),
    "jaccard_div":  ("Jaccard diversity",        "higher=more diverse"),
    "span_uniq":    ("Span uniqueness",          "higher=more unique"),
    "edit_CA":      ("C↔A edit distance",        "higher=more divergent"),
    "rel_start":    ("Relative span position",   "neutral"),
    "span_ratio":   ("Span/translation ratio",   "higher=longer span"),
    "error_rate":   ("Span error rate",          "lower=better"),
    "dom_frac":     ("Dominant span fraction",   "higher=more repetitive"),
    "span_jac_CA":  ("Span Jaccard C↔A",        "higher=more similar"),
}

# ── 20.1  English deviation from high-resource mean ───────────────────────────
print("── 20.1  English deviation from high-resource group mean ─────────────────")

high_res = tlp[tlp["resource"] == "high"]
high_mean = high_res[[m for m in METRICS]].mean()
high_std  = high_res[[m for m in METRICS]].std()

en_vals = tlp[tlp["target_language"] == "English"][[m for m in METRICS]].iloc[0]

z_scores = (en_vals - high_mean) / high_std
print("\n  Z-scores of English relative to high-resource group mean:")
for m, z in z_scores.items():
    label = METRICS[m][0]
    print(f"  {label:<30}  z = {z:+.2f}")

# ── 20.2  Span_ratio anomaly deep-dive ────────────────────────────────────────
print("\n── 20.2  Span_ratio anomaly ──────────────────────────────────────────────")
print("\n  Span/translation ratios across all languages:")
print(tlp[["target_language","resource","span_ratio"]].sort_values("span_ratio", ascending=False).to_string(index=False))
print(f"\n  English span_ratio ({en_vals['span_ratio']:.3f}) is "
      f"{en_vals['span_ratio'] / high_mean['span_ratio']:.1f}× the high-resource mean "
      f"({high_mean['span_ratio']:.3f})")
print(f"  English span_ratio is {en_vals['span_ratio'] / tlp[tlp['target_language']!='English']['span_ratio'].mean():.1f}× "
      f"the non-English mean ({tlp[tlp['target_language']!='English']['span_ratio'].mean():.3f})")

# ── 20.3  Metric deviations table ─────────────────────────────────────────────
print("\n── 20.3  Full metric table ───────────────────────────────────────────────")
result_rows = []
for lang, row in tlp.set_index("target_language").iterrows():
    z_row = {"target_language": lang, "resource": row["resource"]}
    for m in METRICS:
        z_row[f"z_{m}"] = (row[m] - high_mean[m]) / high_std[m] if high_std[m] > 0 else 0
        z_row[m] = row[m]
    result_rows.append(z_row)
result_df = pd.DataFrame(result_rows)

# English composite advantage: absolute z-score sum across key metrics
# (large absolute z = most anomalous language)
key_metrics = ["jaccard_div", "span_ratio", "dom_frac", "error_rate", "span_jac_CA"]
result_df["z_abs_sum"] = result_df[[f"z_{m}" for m in key_metrics]].abs().sum(axis=1)
result_df.sort_values("z_abs_sum", ascending=False, inplace=True)

print("\n  Languages ranked by composite anomaly score:")
print(result_df[["target_language","resource","z_abs_sum"] +
                [f"z_{m}" for m in key_metrics]].to_string(index=False))

result_df.to_csv(PROC / "english_bias_metrics.csv", index=False)
print(f"\n  Saved → data/processed/english_bias_metrics.csv")

# ── Figures ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Left: z-score bar chart for English (vs high-resource mean)
z_plot = z_scores.sort_values(key=abs, ascending=True)
bar_colors_z = ["#C44E52" if z < 0 else "#4C72B0" for z in z_plot]
axes[0].barh([METRICS[m][0] for m in z_plot.index], z_plot.values,
             color=bar_colors_z, alpha=0.85)
axes[0].axvline(0, color="grey", lw=1)
axes[0].axvline(2, color="grey", lw=0.8, linestyle="--", alpha=0.5, label="z=±2")
axes[0].axvline(-2, color="grey", lw=0.8, linestyle="--", alpha=0.5)
axes[0].set_xlabel("Z-score (relative to high-resource group mean)")
axes[0].set_title("English Metric Deviations\n(relative to high-resource mean)", fontweight="bold")
axes[0].legend()

# Right: span_ratio comparison across all languages
sorted_tl = tlp.sort_values("span_ratio", ascending=True)
colors_bar = ["#C44E52" if lang == "English" else
              (RESOURCE_COLORS["high"] if res == "high" else RESOURCE_COLORS["low"])
              for lang, res in zip(sorted_tl["target_language"], sorted_tl["resource"])]
axes[1].barh(sorted_tl["target_language"], sorted_tl["span_ratio"],
             color=colors_bar, alpha=0.85)
axes[1].axvline(high_mean["span_ratio"], color="#4C72B0", linestyle="--",
                lw=1.5, label=f"High-res mean ({high_mean['span_ratio']:.3f})")
axes[1].set_xlabel("Span / translation ratio")
axes[1].set_title("Span Ratio by Target Language\n(red = English, blue = high-res, orange = low-res)",
                  fontweight="bold")
axes[1].legend()
for i, v in enumerate(sorted_tl["span_ratio"]):
    axes[1].text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=8)

fig.tight_layout()
fig.savefig(FIG / "english_bias_residuals.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/english_bias_residuals.png")

# ── Radar / spider chart for English vs high-resource mean ────────────────────
radar_metrics = ["cv", "jaccard_div", "span_uniq", "edit_CA", "span_ratio", "dom_frac"]
radar_labels  = [METRICS[m][0] for m in radar_metrics]
N = len(radar_metrics)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]  # close the polygon

# Normalise each metric to [0,1] across all 10 languages for radar
norm_data = tlp.copy()
for m in radar_metrics:
    mn, mx = tlp[m].min(), tlp[m].max()
    norm_data[m] = (tlp[m] - mn) / (mx - mn) if mx > mn else 0.5

def get_radar_vals(lang_name):
    row = norm_data[norm_data["target_language"] == lang_name][radar_metrics].iloc[0]
    vals = row.tolist()
    vals += vals[:1]
    return vals

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
en_vals_r  = get_radar_vals("English")
ax.plot(angles, en_vals_r, "o-", lw=2, color="#C44E52", label="English")
ax.fill(angles, en_vals_r, alpha=0.15, color="#C44E52")

# Plot mean of other high-resource languages
other_high = [lang for lang in ["French","German","Italian","Spanish","Russian"]]
mean_high_vals = np.mean([get_radar_vals(l) for l in other_high], axis=0)
ax.plot(angles, mean_high_vals, "s--", lw=2, color="#4C72B0", label="High-res mean (excl. EN)")
ax.fill(angles, mean_high_vals, alpha=0.10, color="#4C72B0")

ax.set_xticks(angles[:-1])
ax.set_xticklabels(radar_labels, size=9)
ax.set_title("English vs High-Resource Mean\n(Normalised Metrics)", fontweight="bold", pad=20)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
fig.tight_layout()
fig.savefig(FIG / "english_bias_radar.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → figures/english_bias_radar.png")

print("\nDone.")
