"""
Extract English-language idiom examples for every analysis section that discusses
cross-idiom variation. One example per source language (Chinese, Japanese, Korean).

Output: data/examples/english_examples.md
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from pathlib import Path

from utils import STABILITY_CV_THRESH

ROOT = Path(__file__).parent.parent
DATA_PATH  = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
OUT_PATH   = ROOT / "data" / "examples" / "english_examples.md"

df = pd.read_parquet(DATA_PATH)
en = df[df["target_language"] == "English"].copy()

STRATS = ["translate_creatively", "translate_analogy", "translate_author"]
SPANS  = ["span_creatively",      "span_analogy",      "span_author"]
LABELS = ["Creatively", "Analogy", "Author"]
SRCS   = ["Chinese", "Japanese", "Korean"]


def get_rows(src, idiom, n=1):
    return en[(en["source_language"] == src) & (en["idiom"] == idiom)].head(n)


def fmt_idiom(src, idiom, n=1):
    rows = get_rows(src, idiom, n)
    lines = [f"**{idiom}** [{src}]"]
    for _, r in rows.iterrows():
        lines.append(f"- Source: {r['sentence']}")
        for col, lbl, scol in zip(STRATS, LABELS, SPANS):
            lines.append(f"- {lbl}: {r[col]}")
            lines.append(f"  - Span: *{r[scol]}*")
    return "\n".join(lines)


sections = []

# ── 1. EXPANSION RATIO ────────────────────────────────────────────────────────
en_tmp = en.copy()
en_tmp["exp"] = en_tmp["translate_creatively"].str.len() / \
                en_tmp["sentence"].str.len().replace(0, np.nan)
exp_mean = en_tmp[en_tmp["sentence"].str.len() > 0] \
               .groupby(["source_language", "idiom"])["exp"].mean()

pairs = []
for src in SRCS:
    sub = exp_mean[src].dropna().sort_values()
    low  = sub[sub > 1.0].index[0]
    high = sub.index[-1]
    pairs.append((src, low, f"{sub[low]:.2f}×", high, f"{sub[high]:.2f}×"))

block = ["## Translation Length & Expansion Ratio\n"]
block.append("### Low-expansion examples (idiom maps to a short English phrase)\n")
for src, idiom, ratio, _, _ in pairs:
    block.append(f"Expansion ratio: **{ratio}**\n")
    block.append(fmt_idiom(src, idiom))
    block.append("")
block.append("### High-expansion examples (idiom requires explanatory elaboration)\n")
for src, _, _, idiom, ratio in pairs:
    block.append(f"Expansion ratio: **{ratio}**\n")
    block.append(fmt_idiom(src, idiom))
    block.append("")
sections.append("\n".join(block))

# ── 2. SPAN POSITION ──────────────────────────────────────────────────────────
sp = pd.read_parquet(ROOT / "data/processed/span_positions.parquet")
sp_en = sp[(sp["target_language"] == "English") & (sp["strategy"] == "Creatively") &
           (sp["abs_start"] >= 0)]
mean_pos = sp_en.groupby(["source_language", "idiom"])["rel_start"].mean()
counts   = sp_en.groupby(["source_language", "idiom"]).size()

pairs = []
for src in SRCS:
    valid = counts[src][counts[src] >= 8].index
    sub   = mean_pos[src].dropna()
    sub   = sub[sub.index.isin(valid)]
    pairs.append((src, sub.index[0], f"{sub.iloc[0]:.3f}", sub.index[-1], f"{sub.iloc[-1]:.3f}"))

block = ["## Span Position Within Translation\n"]
block.append("### Earliest-span examples (span appears at sentence start)\n")
for src, idiom, pos, _, _ in pairs:
    block.append(f"Mean relative start: **{pos}**\n")
    block.append(fmt_idiom(src, idiom, n=2))
    block.append("")
block.append("### Latest-span examples (span appears at sentence end)\n")
for src, _, _, idiom, pos in pairs:
    block.append(f"Mean relative start: **{pos}**\n")
    block.append(fmt_idiom(src, idiom, n=2))
    block.append("")
sections.append("\n".join(block))

# ── 3. STRATEGY DIVERGENCE ────────────────────────────────────────────────────
div = pd.read_parquet(ROOT / "data/processed/divergence_scores.parquet")
div_en   = div[div["target_language"] == "English"]
div_mean = div_en.groupby(["source_language", "idiom"])[["div_CA_ng1"]].mean().reset_index()

pairs = []
for src in SRCS:
    sub  = div_mean[div_mean["source_language"] == src].sort_values("div_CA_ng1")
    most  = sub.iloc[-1]
    least = sub.iloc[0]
    pairs.append((src, most["idiom"], f"{most['div_CA_ng1']:.3f}",
                       least["idiom"], f"{least['div_CA_ng1']:.3f}"))

block = ["## Strategy Divergence\n"]
block.append("### Most-divergent idioms (no stable English equivalent)\n")
for src, idiom, score, _, _ in pairs:
    block.append(f"Creatively–Analogy unigram divergence: **{score}**\n")
    block.append(fmt_idiom(src, idiom))
    block.append("")
block.append("### Least-divergent idioms (clear conventional English rendering)\n")
for src, _, _, idiom, score in pairs:
    block.append(f"Creatively–Analogy unigram divergence: **{score}**\n")
    block.append(fmt_idiom(src, idiom))
    block.append("")
sections.append("\n".join(block))

# ── 4. CONTEXT SENSITIVITY ────────────────────────────────────────────────────
cs    = pd.read_parquet(ROOT / "data/processed/context_sensitivity.parquet")
cs_en = cs[cs["target_language"] == "English"]

pairs = []
for src in SRCS:
    sub = cs_en[cs_en["source_language"] == src].sort_values("cv_Creatively")
    low_cands = sub[(sub["n_sentences"] >= 10) & (sub["cv_Creatively"] < STABILITY_CV_THRESH)]  # H24
    low_row   = low_cands.iloc[len(low_cands) // 2] if len(low_cands) else sub.iloc[0]
    high_row  = sub.iloc[-1]
    pairs.append((src, low_row["idiom"], f"{low_row['cv_Creatively']:.3f}",
                       high_row["idiom"], f"{high_row['cv_Creatively']:.3f}"))

block = ["## Context Sensitivity\n"]
block.append("### Low-CV idioms (near-identical translations regardless of context)\n")
for src, idiom, cv, _, _ in pairs:
    block.append(f"CV of Creatively translation length: **{cv}** — showing 3 sentences\n")
    rows = get_rows(src, idiom, 3)
    for i, (_, r) in enumerate(rows.iterrows()):
        block.append(f"s{i+1}. Source: {r['sentence']}")
        block.append(f"   Translation: {r['translate_creatively']}")
    block.append("")

block.append("### High-CV idioms (translations vary substantially with context)\n")
for src, _, _, idiom, cv in pairs:
    block.append(f"CV of Creatively translation length: **{cv}** — showing all 10 sentences\n")
    rows = en[(en["source_language"] == src) & (en["idiom"] == idiom)]
    for i, (_, r) in enumerate(rows.iterrows()):
        block.append(f"s{i+1:02d}. Source: {r['sentence']}")
        block.append(f"    Translation: {r['translate_creatively']}")
    block.append("")
sections.append("\n".join(block))

# ── 5. SPAN REUSE ─────────────────────────────────────────────────────────────
block = ["## Span Reuse\n"]
block.append("### All-different Analogy spans (one fresh metaphor per sentence)\n")
for src in SRCS:
    sub = cs_en[cs_en["source_language"] == src]
    ex  = sub[sub["span_uniq_Analogy"] == 1.0].sample(1, random_state=7)["idiom"].iloc[0]
    rows = en[(en["source_language"] == src) & (en["idiom"] == ex)]
    block.append(f"**{ex}** [{src}]")
    for i, (_, r) in enumerate(rows.iterrows()):
        block.append(f"  span {i+1:2d}: *{r['span_analogy']}*")
    block.append("")

block.append("### Most-reused Creatively spans (same phrase across all sentences)\n")
for src in SRCS:
    sub = cs_en[cs_en["source_language"] == src]
    rep = sub.sort_values("span_uniq_Creatively").iloc[0]
    idiom = rep["idiom"]
    rows  = en[(en["source_language"] == src) & (en["idiom"] == idiom)]
    block.append(f"**{idiom}** [{src}] — uniqueness fraction: {rep['span_uniq_Creatively']:.2f}")
    for i, (_, r) in enumerate(rows.iterrows()):
        block.append(f"  span {i+1:2d}: *{r['span_creatively']}*")
    block.append("")
sections.append("\n".join(block))

# ── 6. CROSS-SOURCE COGNATE EXAMPLES ─────────────────────────────────────────
block = ["## Cross-Source Cognate Comparison (English target)\n"]

# ZH-KO
zhko = pd.read_csv(ROOT / "data/processed/cjk_cognate_pairs.csv")
for _, row in zhko[zhko["match_type"] == "exact_4/4"].iterrows():
    zh_rows = en[(en["source_language"] == "Chinese") & (en["idiom"] == row["zh_idiom"])]
    ko_rows = en[(en["source_language"] == "Korean")  & (en["idiom"] == row["ko_idiom"])]
    if len(zh_rows) >= 3 and len(ko_rows) >= 3:
        zh_idiom, ko_idiom = row["zh_idiom"], row["ko_idiom"]
        block.append(f"### ZH–KO: {zh_idiom} / {ko_idiom}\n")
        for lbl, rows in [("ZH", zh_rows), ("KO", ko_rows)]:
            r = rows.iloc[0]
            block.append(f"**{lbl}** source: {r['sentence']}")
            for col, strat in zip(STRATS, LABELS):
                block.append(f"- {lbl} {strat}: {r[col]}")
        block.append("")
        break

# ZH-JA (genuine cognate)
zhja = pd.read_csv(ROOT / "data/processed/zhja_cognate_pairs.csv")
genuine = zhja[(zhja["match_type"] == "exact_4/4") & (zhja["zh_idiom"] != zhja["ja_idiom"])]
for _, row in genuine.iterrows():
    zh_rows = en[(en["source_language"] == "Chinese")  & (en["idiom"] == row["zh_idiom"])]
    ja_rows = en[(en["source_language"] == "Japanese") & (en["idiom"] == row["ja_idiom"])]
    if len(zh_rows) >= 3 and len(ja_rows) >= 3:
        zh_idiom, ja_idiom = row["zh_idiom"], row["ja_idiom"]
        block.append(f"### ZH–JA: {zh_idiom} (ZH simplified) / {ja_idiom} (JA traditional)\n")
        for lbl, rows in [("ZH", zh_rows), ("JA", ja_rows)]:
            r = rows.iloc[0]
            block.append(f"**{lbl}** source: {r['sentence']}")
            for col, strat in zip(STRATS, LABELS):
                block.append(f"- {lbl} {strat}: {r[col]}")
        block.append("")
        break

# KO-JA
for ja_idiom, ko_idiom in [("電光石火", "전광석화"), ("千差万別", "천차만별")]:
    ja_rows = en[(en["source_language"] == "Japanese") & (en["idiom"] == ja_idiom)]
    ko_rows = en[(en["source_language"] == "Korean")   & (en["idiom"] == ko_idiom)]
    if len(ja_rows) and len(ko_rows):
        block.append(f"### KO–JA: {ko_idiom} (KO) / {ja_idiom} (JA)\n")
        for lbl, rows in [("KO", ko_rows), ("JA", ja_rows)]:
            r = rows.iloc[0]
            block.append(f"**{lbl}** source: {r['sentence']}")
            for col, strat in zip(STRATS, LABELS):
                block.append(f"- {lbl} {strat}: {r[col]}")
        block.append("")
        break

sections.append("\n".join(block))

# ── 7. DIFFICULTY ─────────────────────────────────────────────────────────────
diff_df = pd.read_parquet(ROOT / "data/processed/idiom_difficulty.parquet")

pairs = []
for src in SRCS:
    sub     = diff_df[(diff_df["source_language"] == src) & diff_df["exp_mean"].notna()].sort_values("difficulty")
    easiest = sub.iloc[0]["idiom"]
    hardest = sub.iloc[-1]["idiom"]
    pairs.append((src, easiest, f"{sub.iloc[0]['difficulty']:.3f}",
                       hardest, f"{sub.iloc[-1]['difficulty']:.3f}"))

block = ["## Idiom Difficulty\n"]
block.append("### Easiest idioms (consistent, natural English renderings)\n")
for src, idiom, score, _, _ in pairs:
    block.append(f"Difficulty score: **{score}**\n")
    block.append(fmt_idiom(src, idiom))
    block.append("")
block.append("### Hardest idioms (divergent or interpretively unstable translations)\n")
for src, _, _, idiom, score in pairs:
    block.append(f"Difficulty score: **{score}**\n")
    block.append(fmt_idiom(src, idiom))
    block.append("")
sections.append("\n".join(block))

# ── Write output ──────────────────────────────────────────────────────────────
header = (
    "# English-Language Idiom Examples\n\n"
    "Auto-generated by `scripts/extract_examples.py`. "
    "All examples use English as the target language.\n\n"
    "Each section corresponds to a part of the README analysis where cross-idiom "
    "variation is discussed. One example is shown per source language "
    "(Chinese, Japanese, Korean).\n\n"
    "---\n\n"
)

OUT_PATH.write_text(header + "\n\n---\n\n".join(sections), encoding="utf-8")
print(f"Saved → {OUT_PATH}")
