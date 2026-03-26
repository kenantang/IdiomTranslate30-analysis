"""
Part 10: Additional Analyses
Covers six analyses of the Analogy strategy and span diversity patterns.

10.1  Per-idiom slop score         — fraction of English Analogy spans matching a stock template
10.2  Most span-diverse idioms     — distinct span count per idiom across all languages & strategies
10.3  Template vs surface diversity — reconciling surface uniqueness with template repetition
10.4  Source-language template bias — which templates each source language attracts
10.5  Cultural reference portability — spans appearing verbatim in 3+ target languages
10.6  Bathos patterns              — prosaic single-word/short-phrase Analogy spans

Outputs:
  data/processed/idiom_slop_scores.csv
  data/processed/idiom_span_diversity.csv
  data/processed/template_surface_reconciliation.csv
  data/processed/source_template_crosstab.csv
  data/processed/cross_language_spans.csv
  data/processed/bathos_spans.csv
"""

import pandas as pd
import numpy as np
import re
import unicodedata
from pathlib import Path
from scipy.stats import chi2_contingency

ROOT     = Path(__file__).parent.parent
DATA     = ROOT / "data" / "raw" / "IdiomTranslate30.parquet"
OUT_DIR  = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(DATA)

# ── helpers ──────────────────────────────────────────────────────────────────

def nfc_lower(s):
    return unicodedata.normalize("NFC", s.strip()).lower().strip(".,!?;:'\"")


TEMPLATES = {
    "weaving_thread_tapestry": r"weav|tapestry|unravel|single.*cable|loom|stitch|woven",
    "cosmic_star_galaxy":      r"\bstar\b|\bgalaxy\b|\bcosmic\b|\bconstellation\b|\bnorth star\b|\bcelestial\b",
    "kaleidoscope":            r"kaleidoscope",
    "trying_to_futility":      r"^trying to ",
    "dandelion_scattered":     r"dandelion|scattered.*gale|gale.*scatter",
    "labyrinth_mirror":        r"labyrinth|hall of mirror|forest of mirror",
    "clockmaker_precision":    r"clockmaker|watchmaker|precision of a master",
    "mist_smoke_castle":       r"castle.*(?:mist|smoke|fog)|palace.*(?:mist|smoke|fog)|built of.*(?:mist|smoke)|carved.*(?:mist|smoke)",
}


def classify_template(span: str) -> str:
    for name, pattern in TEMPLATES.items():
        if re.search(pattern, span, re.IGNORECASE):
            return name
    return "original"


# ── build long table (all strategies) ────────────────────────────────────────

rows = []
for strat, scol in [("Creatively", "span_creatively"),
                    ("Analogy",    "span_analogy"),
                    ("Author",     "span_author")]:
    sub = df[["source_language", "target_language", "idiom", scol]].copy()
    sub.columns = ["source_language", "target_language", "idiom", "span"]
    sub["strategy"] = strat
    rows.append(sub)
long = pd.concat(rows, ignore_index=True)
long = long.dropna(subset=["span"])
long = long[long["span"].str.strip() != ""]
long["span_norm"] = long["span"].apply(nfc_lower)

# English Analogy only
en_ana = df[df["target_language"] == "English"][
    ["source_language", "idiom", "span_analogy"]
].copy()
en_ana = en_ana.dropna(subset=["span_analogy"])
en_ana = en_ana[en_ana["span_analogy"].str.strip() != ""]
en_ana["span"] = en_ana["span_analogy"].str.strip().str.lower()
en_ana["template"] = en_ana["span"].apply(classify_template)


# ─────────────────────────────────────────────────────────────────────────────
# 10.1  Per-idiom slop score
# ─────────────────────────────────────────────────────────────────────────────
print("── 10.1  Per-idiom slop score ──────────────────────────────────────────")

total  = en_ana.groupby(["source_language", "idiom"]).size().rename("total")
slop   = (en_ana[en_ana["template"] != "original"]
          .groupby(["source_language", "idiom"]).size().rename("slop"))
scores = pd.concat([total, slop], axis=1).fillna(0)
scores["slop_score"] = scores["slop"] / scores["total"]
scores = scores.reset_index()
scores.to_csv(OUT_DIR / "idiom_slop_scores.csv", index=False)

print(f"  Total English Analogy spans : {len(en_ana):,}")
slop_n = (en_ana["template"] != "original").sum()
print(f"  Templated (slop) spans      : {slop_n:,}  ({100*slop_n/len(en_ana):.1f}%)")
print(f"  Idioms with 0% slop         : {(scores['slop_score']==0).sum()}")
print(f"  Idioms with >50% slop       : {(scores['slop_score']>0.5).sum()}")
print(f"  Mean slop score by source:")
print(scores.groupby("source_language")["slop_score"].mean().round(3).to_string())

print("\n  Template distribution:")
print(en_ana["template"].value_counts().to_string())

print("\n  Top 10 most formulaic idioms (≥5 spans):")
filt = scores[scores["total"] >= 5].nlargest(10, "slop_score")
print(filt[["source_language", "idiom", "slop_score"]].to_string(index=False))

