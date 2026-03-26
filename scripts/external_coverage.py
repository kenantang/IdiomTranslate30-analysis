"""Overlap with External Idiom Sources."""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")


import json
import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import spearmanr, mannwhitneyu

ROOT = Path(__file__).parent.parent
df = pd.read_parquet(ROOT / "data" / "raw" / "IdiomTranslate30.parquet")
FIG  = ROOT / "figures"
PROC = ROOT / "data" / "processed"
EXT  = ROOT / "data" / "external"
EXT.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

LABELS = ["Creatively", "Analogy", "Author"]
from utils import STRATEGY_COLORS as COLORS
TRANS  = ["translate_creatively", "translate_analogy", "translate_author"]
sent_len = df["sentence"].str.len().replace(0, np.nan)
for col, lbl in zip(TRANS, LABELS):
    df[f"exp_{lbl}"]  = df[col].str.len() / sent_len
    df[f"tlen_{lbl}"] = df[col].str.len()
    df[f"slen_{lbl}"] = df[f"span_{lbl.lower()}"].str.len() \
                        if f"span_{lbl.lower()}" in df.columns else \
                        df[["span_creatively","span_analogy","span_author"][LABELS.index(lbl)]].str.len()
span_cols = ["span_creatively","span_analogy","span_author"]
for sc, lbl in zip(span_cols, LABELS):
    df[f"slen_{lbl}"] = df[sc].str.len()

# ── 1. Download external sources ──────────────────────────────────────────────
XINHUA_URL  = "https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data/idiom.json"
THUOCL_URL  = "https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt"
XINHUA_PATH = EXT / "chinese_xinhua.json"
THUOCL_PATH = EXT / "THUOCL_chengyu.txt"

if not XINHUA_PATH.exists():
    print("Downloading chinese-xinhua…")
    urllib.request.urlretrieve(XINHUA_URL, XINHUA_PATH)
else:
    print("chinese-xinhua already cached.")

if not THUOCL_PATH.exists():
    print("Downloading THUOCL chengyu…")
    urllib.request.urlretrieve(THUOCL_URL, THUOCL_PATH)
else:
    print("THUOCL already cached.")

print("Loading HuggingFace: psyche/korean_idioms…")
try:
    from datasets import load_dataset
    ko_ds = load_dataset("psyche/korean_idioms", name="idioms",
                         split="train", trust_remote_code=True)
    ko_df = ko_ds.to_pandas()
    ko_df.to_parquet(EXT / "korean_idioms.parquet")
    print(f"  Korean idioms: {len(ko_df):,} rows, columns: {list(ko_df.columns)}")
except Exception as e:
    print(f"  Korean download failed: {e}")
    ko_df = None

# ── 2. Parse external sources ─────────────────────────────────────────────────
xinhua = pd.DataFrame(json.loads(XINHUA_PATH.read_text(encoding="utf-8")))
print(f"\nchinese-xinhua: {len(xinhua):,} entries, columns: {list(xinhua.columns)}")

raw = THUOCL_PATH.read_bytes().decode("utf-8", errors="ignore")
rows = [l.split("\t") for l in raw.splitlines() if "\t" in l]
thuocl = pd.DataFrame(rows, columns=["word","freq"])
thuocl["word"] = thuocl["word"].str.strip()
thuocl["freq"] = pd.to_numeric(thuocl["freq"].str.strip(), errors="coerce")
print(f"THUOCL: {len(thuocl):,} entries")

# ── 3. Unique idioms from IdiomTranslate30 ─────────────────────────────────────
zh_idioms = df[df["source_language"]=="Chinese"]["idiom"].unique()
ko_idioms = df[df["source_language"]=="Korean"]["idiom"].unique()
print(f"\nIdiomTranslate30 unique Chinese idioms: {len(zh_idioms):,}")
print(f"IdiomTranslate30 unique Korean idioms:  {len(ko_idioms):,}")

