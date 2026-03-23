"""
Module 10 — Extended CJK cognate analysis: ZH-JA and KO-JA pairs.

Matching pipelines
  ZH–JA  Both use CJK characters. Normalise with OpenCC s2t (simplified/shinjitai →
         traditional) then exact and near-3 string comparison.
  KO–JA  Japanese kanji → predicted Korean Hangul via Unihan kHangul (+ s2t fallback),
         then exact and near-3 match against Korean saseong-eoro.
         Mirrors the ZH–KO pipeline in module todo2.

Quantitative comparison
  For every matched pair × target language: sentence length, translation length,
  expansion ratio, span length, cross-source edit distance and Jaccard similarity.
  Results compared across all three language-pair directions:
    ZH–KO (from module9), ZH–JA, KO–JA.
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import opencc
from pathlib import Path
from scipy.stats import wilcoxon, spearmanr
from rapidfuzz.distance import Levenshtein

ROOT  = Path(__file__).parent.parent
FIG   = ROOT / "figures"
PROC  = ROOT / "data/processed"
EXT   = ROOT / "data/external"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
SCOLS  = ["span_creatively",      "span_analogy",      "span_author"]
LABELS = ["Creatively", "Analogy", "Author"]
COLORS = ["#4C72B0", "#DD8452", "#55A868"]
HIGH_RES = {"English","French","German","Spanish","Italian","Russian"}

# ══════════════════════════════════════════════════════════════════════════════
# 0. Load shared resources
# ══════════════════════════════════════════════════════════════════════════════
print("Loading data and resources…")
df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
s2t = opencc.OpenCC("s2t")

zh_idioms = df[df["source_language"]=="Chinese"]["idiom"].unique()
ko_idioms = df[df["source_language"]=="Korean"]["idiom"].unique()
ja_idioms = df[df["source_language"]=="Japanese"]["idiom"].unique()
ko_set    = set(ko_idioms)
zh_set    = set(zh_idioms)
ja_set    = set(ja_idioms)

# Unihan kHangul map (char → first Hangul syllable)
kh_map = {}
for line in (EXT / "Unihan_Readings.txt").read_text(encoding="utf-8").splitlines():
    if "\tkHangul\t" not in line: continue
    parts = line.split("\t")
    kh_map[chr(int(parts[0][2:], 16))] = parts[2].split()[0].split(":")[0]

import hanja as hanja_lib

def char_to_hangul(ch):
    if ch in kh_map:         return kh_map[ch]
    trad = s2t.convert(ch)
    if trad != ch and trad in kh_map: return kh_map[trad]
    try:
        r = hanja_lib.translate(ch, "substitution")
        if r and len(r)==1 and "\uac00"<=r<="\ud7a3": return r
    except Exception: pass
    return None

def idiom_to_hangul(idiom):
    return tuple(char_to_hangul(c) for c in idiom)

# ══════════════════════════════════════════════════════════════════════════════
# 1. ZH–JA COGNATES (character-level CJK comparison)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── ZH–JA cognates ──")

# Normalise to traditional Chinese
zh_norm_map = {i: s2t.convert(i) for i in zh_idioms}
ja_norm_map = {i: s2t.convert(i) for i in ja_idioms}
# Reverse: traditional form → list of original idioms (for lookup)
ja_trad2orig = {}
for ja, jt in ja_norm_map.items():
    ja_trad2orig.setdefault(jt, []).append(ja)

# Exact matches
zhja_exact = {}   # zh_idiom → ja_idiom
for zh, zt in zh_norm_map.items():
    if zt in ja_trad2orig:
        zhja_exact[zh] = ja_trad2orig[zt][0]   # take first if multiple
print(f"ZH–JA exact (s2t normalised): {len(zhja_exact):,}")
print(f"  As % of ZH: {len(zhja_exact)/len(zh_idioms)*100:.1f}%")
print(f"  As % of JA: {len(zhja_exact)/len(ja_idioms)*100:.1f}%")
print("  Sample:", [(k,v) for k,v in list(zhja_exact.items())[:8]])

# Near-3: encode normalised chars as codepoints, vectorised
zh_resolved_zhja = {zh: tuple(ord(c) for c in zt)
                    for zh, zt in zh_norm_map.items()
                    if len(zt)==4 and zh not in zhja_exact}
ja_resolved_zhja = [(ja, tuple(ord(c) for c in jt))
                    for ja, jt in ja_norm_map.items()
                    if len(jt)==4]

zh_keys_zj = list(zh_resolved_zhja.keys())
zh_arr_zj  = np.array(list(zh_resolved_zhja.values()), dtype=np.int32)
ja_keys_zj = [x[0] for x in ja_resolved_zhja]
ja_arr_zj  = np.array([x[1] for x in ja_resolved_zhja], dtype=np.int32)

print("Computing ZH–JA near-3 matches…")
zhja_near3 = []
CHUNK = 500
for start in range(0, len(zh_keys_zj), CHUNK):
    zh_chunk = zh_arr_zj[start:start+CHUNK]
    match_mat = (zh_chunk[:,None,:] == ja_arr_zj[None,:,:])
    n_match   = match_mat.sum(axis=2)
    rows_i, cols_j = np.where(n_match == 3)
    for i, j in zip(rows_i, cols_j):
        mm = int(np.where(~match_mat[i,j])[0][0])
        zhja_near3.append({
            "zh_idiom": zh_keys_zj[start+i],
            "ja_idiom": ja_keys_zj[j],
            "match_type": "near_3/4",
            "mismatch_pos": mm,
        })
zhja_near3_df = pd.DataFrame(zhja_near3).drop_duplicates(["zh_idiom","ja_idiom"])
print(f"ZH–JA near-3 pairs: {len(zhja_near3_df):,}  "
      f"(unique ZH: {zhja_near3_df['zh_idiom'].nunique():,}, "
      f"JA: {zhja_near3_df['ja_idiom'].nunique():,})")

zhja_all = pd.concat([
    pd.DataFrame([{"zh_idiom":k,"ja_idiom":v,"match_type":"exact_4/4"}
                  for k,v in zhja_exact.items()]),
    zhja_near3_df[["zh_idiom","ja_idiom","match_type"]]
], ignore_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# 2. KO–JA COGNATES (Hangul transliteration of JA kanji)
# ══════════════════════════════════════════════════════════════════════════════
print("\n── KO–JA cognates ──")

# Transliterate each JA idiom to predicted Korean
print("Transliterating JA idioms to Sino-Korean…")
ja_hangul = {}
for idiom in ja_idioms:
    tup = idiom_to_hangul(idiom)
    ja_hangul[idiom] = tup

fully_res = sum(1 for t in ja_hangul.values() if all(h is not None for h in t))
print(f"  Fully resolved: {fully_res:,} / {len(ja_idioms):,}")

# Exact
koja_exact = {}
for ja, tup in ja_hangul.items():
    if None in tup: continue
    joined = "".join(tup)
    if joined in ko_set:
        koja_exact[ja] = joined

print(f"KO–JA exact: {len(koja_exact):,}")
print(f"  As % of JA: {len(koja_exact)/len(ja_idioms)*100:.1f}%")
print(f"  As % of KO: {len(koja_exact)/len(ko_idioms)*100:.1f}%")
print("  Sample:", list(koja_exact.items())[:8])

# Near-3 vectorised
ja_resolved_kj = {ja: tup for ja, tup in ja_hangul.items()
                  if None not in tup and len(tup)==4
                  and "".join(tup) not in ko_set}
ko_tuples_kj   = [(ko, tuple(ord(c) for c in ko)) for ko in ko_idioms if len(ko)==4]

ja_keys_kj = list(ja_resolved_kj.keys())
ja_arr_kj  = np.array([[ord(c) for c in t] for t in ja_resolved_kj.values()], dtype=np.int32)
ko_keys_kj = [x[0] for x in ko_tuples_kj]
ko_arr_kj  = np.array([x[1] for x in ko_tuples_kj], dtype=np.int32)

print("Computing KO–JA near-3 matches…")
koja_near3 = []
for start in range(0, len(ja_keys_kj), CHUNK):
    ja_chunk = ja_arr_kj[start:start+CHUNK]
    match_mat = (ja_chunk[:,None,:] == ko_arr_kj[None,:,:])
    n_match   = match_mat.sum(axis=2)
    rows_i, cols_j = np.where(n_match == 3)
    for i, j in zip(rows_i, cols_j):
        mm = int(np.where(~match_mat[i,j])[0][0])
        koja_near3.append({
            "ja_idiom": ja_keys_kj[start+i],
            "ko_idiom": ko_keys_kj[j],
            "ja_hangul": "".join(chr(x) for x in ja_arr_kj[start+i]),
            "match_type": "near_3/4",
            "mismatch_pos": mm,
        })
koja_near3_df = pd.DataFrame(koja_near3).drop_duplicates(["ja_idiom","ko_idiom"])
print(f"KO–JA near-3: {len(koja_near3_df):,}  "
      f"(unique JA: {koja_near3_df['ja_idiom'].nunique():,}, "
      f"KO: {koja_near3_df['ko_idiom'].nunique():,})")

koja_all = pd.concat([
    pd.DataFrame([{"ja_idiom":k,"ko_idiom":v,"match_type":"exact_4/4"}
                  for k,v in koja_exact.items()]),
    koja_near3_df[["ja_idiom","ko_idiom","match_type"]]
], ignore_index=True)

# Save all cognate tables
zhja_all.to_csv(PROC / "zhja_cognate_pairs.csv", index=False)
koja_all.to_csv(PROC / "koja_cognate_pairs.csv", index=False)
print(f"\nSaved ZH–JA pairs: {len(zhja_all):,}  KO–JA pairs: {len(koja_all):,}")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Quantitative sentence + translation comparison
# ══════════════════════════════════════════════════════════════════════════════
def build_pair_table(cog_df, langA, colA, langB, colB):
    """Align cognate rows by target language and compute comparative metrics."""
    sub_A = df[df["source_language"]==langA].copy()
    sub_B = df[df["source_language"]==langB].copy()
    records = []
    for _, row in cog_df.iterrows():
        grp_A = sub_A[sub_A["idiom"]==row[colA]]
        grp_B = sub_B[sub_B["idiom"]==row[colB]]
        for tgt in grp_A["target_language"].unique():
            sA = grp_A[grp_A["target_language"]==tgt]
            sB = grp_B[grp_B["target_language"]==tgt]
            if sA.empty or sB.empty: continue
            rec = {
                f"{colA}": row[colA], f"{colB}": row[colB],
                "match_type": row["match_type"],
                "target_language": tgt,
                "resource": "high" if tgt in HIGH_RES else "low",
                "sent_len_A": sA["sentence"].str.len().mean(),
                "sent_len_B": sB["sentence"].str.len().mean(),
            }
            for tc, sc, lbl in zip(TCOLS, SCOLS, LABELS):
                ta, tb = sA[tc].str.len().mean(), sB[tc].str.len().mean()
                rec[f"tlen_A_{lbl}"] = ta
                rec[f"tlen_B_{lbl}"] = tb
                rec[f"tlen_diff_{lbl}"] = ta - tb
                rec[f"slen_A_{lbl}"] = sA[sc].str.len().mean()
                rec[f"slen_B_{lbl}"] = sB[sc].str.len().mean()
                # One-sentence divergence
                r_A, r_B = sA.iloc[0][tc], sB.iloc[0][tc]
                ml = max(len(str(r_A)), len(str(r_B)))
                rec[f"edit_{lbl}"] = Levenshtein.distance(str(r_A), str(r_B))/ml if ml else 0
                wA = set(str(r_A).lower().split())
                wB = set(str(r_B).lower().split())
                rec[f"jaccard_{lbl}"] = len(wA&wB)/len(wA|wB) if wA|wB else 0
            records.append(rec)
    return pd.DataFrame(records)

print("\nBuilding ZH–JA pair table…")
zhja_pairs = build_pair_table(zhja_all, "Chinese","zh_idiom","Japanese","ja_idiom")
print(f"  {len(zhja_pairs):,} aligned rows")

print("Building KO–JA pair table…")
koja_pairs = build_pair_table(koja_all, "Korean","ko_idiom","Japanese","ja_idiom")
print(f"  {len(koja_pairs):,} aligned rows")

# Load ZH–KO from module 9 summary for cross-pair comparison
zhko_summary = pd.read_csv(PROC / "cognate_comparison_summary.csv")

def summarise_pairs(pairs, labelA, labelB):
    stats = {"pair": f"{labelA}–{labelB}"}
    stats["n_pairs"]       = len(pairs)
    stats["sent_diff"]     = (pairs["sent_len_A"] - pairs["sent_len_B"]).mean()
    for lbl in LABELS:
        stats[f"tlen_diff_{lbl}"] = pairs[f"tlen_diff_{lbl}"].mean()
        stats[f"edit_{lbl}"]      = pairs[f"edit_{lbl}"].mean()
        stats[f"jaccard_{lbl}"]   = pairs[f"jaccard_{lbl}"].mean()
    return stats

zhja_sum = summarise_pairs(zhja_pairs, "ZH", "JA")
koja_sum = summarise_pairs(koja_pairs, "KO", "JA")

print("\n=== Cross-pair summary (Creatively) ===")
print(f"{'Pair':<8} {'Rows':>6}  {'Sent diff':>10}  "
      f"{'tlen diff':>10}  {'Edit dist':>10}  {'Jaccard':>8}")
for s in [zhja_sum, koja_sum]:
    print(f"  {s['pair']:<6} {s['n_pairs']:>6,}  {s['sent_diff']:>+10.1f}  "
          f"{s['tlen_diff_Creatively']:>+10.1f}  "
          f"{s['edit_Creatively']:>10.3f}  {s['jaccard_Creatively']:>8.3f}")

# Print ZH–KO from saved summary for reference
print("\nZH–KO reference (from module 9):")
for _, row in zhko_summary.iterrows():
    print(f"  {row['Strategy']:<14}  tlen_diff={row['tlen_diff_mean']:+.1f}  "
          f"edit={row['edit_dist_mean']:.3f}  jaccard={row['jaccard_mean']:.3f}")

# Wilcoxon tests for ZH–JA
print("\n=== ZH–JA translation length (A=ZH, B=JA) ===")
for lbl in LABELS:
    valid = zhja_pairs[["tlen_A_"+lbl,"tlen_B_"+lbl]].dropna()
    stat, p = wilcoxon(valid["tlen_A_"+lbl], valid["tlen_B_"+lbl], zero_method="wilcox")
    print(f"  {lbl:<14}  ZH={valid['tlen_A_'+lbl].mean():.1f}  "
          f"JA={valid['tlen_B_'+lbl].mean():.1f}  "
          f"diff={valid['tlen_A_'+lbl].mean()-valid['tlen_B_'+lbl].mean():+.1f}  p={p:.2e}")

print("\n=== KO–JA translation length (A=KO, B=JA) ===")
for lbl in LABELS:
    col_a, col_b = "tlen_A_" + lbl, "tlen_B_" + lbl
    valid = koja_pairs[[col_a, col_b]].dropna()
    stat, p = wilcoxon(valid[col_a], valid[col_b], zero_method="wilcox")
    mean_a, mean_b = valid[col_a].mean(), valid[col_b].mean()
    print(f"  {lbl:<14}  KO={mean_a:.1f}  JA={mean_b:.1f}  diff={mean_a-mean_b:+.1f}  p={p:.2e}")

# ══════════════════════════════════════════════════════════════════════════════
# 4. Figures
# ══════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(2, 3, figsize=(17, 10))

PAIR_COLORS = {"ZH–KO":"#4C72B0", "ZH–JA":"#DD8452", "KO–JA":"#55A868"}

# F1: Cognate counts across all three pairs
ax = axes[0, 0]
pair_counts = pd.DataFrame([
    {"pair":"ZH–KO", "match_type":"exact_4/4",
     "count": len(pd.read_csv(PROC/"cjk_cognate_pairs.csv").query("match_type=='exact_4/4'"))},
    {"pair":"ZH–KO", "match_type":"near_3/4",
     "count": len(pd.read_csv(PROC/"cjk_cognate_pairs.csv").query("match_type=='near_3/4'"))},
    {"pair":"ZH–JA", "match_type":"exact_4/4", "count": len(zhja_exact)},
    {"pair":"ZH–JA", "match_type":"near_3/4",  "count": len(zhja_near3_df)},
    {"pair":"KO–JA", "match_type":"exact_4/4", "count": len(koja_exact)},
    {"pair":"KO–JA", "match_type":"near_3/4",  "count": len(koja_near3_df)},
])
pivot_cnt = pair_counts.pivot(index="pair", columns="match_type", values="count")
pivot_cnt.plot(kind="bar", ax=ax, color=["#4C72B0","#AEB6BF"], width=0.6)
ax.set_title("Cognate Pairs per Language Direction", fontweight="bold")
ax.set_ylabel("Count"); ax.tick_params(axis="x", rotation=0)
ax.legend(title="Match type", fontsize=8)
for bar in ax.patches:
    if bar.get_height() > 0:
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                str(int(bar.get_height())), ha="center", fontsize=8)

# F2: Sentence length A vs B by pair
ax = axes[0, 1]
sent_df = pd.concat([
    zhja_pairs[["sent_len_A","sent_len_B"]].assign(pair="ZH–JA", langA="Chinese",langB="Japanese"),
    koja_pairs[["sent_len_A","sent_len_B"]].assign(pair="KO–JA", langA="Korean", langB="Japanese"),
])
sl_melt = pd.melt(sent_df, id_vars=["pair","langA","langB"],
                  value_vars=["sent_len_A","sent_len_B"],
                  var_name="side", value_name="length")
sl_melt["Language"] = sl_melt.apply(
    lambda r: r["langA"] if r["side"]=="sent_len_A" else r["langB"], axis=1)
sns.boxplot(data=sl_melt, x="pair", y="length", hue="Language",
            palette={"Chinese":"#4C72B0","Korean":"#55A868","Japanese":"#DD8452"},
            flierprops=dict(marker=".",alpha=0.2), ax=ax)
ax.set_title("Source Sentence Length\nby Language Pair", fontweight="bold")
ax.set_ylabel("Chars"); ax.set_xlabel(""); ax.legend(fontsize=8)

# F3: Translation length difference (ZH–JA and KO–JA) per strategy
ax = axes[0, 2]
diff_records = []
for lbl in LABELS:
    diff_records.append({"Strategy":lbl, "Pair":"ZH–JA",
                         "mean_diff": zhja_pairs[f"tlen_diff_{lbl}"].mean()})
    diff_records.append({"Strategy":lbl, "Pair":"KO–JA",
                         "mean_diff": koja_pairs[f"tlen_diff_{lbl}"].mean()})
diff_plot = pd.DataFrame(diff_records)
x = np.arange(len(LABELS)); w = 0.35
bars_zj = ax.bar(x - w/2, diff_plot[diff_plot.Pair=="ZH–JA"]["mean_diff"],
                 w, label="ZH–JA", color="#DD8452")
bars_kj = ax.bar(x + w/2, diff_plot[diff_plot.Pair=="KO–JA"]["mean_diff"],
                 w, label="KO–JA", color="#55A868")
ax.axhline(0, ls="--", color="red", lw=1)
ax.set_xticks(x); ax.set_xticklabels(LABELS)
ax.set_title("Mean Translation Length Diff\n(A − B) per Strategy", fontweight="bold")
ax.set_ylabel("Chars (A − B)"); ax.legend(fontsize=8)

# F4: Edit distance heatmap by target language × pair direction
ax = axes[1, 0]
edit_lang = pd.DataFrame({
    "ZH–JA": zhja_pairs.groupby("target_language")["edit_Creatively"].mean(),
    "KO–JA": koja_pairs.groupby("target_language")["edit_Creatively"].mean(),
})
edit_lang = edit_lang.sort_values("ZH–JA")
sns.heatmap(edit_lang, annot=True, fmt=".3f", cmap="OrRd",
            vmin=0.5, vmax=0.9, linewidths=0.4,
            cbar_kws={"label":"Normalised edit distance (Creatively)"}, ax=ax)
ax.set_title("Cross-Source Edit Distance\nby Target Language (Creatively)", fontweight="bold")
ax.set_ylabel("")

# F5: Jaccard similarity — all three pairs × strategy
ax = axes[1, 1]
jacc_data = []
zhko_cog = pd.read_csv(PROC/"cjk_cognate_pairs.csv")
# Recompute ZH-KO Jaccard quickly from module9 summary
jacc_ko = zhko_summary.set_index("Strategy")["jaccard_mean"].to_dict()
for lbl in LABELS:
    jacc_data += [
        {"Strategy":lbl, "Pair":"ZH–KO", "Jaccard": jacc_ko.get(lbl,np.nan)},
        {"Strategy":lbl, "Pair":"ZH–JA", "Jaccard": zhja_pairs[f"jaccard_{lbl}"].mean()},
        {"Strategy":lbl, "Pair":"KO–JA", "Jaccard": koja_pairs[f"jaccard_{lbl}"].mean()},
    ]
jacc_df = pd.DataFrame(jacc_data)
pivot_j = jacc_df.pivot(index="Pair", columns="Strategy", values="Jaccard")
pivot_j[LABELS].plot(kind="bar", ax=ax, color=COLORS, width=0.65)
ax.set_title("Word Overlap (Jaccard) Between\nCognate Translations", fontweight="bold")
ax.set_ylabel("Jaccard similarity"); ax.tick_params(axis="x", rotation=0)
ax.legend(title="Strategy", fontsize=8)

# F6: Scatter tlen_A vs tlen_B for ZH-JA and KO-JA (Creatively)
ax = axes[1, 2]
for pairs_df, label, color in [
    (zhja_pairs, "ZH–JA", "#DD8452"), (koja_pairs, "KO–JA", "#55A868")
]:
    valid = pairs_df[["tlen_A_Creatively","tlen_B_Creatively"]].dropna()
    ax.scatter(valid["tlen_A_Creatively"], valid["tlen_B_Creatively"],
               alpha=0.15, s=5, color=color, label=label)
lim = 300
ax.plot([0,lim],[0,lim],"k--",lw=0.8)
ax.set_xlim(0,lim); ax.set_ylim(0,lim)
ax.set_title("Translation Length: A vs B\n(Creatively)", fontweight="bold")
ax.set_xlabel("Lang A length (chars)"); ax.set_ylabel("Lang B length (chars)")
ax.legend(fontsize=9)

fig.suptitle("Extended CJK Cognate Analysis: ZH–JA and KO–JA Pairs",
             fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG/"module10_cognate_cjk_extended.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/module10_cognate_cjk_extended.png")

# Per-strategy full comparison table
full_table = pd.DataFrame([
    {"Pair":"ZH–JA", "Strategy":lbl,
     "A_tlen": zhja_pairs[f"tlen_A_{lbl}"].mean(),
     "B_tlen": zhja_pairs[f"tlen_B_{lbl}"].mean(),
     "tlen_diff": zhja_pairs[f"tlen_diff_{lbl}"].mean(),
     "A_slen": zhja_pairs[f"slen_A_{lbl}"].mean(),
     "B_slen": zhja_pairs[f"slen_B_{lbl}"].mean(),
     "edit":    zhja_pairs[f"edit_{lbl}"].mean(),
     "jaccard": zhja_pairs[f"jaccard_{lbl}"].mean()}
    for lbl in LABELS
] + [
    {"Pair":"KO–JA", "Strategy":lbl,
     "A_tlen": koja_pairs[f"tlen_A_{lbl}"].mean(),
     "B_tlen": koja_pairs[f"tlen_B_{lbl}"].mean(),
     "tlen_diff": koja_pairs[f"tlen_diff_{lbl}"].mean(),
     "A_slen": koja_pairs[f"slen_A_{lbl}"].mean(),
     "B_slen": koja_pairs[f"slen_B_{lbl}"].mean(),
     "edit":    koja_pairs[f"edit_{lbl}"].mean(),
     "jaccard": koja_pairs[f"jaccard_{lbl}"].mean()}
    for lbl in LABELS
])
print("\n=== Full comparison table ===")
print(full_table.round(3).to_string(index=False))
full_table.to_csv(PROC/"cognate_cjk_extended_summary.csv", index=False)
print("Saved → data/processed/cognate_cjk_extended_summary.csv")