print("\n  Top 10 most original idioms (≥5 spans):")
print(scores[scores["total"] >= 5].nsmallest(10, "slop_score")
      [["source_language", "idiom", "slop_score"]].to_string(index=False))


# ─────────────────────────────────────────────────────────────────────────────
# 10.2  Most span-diverse idioms
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 10.2  Most span-diverse idioms ─────────────────────────────────────")

diversity = (long.groupby(["source_language", "idiom"])
             .agg(total_spans    = ("span_norm", "count"),
                  distinct_spans = ("span_norm", "nunique"))
             .reset_index())
diversity["diversity_ratio"] = diversity["distinct_spans"] / diversity["total_spans"]
diversity.to_csv(OUT_DIR / "idiom_span_diversity.csv", index=False)

print(f"  Distinct spans — mean {diversity['distinct_spans'].mean():.1f}, "
      f"median {diversity['distinct_spans'].median():.0f}, "
      f"std {diversity['distinct_spans'].std():.1f}")

print("\n  Top 10 most span-locked (standard 300-span idioms only):")
standard = diversity[diversity["total_spans"].between(290, 310)]
print(standard.nsmallest(10, "distinct_spans")
      [["source_language", "idiom", "distinct_spans", "diversity_ratio"]].to_string(index=False))

print("\n  Mean distinct spans by source language:")
print(diversity.groupby("source_language")["distinct_spans"].agg(["mean", "median", "std"]).round(2))


# ─────────────────────────────────────────────────────────────────────────────
# 10.3  Template vs surface diversity reconciliation
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 10.3  Template vs surface diversity ─────────────────────────────────")

cell = (en_ana.groupby(["source_language", "idiom"])
        .agg(n_spans           = ("span",     "count"),
             distinct_surface  = ("span",     "nunique"),
             distinct_templates= ("template", "nunique"),
             n_slop            = ("template", lambda s: (s != "original").sum()))
        .reset_index())

named_tmpl = (en_ana[en_ana["template"] != "original"]
              .groupby(["source_language", "idiom"])["template"]
              .nunique().rename("distinct_named"))
cell = cell.merge(named_tmpl, on=["source_language", "idiom"], how="left").fillna(0)
cell.to_csv(OUT_DIR / "template_surface_reconciliation.csv", index=False)

all_unique = cell[cell["distinct_surface"] == cell["n_spans"]]
slop_uniform = all_unique[all_unique["distinct_named"] == 1]
print(f"  Cells with all-unique surface spans : {len(all_unique)} / {len(cell)}"
      f"  ({100*len(all_unique)/len(cell):.1f}%)")
print(f"  Of those, single-template (slop-uniform): {len(slop_uniform)}"
      f"  ({100*len(slop_uniform)/len(all_unique):.1f}%)")

print("\n  Distinct template counts per cell:")
print(cell["distinct_templates"].value_counts().sort_index().to_string())


# ─────────────────────────────────────────────────────────────────────────────
# 10.4  Source-language template bias
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 10.4  Source-language template bias ─────────────────────────────────")

total_by_src = en_ana.groupby("source_language").size().rename("total")
crosstab = en_ana.groupby(["source_language", "template"]).size().unstack(fill_value=0)
pct = (crosstab.div(total_by_src, axis=0) * 100).round(3)
pct.to_csv(OUT_DIR / "source_template_crosstab.csv")

print("  Template % by source language:")
print(pct.to_string())

chi2, p, dof, _ = chi2_contingency(crosstab.drop(columns="original", errors="ignore"))
print(f"\n  Chi-square test: χ²={chi2:.1f}, df={dof}, p={p:.2e}")

print("\n  Max/min ratios across source languages:")
for col in pct.columns:
    if col == "original":
        continue
    vals = pct[col]
    ratio = vals.max() / vals.min() if vals.min() > 0 else float("inf")
    print(f"  {col:<30} ZH={vals['Chinese']:.2f}%  JA={vals['Japanese']:.2f}%"
          f"  KO={vals['Korean']:.2f}%  ratio={ratio:.2f}x")


# ─────────────────────────────────────────────────────────────────────────────
# 10.5  Cultural reference portability
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 10.5  Cultural reference portability ────────────────────────────────")

# Verbatim cross-language spans (Analogy strategy)
ana = long[long["strategy"] == "Analogy"].copy()
lang_per_span = (ana.groupby("span_norm")["target_language"]
                 .nunique().reset_index(name="n_languages")
                 .sort_values("n_languages", ascending=False))
multi = lang_per_span[lang_per_span["n_languages"] >= 3].copy()

# Attach idiom count and total uses
counts = ana.groupby("span_norm").agg(
    n_idioms=("idiom",           "nunique"),
    n_uses  =("idiom",           "count"),
    languages=("target_language", lambda x: "|".join(sorted(x.unique()))),
).reset_index()
multi = multi.merge(counts, on="span_norm")
multi.to_csv(OUT_DIR / "cross_language_spans.csv", index=False)

print(f"  Spans appearing in 3+ target languages: {len(multi)}")
print("\n  Top 20:")
print(multi.head(20)[["span_norm", "n_languages", "n_idioms", "n_uses", "languages"]].to_string(index=False))