# ── 8a: Overlap with chinese-xinhua ──────────────────────────────────────────
xinhua_set = set(xinhua["word"])
zh_in_xinhua  = set(zh_idioms) & xinhua_set
zh_out_xinhua = set(zh_idioms) - xinhua_set
pct_in = len(zh_in_xinhua) / len(zh_idioms) * 100
print(f"\n8a — IdiomTranslate30 Chinese ∩ xinhua: {len(zh_in_xinhua):,} / {len(zh_idioms):,} "
      f"({pct_in:.1f}%)")

idiom_lens = pd.Series({i: len(i) for i in zh_idioms})
in_lens  = idiom_lens[idiom_lens.index.isin(zh_in_xinhua)]
out_lens = idiom_lens[idiom_lens.index.isin(zh_out_xinhua)]
print(f"  Matched — median length: {in_lens.median():.1f}")
print(f"  Unmatched — median length: {out_lens.median():.1f}")
pct4_in  = (in_lens  == 4).mean() * 100
pct4_out = (out_lens == 4).mean() * 100
print(f"  Matched — % 4-char: {pct4_in:.1f}%")
print(f"  Unmatched — % 4-char: {pct4_out:.1f}%")

# Also: how many xinhua idioms are NOT in IdiomTranslate30
xinhua_not_in_it30 = len(xinhua_set - set(zh_idioms))
print(f"  xinhua idioms NOT in IdiomTranslate30: {xinhua_not_in_it30:,} / {len(xinhua_set):,} "
      f"({xinhua_not_in_it30/len(xinhua_set)*100:.1f}%)")

# ── 8b: Overlap with THUOCL ──────────────────────────────────────────────────
thuocl_set = set(thuocl["word"])
zh_in_thuocl  = set(zh_idioms) & thuocl_set
zh_out_thuocl = set(zh_idioms) - thuocl_set
pct_thuocl = len(zh_in_thuocl) / len(zh_idioms) * 100
print(f"\n8b — IdiomTranslate30 Chinese ∩ THUOCL: {len(zh_in_thuocl):,} / {len(zh_idioms):,} "
      f"({pct_thuocl:.1f}%)")

# Attach frequency to matched rows
freq_map = dict(zip(thuocl["word"], thuocl["freq"]))
df_zh = df[df["source_language"]=="Chinese"].copy()
for sc, lbl in zip(span_cols, LABELS):
    df_zh[f"slen_{lbl}"] = df_zh[sc].str.len()
df_zh["thuocl_freq"] = df_zh["idiom"].map(freq_map)
matched_zh  = df_zh[df_zh["thuocl_freq"].notna()]
unmatched_zh = df_zh[df_zh["thuocl_freq"].isna()]

print("\n  Mean translation length — THUOCL matched vs unmatched:")
for lbl in LABELS:
    m_mean = matched_zh[f"tlen_{lbl}"].mean()
    u_mean = unmatched_zh[f"tlen_{lbl}"].mean()
    stat, p = mannwhitneyu(matched_zh[f"tlen_{lbl}"].dropna(),
                           unmatched_zh[f"tlen_{lbl}"].dropna(),
                           alternative="two-sided")
    print(f"    {lbl:<14} matched={m_mean:.1f}  unmatched={u_mean:.1f}  p={p:.2e}")

# ── 8c: Frequency quintile analysis ──────────────────────────────────────────
matched_idioms = df_zh[df_zh["thuocl_freq"].notna()].drop_duplicates("idiom")[["idiom","thuocl_freq"]]
matched_idioms["freq_quintile"] = pd.qcut(
    matched_idioms["thuocl_freq"], q=5, labels=["Q1 (rarest)","Q2","Q3","Q4","Q5 (most freq)"]
)
df_zh = df_zh.merge(matched_idioms[["idiom","freq_quintile"]], on="idiom", how="left")

