"""
Correlation Gap Analyses — Parts 1–8 of TODO.md.

Covers all pairwise correlations identified as missing after the first
round of 15-gap analyses.  Results are written to data/processed/ and
figures/ for inclusion in Part 21 of the MkDocs report.

Outputs (data/processed/)
--------------------------
consistency_intercorr.csv         — Section 1: cv / jaccard_div / span_uniq / dom_frac intercorrelations
slop_outcome_corr.csv             — Section 2: slop_score as dependent variable
cross_target_overlap_corr.csv     — Section 3: cross_target_overlap correlations
attractor_outcome_corr.csv        — Section 4: attractor_coverage correlations
error_rate_corr.csv               — Section 5: error_rate ↔ cv / translation_length / expansion_ratio
cognate_matchtype_mwu.csv         — Section 6: match_type → edit_pair_mean (Mann-Whitney U)
expansion_outcome_corr.csv        — Section 7: expansion_ratio as dependent variable
template_rate_corr.csv            — Section 8: template_rate ↔ per-language metrics

Outputs (figures/)
------------------
consistency_intercorr_heatmap.png
slop_outcome_scatter.png
expansion_outcome_scatter.png
template_rate_corr.png
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
from scipy.stats import spearmanr, mannwhitneyu

from utils import STRATEGY_COLORS

ROOT = Path(__file__).parent.parent
PROC = ROOT / "data" / "processed"
FIG  = ROOT / "figures"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def spearman(x, y):
    """Return (rho, p, n) after dropping NaN pairs."""
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 5:
        return np.nan, np.nan, mask.sum()
    r, p = spearmanr(x[mask], y[mask])
    return float(r), float(p), int(mask.sum())


def fmt(r, p):
    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    return f"{r:+.3f}{stars}"


# ---------------------------------------------------------------------------
# Section 1 — Consistency metric intercorrelations
# ---------------------------------------------------------------------------
print("Section 1: consistency metric intercorrelations")

cs = pd.read_parquet(PROC / "context_sensitivity.parquet")
tlp = pd.read_parquet(PROC / "target_language_profile.parquet")

rows1 = []

# Cell-level (n ~ 90k): cv, jaccard_div, span_uniq per strategy
for strat in ("Creatively", "Analogy", "Author"):
    cv  = cs[f"cv_{strat}"].values.astype(float)
    jac = cs[f"jaccard_div_{strat}"].values.astype(float)
    su  = cs[f"span_uniq_{strat}"].values.astype(float)

    r, p, n = spearman(cv, jac)
    rows1.append({"pair": "cv ↔ jaccard_div", "level": "cell", "strategy": strat,
                  "rho": r, "p": p, "n": n})

    r, p, n = spearman(cv, su)
    rows1.append({"pair": "cv ↔ span_uniq", "level": "cell", "strategy": strat,
                  "rho": r, "p": p, "n": n})

    r, p, n = spearman(jac, su)
    rows1.append({"pair": "jaccard_div ↔ span_uniq", "level": "cell", "strategy": strat,
                  "rho": r, "p": p, "n": n})

# Language-level (n=10): dom_frac, cv, jaccard_div, span_uniq
lv = tlp[["cv", "jaccard_div", "span_uniq", "dom_frac"]].astype(float)
for a, b in [("cv", "dom_frac"), ("dom_frac", "span_uniq")]:
    r, p, n = spearman(lv[a].values, lv[b].values)
    rows1.append({"pair": f"{a} ↔ {b}", "level": "language", "strategy": "all",
                  "rho": r, "p": p, "n": n})

df1 = pd.DataFrame(rows1)
df1.to_csv(PROC / "consistency_intercorr.csv", index=False)
print(df1.to_string(index=False))

# Heatmap of cell-level correlations (average across strategies)
cell = df1[df1["level"] == "cell"].copy()
pivot = cell.groupby("pair")["rho"].mean().reset_index()

metrics = ["cv", "jaccard_div", "span_uniq"]
mat = pd.DataFrame(1.0, index=metrics, columns=metrics)
pair_map = {
    "cv ↔ jaccard_div":      ("cv", "jaccard_div"),
    "cv ↔ span_uniq":        ("cv", "span_uniq"),
    "jaccard_div ↔ span_uniq": ("jaccard_div", "span_uniq"),
}
for _, row in pivot.iterrows():
    if row["pair"] in pair_map:
        a, b = pair_map[row["pair"]]
        mat.loc[a, b] = row["rho"]
        mat.loc[b, a] = row["rho"]

fig, ax = plt.subplots(figsize=(5, 4))
sns.heatmap(mat, annot=True, fmt=".3f", cmap="coolwarm", center=0,
            vmin=-1, vmax=1, ax=ax, square=True,
            xticklabels=metrics, yticklabels=metrics)
ax.set_title("Consistency metric intercorrelations\n(mean Spearman ρ across strategies, cell level)")
plt.tight_layout()
fig.savefig(FIG / "consistency_intercorr_heatmap.png", dpi=150)
plt.close(fig)
print("  -> consistency_intercorr_heatmap.png")


# ---------------------------------------------------------------------------
# Section 2 — Slop score as outcome
# ---------------------------------------------------------------------------
print("\nSection 2: slop_score as outcome")

slop = pd.read_csv(PROC / "idiom_slop_scores.csv")
diff = pd.read_parquet(PROC / "idiom_difficulty.parquet")
sc   = pd.read_csv(PROC / "semantic_consistency.csv")
meta = pd.read_parquet(PROC / "idiom_metadata.parquet")

# merge slop with difficulty
m2 = slop.merge(diff[["source_language", "idiom", "difficulty", "exp_mean"]],
                on=["source_language", "idiom"], how="inner")
m2 = m2.merge(sc[["source_language", "idiom", "stability"]],
              on=["source_language", "idiom"], how="left")

# idiom_metadata lacks source_language — join on idiom only (may have duplicates)
meta_agg = meta.groupby("idiom")[["in_xinhua", "def_len"]].first().reset_index()
m2 = m2.merge(meta_agg, on="idiom", how="left")

rows2 = []
for col, label in [("difficulty", "difficulty"), ("stability", "stability"),
                   ("exp_mean", "expansion_ratio"),
                   ("in_xinhua", "in_xinhua"), ("def_len", "def_len")]:
    r, p, n = spearman(m2["slop_score"].values.astype(float),
                       m2[col].values.astype(float))
    rows2.append({"predictor": col, "outcome": "slop_score",
                  "rho": r, "p": p, "n": n})
    print(f"  slop_score ↔ {label}: ρ={r:+.3f} p={p:.3e} n={n}")

df2 = pd.DataFrame(rows2)
df2.to_csv(PROC / "slop_outcome_corr.csv", index=False)

# Scatter: slop_score vs difficulty + stability
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sub = m2.dropna(subset=["slop_score", "difficulty"]).sample(min(3000, len(m2)), random_state=42)
axes[0].scatter(sub["difficulty"], sub["slop_score"], alpha=0.15, s=6, color="#e07b54")
axes[0].set_xlabel("Composite difficulty score")
axes[0].set_ylabel("Slop score")
r0 = df2.loc[df2["predictor"] == "difficulty", "rho"].values[0]
p0 = df2.loc[df2["predictor"] == "difficulty", "p"].values[0]
axes[0].set_title(f"slop_score ↔ difficulty\nρ={r0:+.3f}, p={p0:.2e}")

sub2 = m2.dropna(subset=["slop_score", "stability"]).sample(min(3000, len(m2)), random_state=42)
axes[1].scatter(sub2["stability"], sub2["slop_score"], alpha=0.15, s=6, color="#5b8db8")
axes[1].set_xlabel("Semantic stability")
axes[1].set_ylabel("Slop score")
r1 = df2.loc[df2["predictor"] == "stability", "rho"].values[0]
p1 = df2.loc[df2["predictor"] == "stability", "p"].values[0]
axes[1].set_title(f"slop_score ↔ stability\nρ={r1:+.3f}, p={p1:.2e}")

plt.suptitle("Slop score as outcome variable", fontsize=12)
plt.tight_layout()
fig.savefig(FIG / "slop_outcome_scatter.png", dpi=150)
plt.close(fig)
print("  -> slop_outcome_scatter.png")


# ---------------------------------------------------------------------------
# Section 3 — Cross-target vocabulary overlap as outcome
# ---------------------------------------------------------------------------
print("\nSection 3: cross_target_overlap as outcome")

cto_raw = pd.read_parquet(PROC / "cross_target_overlap.parquet")
# per-idiom mean Jaccard across all language pairs and strategies
cto_idiom = (cto_raw.groupby(["source_language", "idiom"])["jaccard"]
             .mean().reset_index().rename(columns={"jaccard": "cross_target_overlap"}))

m3 = cto_idiom.merge(sc[["source_language", "idiom", "stability"]],
                     on=["source_language", "idiom"], how="inner")
m3 = m3.merge(slop[["source_language", "idiom", "slop_score"]],
              on=["source_language", "idiom"], how="left")

# Attractor coverage per idiom: not directly available — use mean n_idioms per target
# as a language-level proxy instead (see Section 4)

rows3 = []
for col, label in [("stability", "stability"), ("slop_score", "slop_score")]:
    r, p, n = spearman(m3["cross_target_overlap"].values.astype(float),
                       m3[col].values.astype(float))
    rows3.append({"predictor": col, "outcome": "cross_target_overlap",
                  "rho": r, "p": p, "n": n})
    print(f"  cross_target_overlap ↔ {label}: ρ={r:+.3f} p={p:.3e} n={n}")

df3 = pd.DataFrame(rows3)
df3.to_csv(PROC / "cross_target_overlap_corr.csv", index=False)


# ---------------------------------------------------------------------------
# Section 4 — Attractor coverage as outcome (language level)
# ---------------------------------------------------------------------------
print("\nSection 4: attractor_coverage as outcome (language level)")

att = pd.read_parquet(PROC / "span_attractor_counts.parquet")

# Per-language: mean and max n_idioms for spans covering ≥ 2 idioms
att_lang = (att[att["n_idioms"] >= 2]
            .groupby("target_language")
            .agg(mean_attractor_coverage=("n_idioms", "mean"),
                 max_attractor_coverage=("n_idioms", "max"),
                 n_attractors=("n_idioms", "count"))
            .reset_index())

# Per-language difficulty: mean over all idioms in target_language not available
# directly — use tlp error_rate as proxy for overall difficulty
tlp2 = tlp.copy()
tlp2.index.name = "target_language"
tlp2 = tlp2.reset_index()

# Per-language slop: multilingual_template_scores
tmpl = pd.read_csv(PROC / "multilingual_template_scores.csv")
tmpl_lang = (tmpl.groupby("target_language")["template_rate"]
             .mean().reset_index().rename(columns={"template_rate": "template_rate_mean"}))

m4 = att_lang.merge(tlp2[["target_language", "error_rate", "cv", "jaccard_div"]],
                    on="target_language", how="inner")
m4 = m4.merge(tmpl_lang, on="target_language", how="left")

rows4 = []
for predictor in ["error_rate", "cv", "jaccard_div", "template_rate_mean"]:
    r, p, n = spearman(m4["mean_attractor_coverage"].values.astype(float),
                       m4[predictor].values.astype(float))
    rows4.append({"predictor": predictor, "outcome": "mean_attractor_coverage",
                  "rho": r, "p": p, "n": n})
    print(f"  mean_attractor_coverage ↔ {predictor}: ρ={r:+.3f} p={p:.3e} n={n}")

df4 = pd.DataFrame(rows4)
df4.to_csv(PROC / "attractor_outcome_corr.csv", index=False)


# ---------------------------------------------------------------------------
# Section 5 — Error rate ↔ consistency and length metrics
# ---------------------------------------------------------------------------
print("\nSection 5: error_rate ↔ cv / translation_length / expansion_ratio")

err = pd.read_csv(PROC / "pairwise_error_rates.csv")
tls = pd.read_csv(PROC / "translation_length_stats.csv")

# Aggregate context_sensitivity to per-(source, target, strategy)
cs_agg = (cs.groupby(["source_language", "target_language"])
          .agg(mean_cv_C=("cv_Creatively", "mean"),
               mean_cv_A=("cv_Analogy", "mean"),
               mean_cv_Au=("cv_Author", "mean"))
          .reset_index())
cs_agg["mean_cv"] = cs_agg[["mean_cv_C", "mean_cv_A", "mean_cv_Au"]].mean(axis=1)

# Aggregate error rate to per-(source, target): mean over strategies
err_agg = (err.groupby(["source_language", "target_language"])["error_rate"]
           .mean().reset_index())

# Merge translation_length_stats (per target × strategy) -> per target
tls_agg = (tls.groupby("target_language")
           .agg(median_chars=("median_chars", "mean"),
                expansion_mean=("expansion_mean", "mean"))
           .reset_index())

m5 = err_agg.merge(cs_agg[["source_language", "target_language", "mean_cv"]],
                   on=["source_language", "target_language"], how="inner")
m5 = m5.merge(tls_agg, on="target_language", how="left")

# Also include per-source expansion from idiom_difficulty
exp_src = (diff.groupby("source_language")["exp_mean"].mean().reset_index()
           .rename(columns={"exp_mean": "src_exp_mean"}))
m5 = m5.merge(exp_src, on="source_language", how="left")

rows5 = []
for col, label in [("mean_cv", "cv"),
                   ("median_chars", "translation_length"),
                   ("expansion_mean", "expansion_ratio")]:
    r, p, n = spearman(m5["error_rate"].values.astype(float),
                       m5[col].values.astype(float))
    rows5.append({"predictor": col, "outcome": "error_rate",
                  "rho": r, "p": p, "n": n})
    print(f"  error_rate ↔ {label}: ρ={r:+.3f} p={p:.3e} n={n}")

df5 = pd.DataFrame(rows5)
df5.to_csv(PROC / "error_rate_corr.csv", index=False)


# ---------------------------------------------------------------------------
# Section 6 — Cognate match type → translation divergence (Mann-Whitney U)
# ---------------------------------------------------------------------------
print("\nSection 6: cognate match_type → edit_pair_mean (Mann-Whitney U)")

cog = pd.read_csv(PROC / "cognate_divergence_ranking.csv")
print(f"  match types: {cog['match_type'].value_counts().to_dict()}")

exact = cog.loc[cog["match_type"] == "exact_4/4", "edit_pair_mean"].dropna()
near  = cog.loc[cog["match_type"] == "near_3/4",  "edit_pair_mean"].dropna()

stat, p_mwu = mannwhitneyu(exact, near, alternative="less")  # exact has lower divergence?
print(f"  exact_4/4 mean={exact.mean():.4f}, near_3/4 mean={near.mean():.4f}")
print(f"  MWU stat={stat:.1f} p={p_mwu:.4e} (one-sided: exact < near)")

rows6 = [
    {"group": "exact_4/4", "n": len(exact), "mean_edit": exact.mean(),
     "median_edit": exact.median()},
    {"group": "near_3/4",  "n": len(near),  "mean_edit": near.mean(),
     "median_edit": near.median()},
    {"group": "MWU_stat", "n": None, "mean_edit": stat, "median_edit": p_mwu},
]
df6 = pd.DataFrame(rows6)
df6.to_csv(PROC / "cognate_matchtype_mwu.csv", index=False)

# Triple cognates: all_exact vs mixed
triples = pd.read_csv(PROC / "triple_cognates.csv")
print(f"  triples all_exact: {triples['all_exact'].sum()} / {len(triples)}")
# triple_cognates has no edit scores — note this limitation


# ---------------------------------------------------------------------------
# Section 7 — Expansion ratio as outcome
# ---------------------------------------------------------------------------
print("\nSection 7: expansion_ratio as outcome")

m7 = diff[["source_language", "idiom", "exp_mean", "difficulty"]].copy()
m7 = m7.merge(sc[["source_language", "idiom", "stability", "char_len"]],
              on=["source_language", "idiom"], how="left")
m7 = m7.merge(slop[["source_language", "idiom", "slop_score"]],
              on=["source_language", "idiom"], how="left")

rows7 = []
for col, label in [("char_len", "idiom_char_len"),
                   ("stability", "stability"),
                   ("slop_score", "slop_score")]:
    r, p, n = spearman(m7["exp_mean"].values.astype(float),
                       m7[col].values.astype(float))
    rows7.append({"predictor": col, "outcome": "expansion_ratio",
                  "rho": r, "p": p, "n": n})
    print(f"  expansion_ratio ↔ {label}: ρ={r:+.3f} p={p:.3e} n={n}")

df7 = pd.DataFrame(rows7)
df7.to_csv(PROC / "expansion_outcome_corr.csv", index=False)

# Scatter: expansion_ratio vs char_len + stability
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
sub = m7.dropna(subset=["exp_mean", "char_len"]).sample(min(3000, len(m7)), random_state=42)
axes[0].scatter(sub["char_len"], sub["exp_mean"], alpha=0.15, s=6, color="#7cb87c")
axes[0].set_xlabel("Idiom character length")
axes[0].set_ylabel("Mean expansion ratio")
r0 = df7.loc[df7["predictor"] == "char_len", "rho"].values[0]
p0 = df7.loc[df7["predictor"] == "char_len", "p"].values[0]
axes[0].set_title(f"expansion_ratio ↔ char_len\nρ={r0:+.3f}, p={p0:.2e}")

sub2 = m7.dropna(subset=["exp_mean", "stability"]).sample(min(3000, len(m7)), random_state=42)
axes[1].scatter(sub2["stability"], sub2["exp_mean"], alpha=0.15, s=6, color="#a07cc5")
axes[1].set_xlabel("Semantic stability")
axes[1].set_ylabel("Mean expansion ratio")
r1 = df7.loc[df7["predictor"] == "stability", "rho"].values[0]
p1 = df7.loc[df7["predictor"] == "stability", "p"].values[0]
axes[1].set_title(f"expansion_ratio ↔ stability\nρ={r1:+.3f}, p={p1:.2e}")

plt.suptitle("Expansion ratio as outcome variable", fontsize=12)
plt.tight_layout()
fig.savefig(FIG / "expansion_outcome_scatter.png", dpi=150)
plt.close(fig)
print("  -> expansion_outcome_scatter.png")


# ---------------------------------------------------------------------------
# Section 8 — Multilingual template_rate ↔ per-language metrics
# ---------------------------------------------------------------------------
print("\nSection 8: template_rate ↔ per-language metrics (n=10)")

tmpl_overall = (tmpl.groupby("target_language")["template_rate_overall"]
                .first().reset_index())
m8 = tmpl_overall.merge(tlp2[["target_language", "cv", "error_rate", "resource"]],
                        on="target_language", how="inner")

rows8 = []
for col, label in [("cv", "cv"), ("error_rate", "error_rate")]:
    r, p, n = spearman(m8["template_rate_overall"].values.astype(float),
                       m8[col].values.astype(float))
    rows8.append({"predictor": col, "outcome": "template_rate",
                  "rho": r, "p": p, "n": n})
    print(f"  template_rate ↔ {label}: ρ={r:+.3f} p={p:.3e} n={n}")

# Resource group (Mann-Whitney U: low vs high)
low  = m8.loc[m8["resource"] == "low",  "template_rate_overall"].dropna()
high = m8.loc[m8["resource"] == "high", "template_rate_overall"].dropna()
stat8, p8 = mannwhitneyu(low, high, alternative="greater")
print(f"  MWU resource: low mean={low.mean():.4f} high mean={high.mean():.4f} "
      f"stat={stat8:.1f} p={p8:.4f} (one-sided: low > high)")
rows8.append({"predictor": "resource (low>high MWU)", "outcome": "template_rate",
              "rho": np.nan, "p": float(p8), "n": len(m8)})

df8 = pd.DataFrame(rows8)
df8.to_csv(PROC / "template_rate_corr.csv", index=False)

# Bar chart: template_rate by language, coloured by resource
fig, ax = plt.subplots(figsize=(8, 4))
m8_sorted = m8.sort_values("template_rate_overall", ascending=False)
colors = ["#e07b54" if r == "low" else "#5b8db8"
          for r in m8_sorted["resource"]]
ax.bar(m8_sorted["target_language"], m8_sorted["template_rate_overall"] * 100,
       color=colors, edgecolor="white", linewidth=0.5)
ax.set_ylabel("Template rate (%)")
ax.set_title("Template rate by target language\n(orange = low-resource, blue = high-resource)")
ax.set_xlabel("Target language")

from matplotlib.patches import Patch
ax.legend(handles=[Patch(color="#e07b54", label="Low-resource"),
                   Patch(color="#5b8db8", label="High-resource")])
plt.tight_layout()
fig.savefig(FIG / "template_rate_corr.png", dpi=150)
plt.close(fig)
print("  -> template_rate_corr.png")

print("\nAll sections complete.")
