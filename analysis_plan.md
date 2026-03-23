# IdiomTranslate30 — Data Analysis Plan

*Revised 2026-03-22. Informed by 14 papers in [papers/](papers/index.md).
Method provenance (with verbatim citations) in [papers/methods_provenance.md](papers/methods_provenance.md).*

**Scope:** All analyses use only the dataset itself. No ground-truth translations, no external
embeddings, no LLM scoring. Every measure is derived from character strings, token counts, and
span annotations already present in the data.

---

## Research Questions

1. Does translation strategy (Creatively / Analogy / Author) produce systematically different
   lengths and structures, and does the difference hold uniformly across all 30 language pairs?
2. Do the span annotations reveal differences in how "elaborately" each strategy renders the idiom?
3. How divergent are the three strategies for the same (idiom, target language) instance —
   and which idioms or language pairs show the most / least divergence?
4. Does translation behaviour vary with target language or source language in ways that suggest
   systematic generation patterns?
5. What structural properties of the source idiom (character length, language of origin) correlate
   with translation length and span behaviour?
6. Where are the annotation errors and degenerate outputs in the dataset?

---

## Module 1 — Translation Length & Expansion Ratio
*Methods provenance: §1, §8, §12 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Quantify how much each strategy expands the source sentence, and test whether the
ordering Analogy ≥ Author ≥ Creatively is consistent across all language pairs.

**Measures:**
- **Expansion ratio** = `len(translation) / len(sentence)` per strategy per row
- Summary statistics (min, p25, median, mean, p75, p95, max) per strategy and per language pair,
  **macro-averaged over unique idioms** to avoid bias from unequal source-language coverage
  (see Baziotis et al.: *"over-represented idioms can skew the reported results"*)
- Distribution plots (violin + box) of expansion ratio per strategy, faceted by source language
- Wilcoxon signed-rank test (non-parametric, consistent with Liu et al.'s use of permutation
  tests) between each strategy pair, per target language — report effect size (rank-biserial r)

**Outputs:** `figures/module1_expansion_ratio.png`, `figures/module1_length_by_target.png`,
statistics table in report.

---

