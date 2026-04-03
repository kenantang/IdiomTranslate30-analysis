# IdiomTranslate30 — Analysis

> **Disclaimer:** This report was generated with the assistance of [Claude Code](https://claude.ai/claude-code).
> Numerical results are derived from scripts run against the raw data, but interpretations and
> prose descriptions may contain errors. Verify critical findings against the source scripts
> and data before citing.

**IdiomTranslate30** is a massively multilingual dataset of context-aware translations of East
Asian idioms across 30 language pairs (3 source × 10 target), generated using Google Gemini 3.0
Flash Preview. It extends the methodology of *Tang et al. (2024)* (EMNLP Findings, pp. 9285–9305),
scaling from a single language pair to 30 and switching from GPT-4 to Gemini 3.0.

| Property | Value |
|---|---|
| Total rows | 906,600 |
| Total translations | 2,719,800 (× 3 strategies) |
| Source languages | 3 (Chinese, Japanese, Korean) |
| Target languages | 10 |
| Unique idioms | 8,949 |
| License | CC-BY-NC-SA-4.0 |

## Documentation

The full analysis is in the MkDocs site under [`docs/`](docs/). To browse locally:

```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

Then open <http://127.0.0.1:8000>.

### Contents

| Section | Topic |
|---|---|
| [Dataset Overview](docs/dataset/overview.md) | Row counts, language distributions, length statistics |
| [Edge Cases](docs/dataset/edge_cases.md) | Zero-length sentences, doubled idioms, failure modes |
| [Pre-processing](docs/dataset/preprocessing.md) | Long-translation filtering |
| [Figures](docs/dataset/figures.md) | All dataset figures (fig1–fig7) |
| [Part 1 — Data Quality](docs/analysis/part1_data_quality.md) | Span annotation audit and error classification |
| [Part 2 — Idiom Coverage](docs/analysis/part2_idiom_coverage.md) | Morphology, external coverage, yojijukugo |
| [Part 3 — Translation Behaviour](docs/analysis/part3_translation_behaviour.md) | Length, span position, diversity, context sensitivity |
| [Part 4 — Cross-Lingual Patterns](docs/analysis/part4_cross_lingual.md) | Consistency and vocabulary overlap across targets |
| [Part 5 — Cognate Analysis](docs/analysis/part5_cognate_analysis.md) | ZH–KO, ZH–JA, KO–JA cognate pairs |
| [Part 6 — Synthesis](docs/analysis/part6_synthesis.md) | Composite idiom difficulty score |
| [Part 7 — Language Profiles](docs/analysis/part7_language_profiles.md) | English fingerprint; high- vs low-resource target patterns |
| [Part 8 — Reverse Span Analysis](docs/analysis/part8_reverse_span.md) | Translation attractors; most overloaded spans per language |
| [Part 9 — Analogy Slop Patterns](docs/analysis/part9_analogy_slop.md) | Recurring LLM clichés in the Analogy strategy |
| [Part 10 — Additional Analyses](docs/analysis/part10_additional.md) | Slop scores, template vs surface diversity, bathos |
| [Part 11 — Heuristics & LLM-as-a-Judge](docs/analysis/part11_heuristics.md) | All 29 heuristic matching choices; upgrade proposals |
| [Part 12 — Pairwise & Stratified Analysis](docs/analysis/part12_pairwise_stratified.md) | Error rates per (source × target) cell; script-family groupings |
| [Part 13 — Extended Cognate Analysis](docs/analysis/part13_extended_cognates.md) | Three-way ZH–JA–KO triples; divergence ranking |
| [Part 14 — Anomaly & Divergence Baseline](docs/analysis/part14_anomaly_divergence.md) | Zero-sentence rows; within- vs between-idiom CV ratio |
| [Part 15 — Context, Difficulty & Typology](docs/analysis/part15_context_difficulty.md) | Sentence length → CV; OLS difficulty regression; typology effects |
| [Part 16 — Multilingual Templates](docs/analysis/part16_multilingual_templates.md) | Data-driven bigram over-representation across all 10 target languages |
| [Part 17 — Strategy Length Correlations](docs/analysis/part17_strategy_correlations.md) | Pearson r(C↔A/Au) per target language; resource-level effect |
| [Part 18 — Strategy by Idiom Category](docs/analysis/part18_strategy_by_category.md) | Error rates and CV across difficulty quartile, source language, 4-char flag |
| [Part 19 — Semantic Consistency Audit](docs/analysis/part19_semantic_consistency.md) | Stability = 1 − mean edit distance; most/least stable idioms |
| [Part 20 — English Pretraining Bias](docs/analysis/part20_english_pretraining_bias.md) | English z-scores vs high-resource group; span-ratio anomaly; anomaly ranking |
| [Part 21 — Correlation Gap Analyses](docs/analysis/part21_correlation_gaps.md) | 22 pairwise correlations across consistency metrics, slop, expansion, error rate, cognates, and templates |
| [Reference: Definitions](docs/reference/definitions.md) | All metrics, scores, and derived variables |
| [Reference: Correlation Map](docs/reference/correlation_map.md) | All pairwise correlations organized by outcome variable |

## Repository Structure

```
IdiomTranslate30-analysis/
├── data/
│   ├── raw/          IdiomTranslate30.parquet
│   ├── processed/    Per-script result files (CSV / Parquet / JSON)
│   └── audit/        Anomaly and error logs
├── docs/             MkDocs source (one page per analysis part)
├── figures/          All generated figures (PNG)
├── scripts/          Analysis scripts (one script per analysis)
├── site/             Built MkDocs HTML (gitignored)
└── mkdocs.yml        MkDocs configuration
```

## Reproducing the Analysis

Run scripts in roughly this order (each is independent and writes to `data/processed/`):

```bash
python scripts/basic_stats.py          # dataset overview + fig1/2/5
python scripts/span_audit.py           # data quality + fig7
python scripts/span_errors.py          # span error classification
python scripts/translation_length.py   # length analysis + fig3/4
python scripts/span_analysis.py        # span footprint + fig6
python scripts/span_position.py
python scripts/strategy_divergence.py
python scripts/lexical_diversity.py
python scripts/context_sensitivity.py
python scripts/crosslingual_consistency.py
python scripts/cross_target_overlap.py
python scripts/external_coverage.py
python scripts/idiom_morphology.py
python scripts/unmatched_chinese.py
python scripts/japanese_yojijukugo.py
python scripts/complementary_idiom_types.py
python scripts/cjk_cognates.py
python scripts/cognate_comparison_zhko.py
python scripts/cognate_comparison_extended.py
python scripts/difficulty.py
python scripts/english_and_resource_profile.py
python scripts/reverse_span_analysis.py
python scripts/analogy_deep_analysis.py
python scripts/pairwise_error_analysis.py
python scripts/triple_cognate_analysis.py
python scripts/anomaly_divergence.py
python scripts/context_difficulty_extended.py
python scripts/multilingual_slop.py
python scripts/strategy_length_correlations.py
python scripts/strategy_by_idiom_category.py
python scripts/semantic_consistency_audit.py
python scripts/english_pretraining_bias.py
python scripts/correlation_gaps.py
```
