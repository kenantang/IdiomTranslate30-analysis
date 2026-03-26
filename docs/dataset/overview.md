# Overview

**IdiomTranslate30** is a massively multilingual dataset of context-aware translations of East Asian
idioms across 30 language pairs, generated using Google Gemini 3.0 Flash Preview. It extends the
translation methodology introduced in *Tang et al. (2024), "Creative and Context-Aware Translation
of East Asian Idioms with GPT-4"* (Findings of EMNLP 2024, pp. 9285–9305), scaling from a single
language pair to 30 language pairs and switching the backbone model from GPT-4 to Gemini 3.0.

The name **IdiomTranslate30** is doubly meaningful: 30 language pairs (3 source × 10 target), and
30 parallel translations per (idiom, target language) — 10 context sentences each translated under
3 strategies (Creatively, Analogy, Author), giving 30 translations per cell.

Each row in the dataset corresponds to one (source idiom, target language, context sentence) triple
and contains **3 translations** (one per strategy) plus 3 span annotations, for a total of
**2,719,800 individual translations** (906,600 rows × 3 strategies).

The 906,600 rows are derived as follows:

| Source | Idioms | × Target langs | × Sentences | = Rows |
|---|---|---|---|---|
| Chinese | 4,306 | 10 | 10 (20 for 4 idioms) | 431,000 |
| Japanese | 2,440 | 10 | 10 | 244,000 |
| Korean | 2,316 | 10 | 10 | 231,600 |
| **Total** | **9,062** | | | **906,600** |

> **Unintentional dictionary duplicates — two types:**
>
> **(1) 113 ZH–JA shared idiom strings.** The per-source totals sum to **9,062**, but the
> dataset-wide unique count is **8,949** because 113 classical Chinese idiom strings (e.g.
> 一丘之貉, 一刻千金, 一字千金) appear identically as both a Chinese entry and a Japanese
> yojijukugo entry. These are unintentional duplicates caused by the same string being present
> in both the Chinese and Japanese source dictionaries. All 113 appear as "exact_4/4" pairs in
> the ZH–JA cognate table (see Extended Cognate Analysis below), accounting for 113 of the 266 reported exact matches;
> the remaining 153 are genuine cognates with different raw forms (e.g. simplified ZH 精明强干
> vs Japanese 精明強幹) that match only after s2t normalisation.
>
> **(2) 4 Chinese idioms entered twice in the source dictionary.** 前仆后继, 固执己见,
> 生龙活虎, and 触景生情 each triggered two independent sentence-generation prompt runs instead
> of one, producing 20 sentences per target language rather than 10. Inspection confirms the
> two runs are stored as consecutive blocks of 10: sentences 1–10 and 11–20 are generated
> independently from the same prompt, and do overlap — for 触景生情, sentences 11–13 are exact
> duplicates of sentences 1–3. This adds 4 × 10 × 10 = 400 extra rows, explaining why
> 4,306 × 10 × 10 = 430,600 ≠ 431,000.

| Property | Value |
|---|---|
| Total rows | 906,600 |
| Total translations | 2,719,800 (906,600 × 3 strategies) |
| Columns | 10 |
| Source languages | 3 (Chinese, Japanese, Korean) |
| Target languages | 10 |
| Language pairs | 30 (3 × 10) |
| Context sentences per (idiom, target language) | 10 |
| Translation strategies per sentence | 3 (Creatively, Analogy, Author) |
| Unique idioms | 8,949 |
| Missing span annotations | 62 |
| License | CC-BY-NC-SA-4.0 |

---

# Language Distribution

## Source Languages

| Language | Rows | Share |
|---|---|---|
| Chinese | 431,000 | 47.5% |
| Japanese | 244,000 | 26.9% |
| Korean | 231,600 | 25.5% |

## Target Languages

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

# Idiom Coverage

| Source Language | Unique Idioms |
|---|---|
| Chinese | 4,306 |
| Japanese | 2,440 |
| Korean | 2,316 |
| **Total** | **8,949** |

Most idioms appear **100 times** in the dataset (10 target languages × 10 context sentences).
Four Chinese idioms appear 200 times (see [Data Edge Cases](edge_cases.md)).

---

# Translation Length Statistics

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

# Source Sentence Lengths

Source sentences are short by design (they carry exactly one idiom):

| Statistic | Value |
|---|---|
| Min | 0 chars |
| Median | 27 chars |
| Mean | 27.9 chars |
| Max | 108 chars |

---

# Missing Values

| Column | Missing |
|---|---|
| span_creatively | 19 |
| span_analogy | 19 |
| span_author | 24 |
| All others | 0 |

Missingness is negligible (<0.003% of rows) and only affects span annotation columns.
