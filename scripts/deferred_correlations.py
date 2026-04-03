"""
Deferred Correlation Analyses — items requiring raw parquet join.

Addresses the three items left in TODO.md after the first correlation gap pass:

  1. cross_target_overlap ↔ attractor_coverage  (per-idiom, raw span join)
  2. error_rate ↔ expansion_ratio               (per-idiom, computed from raw)
  3. Triple cognate triples: all-exact vs mixed → divergence (edit distance join)

Outputs (data/processed/)
--------------------------
attractor_coverage_per_idiom.csv    — per-idiom mean attractor n_idioms
error_rate_per_idiom.csv            — per-idiom span annotation error rate
deferred_corr_results.csv           — all Spearman / MWU results

Outputs (figures/)
------------------
attractor_vs_overlap_scatter.png
error_rate_vs_expansion_scatter.png
triple_cognate_divergence_box.png
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

ROOT = Path(__file__).parent.parent
RAW  = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
PROC = ROOT / "data" / "processed"
FIG  = ROOT / "figures"

STRATEGIES = ["creatively", "analogy", "author"]


def spearman(x, y):
    mask = ~(np.isnan(x) | np.isnan(y))
    if mask.sum() < 5:
        return np.nan, np.nan, int(mask.sum())
    r, p = spearmanr(x[mask], y[mask])
    return float(r), float(p), int(mask.sum())


# ---------------------------------------------------------------------------
# Load raw parquet (needed for items 1 & 2)
# ---------------------------------------------------------------------------
print("Loading raw parquet …")
raw = pd.read_parquet(RAW)
print(f"  {len(raw):,} rows loaded")

# Normalise idiom key
for col in ["source_language", "idiom", "target_language"]:
    raw[col] = raw[col].astype(str).str.strip()


# ===========================================================================
# Item 1: cross_target_overlap ↔ attractor_coverage (per-idiom)
# ===========================================================================
print("\n--- Item 1: attractor_coverage per idiom ---")

att = pd.read_parquet(PROC / "span_attractor_counts.parquet")
# span_norm in attractor table: build a lookup dict per target_language
att_lookup = {}
for tl, grp in att.groupby("target_language"):
    att_lookup[tl] = grp.set_index("span_norm")["n_idioms"].to_dict()

rows_att = []
for strat in STRATEGIES:
    span_col = f"span_{strat}"
    sub = raw[["source_language", "idiom", "target_language", span_col]].copy()
    sub["span_norm"] = (sub[span_col].fillna("").astype(str)
                        .str.lower().str.strip())
    sub = sub[sub["span_norm"] != ""]

    def lookup(row):
        return att_lookup.get(row["target_language"], {}).get(row["span_norm"], np.nan)

    # Use vectorised approach per target_language for speed
    chunks = []
    for tl, lookup_dict in att_lookup.items():
        chunk = sub[sub["target_language"] == tl].copy()
        chunk["n_idioms"] = chunk["span_norm"].map(lookup_dict)
        chunks.append(chunk[["source_language", "idiom", "n_idioms"]])
    sub_all = pd.concat(chunks, ignore_index=True)
    sub_all["strategy"] = strat
    rows_att.append(sub_all)

att_raw = pd.concat(rows_att, ignore_index=True)

# Per-idiom mean n_idioms (attractor coverage)
att_idiom = (att_raw.groupby(["source_language", "idiom"])["n_idioms"]
             .mean().reset_index()
             .rename(columns={"n_idioms": "attractor_coverage"}))
att_idiom.to_csv(PROC / "attractor_coverage_per_idiom.csv", index=False)
print(f"  attractor_coverage_per_idiom.csv: {len(att_idiom)} idioms, "
      f"mean={att_idiom['attractor_coverage'].mean():.2f}")

# Load cross_target_overlap (per-idiom mean jaccard)
cto = pd.read_parquet(PROC / "cross_target_overlap.parquet")
cto_idiom = (cto.groupby(["source_language", "idiom"])["jaccard"]
             .mean().reset_index()
             .rename(columns={"jaccard": "cross_target_overlap"}))

diff = pd.read_parquet(PROC / "idiom_difficulty.parquet")
slop = pd.read_csv(PROC / "idiom_slop_scores.csv")

m1 = att_idiom.merge(cto_idiom, on=["source_language", "idiom"], how="inner")
m1 = m1.merge(diff[["source_language", "idiom", "difficulty"]], on=["source_language", "idiom"], how="left")
m1 = m1.merge(slop[["source_language", "idiom", "slop_score"]], on=["source_language", "idiom"], how="left")

results = []
for col, label in [("cross_target_overlap", "cross_target_overlap"),
                   ("difficulty", "difficulty"),
                   ("slop_score", "slop_score")]:
    r, p, n = spearman(m1["attractor_coverage"].values.astype(float),
                       m1[col].values.astype(float))
    results.append({"analysis": "Item1_attractor_coverage",
                    "outcome": "attractor_coverage", "predictor": col,
                    "rho": r, "p": p, "n": n})
    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  attractor_coverage ↔ {label}: ρ={r:+.3f}{stars} p={p:.3e} n={n}")

# Scatter: attractor_coverage vs cross_target_overlap
fig, ax = plt.subplots(figsize=(6, 4))
sub = m1.dropna(subset=["attractor_coverage", "cross_target_overlap"])
ax.scatter(sub["cross_target_overlap"], sub["attractor_coverage"],
           alpha=0.12, s=5, color="#7cb87c")
r0, p0, _ = spearman(sub["cross_target_overlap"].values.astype(float),
                     sub["attractor_coverage"].values.astype(float))
ax.set_xlabel("Cross-target vocabulary overlap (mean Jaccard)")
ax.set_ylabel("Attractor coverage (mean n_idioms per span)")
ax.set_title(f"attractor_coverage ↔ cross_target_overlap\nρ={r0:+.3f}, p={p0:.2e}")
plt.tight_layout()
fig.savefig(FIG / "attractor_vs_overlap_scatter.png", dpi=150)
plt.close(fig)
print("  -> attractor_vs_overlap_scatter.png")


# ===========================================================================
# Item 2: error_rate ↔ expansion_ratio (per-idiom)
# ===========================================================================
print("\n--- Item 2: error_rate ↔ expansion_ratio per idiom ---")

# Compute per-row errors and expansion ratios from raw
err_rows = []
for strat in STRATEGIES:
    tcol = f"translate_{strat}"
    scol = f"span_{strat}"
    sub = raw[["source_language", "idiom", "target_language", "sentence", tcol, scol]].copy()
    sub["translation"] = sub[tcol].fillna("").astype(str)
    sub["span"]        = sub[scol].fillna("").astype(str)
    sub["error"]       = ~sub.apply(
        lambda r: bool(r["span"]) and (r["span"] in r["translation"]), axis=1)
    sub["tlen_chars"]  = sub["translation"].str.len()
    sub["slen_chars"]  = sub["sentence"].fillna("").astype(str).str.len()
    sub["exp_ratio"]   = sub["tlen_chars"] / sub["slen_chars"].replace(0, np.nan)
    sub["strategy"]    = strat
    err_rows.append(sub[["source_language", "idiom", "target_language",
                          "strategy", "error", "exp_ratio"]])

err_all = pd.concat(err_rows, ignore_index=True)

# Per-idiom: mean error rate and mean expansion ratio
err_idiom = (err_all.groupby(["source_language", "idiom"])
             .agg(error_rate=("error", "mean"),
                  exp_ratio_mean=("exp_ratio", "mean"))
             .reset_index())
err_idiom.to_csv(PROC / "error_rate_per_idiom.csv", index=False)
print(f"  error_rate_per_idiom.csv: {len(err_idiom)} idioms, "
      f"mean_error={err_idiom['error_rate'].mean():.4f}, "
      f"mean_exp={err_idiom['exp_ratio_mean'].mean():.3f}")

# Also join with processed exp_mean from idiom_difficulty (word-count based)
m2 = err_idiom.merge(diff[["source_language", "idiom", "exp_mean", "difficulty"]],
                     on=["source_language", "idiom"], how="inner")

for col, label in [("exp_ratio_mean", "expansion_ratio (char-level)"),
                   ("exp_mean", "expansion_ratio (word-level, from difficulty)"),
                   ("difficulty", "difficulty")]:
    r, p, n = spearman(m2["error_rate"].values.astype(float),
                       m2[col].values.astype(float))
    results.append({"analysis": "Item2_error_rate",
                    "outcome": "error_rate", "predictor": col,
                    "rho": r, "p": p, "n": n})
    stars = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  error_rate ↔ {label}: ρ={r:+.3f}{stars} p={p:.3e} n={n}")

# Scatter: error_rate vs expansion_ratio
fig, ax = plt.subplots(figsize=(6, 4))
sub2 = m2.dropna(subset=["error_rate", "exp_ratio_mean"])
sample = sub2.sample(min(4000, len(sub2)), random_state=42)
ax.scatter(sample["exp_ratio_mean"], sample["error_rate"],
           alpha=0.15, s=5, color="#e07b54")
r2, p2, _ = spearman(sub2["error_rate"].values.astype(float),
                     sub2["exp_ratio_mean"].values.astype(float))
ax.set_xlabel("Mean expansion ratio (char-level) per idiom")
ax.set_ylabel("Per-idiom span annotation error rate")
ax.set_title(f"error_rate ↔ expansion_ratio\nρ={r2:+.3f}, p={p2:.2e}")
plt.tight_layout()
fig.savefig(FIG / "error_rate_vs_expansion_scatter.png", dpi=150)
plt.close(fig)
print("  -> error_rate_vs_expansion_scatter.png")


# ===========================================================================
# Item 3: Triple cognate triples — all-exact vs mixed → divergence
# ===========================================================================
print("\n--- Item 3: triple cognate all-exact vs mixed → divergence ---")

triples = pd.read_csv(PROC / "triple_cognates.csv")
cog_div = pd.read_csv(PROC / "cognate_divergence_ranking.csv")

# Join ZH-KO edit_pair_mean into triples
t = triples.merge(cog_div[["zh_idiom", "ko_idiom", "edit_pair_mean"]],
                  on=["zh_idiom", "ko_idiom"], how="left")

# Also compute a combined match score: number of exact pairs (0–3)
t["n_exact"] = (
    (t["zhja_match"] == "exact_4/4").astype(int) +
    (t["zhko_match"] == "exact_4/4").astype(int) +
    (t["koja_match"] == "exact_4/4").astype(int)
)

print(f"  Triples with ZH-KO edit distance available: {t['edit_pair_mean'].notna().sum()} / {len(t)}")
print(f"  all_exact: {t['all_exact'].sum()}, mixed: {(~t['all_exact']).sum()}")

exact_div = t.loc[t["all_exact"] & t["edit_pair_mean"].notna(), "edit_pair_mean"]
mixed_div = t.loc[~t["all_exact"] & t["edit_pair_mean"].notna(), "edit_pair_mean"]

print(f"  all-exact (n={len(exact_div)}): mean={exact_div.mean():.4f} median={exact_div.median():.4f}")
print(f"  mixed     (n={len(mixed_div)}): mean={mixed_div.mean():.4f} median={mixed_div.median():.4f}")

if len(exact_div) >= 3 and len(mixed_div) >= 3:
    stat, p_mwu = mannwhitneyu(exact_div, mixed_div, alternative="less")
    print(f"  MWU (one-sided, all-exact < mixed): stat={stat:.1f} p={p_mwu:.4f}")
    results.append({"analysis": "Item3_triple_cognate",
                    "outcome": "edit_pair_mean", "predictor": "all_exact (vs mixed)",
                    "rho": np.nan, "p": float(p_mwu), "n": len(exact_div) + len(mixed_div)})
else:
    print("  Insufficient data for MWU")

# n_exact (0–3) ↔ edit_pair_mean (Spearman)
valid = t.dropna(subset=["edit_pair_mean"])
r3, p3, n3 = spearman(valid["n_exact"].values.astype(float),
                      valid["edit_pair_mean"].values.astype(float))
results.append({"analysis": "Item3_triple_cognate",
                "outcome": "edit_pair_mean", "predictor": "n_exact_pairs (0-3)",
                "rho": r3, "p": float(p3), "n": n3})
stars = "***" if p3 < 0.001 else "**" if p3 < 0.01 else "*" if p3 < 0.05 else ""
print(f"  n_exact ↔ edit_pair_mean: ρ={r3:+.3f}{stars} p={p3:.3e} n={n3}")

# Boxplot: divergence by match category
fig, ax = plt.subplots(figsize=(6, 4))
data_box = [exact_div.values, mixed_div.values]
bp = ax.boxplot(data_box, labels=["All-exact\n(3×exact_4/4)", "Mixed\n(≥1 near_3/4)"],
                patch_artist=True,
                boxprops=dict(facecolor="#5b8db8", alpha=0.6),
                medianprops=dict(color="black", linewidth=2))
bp["boxes"][1].set_facecolor("#e07b54")
ax.set_ylabel("ZH–KO edit_pair_mean divergence")
ax.set_title(f"Triple cognate: all-exact vs mixed match type\n"
             f"MWU p={p_mwu:.3f} (one-sided, n={len(exact_div)}+{len(mixed_div)})")
plt.tight_layout()
fig.savefig(FIG / "triple_cognate_divergence_box.png", dpi=150)
plt.close(fig)
print("  -> triple_cognate_divergence_box.png")


# ===========================================================================
# Save all results
# ===========================================================================
df_results = pd.DataFrame(results)
df_results.to_csv(PROC / "deferred_corr_results.csv", index=False)
print(f"\nAll results saved to deferred_corr_results.csv")
print(df_results.to_string(index=False))
