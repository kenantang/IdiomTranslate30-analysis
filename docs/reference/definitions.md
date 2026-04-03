# Definitions

All metrics, scores, and derived variables used across the analysis, organized by
domain.  The "Computed in" column points to the script that produces the value.

---

## Translation & Length

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Translation length | — | Character count of the translated sentence for one strategy | `translation_length.py` |
| Expansion ratio | — | `len(translation) / len(source_sentence)` | `translation_length.py` |
| Word expansion ratio | `wexp` | Translation word count / source idiom character count | `english_and_resource_profile.py` |
| Span/translation ratio | — | `len(span) / len(translation)` | `span_analysis.py` |
| Relative span position | `rel_start` | `span_start_offset / (len(translation) − len(span))`, 0 = start, 1 = end | `span_position.py` |
| Position zone | — | Categorical: beginning / middle / end based on `rel_start` thresholds | `span_position.py` |

---

## Span Annotation Quality

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Span containment error | — | Span is not a substring of its translation (exact match fails) | `span_audit.py` |
| Span classification | — | One of: ok / whitespace / case mismatch / punctuation / off-by-one / partial word overlap / no overlap | `utils.py` H1–H6 |
| Missing span | — | `span` field is null or empty | `span_audit.py` |
| Span equals idiom | — | `span == idiom` verbatim (model copied the source rather than translating) | `span_audit.py` |
| Degenerate translation | — | Translation equals source sentence (no translation performed) | `span_audit.py` |
| Short translation | — | Translation length < SHORT\_THRESH (5 or 10 chars depending on context) | `span_audit.py` |
| Long translation | — | Translation length > LONG\_THRESH (500 chars) | `basic_stats.py` |
| Flagged row | — | Row carries at least one of the above quality flags | `span_audit.py` |
| Pairwise error rate | — | Fraction of flagged rows per (source, target, strategy) cell | `pairwise_error_analysis.py` |

---

## Diversity & Consistency

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Within-cell CV | `cv` | Coefficient of variation of translation length across the 10 context sentences for one (idiom, target, strategy) cell | `context_sensitivity.py` |
| Jaccard similarity | `jaccard_div` | Mean pairwise word-set Jaccard similarity across all C(10, 2) sentence pairs in a cell: `|A∩B| / |A∪B|`. **Higher = more vocabulary overlap = less within-cell diversity.** Named `jaccard_div` historically but measures similarity, not distance. Note: inflection-blind and inapplicable to CJK (no inter-word spaces), so Arabic and Indic-script values are systematically lower than Latin-script values for structural rather than purely behavioural reasons. | `context_sensitivity.py` |
| Span uniqueness | `span_uniq` | Fraction of the 10 sentence-level spans that are distinct strings in a cell | `context_sensitivity.py` |
| Dominant span fraction | `dom_frac` | Fraction of the 10 sentences that share the single most-common span phrase | `english_and_resource_profile.py` |
| Type–token ratio (TTR) | — | Unique word types / total word tokens in a translation or span | `lexical_diversity.py` |
| Between-cell CV std | — | Standard deviation of `cv` across different idioms within the same (target, strategy); used as a divergence baseline | `anomaly_divergence.py` |

---

## Cross-Strategy Divergence

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Unigram divergence C↔A | `div_CA_ng1` | Proportion of unigrams that differ between the Creatively and Analogy spans for the same (idiom, target) | `strategy_divergence.py` |
| Normalized edit distance | `edit_CA` etc. | `levenshtein(span_A, span_B) / max(len(span_A), len(span_B))` | `strategy_divergence.py` |
| Span Jaccard C↔A | `span_jac_CA` | Word-set Jaccard similarity between Creatively and Analogy spans | `english_and_resource_profile.py` |
| Semantic stability | — | `1 − mean(edit_CA, edit_CAu, edit_AAu)`, averaged across available target languages per idiom; higher = strategies agree more | `semantic_consistency_audit.py` |

---

## Idiom Difficulty

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Composite difficulty score | `difficulty` | Average of four percentile-ranked components (each mapped 0–1 via `rank / max_rank`): (1) mean cross-strategy unigram divergence `div_mean_edit`, (2) mean expansion ratio `exp_mean`, (3) mean within-cell CV `mean_cv`, (4) mean cross-target Jaccard dissimilarity `wf_jaccard`. Higher score = harder to translate consistently. | `difficulty.py` |
| Slop score | `slop_score` | Fraction of the 10 English Analogy spans for an idiom that match one of the 8 named template families | `analogy_deep_analysis.py` |
| Template rate (multilingual) | — | Fraction of Analogy spans containing ≥ 1 over-represented bigram (2.5× Creatively rate) for a given target language | `multilingual_slop.py` |

---