## Module 2 — Span Length & Idiom Footprint Analysis
*Methods provenance: §3, §6 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Characterise the size of the idiom's "footprint" in each translation and how it differs
by strategy, following the span extraction design described in Tang et al. (*"We extract the span
in each translation that corresponds to the idiom"*).

**Measures:**
- **Span-to-translation ratio** = `len(span) / len(translation)` — what fraction of the
  translation is occupied by the idiom rendering
- **Span length** in characters: distributions per strategy (violin), per target language (box),
  and per source language
- **Span vs. idiom length** scatter: does a longer source idiom produce a longer span? Fit a
  simple linear regression per strategy
- **Cross-strategy span correlation**: for each (idiom, target language) pair, compute the
  Pearson r between `len(span_creatively)`, `len(span_analogy)`, `len(span_author)` — report as
  a 3×3 correlation heatmap per target language

**Outputs:** `figures/module2_span_ratio.png`, `figures/module2_span_vs_idiom_length.png`,
`figures/module2_span_correlation.png`.

---

## Module 3 — Strategy Divergence via N-gram Analysis
*Methods provenance: §7, §12 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Measure how differently the three strategies render the same idiom using the n-gram
divergence approach from Zhou et al.: *"the percentage of n-grams in the literal sentences which
do not appear in the idiomatic sentences as a measure of the difference"*.

**Measures:**
- For each row, compute pairwise n-gram divergence (unigrams through 4-grams) between the three
  strategy translations: `div(A, B)` = fraction of A's n-grams absent from B
- Aggregate into a 3×3 matrix of mean divergence per strategy pair, reported per target language
  and per source language (macro-averaged over idioms)
- **Character-level edit distance** (normalised Levenshtein) between strategy pairs as a
  complementary distance measure not confounded by tokenisation
- Identify the 20 idioms with the **highest** cross-strategy divergence and the 20 with the
  **lowest** — sample and display in the report for qualitative inspection

**Outputs:** `figures/module3_ngram_divergence_heatmap.png`,
`figures/module3_edit_distance_distribution.png`, sampled idiom tables in report.

---

## Module 4 — Cross-Lingual Consistency Analysis
*Methods provenance: §5, §12 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Test whether the same idiom receives consistent treatment across the 10 target languages.
Inconsistency (high variance across targets for the same idiom) signals generation instability.

**Measures:**
- For each (source language, idiom, strategy) group: compute the **coefficient of variation (CV)**
  of translation length across the 10 target languages
- Group target languages by NLP resource level:
  - High-resource: English, French, German, Spanish, Italian, Russian
  - Lower-resource: Arabic, Bengali, Hindi, Swahili
- Compare CV distributions between groups with a Mann-Whitney U test — test whether lower-resource
  targets show higher length variance (consistent with findings in Liu et al. and Khoshtab et al.)
- Heatmap: median span length per (source language × target language) per strategy — identify
  systematic directional biases

**Outputs:** `figures/module4_cv_by_resource_level.png`, `figures/module4_span_heatmap.png`.

---

## Module 5 — Idiom Morphology & Structural Analysis
*Methods provenance: §9, §1 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Examine whether idiom-level properties predict translation behaviour, following Liu et
al.'s frequency bucketing: *"we bucket idioms into quintiles based on their occurrence frequency
in source text"* — adapted here to idiom character length instead of corpus frequency.

**Measures:**
- **Idiom character length distribution** per source language: histogram and descriptive stats
  - Chinese: test whether 4-character idioms (chengyu) form a distinct cluster
  - Japanese: test whether 4-character yojijukugo similarly cluster
- **Idiom length quintile analysis**: bucket idioms into 5 quintiles by character length;
  for each quintile report mean expansion ratio and mean span-to-translation ratio per strategy
- **Sentence context length**: within each (idiom, target language) group, compute Spearman
  correlation between source sentence length and translation length — test whether longer context
  sentences produce longer translations

**Outputs:** `figures/module5_idiom_length_distribution.png`,
`figures/module5_quintile_analysis.png`, correlation table.

---

## Module 6 — Data Quality Audit
*Methods provenance: §3, §4, §10 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Systematically locate annotation errors and degenerate outputs before any downstream use.
Tang et al. report that the span is a valid substring *"for 1994 out of 2000 Chinese-English
sentence pairs"* — we replicate this check at scale across all 906k rows.

**Checks:**

| Check | Flag condition | Column(s) |
|---|---|---|
| Span not in translation | `span not in translation` (exact match) | all 3 strategy pairs |
| Span longer than translation | `len(span) > len(translation)` | all 3 strategy pairs |
| Empty span | `len(span) == 0` after stripping whitespace | all 3 strategy pairs |
| Missing span | `isnull(span)` | all 3 strategy pairs |
| Degenerate translation | `translation == sentence` | all 3 strategies |
| Very short translation | `len(translation) < 10` | all 3 strategies |
| Span equals source idiom verbatim | `span == idiom` (literal pass-through) | all 3 strategy pairs |

**Outputs:** `data/audit/anomalies.csv` (one row per flagged instance with flag type),
`figures/module6_flag_rates.png` (bar chart of flag rates per strategy and check type).

---

## Module 7 — Lexical Diversity Analysis
*Methods provenance: §2 of [methods_provenance.md](papers/methods_provenance.md)*

**Goal:** Quantify lexical variety in the idiom spans and full translations, following Tang et al.'s
proxy: *"We use the number of unique unigrams in the spans as a proxy for the number of different
translations for each idiom."*

**Measures:**
- **Unique unigrams per idiom** in `span_*` columns: for each (source language, idiom, strategy),
  count the number of distinct unigram types across all 10 target-language spans — high count = the
  strategy produces more lexically varied idiom renderings
- **Type-token ratio (TTR)** of translations: `unique_tokens / total_tokens` per row, per strategy
  — summarised as mean TTR by target language and source language
- **Span TTR vs. full translation TTR**: scatter per strategy — does a more lexically rich span
  occur in a more lexically rich translation?
- Distribution of unique unigram counts per idiom across strategies — test whether Analogy produces
  higher diversity than Creatively (as would be expected from its prompting design)

**Outputs:** `figures/module7_unique_unigrams.png`, `figures/module7_ttr_by_language.png`.

---

## Module 8 — Overlap with External Idiom Sources
*No direct methods provenance — this module uses publicly available idiom lexicons as external
reference points. All matching is exact string comparison on the idiom field; no inference required.*

**Goal:** Establish how IdiomTranslate30's idiom inventory relates to the broader documented
landscape of CJK idioms. Three questions drive the overlap investigation:
1. What fraction of IdiomTranslate30 idioms are attested in large external lexicons?
2. Do in-lexicon vs. out-of-lexicon idioms show different translation behaviour (length, span, divergence)?
3. What additional metadata (frequency, definition length) can be attached to matched idioms for use in other modules?

### External Sources

Search was restricted to freely downloadable resources (no account registration, file size ≤ ~15 MB).
No Japanese dataset meeting the ≥2,000-idiom threshold exists publicly; Japanese analyses are omitted.

| Source | Language | Idioms | Key annotation | Format | Size | Download URL |
|---|---|---|---|---|---|---|
| [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) | ZH | 31,648 | pinyin, Chinese definition, derivation, example sentence | JSON | 10.3 MB | `https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data/idiom.json` |
| [THUOCL chengyu](https://github.com/thunlp/THUOCL) | ZH | 8,519 | corpus document frequency only | TSV | 163 KB | `https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt` |
| [chinese-enthusiasts/idiom-embeddings](https://huggingface.co/datasets/chinese-enthusiasts/idiom-embeddings) | ZH | 2,999 | brief English gloss | Parquet | 185 KB | HuggingFace (no login) |
| [psyche/korean_idioms](https://huggingface.co/datasets/psyche/korean_idioms) | KO | ~7,986 rows (sokdam) | Korean definition, Q&A format | Parquet | 3 MB | HuggingFace (no login) |

### Analyses

**8a — Overlap audit: IdiomTranslate30 ∩ chinese-xinhua**

*Matching:* exact string match on the `word` field of chinese-xinhua against the `idiom` field of
IdiomTranslate30 Chinese rows (4,306 unique idioms).

- Report: number and percentage matched / unmatched overall, and broken down by idiom character
  length (4-char chengyu vs. other lengths)
- For unmatched idioms: compute their character length distribution — if they skew shorter or
  longer than the matched set, that signals a systematic difference in the idiom types covered
- Venn-style summary: how many of the 31,648 xinhua idioms never appear in IdiomTranslate30 (i.e.,
  what IdiomTranslate30 leaves out of the full chengyu lexicon)

**8b — Overlap audit: IdiomTranslate30 ∩ THUOCL**

*Matching:* exact string match against THUOCL's chengyu list (8,519 entries with document
frequency).

- Report: overlap count; THUOCL covers the most common chengyu, so the matched set can be
  interpreted as the "high-frequency" subset of IdiomTranslate30's Chinese idioms
- Frequency distribution of matched idioms (log-scale histogram of THUOCL document frequency)
- Compare matched vs. unmatched idioms on translation length and span length (Mann-Whitney U test)
  to test whether more-frequent chengyu receive longer or shorter translations

**8c — Frequency quintile analysis (Chinese)**

*Using the THUOCL-matched subset from 8b*, following Liu et al.'s bucketing approach:

- Assign each matched idiom to one of 5 frequency quintiles by THUOCL document frequency
- For each quintile, report: mean expansion ratio, mean span-to-translation ratio, and mean
  cross-strategy n-gram divergence (from Module 3) — all three per strategy
- Test monotonicity with Spearman ρ (frequency rank vs. each measure, per strategy)
- Expected finding from Liu et al.: higher-frequency idioms may receive more idiomatic (longer,
  more divergent) renderings across strategies

**8d — Definition length as complexity proxy (Chinese)**

*Using the chinese-xinhua-matched subset from 8a*, treating the character length of the `explanation`
field as a proxy for how semantically complex or culturally loaded an idiom is.

- Attach `len(explanation)` to each matched row
- Compute Spearman ρ between definition length and (a) mean translation length, (b) mean span
  length, (c) mean cross-strategy n-gram divergence — per strategy, macro-averaged over idioms
- Scatter plots: definition length (x) vs. each response variable (y), one panel per strategy

**8e — English gloss availability (Chinese)**

*Using chinese-enthusiasts/idiom-embeddings (2,999 idioms with brief English glosses):*

- Overlap with IdiomTranslate30 Chinese idioms: count and percentage matched
- For matched idioms, compare the gloss length against the span lengths in IdiomTranslate30
  English translations — does a longer English gloss predict a longer English span?

**8f — Overlap audit: IdiomTranslate30 ∩ psyche/korean_idioms**

*Matching:* exact string match between the `answer` field of psyche/korean_idioms (the proverb
text) and IdiomTranslate30 Korean idioms (2,316 unique).

- Report: overlap count. Because psyche/korean_idioms covers sokdam (sentence-form proverbs)
  while IdiomTranslate30 likely contains mostly saseong-eoro (Sino-Korean four-character idioms),
  near-zero overlap is expected — and is itself a finding that characterises the Korean idiom type
  in IdiomTranslate30
- Character length distribution of Korean idioms in IdiomTranslate30: confirm whether they are
  predominantly 4-character forms (saseong-eoro) vs. longer forms (sokdam/proverbs)

**Outputs:**
- `figures/module8_overlap_chinese_xinhua.png` — matched/unmatched breakdown by idiom length
- `figures/module8_thuocl_frequency_dist.png` — frequency distribution of matched chengyu
- `figures/module8_frequency_quintiles.png` — quintile analysis (expansion ratio, span ratio, divergence)
- `figures/module8_definition_length_corr.png` — definition length vs. translation behaviour scatter
- `figures/module8_overlap_korean.png` — Korean idiom length distribution + overlap result
- `data/processed/idiom_metadata.parquet` — IdiomTranslate30 unique idioms enriched with: THUOCL
  frequency, xinhua definition length, xinhua match flag, English gloss (where available)

---

## Implementation Roadmap

| Phase | Module | Script | Depends on | Status |
|---|---|---|---|---|
| 0 — Basic stats | — | `scripts/basic_stats.py` | — | Done |
| 0 — Figures & report | — | `scripts/generate_report.py` | — | Done |
| 1 — Length & expansion | 1 | `scripts/module1_length.py` | — | Planned |
| 2 — Span footprint | 2 | `scripts/module2_spans.py` | — | Planned |
| 3 — N-gram divergence | 3 | `scripts/module3_divergence.py` | — | Planned |
| 4 — Cross-lingual consistency | 4 | `scripts/module4_crosslingual.py` | — | Planned |
| 5 — Idiom morphology | 5 | `scripts/module5_morphology.py` | — | Planned |
| 6 — Data audit | 6 | `scripts/module6_audit.py` | — | Planned |
| 7 — Lexical diversity | 7 | `scripts/module7_lexdiv.py` | 6 (clean data) | Planned |
| 8 — External cross-ref | 8 | `scripts/module8_external.py` | 5, 6 | Planned |

All figures → `figures/`, all processed/audit data → `data/audit/` and `data/processed/`,
running report → `report.md`.

---

## Design Decisions

- **No ground-truth references.** Every measure is derived solely from string properties of the
  dataset's own columns. Wang et al. (MMTE) confirm that *"BERTScore struggles to distinguish the
  performance between metaphorical and literal translations"* — reference-based embedding metrics
  are unreliable for figurative language even when references are available.
- **No LLM judges.** All scoring is deterministic and reproducible from the raw parquet file alone.
- **Macro-averaging over idioms.** Following Baziotis et al.: aggregate statistics are always
  macro-averaged over unique idioms to avoid inflation from the larger Chinese idiom inventory.
- **Non-parametric tests throughout.** Translation lengths are heavy-tailed; Wilcoxon signed-rank
  and Mann-Whitney U are used in place of t-tests, consistent with Liu et al.'s permutation tests.
- **Span containment as primary quality signal.** Tang et al. establish substring containment as
  the canonical validity criterion for span annotations; all modules treat rows failing this check
  (from Module 6) as potentially unreliable.

---

## References (with provenance)

| Paper | Informs module(s) | Provenance entry |
|---|---|---|
| Tang et al., EMNLP 2024 Findings (Paper 7) | 1, 2, 6, 7 | §1, §2, §3 |
| Baziotis et al., EACL 2023 (Paper 2) | 1, 6 | §4, §5 |
| Zhou et al., MWE 2021 (Paper 10) | 3 | §6, §7, §8 |
| Liu et al., EMNLP 2023 (Paper 3) | 1, 4, 5 | §9, §12 |
| Dankers et al., ACL 2022 (Paper 1) | 6 | §10 |
| Wang et al., EMNLP 2024 (Paper 8) | design rationale | §11 |

Full citations and verbatim phrases: [papers/methods_provenance.md](papers/methods_provenance.md)