quint_stats = []
for q, grp in df_zh.dropna(subset=["freq_quintile"]).groupby("freq_quintile", observed=True):
    row = {"quintile": str(q)}
    for lbl in LABELS:
        row[f"exp_{lbl}"]  = grp[f"exp_{lbl}"].mean()
        row[f"slen_{lbl}"] = (grp[f"slen_{lbl}"] / grp[f"tlen_{lbl}"]).mean()
    quint_stats.append(row)
qdf = pd.DataFrame(quint_stats)
print("\n8c — Frequency quintile analysis (mean expansion ratio):")
print(qdf[["quintile"] + [f"exp_{l}" for l in LABELS]].to_string(index=False))

freq_valid = df_zh[df_zh["thuocl_freq"].notna() & df_zh[[f"exp_{l}" for l in LABELS]].notna().all(axis=1)]
for lbl in LABELS:
    r, p = spearmanr(freq_valid["thuocl_freq"], freq_valid[f"exp_{lbl}"])
    print(f"  Spearman ρ (freq vs exp_{lbl}): {r:.3f}  p={p:.2e}")

# ── 8d: Definition length proxy ──────────────────────────────────────────────
xinhua_zh = xinhua[["word","explanation"]].copy()
xinhua_zh["def_len"] = xinhua_zh["explanation"].str.len()
df_zh = df_zh.merge(xinhua_zh[["word","def_len"]].rename(columns={"word":"idiom"}),
                    on="idiom", how="left")
matched_def = df_zh[df_zh["def_len"].notna()]

print(f"\n8d — Matched with xinhua definitions: {matched_def['idiom'].nunique():,} idioms")
for lbl in LABELS:
    sl_col = f"slen_{lbl}"
    sub_tl = matched_def[["def_len", f"tlen_{lbl}"]].dropna()
    sub_sl = matched_def[["def_len", sl_col]].dropna()
    r_tl, _ = spearmanr(sub_tl["def_len"], sub_tl[f"tlen_{lbl}"])
    r_sl, _ = spearmanr(sub_sl["def_len"], sub_sl[sl_col]) if len(sub_sl) > 10 else (float("nan"), float("nan"))
    print(f"  {lbl:<14} ρ(def_len, tlen)={r_tl:.3f}  ρ(def_len, slen)={r_sl:.3f}")

# ── 8f: Korean overlap ────────────────────────────────────────────────────────
ko_len_dist = pd.Series([len(i) for i in ko_idioms])
print(f"\n8f — Korean idiom length distribution in IdiomTranslate30:")
print(ko_len_dist.value_counts().sort_index().to_string())

if ko_df is not None and "answer" in ko_df.columns:
    ko_proverb_set = set(ko_df["answer"].dropna())
    overlap = set(ko_idioms) & ko_proverb_set
    print(f"\n  IdiomTranslate30 Korean ∩ psyche/korean_idioms: {len(overlap)} idioms "
          f"({len(overlap)/len(ko_idioms)*100:.1f}%)")
else:
    print("\n  Korean dataset unavailable for overlap check.")

# ── Save enriched metadata ────────────────────────────────────────────────────
unique_zh = df[df["source_language"]=="Chinese"].drop_duplicates("idiom")[["idiom"]].copy()
unique_zh["in_xinhua"]   = unique_zh["idiom"].isin(xinhua_set)
unique_zh["in_thuocl"]   = unique_zh["idiom"].isin(thuocl_set)
unique_zh["thuocl_freq"] = unique_zh["idiom"].map(freq_map)
unique_zh = unique_zh.merge(xinhua_zh[["word","def_len"]].rename(columns={"word":"idiom"}),
                             on="idiom", how="left")
unique_zh.to_parquet(PROC / "idiom_metadata.parquet", index=False)
print("\nSaved → data/processed/idiom_metadata.parquet")

# ── Figures ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(13, 10))