# Known reference keyword search
print("\n  Named reference keyword search:")
reference_keywords = {
    "Hongmen Banquet":  r"\bhongmen\b",
    "Natural selection":r"natural selection|sélection naturelle|natürliche auslese|selezione naturale|selección natural",
    "Gordian knot":     r"gordian",
    "Prodigal son":     r"prodigal son|fils prodigue|figlio prodigo",
    "Möbius":           r"möbius|mobius",
}
ana_full = df[["source_language", "target_language", "idiom", "span_analogy"]].copy()
ana_full = ana_full.dropna(subset=["span_analogy"])
ana_full["span_norm"] = ana_full["span_analogy"].apply(nfc_lower)

for ref, pattern in reference_keywords.items():
    hits = ana_full[ana_full["span_norm"].str.contains(pattern, case=False, na=False, regex=True)]
    print(f"  {ref:<25} {len(hits):4d} uses / {hits['idiom'].nunique():2d} idioms / "
          f"{hits['target_language'].nunique()} languages")


# ─────────────────────────────────────────────────────────────────────────────
# 10.6  Bathos patterns
# ─────────────────────────────────────────────────────────────────────────────
print("\n── 10.6  Bathos patterns ───────────────────────────────────────────────")

bathos_patterns = {
    "English":  r"^(immortality|metabolism|natural selection|agnosticism|monogamy|cynicism|"
                r"self-reliance|self-sufficiency|self-awareness|self-reflection|"
                r"physiocracy|q&a session|day and night|once upon a time|"
                r"cutting corners|hesitation|arrogance|carelessness|extortion|"
                r"eternal life|eternal recurrence|separation of church and state|"
                r"time and again|over time|throughout the ages)$",
    "French":   r"^(l'immortalité|séance de questions-réponses|métabolisme|"
                r"l'autosuffisance|l'indécision|depuis la nuit des temps|"
                r"au fil du temps|inlassablement|sans relâche|clairvoyance)$",
    "Spanish":  r"^(la inmortalidad|metabolismo|una y otra vez|día y noche|"
                r"sesión de preguntas y respuestas|la indecisión|gota a gota|en resumen)$",
    "German":   r"^(beispiellos|fragerunde|unermüdlich|unerschütterlich|stoffwechsel|"
                r"seit urzeiten|abschiedsworte|vetternwirtschaft|unentschlossenheit|"
                r"weitblick|hochmut|lebensecht)$",
    "Russian":  r"^(нерешительность|высокомерие|бесстыдство|бездействие|неоспорим|"
                r"самоотверженность|прозорливость|беспечность|бессмертие|"
                r"снова и снова|раз за разом|добровольно)$",
    "Arabic":   r"^(الخلود|التردد|مراراً وتكراراً|ليل نهار|القناعة|"
                r"استشاط غضباً|الاكتفاء الذاتي|الأسئلة والأجوبة)$",
    "Hindi":    r"^(अमरता|पुनर्जन्म|दूरदर्शिता|छल-कपट|अहंकार|"
                r"बार-बार|दिन-रात|अजीबोगरीब|हर पल|लोक-कल्याण)$",
    "Bengali":  r"^(অগণিত|বারবার|অবিনশ্বর|অবিচল|অদম্য|নিখুঁত|"
                r"অভূতপূর্ব|অনস্বীকার্য|অপ্রতিরোধ্য|একের পর এক)$",
    "Swahili":  r"^(milele|kujitegemea|kusita-sita|mara mfululizo|siku moja|"
                r"maswali na majibu|mchana na usiku|kwa ufupi)$",
    "Italian":  r"^(l'immortalità|metabolismo|selezione naturale|botta e risposta|"
                r"mutuo soccorso|lungimiranza|giorno e notte|senza precedenti)$",
}

bathos_rows = []
summary = []
for lang, pattern in bathos_patterns.items():
    sub = ana_full[ana_full["target_language"] == lang].copy()
    mask = sub["span_norm"].str.match(pattern, na=False)
    hits = sub[mask]
    hits = hits.copy()
    hits["language"] = lang
    bathos_rows.append(hits)
    pct = 100 * len(hits) / len(sub) if len(sub) else 0
    summary.append({"language": lang, "bathos_spans": len(hits),
                    "idioms": hits["idiom"].nunique(), "pct": round(pct, 3)})
    top5 = hits.groupby("span_norm").size().sort_values(ascending=False).head(3)
    print(f"  [{lang}] {len(hits)} spans ({pct:.2f}%)  —  "
          + "  |  ".join(f"'{s}' ({n})" for s, n in top5.items()))

bathos_all = pd.concat(bathos_rows)
bathos_all.to_csv(OUT_DIR / "bathos_spans.csv", index=False)

# Cross-language bathos: idioms attracting bathos in many languages
print("\n  Idioms attracting bathos in 5+ languages:")
print(bathos_all.groupby(["source_language", "idiom"])["target_language"]
      .nunique().sort_values(ascending=False).head(15).to_string())

print("\n✓ All outputs saved to data/processed/")