## Idiom Coverage

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Xinhua coverage | `in_xinhua` | Boolean: idiom appears in the chinese-xinhua 31k chengyu dictionary | `external_coverage.py` |
| THUOCL coverage | `in_thuocl` | Boolean: idiom appears in the THUOCL 8,519-entry frequency corpus | `external_coverage.py` |
| THUOCL frequency | `thuocl_freq` | Raw corpus frequency count from THUOCL | `external_coverage.py` |
| Definition length | `def_len` | Character count of the xinhua dictionary definition for an idiom | `external_coverage.py` |
| Wiktionary coverage | — | Boolean: idiom appears in the kaikki.org Japanese Wiktionary dump | `japanese_yojijukugo.py` |

---

## Cross-Lingual & Cognate

| Name | Notation | Definition | Computed in |
|---|---|---|---|
| Cognate pair | — | Two idioms in different source languages that share CJK characters after simplified/traditional normalisation | `cjk_cognates.py` |
| Exact match (4/4) | `exact_4/4` | All 4 character positions match between the two idiom forms | `cjk_cognates.py` |
| Near match (3/4) | `near_3/4` | Exactly 3 of 4 character positions match | `cjk_cognates.py` |
| Three-way triple | — | A (ZH, JA, KO) tuple where all three pairwise cognate links exist simultaneously | `triple_cognate_analysis.py` |
| Pair edit mean | `edit_pair_mean` | Average of edit distances for the ZH and KO members of a cognate pair, each averaged across all available target languages | `triple_cognate_analysis.py` |
| Cross-target vocabulary overlap | — | Mean word-set Jaccard between translations of the same idiom across all 45 pairs of target languages | `cross_target_overlap.py` |
| Cross-lingual consistency | — | Stability of vocabulary choice across multiple source or target languages for the same idiom concept | `crosslingual_consistency.py` |

---

## Target Language Profile

Each entry in `target_language_profile.parquet` summarises an entire target language
across all (idiom, source, strategy) triples.

| Column | Definition |
|---|---|
| `cv` | Mean within-cell CV across all cells for this target |
| `jaccard_div` | Mean pairwise Jaccard diversity across all cells |
| `span_uniq` | Mean span uniqueness across all cells |
| `div_CA` | Mean unigram divergence C↔A across all cells |
| `edit_CA` | Mean normalised edit distance C↔A across all cells |
| `rel_start` | Mean relative span position across all cells |
| `span_ratio` | Mean word-expansion ratio (wexp normalised form) |
| `wexp` | Mean word expansion ratio |
| `error_rate` | Mean span containment error rate (%) |
| `dom_frac` | Mean dominant span fraction |
| `span_jac_CA` | Mean span Jaccard C↔A |
| `resource` | `high` or `low`, based on NLP resource availability |

---

## Script Family Grouping (Part 12)

Target languages grouped by writing system for the pairwise error analysis.

| Script family | Languages |
|---|---|
| Latin | English, French, German, Spanish, Italian, Swahili |
| Cyrillic | Russian |
| Arabic | Arabic |
| Indic | Bengali, Hindi |

---

## Linguistic Typology (Part 15)

| Property | Values | Languages |
|---|---|---|
| Word order | SVO | EN, FR, DE, ES, IT, RU, SW |
| Word order | SOV | BN, HI |
| Word order | VSO | AR |
| Morphology | Low    | EN, FR, ES, IT |
| Morphology | Medium | DE, BN, HI |
| Morphology | High   | RU, AR, SW |
| Script     | Latin    | EN, FR, DE, ES, IT, SW |
| Script     | Cyrillic | RU |
| Script     | Arabic   | AR |
| Script     | Indic    | BN, HI |

---

## Attractor & Template (Parts 8–9, 16)

| Name | Definition | Computed in |
|---|---|---|
| Translation attractor | A span phrase that is reused across multiple source idioms mapping to the same target concept | `reverse_span_analysis.py` |
| Attractor coverage (per span) | Number of distinct source idioms (`n_idioms`) that produce the same normalized span phrase in a given target language | `reverse_span_analysis.py` |
| Attractor coverage (per idiom) | Mean `n_idioms` across all span phrases produced by an idiom across strategies and target languages; measures how "attractor-shared" an idiom's translations are | `deferred_correlations.py` |
| Template family | One of 8 named metaphor frames in English Analogy spans: weaving/thread, cosmic/star, kaleidoscope, futility ("trying to…"), dandelion/scattered, labyrinth/mirror, clockmaker precision, mist/castle | `utils.py` H16 |
| Bathos span | Analogy span that is a single word or simple noun phrase rather than an extended metaphor | `analogy_deep_analysis.py` |
| Over-represented bigram | A bigram whose Analogy frequency is ≥ 2.5× its Creatively frequency (with Laplace smoothing, min count 30); word bigrams for Latin-script languages, character bigrams for Arabic, Indic, and Cyrillic scripts | `multilingual_slop.py` |