# 8a: matched vs unmatched bar by idiom length
ax = axes[0, 0]
all_lens = pd.Series([len(i) for i in zh_idioms])
for_bar = pd.DataFrame({
    "Matched (xinhua)":   in_lens.value_counts().sort_index(),
    "Not in xinhua":      out_lens.value_counts().sort_index(),
}).fillna(0)
for_bar.iloc[:10].plot(kind="bar", ax=ax, color=["#4C72B0","#C44E52"], width=0.7)
ax.set_title("Chinese Idiom Coverage\nvs chinese-xinhua by Character Length", fontweight="bold")
ax.set_xlabel("Idiom character length")
ax.set_ylabel("Count of unique idioms")
ax.tick_params(axis="x", rotation=0)

# 8b: THUOCL frequency histogram
ax = axes[0, 1]
ax.hist(np.log10(matched_idioms["thuocl_freq"].dropna() + 1), bins=30,
        color="#DD8452", edgecolor="white")
ax.set_title(f"THUOCL Corpus Frequency\nof Matched Idioms (n={len(matched_idioms):,})",
             fontweight="bold")
ax.set_xlabel("log₁₀(document frequency)")
ax.set_ylabel("Count of idioms")

# 8c: quintile expansion ratio
ax = axes[1, 0]
x = np.arange(len(qdf))
w = 0.26
for i, (lbl, color) in enumerate(zip(LABELS, COLORS)):
    ax.bar(x + i*w, qdf[f"exp_{lbl}"], w, label=lbl, color=color)
ax.set_xticks(x + w)
ax.set_xticklabels(qdf["quintile"], fontsize=8, rotation=15, ha="right")
ax.set_title("Mean Expansion Ratio\nby THUOCL Frequency Quintile", fontweight="bold")
ax.set_ylabel("Mean expansion ratio")
ax.legend(title="Strategy", fontsize=8)

# 8f: Korean idiom length distribution
ax = axes[1, 1]
ko_len_dist.value_counts().sort_index().plot(kind="bar", ax=ax, color="#55A868", width=0.6)
ax.set_title("Korean Idiom Length Distribution\nin IdiomTranslate30", fontweight="bold")
ax.set_xlabel("Idiom character length")
ax.set_ylabel("Count of unique idioms")
ax.tick_params(axis="x", rotation=0)

fig.tight_layout()
fig.savefig(FIG / "overlap_chinese_xinhua.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/overlap_chinese_xinhua.png")

# ── Fig: frequency quintile detail ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4))
x = np.arange(len(qdf))
w = 0.26
for i, (lbl, color) in enumerate(zip(LABELS, COLORS)):
    ax.bar(x + i*w, qdf[f"exp_{lbl}"], w, label=lbl, color=color)
ax.set_xticks(x + w)
ax.set_xticklabels(qdf["quintile"], rotation=15, ha="right")
ax.set_title("Mean Expansion Ratio by THUOCL Frequency Quintile", fontweight="bold")
ax.set_ylabel("Mean expansion ratio")
ax.legend(title="Strategy")
fig.tight_layout()
fig.savefig(FIG / "frequency_quintiles.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/frequency_quintiles.png")

# ── Fig: definition length correlation ───────────────────────────────────────
s2 = matched_def.sample(min(20_000, len(matched_def)), random_state=8)
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, lbl, color in zip(axes, LABELS, COLORS):
    ax.scatter(s2["def_len"], s2[f"tlen_{lbl}"], alpha=0.07, s=4, color=color)
    r, _ = spearmanr(s2["def_len"], s2[f"tlen_{lbl}"])
    ax.set_title(f"{lbl}\nρ={r:.3f}", fontweight="bold")
    ax.set_xlabel("Definition length (chars)")
    ax.set_ylabel("Translation length" if ax is axes[0] else "")
    ax.set_xlim(0, 300); ax.set_ylim(0, 600)
fig.suptitle("Xinhua Definition Length vs Translation Length", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "definition_length_corr.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/definition_length_corr.png")
