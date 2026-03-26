"""
Target-language profile analysis: English vs peers, high-resource vs low-resource.

Sections:
  1. English fingerprint   — stable lengths, varied wording (CV vs Jaccard)
  2. Conventional locking  — idioms that converge to a fixed English phrase
  3. Strategy divergence   — by resource level
  4. Word-level expansion  — controlling for script density
  5. Span position         — by target language (typological signal)
  6. Annotation errors     — by target language
  7. Cross-strategy span   — overlap within a target language
  8. Resource synthesis    — PCA + radar chart

Outputs → figures/  and  data/processed/
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from scipy import stats
from pathlib import Path

from utils import RESOURCE_LEVEL, HIGH_RESOURCE_LANGS, LOW_RESOURCE_LANGS

ROOT = Path(__file__).parent.parent
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.05)

RESOURCE  = RESOURCE_LEVEL                    # H27: imported from utils
HIGH      = sorted(HIGH_RESOURCE_LANGS)
LOW       = sorted(LOW_RESOURCE_LANGS)
ALL_LANGS = HIGH + LOW

STRATS = ["Creatively", "Analogy", "Author"]
TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
SCOLS  = ["span_creatively",      "span_analogy",      "span_author"]
COLORS = {"high": "#4C72B0", "low": "#DD8452", "English": "#C44E52"}

def mwu(a, b):
    """Mann-Whitney U, returns (stat, p, rank-biserial r)."""
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    r = 1 - 2 * u / (len(a) * len(b))
    return u, p, r

def bonferroni_star(p, n):
    return "*" if p < 0.05 / n else ""

print("Loading data …")
raw = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
cs  = pd.read_parquet(ROOT / "data/processed/context_sensitivity.parquet")
div = pd.read_parquet(ROOT / "data/processed/divergence_scores.parquet")
sp  = pd.read_parquet(ROOT / "data/processed/span_positions.parquet")
an  = pd.read_csv(ROOT / "data/audit/anomalies.csv")
print(f"  raw {len(raw):,} rows  |  cs {len(cs):,}  |  div {len(div):,}  |  sp {len(sp):,}  |  an {len(an):,}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — English fingerprint: low CV + high Jaccard diversity
# ══════════════════════════════════════════════════════════════════════════════
print("\n[1] English fingerprint …")

s1 = {}
for strat in STRATS:
    cv_col  = f"cv_{strat}"
    jac_col = f"jaccard_div_{strat}"
    grp = cs.groupby("target_language")[[cv_col, jac_col]].mean().rename(
        columns={cv_col: "cv", jac_col: "jac"})
    grp["resource"] = grp.index.map(RESOURCE)
    s1[strat] = grp

fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharey="row")
for col, strat in enumerate(STRATS):
    g = s1[strat]
    g_sorted_cv  = g["cv"].sort_values()
    g_sorted_jac = g["jac"].sort_values()

    ax_cv  = axes[0, col]
    ax_jac = axes[1, col]

    colors_cv  = [COLORS["English"] if l == "English" else COLORS[RESOURCE[l]] for l in g_sorted_cv.index]
    colors_jac = [COLORS["English"] if l == "English" else COLORS[RESOURCE[l]] for l in g_sorted_jac.index]

    ax_cv.barh(range(len(g_sorted_cv)),  g_sorted_cv.values,  color=colors_cv)
    ax_cv.set_yticks(range(len(g_sorted_cv)));  ax_cv.set_yticklabels(g_sorted_cv.index, fontsize=8)
    ax_cv.set_title(f"{strat}", fontsize=10, fontweight="bold")
    ax_cv.axvline(g[g["resource"] == "high"]["cv"].mean(), color="#4C72B0", lw=1.2, ls="--", alpha=.7)
    ax_cv.axvline(g[g["resource"] == "low"]["cv"].mean(),  color="#DD8452", lw=1.2, ls="--", alpha=.7)

    ax_jac.barh(range(len(g_sorted_jac)), g_sorted_jac.values, color=colors_jac)
    ax_jac.set_yticks(range(len(g_sorted_jac))); ax_jac.set_yticklabels(g_sorted_jac.index, fontsize=8)
    ax_jac.axvline(g[g["resource"] == "high"]["jac"].mean(), color="#4C72B0", lw=1.2, ls="--", alpha=.7)
    ax_jac.axvline(g[g["resource"] == "low"]["jac"].mean(),  color="#DD8452", lw=1.2, ls="--", alpha=.7)

axes[0, 0].set_ylabel("CV of translation length\n(lower = more stable)", fontsize=9)
axes[1, 0].set_ylabel("Mean pairwise Jaccard diversity\n(higher = more varied vocabulary)", fontsize=9)
patches = [mpatches.Patch(color=COLORS["high"], label="High-resource"),
           mpatches.Patch(color=COLORS["low"],  label="Low-resource"),
           mpatches.Patch(color=COLORS["English"], label="English")]
fig.legend(handles=patches, loc="lower center", ncol=3, fontsize=9, frameon=False)
fig.suptitle("English Fingerprint: Lowest CV, Highest Jaccard Diversity", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig(ROOT / "figures/english_fingerprint_cv_jaccard.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → english_fingerprint_cv_jaccard.png")

# Print MWU: English CV vs each other language (Creatively)
cv_en = cs[cs["target_language"] == "English"]["cv_Creatively"].dropna()
print("  MWU — English CV vs other languages (Creatively, Bonferroni n=9):")
for lang in [l for l in ALL_LANGS if l != "English"]:
    cv_l = cs[cs["target_language"] == lang]["cv_Creatively"].dropna()
    _, p, r = mwu(cv_en, cv_l)
    print(f"    English vs {lang:10s}: p={p:.2e}  r={r:+.3f} {bonferroni_star(p,9)}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — Conventional equivalent locking
# ══════════════════════════════════════════════════════════════════════════════
print("\n[2] Conventional locking …")

# Compute dominant span fraction per (idiom, target_language, strategy)
def dominant_frac(series):
    if len(series) == 0: return np.nan
    vc = series.value_counts(normalize=True)
    return vc.iloc[0]

dom_records = []
for strat, scol in zip(STRATS, SCOLS):
    grp = raw.groupby(["source_language", "idiom", "target_language"])[scol].apply(dominant_frac).reset_index()
    grp.columns = ["source_language", "idiom", "target_language", "dom_frac"]
    grp["strategy"] = strat
    dom_records.append(grp)
dom = pd.concat(dom_records, ignore_index=True)

# Mean dominant frac across strategies per (idiom, target_language)
dom_mean = dom.groupby(["source_language", "idiom", "target_language"])["dom_frac"].mean().reset_index(name="mean_dom_frac")

# Per-language summary
dom_en    = dom_mean[dom_mean["target_language"] == "English"]["mean_dom_frac"].dropna()
dom_other = dom_mean[dom_mean["target_language"] != "English"]["mean_dom_frac"].dropna()

thresh = 0.70
locked_en = dom_mean[(dom_mean["target_language"] == "English") & (dom_mean["mean_dom_frac"] >= thresh)]
print(f"  Locked English idioms (mean_dom_frac ≥ {thresh}): {len(locked_en)}")

# Dominant span text for Creatively in English
en_raw = raw[raw["target_language"] == "English"]
dom_spans = en_raw.groupby(["source_language", "idiom"])["span_creatively"].agg(
    lambda s: s.value_counts().index[0] if len(s) > 0 else ""
).reset_index().rename(columns={"span_creatively": "dominant_span_en"})
locked_en = locked_en.merge(dom_spans, on=["source_language", "idiom"], how="left")

# Mean dom_frac in other languages for the same idiom
dom_others_mean = dom_mean[dom_mean["target_language"] != "English"].groupby(
    ["source_language", "idiom"])["mean_dom_frac"].mean().reset_index(name="mean_dom_frac_other")
locked_en = locked_en.merge(dom_others_mean, on=["source_language", "idiom"], how="left")
locked_en["convergence_gap"] = locked_en["mean_dom_frac"] - locked_en["mean_dom_frac_other"]

# Add divergence score
div_mean_idiom = div.groupby(["source_language", "idiom"])["div_CA_ng1"].mean().reset_index()
locked_en = locked_en.merge(div_mean_idiom, on=["source_language", "idiom"], how="left")

locked_en.to_csv(ROOT / "data/processed/english_locked_idioms.csv", index=False)
print(f"  Saved → english_locked_idioms.csv")
print("  Top locked idioms (by English dom frac):")
for _, r in locked_en.nlargest(10, "mean_dom_frac").iterrows():
    print(f"    [{r['source_language']}] {r['idiom']:12s}  dom={r['mean_dom_frac']:.2f}  "
          f"other={r['mean_dom_frac_other']:.2f}  span={r['dominant_span_en']}")

# Dominant frac by language
dom_by_lang = dom_mean.groupby("target_language")["mean_dom_frac"].agg(
    ["mean", "median", lambda x: (x >= thresh).sum()]
).rename(columns={"mean": "mean_dom_frac", "median": "median_dom_frac", "<lambda_0>": f"n_locked_{thresh}"})
dom_by_lang["resource"] = dom_by_lang.index.map(RESOURCE)
print("\n  Dominant span fraction by target language:")
print(dom_by_lang.sort_values("mean_dom_frac", ascending=False).to_string())

# Figure
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel 1: KDE of mean_dom_frac by language
ax = axes[0]
for lang in ALL_LANGS:
    d = dom_mean[dom_mean["target_language"] == lang]["mean_dom_frac"].dropna()
    lw = 2.5 if lang == "English" else 1.0
    ls = "-" if lang == "English" else ("--" if RESOURCE[lang] == "high" else ":")
    color = COLORS["English"] if lang == "English" else COLORS[RESOURCE[lang]]
    alpha = 1.0 if lang == "English" else 0.4
    d.plot.kde(ax=ax, label=lang if lang in ["English", "Bengali", "German", "Spanish"] else None,
               color=color, lw=lw, ls=ls, alpha=alpha)
ax.axvline(thresh, color="black", lw=1, ls=":", label=f"Lock threshold ({thresh})")
ax.set_xlim(0, 1); ax.set_xlabel("Mean dominant span fraction"); ax.set_title("Distribution by Language")
ax.legend(fontsize=7)

# Panel 2: Top locked idioms (Chinese/Japanese/Korean, English ≥0.7)
ax = axes[1]
top20 = locked_en.nlargest(20, "mean_dom_frac")
colors_bar = [{"Chinese": "#4C72B0", "Japanese": "#DD8452", "Korean": "#55A868"}[s] for s in top20["source_language"]]
bars = ax.barh(range(len(top20)), top20["mean_dom_frac"].values, color=colors_bar)
ax.set_yticks(range(len(top20)))
ax.set_yticklabels([f"{r['idiom']} [{r['source_language'][:2]}]" for _, r in top20.iterrows()], fontsize=7)
ax.set_xlabel("Mean dominant span fraction (English)")
ax.set_title("Top 20 Locked Idioms in English")
ax.axvline(thresh, color="black", lw=1, ls=":")
for bar, (_, r) in zip(bars, top20.iterrows()):
    span_text = str(r["dominant_span_en"])[:25] + ("…" if len(str(r["dominant_span_en"])) > 25 else "")
    ax.text(0.02, bar.get_y() + bar.get_height() / 2, f'"{span_text}"',
            va="center", fontsize=5.5, color="white" if r["mean_dom_frac"] > 0.75 else "black")

# Panel 3: Convergence gap scatter
ax = axes[2]
for src, marker in [("Chinese", "o"), ("Japanese", "s"), ("Korean", "^")]:
    sub = locked_en[locked_en["source_language"] == src]
    ax.scatter(sub["mean_dom_frac_other"], sub["convergence_gap"],
               alpha=0.5, marker=marker, label=src, s=30)
ax.axhline(0, color="black", lw=0.8, ls=":")
ax.set_xlabel("Mean dominant frac in other languages")
ax.set_ylabel("Convergence gap (English − other)")
ax.set_title("Locking is English-specific\n(most points above 0)")
ax.legend(fontsize=8)

fig.suptitle("Conventional Equivalent Locking in English", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/english_locking.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → english_locking.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Strategy divergence by resource level
# ══════════════════════════════════════════════════════════════════════════════
print("\n[3] Divergence by resource level …")

div["resource"] = div["target_language"].map(RESOURCE)
div["mean_div"]  = div[["div_CA_ng1", "div_CAu_ng1", "div_AAu_ng1"]].mean(axis=1)
div["mean_edit"] = div[["edit_CA", "edit_CAu", "edit_AAu"]].mean(axis=1)

print("  Mean divergence by resource group:")
print(div.groupby("resource")[["mean_div", "mean_edit"]].mean().round(4))

print("  MWU high vs low (mean unigram divergence, Bonferroni n=3):")
for metric in ["div_CA_ng1", "div_CAu_ng1", "div_AAu_ng1"]:
    hi = div[div["resource"] == "high"][metric].dropna()
    lo = div[div["resource"] == "low"][metric].dropna()
    _, p, r = mwu(hi, lo)
    print(f"    {metric}: p={p:.2e}  r={r:+.3f} {bonferroni_star(p,3)}")

# Per-language mean divergence ranking
div_lang = div.groupby("target_language")[["div_CA_ng1", "edit_CA"]].mean().reset_index()
div_lang["resource"] = div_lang["target_language"].map(RESOURCE)
div_lang = div_lang.sort_values("div_CA_ng1", ascending=False)
print("\n  Per-language divergence ranking (C→A unigram):")
print(div_lang[["target_language", "resource", "div_CA_ng1", "edit_CA"]].to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Panel 1: violin by resource group
ax = axes[0]
div_plot = div.melt(id_vars=["resource", "target_language"],
                    value_vars=["div_CA_ng1", "div_CAu_ng1", "div_AAu_ng1"],
                    var_name="pair", value_name="divergence")
div_plot["pair"] = div_plot["pair"].map({"div_CA_ng1": "C→A", "div_CAu_ng1": "C→Au", "div_AAu_ng1": "A→Au"})
# Highlight English separately
div_en_only = div_plot[div_plot["target_language"] == "English"].copy()
div_en_only["resource"] = "English"
div_combined = pd.concat([div_plot, div_en_only])
sns.boxplot(data=div_combined[div_combined["resource"].isin(["high", "low", "English"])],
            x="pair", y="divergence", hue="resource",
            hue_order=["high", "low", "English"],
            palette=COLORS, ax=ax, flierprops=dict(marker=".", alpha=0.1, ms=2))
ax.set_xlabel("Strategy pair"); ax.set_ylabel("Unigram divergence")
ax.set_title("Divergence by Resource Group")
ax.legend(title="", fontsize=8)

# Panel 2: dot plot of per-language means
ax = axes[1]
lang_order = div_lang["target_language"].tolist()
colors_dots = [COLORS["English"] if l == "English" else COLORS[RESOURCE[l]] for l in lang_order]
ax.barh(range(len(lang_order)), div_lang["div_CA_ng1"].values, color=colors_dots)
ax.set_yticks(range(len(lang_order))); ax.set_yticklabels(lang_order, fontsize=9)
ax.set_xlabel("Mean C→A unigram divergence")
ax.set_title("Per-Language Divergence Ranking\n(C→A)")
for i, (_, row) in enumerate(div_lang.iterrows()):
    ax.text(row["div_CA_ng1"] + 0.002, i, f"{row['div_CA_ng1']:.3f}", va="center", fontsize=7.5)

fig.suptitle("Strategy Divergence by Target Language and Resource Level", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/divergence_by_resource.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → divergence_by_resource.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Word-level expansion ratio by target language
# ══════════════════════════════════════════════════════════════════════════════
print("\n[4] Word-level expansion ratio …")

raw2 = raw[raw["sentence"].str.len() > 0].copy()
for strat, tcol in zip(STRATS, TCOLS):
    raw2[f"wexp_{strat}"] = raw2[tcol].str.split().str.len() / \
                            raw2["sentence"].str.len().replace(0, np.nan)

wexp_lang = raw2.groupby("target_language")[[f"wexp_{s}" for s in STRATS]].median()
wexp_lang["resource"] = wexp_lang.index.map(RESOURCE)
print("  Median word expansion ratio by target language:")
print(wexp_lang.sort_values("wexp_Creatively", ascending=False).to_string())

print("  MWU high vs low (word expansion, Creatively):")
hi = raw2[raw2["target_language"].isin(HIGH)]["wexp_Creatively"].dropna()
lo = raw2[raw2["target_language"].isin(LOW)]["wexp_Creatively"].dropna()
_, p, r = mwu(hi, lo)
print(f"    p={p:.2e}  r={r:+.3f}")

# Char vs word expansion comparison
char_exp = raw2.groupby("target_language")[[f"translate_{s.lower()}" for s in STRATS]].apply(
    lambda g: g.apply(lambda col: (col.str.len() / raw2.loc[g.index, "sentence"].str.len().replace(0, np.nan)).median())
)
char_exp.columns = [f"cexp_{s}" for s in STRATS]

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
wexp_sorted = wexp_lang.sort_values("wexp_Creatively")
colors_w = [COLORS["English"] if l == "English" else COLORS[RESOURCE[l]] for l in wexp_sorted.index]
ax.barh(range(len(wexp_sorted)), wexp_sorted["wexp_Creatively"].values, color=colors_w)
ax.set_yticks(range(len(wexp_sorted))); ax.set_yticklabels(wexp_sorted.index, fontsize=9)
ax.set_xlabel("Median word-count expansion ratio (Creatively)")
ax.set_title("Word-Level Expansion by Target Language")
for i, v in enumerate(wexp_sorted["wexp_Creatively"].values):
    ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=7.5)

ax = axes[1]
combined = wexp_lang[["wexp_Creatively"]].join(char_exp[["cexp_Creatively"]])
combined["resource"] = combined.index.map(RESOURCE)
for lang in combined.index:
    c = COLORS["English"] if lang == "English" else COLORS[RESOURCE[lang]]
    marker = "D" if lang == "English" else ("o" if RESOURCE[lang] == "high" else "^")
    ax.scatter(combined.loc[lang, "cexp_Creatively"], combined.loc[lang, "wexp_Creatively"],
               color=c, s=60, marker=marker, zorder=3)
    ax.annotate(lang, (combined.loc[lang, "cexp_Creatively"], combined.loc[lang, "wexp_Creatively"]),
                fontsize=7, ha="left", va="bottom", xytext=(3, 3), textcoords="offset points")
ax.set_xlabel("Char-level expansion ratio"); ax.set_ylabel("Word-level expansion ratio")
ax.set_title("Char vs Word Expansion (Creatively)\nDivergence reveals script-density effects")
# Add diagonal reference line
lims = [min(ax.get_xlim()[0], ax.get_ylim()[0]), max(ax.get_xlim()[1], ax.get_ylim()[1])]
ax.plot(lims, lims, "k--", alpha=0.3, lw=1)

fig.suptitle("Word-Level Expansion Ratio by Target Language", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/word_expansion_by_target.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → word_expansion_by_target.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Span position by target language
# ══════════════════════════════════════════════════════════════════════════════
print("\n[5] Span position by target language …")

sp_c = sp[(sp["strategy"] == "Creatively") & (sp["abs_start"] >= 0)].copy()
sp_c["resource"] = sp_c["target_language"].map(RESOURCE)

pos_lang = sp_c.groupby("target_language")["rel_start"].agg(["mean", "median", "std"]).round(3)
pos_lang["resource"] = pos_lang.index.map(RESOURCE)
print("  Mean relative span start by target language (Creatively):")
print(pos_lang.sort_values("mean").to_string())

hi_pos = sp_c[sp_c["target_language"].isin(HIGH)]["rel_start"].dropna()
lo_pos = sp_c[sp_c["target_language"].isin(LOW)]["rel_start"].dropna()
_, p, r = mwu(hi_pos, lo_pos)
print(f"  MWU high vs low (rel_start): p={p:.2e}  r={r:+.3f}")

# Zone proportions
zone_pct = sp_c.groupby("target_language")["position_zone"].value_counts(normalize=True).unstack(fill_value=0)
zone_pct = zone_pct.reindex(columns=["beginning", "middle", "end"], fill_value=0)
zone_pct["resource"] = zone_pct.index.map(RESOURCE)
zone_pct = zone_pct.sort_values("end")

# Source×target interaction
st_pos = sp_c.groupby(["source_language", "target_language"])["rel_start"].mean().unstack()
print("\n  Mean rel_start by source × target language:")
print(st_pos.round(3).to_string())

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Panel 1: stacked bar of zones sorted by "end" proportion
ax = axes[0]
zone_sorted = zone_pct.sort_values("end")
lang_list   = zone_sorted.index.tolist()
colors_zone = {"beginning": "#4C72B0", "middle": "#8172B2", "end": "#C44E52"}
bottoms = np.zeros(len(lang_list))
for zone in ["beginning", "middle", "end"]:
    vals = zone_sorted[zone].values
    bars = ax.barh(range(len(lang_list)), vals, left=bottoms,
                   color=colors_zone[zone], label=zone, alpha=0.85)
    bottoms += vals
ax.set_yticks(range(len(lang_list)))
bar_colors = [COLORS["English"] if l == "English" else "black" for l in lang_list]
ax.set_yticklabels(lang_list, fontsize=9)
for i, lbl in enumerate(lang_list):
    if lbl == "English":
        ax.get_yticklabels()[i].set_color(COLORS["English"])
        ax.get_yticklabels()[i].set_fontweight("bold")
ax.set_xlabel("Proportion of spans")
ax.set_title("Span Position Zone by Target Language\n(Creatively, sorted by 'end')")
ax.legend(loc="lower right", fontsize=8)

# Panel 2: KDE of rel_start, all 10 languages
ax = axes[1]
for lang in ALL_LANGS:
    d = sp_c[sp_c["target_language"] == lang]["rel_start"].dropna()
    lw = 2.5 if lang == "English" else 0.9
    ls = "-" if lang == "English" else ("--" if RESOURCE[lang] == "high" else ":")
    col = COLORS["English"] if lang == "English" else COLORS[RESOURCE[lang]]
    alpha = 1.0 if lang == "English" else 0.4
    label = lang if lang in ["English", "Bengali", "Hindi", "Swahili", "Italian"] else None
    d.plot.kde(ax=ax, color=col, lw=lw, ls=ls, alpha=alpha, label=label)
ax.set_xlim(0, 1); ax.set_xlabel("Relative span start position")
ax.set_title("KDE of Span Position\n(Creatively, all languages)")
ax.legend(fontsize=7)

# Panel 3: source×target heatmap
ax = axes[2]
sns.heatmap(st_pos, annot=True, fmt=".3f", cmap="RdYlGn_r",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Mean rel start"})
ax.set_title("Mean Rel. Start by Source × Target\n(Creatively)")
ax.set_xlabel("Target language"); ax.set_ylabel("Source language")

fig.suptitle("Span Position Distribution by Target Language", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/span_position_by_target.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → span_position_by_target.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — Annotation error rates by target language
# ══════════════════════════════════════════════════════════════════════════════
print("\n[6] Annotation error rates by target language …")

total_by_lang = raw.groupby("target_language").size().rename("total")
flags = ["missing_span", "span_not_in_trans", "span_longer", "span_equals_idiom", "degenerate_trans"]

# anomalies.csv is wide: boolean columns named <flag>_<Strategy>
err_pct = {}
for strat in STRATS:
    tbl = pd.DataFrame(index=ALL_LANGS, columns=flags, dtype=float)
    for flag in flags:
        col = f"{flag}_{strat}"
        if col in an.columns:
            counts = an[an[col] == True].groupby("target_language").size().reindex(ALL_LANGS, fill_value=0)
        else:
            counts = pd.Series(0, index=ALL_LANGS)
        tbl[flag] = counts.values
    tbl = tbl.div(total_by_lang.reindex(ALL_LANGS), axis=0) * 100
    err_pct[strat] = tbl
    print(f"\n  Error rates (%) — {strat}")
    print(tbl.round(3).to_string())

# Focus on span_not_in_trans
sni_table = pd.DataFrame({s: err_pct[s]["span_not_in_trans"] for s in STRATS})
sni_table["resource"] = sni_table.index.map(RESOURCE)
sni_table = sni_table.sort_values("Creatively", ascending=False)
print("\n  Span-not-in-trans rates by target language:")
print(sni_table.to_string())

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Panel 1: heatmap of top 4 error types × 10 languages (Creatively)
ax = axes[0]
heat_data = err_pct["Creatively"][["span_not_in_trans", "span_longer", "span_equals_idiom", "missing_span"]]
heat_data.columns = ["not-in-trans", "span longer", "equals idiom", "missing"]
sns.heatmap(heat_data.loc[ALL_LANGS], annot=True, fmt=".2f", cmap="YlOrRd",
            linewidths=0.5, ax=ax, vmin=0, vmax=7,
            cbar_kws={"label": "Error rate %"})
ax.set_title("Annotation Error Rates (%) by Target Language\n(Creatively strategy)")
ax.set_xlabel("Flag type"); ax.set_ylabel("")
# Bold English row label
for tick in ax.get_yticklabels():
    if tick.get_text() == "English":
        tick.set_fontweight("bold"); tick.set_color(COLORS["English"])

# Panel 2: grouped bar for span_not_in_trans × 3 strategies
ax = axes[1]
x = np.arange(len(ALL_LANGS))
w = 0.25
for i, strat in enumerate(STRATS):
    vals = [err_pct[strat].loc[l, "span_not_in_trans"] for l in ALL_LANGS]
    cols = [COLORS["English"] if l == "English" else COLORS[RESOURCE[l]] for l in ALL_LANGS]
    bars = ax.bar(x + i * w, vals, w, label=strat, alpha=0.75)
ax.set_xticks(x + w); ax.set_xticklabels(ALL_LANGS, rotation=40, ha="right", fontsize=8)
ax.set_ylabel("Span-not-in-translation rate (%)")
ax.set_title("Span-Not-in-Translation by Target Language\n(all 3 strategies)")
ax.legend(fontsize=8)
# mark English
en_x = ALL_LANGS.index("English")
ax.axvspan(en_x - 0.1, en_x + 3 * w + 0.1, alpha=0.08, color=COLORS["English"])

fig.suptitle("Span Annotation Error Rates by Target Language", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/error_rate_by_target.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → error_rate_by_target.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — Cross-strategy span overlap within a target language
# ══════════════════════════════════════════════════════════════════════════════
print("\n[7] Cross-strategy span overlap …")

def jaccard_words(a, b):
    if pd.isna(a) or pd.isna(b) or not a or not b:
        return np.nan
    sa, sb = set(str(a).lower().split()), set(str(b).lower().split())
    if not sa and not sb: return np.nan
    return len(sa & sb) / len(sa | sb)

# Sample for speed (2M rows is too slow for row-level Jaccard in Python)
sample = raw.sample(min(200_000, len(raw)), random_state=42)
sample = sample[sample[SCOLS[0]].notna() & sample[SCOLS[1]].notna() & sample[SCOLS[2]].notna()]

sample["span_jac_CA"]  = [jaccard_words(a, b) for a, b in zip(sample["span_creatively"], sample["span_analogy"])]
sample["span_jac_CAu"] = [jaccard_words(a, b) for a, b in zip(sample["span_creatively"], sample["span_author"])]
sample["span_jac_AAu"] = [jaccard_words(a, b) for a, b in zip(sample["span_analogy"],    sample["span_author"])]
sample["span_jac_mean"] = sample[["span_jac_CA", "span_jac_CAu", "span_jac_AAu"]].mean(axis=1)

span_jac_lang = sample.groupby("target_language")[["span_jac_CA", "span_jac_CAu", "span_jac_AAu", "span_jac_mean"]].mean()
span_jac_lang["resource"] = span_jac_lang.index.map(RESOURCE)
span_jac_lang = span_jac_lang.sort_values("span_jac_mean", ascending=False)
print("  Mean cross-strategy span Jaccard by target language:")
print(span_jac_lang.round(4).to_string())

hi_j = sample[sample["target_language"].isin(HIGH)]["span_jac_CA"].dropna()
lo_j = sample[sample["target_language"].isin(LOW)]["span_jac_CA"].dropna()
en_j = sample[sample["target_language"] == "English"]["span_jac_CA"].dropna()
_, p_hl, r_hl = mwu(hi_j, lo_j)
print(f"  MWU high vs low (span_jac_CA): p={p_hl:.2e}  r={r_hl:+.3f}")

# Correlation with dominant_frac
dom_en_mean = dom_mean[dom_mean["target_language"] == "English"].groupby("target_language")["mean_dom_frac"].mean()
corr_df = span_jac_lang[["span_jac_mean"]].copy()
corr_df["mean_dom_frac"] = [dom_mean[dom_mean["target_language"] == l]["mean_dom_frac"].mean() for l in corr_df.index]
rho, p_corr = stats.spearmanr(corr_df["span_jac_mean"], corr_df["mean_dom_frac"])
print(f"  Spearman ρ(span_jac_mean, mean_dom_frac) across languages: ρ={rho:.3f}  p={p_corr:.3f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Panel 1: heatmap of span_jac by language × pair
ax = axes[0]
jac_heat = span_jac_lang[["span_jac_CA", "span_jac_CAu", "span_jac_AAu"]].copy()
jac_heat.columns = ["C vs A", "C vs Au", "A vs Au"]
sns.heatmap(jac_heat, annot=True, fmt=".3f", cmap="YlGnBu",
            linewidths=0.5, ax=ax, cbar_kws={"label": "Mean Jaccard"})
ax.set_title("Cross-Strategy Span Word Overlap\nby Target Language")
for tick in ax.get_yticklabels():
    if tick.get_text() == "English":
        tick.set_fontweight("bold"); tick.set_color(COLORS["English"])

# Panel 2: KDE of span_jac_CA for high vs low vs English
ax = axes[1]
for group, label, ls in [("high", "High-resource (excl. EN)", "--"), ("low", "Low-resource", ":")]:
    langs = [l for l in (HIGH if group == "high" else LOW) if l != "English"]
    d = sample[sample["target_language"].isin(langs)]["span_jac_CA"].dropna()
    d.plot.kde(ax=ax, label=label, color=COLORS[group], lw=1.5, ls=ls, alpha=0.8)
en_j.plot.kde(ax=ax, label="English", color=COLORS["English"], lw=2.5)
ax.set_xlabel("Cross-strategy span Jaccard (C vs A)")
ax.set_title("Distribution of Span Similarity\nAcross Strategies (C vs A)")
ax.set_xlim(0, 1); ax.legend(fontsize=9)

fig.suptitle("Cross-Strategy Span Overlap by Target Language", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/cross_strategy_span_overlap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → cross_strategy_span_overlap.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — Resource profile synthesis
# ══════════════════════════════════════════════════════════════════════════════
print("\n[8] Resource profile synthesis …")

profile = pd.DataFrame(index=ALL_LANGS)

# CV and Jaccard from context_sensitivity
cs_en_grp = cs.groupby("target_language")[["cv_Creatively", "jaccard_div_Creatively", "span_uniq_Creatively"]].mean()
profile["cv"]          = cs_en_grp["cv_Creatively"]
profile["jaccard_div"] = cs_en_grp["jaccard_div_Creatively"]
profile["span_uniq"]   = cs_en_grp["span_uniq_Creatively"]

# Divergence
div_grp = div.groupby("target_language")[["div_CA_ng1", "edit_CA"]].mean()
profile["div_CA"]  = div_grp["div_CA_ng1"]
profile["edit_CA"] = div_grp["edit_CA"]

# Span position
sp_grp = sp[(sp["strategy"] == "Creatively") & (sp["abs_start"] >= 0)].groupby("target_language")["rel_start"].mean()
profile["rel_start"] = sp_grp

# Span ratio (char level)
raw["span_ratio_C"] = raw["span_creatively"].str.len() / raw["translate_creatively"].str.len().replace(0, np.nan)
sr_grp = raw.groupby("target_language")["span_ratio_C"].mean()
profile["span_ratio"] = sr_grp

# Word expansion
wexp_grp = raw2.groupby("target_language")["wexp_Creatively"].median()
profile["wexp"] = wexp_grp

# Error rate
sni_col = sni_table["Creatively"]
profile["error_rate"] = sni_col

# Dominant frac
dom_grp = dom_mean.groupby("target_language")["mean_dom_frac"].mean()
profile["dom_frac"] = dom_grp

# Cross-strategy span Jaccard
sj_grp = sample.groupby("target_language")["span_jac_CA"].mean()
profile["span_jac_CA"] = sj_grp

profile["resource"] = profile.index.map(RESOURCE)
profile = profile.dropna()
print("  Profile matrix:")
print(profile.drop("resource", axis=1).round(4).to_string())

profile.to_parquet(ROOT / "data/processed/target_language_profile.parquet")
print("  Saved → target_language_profile.parquet")

# MWU for each metric (high vs low), BH correction
from statsmodels.stats.multitest import multipletests
metrics = ["cv", "jaccard_div", "span_uniq", "div_CA", "edit_CA",
           "rel_start", "span_ratio", "wexp", "error_rate", "dom_frac", "span_jac_CA"]
mwu_results = []
for m in metrics:
    hi_v = profile.loc[profile["resource"] == "high", m].dropna()
    lo_v = profile.loc[profile["resource"] == "low",  m].dropna()
    if len(hi_v) < 2 or len(lo_v) < 2: continue
    _, p, r = mwu(hi_v.values, lo_v.values)
    direction = "high>low" if hi_v.mean() > lo_v.mean() else "low>high"
    mwu_results.append({"metric": m, "p_raw": p, "r": r, "direction": direction,
                         "high_mean": hi_v.mean(), "low_mean": lo_v.mean()})
mwu_df = pd.DataFrame(mwu_results)
_, mwu_df["p_adj"], _, _ = multipletests(mwu_df["p_raw"], method="fdr_bh")
print("\n  MWU results (high vs low), BH-corrected:")
print(mwu_df[["metric","direction","high_mean","low_mean","r","p_raw","p_adj"]].round(4).to_string(index=False))

# PCA
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

num_cols = metrics
feat = profile[num_cols].dropna()
X = StandardScaler().fit_transform(feat)
pca = PCA(n_components=2)
coords = pca.fit_transform(X)
pca_df = pd.DataFrame(coords, index=feat.index, columns=["PC1", "PC2"])
pca_df["resource"] = pca_df.index.map(RESOURCE)
print(f"\n  PCA explained variance: PC1={pca.explained_variance_ratio_[0]:.1%}  PC2={pca.explained_variance_ratio_[1]:.1%}")

# Radar chart data (normalised 0-1)
radar_cols = ["cv", "jaccard_div", "div_CA", "rel_start", "span_ratio",
              "wexp", "error_rate", "dom_frac", "span_jac_CA"]
normed = profile[radar_cols].copy()
for c in radar_cols:
    cmin, cmax = normed[c].min(), normed[c].max()
    normed[c] = (normed[c] - cmin) / (cmax - cmin + 1e-9)
high_radar = normed[profile["resource"] == "high"].mean()
low_radar  = normed[profile["resource"] == "low"].mean()
en_radar   = normed.loc["English"]

fig = plt.figure(figsize=(16, 6))

# Radar
ax_r = fig.add_subplot(1, 3, 1, polar=True)
angles = np.linspace(0, 2 * np.pi, len(radar_cols), endpoint=False).tolist()
angles += angles[:1]
radar_labels = ["CV", "Jaccard div", "Divergence", "Span position",
                "Span ratio", "Word exp", "Error rate", "Dom frac", "Span Jac"]
for vals, label, color, ls in [
    (high_radar.values.tolist(), "High-resource", "#4C72B0", "--"),
    (low_radar.values.tolist(),  "Low-resource",  "#DD8452", ":"),
    (en_radar.values.tolist(),   "English",        "#C44E52", "-"),
]:
    vals_circ = vals + vals[:1]
    ax_r.plot(angles, vals_circ, color=color, lw=2, ls=ls, label=label)
    ax_r.fill(angles, vals_circ, color=color, alpha=0.07)
ax_r.set_thetagrids(np.degrees(angles[:-1]), radar_labels, fontsize=7.5)
ax_r.set_title("Resource Profile\n(normalised metrics)", pad=15, fontsize=9)
ax_r.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1), fontsize=8)

# PCA biplot
ax_p = fig.add_subplot(1, 3, 2)
for lang in pca_df.index:
    c = COLORS["English"] if lang == "English" else COLORS[RESOURCE[lang]]
    m = "D" if lang == "English" else ("o" if RESOURCE[lang] == "high" else "^")
    ax_p.scatter(pca_df.loc[lang, "PC1"], pca_df.loc[lang, "PC2"], color=c, marker=m, s=80, zorder=3)
    ax_p.annotate(lang, (pca_df.loc[lang, "PC1"], pca_df.loc[lang, "PC2"]),
                  xytext=(4, 4), textcoords="offset points", fontsize=7.5)
ax_p.axhline(0, color="gray", lw=0.5); ax_p.axvline(0, color="gray", lw=0.5)
ax_p.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.0%})")
ax_p.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.0%})")
ax_p.set_title("PCA of Target Language Profiles")

# MWU summary heatmap
ax_h = fig.add_subplot(1, 3, 3)
heat = mwu_df.set_index("metric")[["r", "p_adj"]].copy()
heat["sig"] = heat["p_adj"].apply(lambda p: "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else "")))
heat_r = heat[["r"]].T
sns.heatmap(heat_r, annot=True, fmt=".3f", cmap="RdBu", center=0,
            linewidths=0.5, ax=ax_h, vmin=-1, vmax=1,
            cbar_kws={"label": "Rank-biserial r"})
for i, (_, row) in enumerate(heat.iterrows()):
    ax_h.text(i + 0.5, 1.6, row["sig"], ha="center", fontsize=9, color="black")
ax_h.set_title("MWU Effect Sizes\n(high vs low resource, * = BH-adj. sig.)")
ax_h.set_yticklabels(["effect r"], rotation=0, fontsize=8)
ax_h.set_xticklabels(heat.index.tolist(), rotation=45, ha="right", fontsize=7.5)

fig.suptitle("Target Language Resource-Level Profile Synthesis", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(ROOT / "figures/resource_profile_synthesis.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("  Saved → resource_profile_synthesis.png")

print("\n✓ All sections complete.")
