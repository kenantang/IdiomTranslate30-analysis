"""
Chinese–Korean saseong-eoro cognate identification.

Three-layer transliteration pipeline:
  Layer 1  Unihan kHangul — authoritative Unicode per-codepoint Hangul readings,
           covers both simplified and traditional CJK characters directly.
  Layer 2  OpenCC s2t + Unihan — convert simplified → traditional, then kHangul.
  Layer 3  hanja library — fallback for chars still unresolved after layers 1–2.

Matching tiers:
  Exact    All 4 predicted Hangul syllables match the Korean idiom.
  Near-3   Exactly 3 of 4 positions match (partial cognate / variant spelling).
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import re
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr

from utils import build_kHangul_map, build_s2t_converter, char_to_hangul, idiom_to_hangul_tuple, STRATEGY_COLORS

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
EXT  = ROOT / "data/external"
PROC = ROOT / "data/processed"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

df        = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
zh_idioms = df[df["source_language"]=="Chinese"]["idiom"].unique()
ko_idioms = df[df["source_language"]=="Korean"]["idiom"].unique()
ja_idioms = df[df["source_language"]=="Japanese"]["idiom"].unique()
ko_set    = set(ko_idioms)

# ══════════════════════════════════════════════════════════════════════════════
# 1. Build Unihan kHangul char → first Hangul syllable map  (H10)
# ══════════════════════════════════════════════════════════════════════════════
print("Building Unihan kHangul map…")
unihan_path = EXT / "Unihan_Readings.txt"
kh_map = build_kHangul_map(unihan_path)
print(f"  {len(kh_map):,} codepoints with kHangul readings")

# ══════════════════════════════════════════════════════════════════════════════
# 2. OpenCC simplified → traditional converter  (H9)
# ══════════════════════════════════════════════════════════════════════════════
s2t = build_s2t_converter()

# ══════════════════════════════════════════════════════════════════════════════
# 3. Three-layer per-character transliteration  (H10)
# ══════════════════════════════════════════════════════════════════════════════
print("\nTransliterating Chinese idioms (3-layer)…")
zh_hangul = {}   # idiom → tuple of 4 Hangul syllables (or None)
unresolved_chars = set()
for idiom in zh_idioms:
    tup = idiom_to_hangul_tuple(idiom, kh_map, s2t)
    zh_hangul[idiom] = tup
    unresolved_chars.update(c for c, h in zip(idiom, tup) if h is None)

fully_resolved = sum(1 for t in zh_hangul.values() if all(h is not None for h in t))
print(f"  Fully resolved:   {fully_resolved:,} / {len(zh_idioms):,}")
print(f"  Unresolvable chars: {len(unresolved_chars)} unique — {sorted(unresolved_chars)[:15]}")

# ══════════════════════════════════════════════════════════════════════════════
# 5. Build Korean idiom → tuple map for fast matching
# ══════════════════════════════════════════════════════════════════════════════
ko_tuple = {ko: tuple(ko) for ko in ko_idioms}   # char == syllable for Hangul

# ══════════════════════════════════════════════════════════════════════════════
# 6. Exact matching (all 4 positions)
# ══════════════════════════════════════════════════════════════════════════════
exact_cognates = {}   # zh → ko
for zh, zh_tup in zh_hangul.items():
    if None in zh_tup:
        continue
    joined = "".join(zh_tup)
    if joined in ko_set:
        exact_cognates[zh] = joined

print(f"\nExact cognates (4/4 match): {len(exact_cognates):,}")
print(f"  As % of Chinese: {len(exact_cognates)/len(zh_idioms)*100:.1f}%")
print(f"  As % of Korean:  {len(exact_cognates)/len(ko_idioms)*100:.1f}%")

# ══════════════════════════════════════════════════════════════════════════════
# 7. Near-3 matching — vectorised with numpy
# ══════════════════════════════════════════════════════════════════════════════
print("\nComputing near-3 matches (3/4 positions, vectorised)…")

# Build character-level arrays: only 4-char, fully resolved idioms
zh_resolved = {zh: tup for zh, tup in zh_hangul.items()
               if None not in tup and len(tup) == 4
               and "".join(tup) not in ko_set}   # exclude exact matches

# Encode each Hangul syllable as a unicode codepoint for numpy comparison
zh_keys  = list(zh_resolved.keys())
zh_arr   = np.array([[ord(c) for c in tup] for tup in zh_resolved.values()],
                    dtype=np.int32)    # shape: (n_zh, 4)

ko_keys  = [ko for ko in ko_idioms if len(ko) == 4]
ko_arr   = np.array([[ord(c) for c in ko] for ko in ko_keys],
                    dtype=np.int32)    # shape: (n_ko, 4)

# Broadcast comparison: (n_zh, 1, 4) == (1, n_ko, 4) → (n_zh, n_ko, 4)
# Process in chunks to avoid OOM at 4306 × 2316 × 4 × 4 bytes ≈ 160 MB
CHUNK = 500
near3_cognates = []
for start in range(0, len(zh_keys), CHUNK):
    zh_chunk = zh_arr[start:start+CHUNK]        # (chunk, 4)
    match_mat = (zh_chunk[:, None, :] == ko_arr[None, :, :])  # (chunk, n_ko, 4)
    n_match   = match_mat.sum(axis=2)            # (chunk, n_ko)
    rows_i, cols_j = np.where(n_match == 3)
    for i, j in zip(rows_i, cols_j):
        zh_idx   = start + i
        mm_pos   = int(np.where(~match_mat[i, j])[0][0])
        near3_cognates.append({
            "zh_idiom":    zh_keys[zh_idx],
            "ko_idiom":    ko_keys[j],
            "zh_hangul":   "".join(chr(x) for x in zh_arr[zh_idx]),
            "n_match":     3,
            "mismatch_pos": mm_pos,
        })

near3_df = pd.DataFrame(near3_cognates).drop_duplicates(subset=["zh_idiom","ko_idiom"])
print(f"Near-3 pairs: {len(near3_df):,}")
print(f"  Unique Chinese idioms involved: {near3_df['zh_idiom'].nunique():,}")
print(f"  Unique Korean idioms involved:  {near3_df['ko_idiom'].nunique():,}")
print(f"\nSample near-3 pairs:")
for _, row in near3_df.head(15).iterrows():
    mm = row["mismatch_pos"]
    print(f"  ZH:{row['zh_idiom']} → ZH_hangul:{row['zh_hangul']}  KO:{row['ko_idiom']}  "
          f"mismatch pos {mm}: {row['zh_hangul'][mm]}≠{row['ko_idiom'][mm]}")

print(f"\nSample exact cognates:")
for zh, ko in list(exact_cognates.items())[:15]:
    print(f"  ZH: {zh}  →  SK: {ko}")

# ══════════════════════════════════════════════════════════════════════════════
# 8. Method comparison (old hanja-only vs new 3-layer)
# ══════════════════════════════════════════════════════════════════════════════
# Reconstruct old method result for comparison
print("\nReconstructing old hanja-only results for comparison…")
import hanja as hanja_lib  # needed only for the old-method comparison below
old_cognates = {}
for zh in zh_idioms:
    try:
        sk = hanja_lib.translate(zh, "substitution")
        if sk and len(sk) == len(zh) and sk in ko_set:
            old_cognates[zh] = sk
    except Exception:
        pass

new_only    = set(exact_cognates) - set(old_cognates)
old_only    = set(old_cognates)   - set(exact_cognates)
both        = set(exact_cognates) & set(old_cognates)
print(f"  Old method (hanja only): {len(old_cognates):,} exact")
print(f"  New method (3-layer):    {len(exact_cognates):,} exact")
print(f"  Gained by new method:    {len(new_only):,}")
print(f"  Lost (old had, new doesn't): {len(old_only):,}")
if old_only:
    print(f"  Lost examples: {list(old_only)[:5]}")

# ══════════════════════════════════════════════════════════════════════════════
# 9. Translation similarity analysis on exact cognates
# ══════════════════════════════════════════════════════════════════════════════
SPAN_COLS  = ["span_creatively","span_analogy","span_author"]
LABELS     = ["Creatively","Analogy","Author"]
COLORS     = STRATEGY_COLORS

def mean_span_len(idiom_list, lang):
    sub = df[df["source_language"]==lang]
    rows = []
    for idiom in idiom_list:
        grp = sub[sub["idiom"]==idiom]
        row = {"idiom": idiom}
        for sc, lbl in zip(SPAN_COLS, LABELS):
            row[f"slen_{lbl}"] = grp[sc].str.len().mean()
        rows.append(row)
    return pd.DataFrame(rows).set_index("idiom")

cog_list = list(exact_cognates.keys())
zh_spans = mean_span_len(cog_list, "Chinese")
ko_spans = mean_span_len(list(exact_cognates.values()), "Korean")
ko_spans.index = cog_list

print("\nSpearman ρ — ZH vs KO span length for exact cognates:")
for lbl in LABELS:
    valid = zh_spans[f"slen_{lbl}"].notna() & ko_spans[f"slen_{lbl}"].notna()
    r, p = spearmanr(zh_spans.loc[valid, f"slen_{lbl}"],
                     ko_spans.loc[valid, f"slen_{lbl}"])
    print(f"  {lbl:<14} ρ={r:.3f}  p={p:.2e}  n={valid.sum()}")

# Near-3: same analysis on subset
if len(near3_df) > 20:
    n3_zh_list = near3_df["zh_idiom"].tolist()
    n3_ko_list = near3_df["ko_idiom"].tolist()
    n3_zh_spans = mean_span_len(n3_zh_list, "Chinese")
    n3_ko_spans = mean_span_len(n3_ko_list, "Korean")
    n3_ko_spans.index = n3_zh_list
    print("\nSpearman ρ — ZH vs KO span length for near-3 cognates:")
    for lbl in LABELS:
        valid = n3_zh_spans[f"slen_{lbl}"].notna() & n3_ko_spans[f"slen_{lbl}"].notna()
        r, p = spearmanr(n3_zh_spans.loc[valid, f"slen_{lbl}"],
                         n3_ko_spans.loc[valid, f"slen_{lbl}"])
        print(f"  {lbl:<14} ρ={r:.3f}  p={p:.2e}  n={valid.sum()}")

# ══════════════════════════════════════════════════════════════════════════════
# 10. Figures
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# 10a: Method comparison bar
ax = axes[0, 0]
method_data = pd.Series({
    "hanja only\n(old)": len(old_cognates),
    "3-layer exact\n(new)": len(exact_cognates),
    "near-3\n(partial)": len(near3_df),
    "total linked\n(exact+near3)": len(exact_cognates) + near3_df["zh_idiom"].nunique() - len(set(exact_cognates) & set(near3_df["zh_idiom"].tolist())),
})
method_data.plot(kind="bar", ax=ax, color=["#AEB6BF","#4C72B0","#DD8452","#55A868"], width=0.6)
ax.set_title("Cognate Pairs by Method", fontweight="bold")
ax.set_ylabel("Count of pairs")
ax.tick_params(axis="x", rotation=15)
for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
            str(int(bar.get_height())), ha="center", va="bottom", fontsize=9)

# 10b: Span length scatter — exact cognates (Creatively)
ax = axes[0, 1]
lbl = "Creatively"
valid = zh_spans[f"slen_{lbl}"].notna() & ko_spans[f"slen_{lbl}"].notna()
ax.scatter(zh_spans.loc[valid, f"slen_{lbl}"],
           ko_spans.loc[valid, f"slen_{lbl}"],
           alpha=0.45, s=15, color="#4C72B0", label="Exact (4/4)")
if len(near3_df) > 5:
    valid_n3 = n3_zh_spans[f"slen_{lbl}"].notna() & n3_ko_spans[f"slen_{lbl}"].notna()
    ax.scatter(n3_zh_spans.loc[valid_n3, f"slen_{lbl}"],
               n3_ko_spans.loc[valid_n3, f"slen_{lbl}"],
               alpha=0.25, s=8, color="#DD8452", label="Near-3")
ax.set_title(f"ZH vs KO Span Length — Cognates\n({lbl})", fontweight="bold")
ax.set_xlabel("Chinese idiom span length (chars)")
ax.set_ylabel("Korean idiom span length (chars)")
r, _ = spearmanr(zh_spans.loc[valid, f"slen_{lbl}"],
                 ko_spans.loc[valid, f"slen_{lbl}"])
ax.text(0.05, 0.95, f"ρ={r:.3f} (exact)", transform=ax.transAxes, va="top", fontsize=10)
ax.legend(fontsize=8)

# 10c: Coverage venn-style bars
ax = axes[1, 0]
cov = pd.Series({
    "ZH total": len(zh_idioms),
    "ZH exact cognate": len(exact_cognates),
    "ZH near-3 cognate": near3_df["zh_idiom"].nunique(),
    "KO total": len(ko_idioms),
    "KO exact cognate": len(exact_cognates),
    "KO near-3 cognate": near3_df["ko_idiom"].nunique(),
})
colors = ["#4C72B0","#4C72B0","#4C72B0","#55A868","#55A868","#55A868"]
alphas = [1.0, 0.7, 0.4, 1.0, 0.7, 0.4]
bars = ax.barh(cov.index[::-1], cov.values[::-1], color=colors[::-1])
ax.set_title("Cognate Coverage by Language", fontweight="bold")
ax.set_xlabel("Count of unique idioms")

# 10d: Mismatch position distribution for near-3
ax = axes[1, 1]
if len(near3_df) > 0:
    near3_df["mismatch_pos"].value_counts().sort_index().plot(
        kind="bar", ax=ax, color="#DD8452", width=0.6)
    ax.set_title("Near-3 Cognates: Mismatch Position\n(0=first char, 3=last char)", fontweight="bold")
    ax.set_ylabel("Number of pairs")
    ax.set_xlabel("Position of mismatched syllable")
    ax.tick_params(axis="x", rotation=0)

fig.suptitle("Chinese–Korean Cognate Analysis (Improved 3-Layer Method)",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "cjk_cognates.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/cjk_cognates.png")

# ══════════════════════════════════════════════════════════════════════════════
# 11. Save results
# ══════════════════════════════════════════════════════════════════════════════
# Exact cognates
exact_df = pd.DataFrame([
    {"zh_idiom": zh, "ko_idiom": ko, "match_type": "exact_4/4"}
    for zh, ko in exact_cognates.items()
])

# Near-3
near3_df["match_type"] = "near_3/4"
all_cognates = pd.concat([
    exact_df[["zh_idiom","ko_idiom","match_type"]],
    near3_df[["zh_idiom","ko_idiom","match_type"]]
], ignore_index=True)

all_cognates.to_csv(PROC / "cjk_cognate_pairs.csv", index=False)
print(f"Saved → data/processed/cjk_cognate_pairs.csv "
      f"({len(exact_df)} exact + {len(near3_df)} near-3 = {len(all_cognates)} total)")
