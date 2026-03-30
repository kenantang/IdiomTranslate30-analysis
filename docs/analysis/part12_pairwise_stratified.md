# Part 12: Pairwise & Stratified Analysis

The analyses in Parts 1–11 aggregate error rates and translation properties at the level
of individual target languages or individual strategies.  Three complementary
stratification dimensions were left unexplored: **which specific source–target pairs**
are most error-prone, **whether the script family of the target** explains span
properties independently of language identity, and **whether the three source languages
produce systematically different lengths** under the same strategy.

---

## 12.1 Error Rates by Source–Target Pair

For each of the 90 cells (3 source × 10 target × aggregated across 3 strategies) we
compute the fraction of rows where the span is not a substring of the translation — the
same containment check as in Part 1, now broken down at the finest granularity available.

| Source | Mean error | Min | Max |
|---|---|---|---|
| Chinese  | 2.28% | 0.90% | 6.58% |
| Japanese | 1.82% | 0.64% | 6.97% |
| Korean   | 2.23% | 0.72% | 7.76% |

**Error rates vary 7–11× across source–target pairs**, far more than the aggregate
~2% figure suggests.  The *per-strategy* heatmap (Figure below) reveals three
consistent patterns:

- **Indic targets (Bengali, Hindi) carry the highest error rates** across all three
  source languages (4–8% vs 0.9–2.5% elsewhere).  Devanagari and Bengali script make
  partial-word overlap harder to detect with simple substring matching, inflating
  the apparent error rate — but the absolute gap is large enough to warrant specific
  attention when using span annotations for Indic outputs.
- **Cyrillic (Russian) is the most reliable target**, consistently below 1.5% across
  all strategies and source languages.
- **Strategy effect is small within a pair** (max 1–2 pp difference between Creatively
  and Author for any given source–target), confirming that error risk is dominated by
  the target language rather than the translation strategy.

![pairwise_error_heatmap](../figures/pairwise_error_heatmap.png)

---

## 12.2 Script-Family Effects on Span Properties

Rather than treating each of the 10 target languages independently, grouping them by
**script family** (Latin, Cyrillic, Arabic, Indic) isolates the contribution of writing
system from lexical or typological differences.

| Script family | Target languages | Median span ratio (Creatively) | Median trans. length | Mean error rate |
|---|---|---|---|---|
| Latin    | EN, FR, DE, ES, IT, SW | 0.277 | 103 chars | 1.45% |
| Cyrillic | RU                     | 0.282 |  94 chars | 1.04% |
| Arabic   | AR                     | 0.278 |  83 chars | 2.58% |
| Indic    | BN, HI                 | 0.260 |  88 chars | 4.37% |

Key observations:

- **Latin-script languages produce the longest translations** (median 103 chars) but have
  moderate span-to-translation ratios (~0.28).  Within this family, word-boundary
  matching works best, keeping error rates low.
- **Indic-script languages produce shorter translations on average** (88 chars) but have
  the lowest span ratios (0.26) and highest error rates (4.37%).  Agglutinative morphology
  means the span often embeds within a larger word stem, causing substring failures.
- **Arabic script sits between** Latin and Indic in most metrics: compact translations
  (83 chars), average span ratio, but elevated error (2.58%), consistent with
  VSO word order and rich morphological prefixation/suffixation.
- **Cyrillic shows the best quality metrics** across all three dimensions — relatively
  long translations, high span ratio, lowest error rate — likely reflecting both Russian's
  word-boundary structure and the model's strong performance on high-resource Cyrillic data.

![script_family_stats](../figures/script_family_stats.png)

---

## 12.3 Strategy Consistency Across Source Languages

Each strategy (Creatively, Analogy, Author) is nominally language-agnostic — the same
prompt is used regardless of whether the source idiom is Chinese, Japanese, or Korean.
If the strategy is truly source-agnostic, translation lengths should not vary
systematically by source language within the same target language.

A one-way ANOVA tests this for each strategy:

| Strategy | F-statistic | p-value |
|---|---|---|
| Creatively | 369.0 | 4.88 × 10⁻¹⁵⁹ |
| Analogy    | 479.5 | 1.08 × 10⁻²⁰⁵ |
| Author     | 460.5 | 1.03 × 10⁻¹⁹⁷ |

All three strategies show **highly significant source-language effects** — the same
strategy applied to Chinese vs Japanese vs Korean idioms produces measurably different
translation lengths across all 10 target languages.

The bar chart below shows the direction: **Chinese idioms consistently produce shorter
translations than Japanese or Korean idioms** under all three strategies.  This aligns
with the observation in Part 2 that Chinese chengyu tend to have more compact, standard
meanings (higher xinhua coverage, more frequent THUOCL entries), while Japanese and
Korean idioms in IT30 include many rarer or more culturally specific compounds that
require longer explication.  The strategy label shapes the *style* of the output, but
the source idiom's cultural specificity shapes its *length*.

![strategy_source_consistency](../figures/strategy_source_consistency.png)
