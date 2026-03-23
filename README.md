# IdiomTranslate30 — Basic Statistics Report

*Generated on 2026-03-22*

---

## Overview

**IdiomTranslate30** is a massively multilingual dataset of context-aware translations of East Asian
idioms across 30 language pairs, generated using Google Gemini 3.0 Flash Preview and published in
*EMNLP 2024 Findings*.

| Property | Value |
|---|---|
| Total rows | 906,600 |
| Columns | 10 |
| Source languages | 3 (Chinese, Japanese, Korean) |
| Target languages | 10 |
| Language pairs | 30 |
| Unique idioms | 8,949 |
| Missing span annotations | 62 |
| License | CC-BY-NC-SA-4.0 |

---

## Language Distribution

### Source Languages

| Language | Rows | Share |
|---|---|---|
| Chinese | 431,000 | 47.5% |
| Japanese | 244,000 | 26.9% |
| Korean | 231,600 | 25.5% |

### Target Languages

| Language | Rows | Share |
|---|---|---|
| Arabic | 90,660 | 10.0% |
| Bengali | 90,660 | 10.0% |
| English | 90,660 | 10.0% |
| French | 90,660 | 10.0% |
| German | 90,660 | 10.0% |
| Hindi | 90,660 | 10.0% |
| Italian | 90,660 | 10.0% |
| Russian | 90,660 | 10.0% |
| Spanish | 90,660 | 10.0% |
| Swahili | 90,660 | 10.0% |

Each of the 10 target languages is perfectly balanced (~90,660 rows, 10.0%).
Each of the 30 language pairs contains a fixed number of rows proportional to the source language's
idiom inventory size (Chinese: 43,100 / pair; Japanese: 24,400 / pair; Korean: 23,160 / pair).

---

## Idiom Coverage

| Source Language | Unique Idioms |
|---|---|
| Chinese | 4,306 |
| Japanese | 2,440 |
| Korean | 2,316 |
| **Total** | **8,949** |

Each idiom appears **200 times** in the dataset (10 target languages × ~20 context sentences),
ensuring balanced coverage across translation directions.

---

## Translation Length Statistics

Character-level length statistics for the three translation strategies:

| Strategy | Min | Median | Mean | Max |
|---|---|---|---|---|
| Creatively | 16 | 97 | 100 | 9472 |
| Analogy | 15 | 121 | 124 | 11821 |
| Author | 17 | 118 | 123 | 3034 |

Key observations:
- **Analogy** and **Author** strategies produce longer translations than **Creatively** (median ~121 vs 97 chars).
- All strategies have heavy-tailed distributions — the maximum lengths are 3–12× the median,
  indicating occasional verbose outputs.
- No translation is shorter than 15 characters (no empty outputs).

---

## Source Sentence Lengths

Source sentences are short by design (they carry exactly one idiom):

| Statistic | Value |
|---|---|
| Min | 0 chars |
| Median | 27 chars |
| Mean | 27.9 chars |
| Max | 108 chars |

---

## Missing Values

| Column | Missing |
|---|---|
| span_creatively | 19 |
| span_analogy | 19 |
| span_author | 24 |
| All others | 0 |

Missingness is negligible (<0.003% of rows) and only affects span annotation columns.

---

## Figures

### 1. Fig1 Language Distribution

![fig1_language_distribution.png](figures/fig1_language_distribution.png)

Distribution of rows across source (left) and target (right) languages. Target languages are perfectly balanced (~90,660 rows each), while Chinese contributes nearly half the source sentences.

### 2. Fig2 Idiom Coverage

![fig2_idiom_coverage.png](figures/fig2_idiom_coverage.png)

Number of unique idioms per source language. Chinese has the largest inventory (4,306), followed by Japanese (2,440) and Korean (2,316).

### 3. Fig3 Translation Length Violin

![fig3_translation_length_violin.png](figures/fig3_translation_length_violin.png)

Violin plot of translation lengths (characters) for each strategy on a 50k-row sample. Inner lines show quartiles. Analogy and Author strategies tend to produce longer translations than the Creatively strategy.

### 4. Fig4 Length By Target Language

![fig4_length_by_target_language.png](figures/fig4_length_by_target_language.png)

Median character count of each translation strategy grouped by target language. Languages with complex scripts (e.g., Arabic, Bengali, Hindi) tend to have shorter character counts despite equivalent semantic content.

### 5. Fig5 Sentence Length By Source

![fig5_sentence_length_by_source.png](figures/fig5_sentence_length_by_source.png)

Density histogram of source sentence lengths by language. All three languages show a similar unimodal distribution peaking around 25–30 characters, consistent with the dataset's design of short, idiom-carrying sentences.

### 6. Fig6 Span Length By Strategy

![fig6_span_length_by_strategy.png](figures/fig6_span_length_by_strategy.png)

Box plots of the character length of the idiom span identified within each translation. The Analogy strategy produces noticeably longer spans, suggesting more elaborate idiomatic substitutions.

### 7. Fig7 Missing Spans

![fig7_missing_spans.png](figures/fig7_missing_spans.png)

Count of missing span annotations per source language and strategy. Missingness is very low overall (<25 rows) and concentrated in Chinese rows.

## TODO

- [ ] **Expand to other idiom type datasets.** The Korean overlap analysis revealed that
  IdiomTranslate30 covers only saseong-eoro (사자성어, four-character Sino-Korean idioms), not
  the full range of Korean idiomatic expression. The same gap likely applies to Japanese
  (yojijukugo only, not kotowaza proverbs) and Chinese (chengyu only, not xiehouyu or
  other figurative forms). Identify and analyse datasets covering these complementary types:
  - Korean 속담 (sokdam): sentence-form proverbs — e.g. `psyche/korean_idioms`
  - Japanese ことわざ (kotowaza): proverbs — e.g. `sepTN/kotowaza` (small, 100 entries; larger source needed)
  - Japanese 慣用句 (kan'youku): idiomatic verb phrases distinct from yojijukugo
  - Chinese 歇后语 (xiehouyu): two-part allegorical sayings structurally unlike chengyu

- [ ] **Cross-lingual semantic overlap between Chinese and Korean saseong-eoro.** Since
  saseong-eoro are phonetic Hangul renderings of Chinese-origin four-character idioms, many
  should share the same underlying meaning as Chinese chengyu (e.g. 일석이조 ≈ 一石二鸟). Quantify
  the semantic overlap using transliteration or shared Hanja etymology, and measure whether
  idioms with Chinese cognates receive more similar translations across the two source languages.

- [ ] **Analyse the 4.4% Chinese idioms not in chinese-xinhua.** The 189 unmatched chengyu are
  predominantly non-4-character forms. Characterise them: are they archaic, regional, or
  recently coined? Check against additional lexicons (e.g. online dictionaries, CHID candidate
  list).

- [ ] **Investigate span-not-in-translation errors (~2% of rows).** Determine whether these are
  purely formatting artefacts (whitespace, punctuation) or reflect genuine annotation errors.
  Classify by error type and assess whether they are safe to ignore or require filtering.

- [ ] **Extend external overlap to Japanese.** No public Japanese idiom dataset ≥ 2,000 entries
  was found. Consider scraping or constructing a yojijukugo reference list from freely available
  sources (e.g. Wiktionary JA, jisho.org bulk export) to enable the same coverage and frequency
  analyses applied to Chinese.
