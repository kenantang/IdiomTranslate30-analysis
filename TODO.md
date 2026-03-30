# TODO

## Pending: Correlation Gap Analyses

Identified by systematic audit of `docs/reference/correlation_map.md` against `docs/reference/definitions.md`.
All items below have the necessary data already available in `data/processed/`.

---

### 1. Consistency metric intercorrelations

`cv`, `jaccard_div`, `span_uniq`, and `dom_frac` are all used as consistency measures
throughout the analysis but their pairwise correlations have never been computed.
If they are near-redundant, reporting them separately is misleading.

- [ ] `cv` ↔ `jaccard_div` (Spearman ρ, per strategy)
- [ ] `cv` ↔ `span_uniq` (Spearman ρ, per strategy)
- [ ] `cv` ↔ `dom_frac` (Spearman ρ)
- [ ] `dom_frac` ↔ `span_uniq` (Spearman ρ)
- [ ] `jaccard_div` ↔ `span_uniq` (Spearman ρ)

Data: `data/processed/context_sensitivity.parquet`, `data/processed/target_language_profile.parquet`

---

### 2. Slop score as outcome

`slop_score` is defined and used in Parts 9–10 but never treated as a dependent variable.

- [ ] `slop_score` ↔ `difficulty` — do templated Analogy outputs cluster on easier or harder idioms?
- [ ] `slop_score` ↔ `stability` (semantic stability, Part 19)
- [ ] `slop_score` ↔ `expansion_ratio` — does the model use longer output when it can't find a template?
- [ ] `slop_score` ↔ `in_xinhua` / `def_len` — does better documentation suppress template use?

Data: `data/processed/idiom_slop_scores.csv`, `data/processed/idiom_difficulty.parquet`,
`data/processed/semantic_consistency.csv`, `data/processed/idiom_metadata.parquet`

---

### 3. Cross-target vocabulary overlap as outcome

`cross_target_overlap` (mean cross-language Jaccard per idiom) is a component of the
difficulty score but has never been analyzed as a standalone outcome.

- [ ] `cross_target_overlap` ↔ `stability` — is cross-language consistency correlated with cross-strategy consistency?
- [ ] `cross_target_overlap` ↔ `slop_score` — do templated idioms show higher cross-language overlap?
- [ ] `cross_target_overlap` ↔ `attractor_coverage` — do high-attractor idioms also cluster cross-linguistically?

Data: `data/processed/cross_target_overlap.parquet`, `data/processed/semantic_consistency.csv`,
`data/processed/idiom_slop_scores.csv`, `data/processed/span_attractor_counts.parquet`

---

### 4. Attractor coverage as outcome

`attractor_coverage` (n_idioms per span phrase) is reported qualitatively in Part 8
but never correlated with other metrics.

- [ ] `attractor_coverage` ↔ `difficulty` — do semantically clear idioms (low difficulty) produce high-coverage attractors?
- [ ] `attractor_coverage` ↔ `slop_score` — do high-attractor spans coincide with template-prone idioms?
- [ ] `attractor_coverage` ↔ `cross_target_overlap`

Data: `data/processed/span_attractor_counts.parquet`, `data/processed/idiom_difficulty.parquet`,
`data/processed/idiom_slop_scores.csv`, `data/processed/cross_target_overlap.parquet`

---

### 5. Error rate ↔ consistency and length metrics

Section 8 of the correlation map only tests difficulty quartile and zero-sentence as
predictors of error rate. Missing direct correlations:

- [ ] `error_rate` ↔ `cv` — do spans from high-CV cells also fail containment more often?
- [ ] `error_rate` ↔ `translation_length` — do longer translations produce more span mismatches?
- [ ] `error_rate` ↔ `expansion_ratio` — does a high expansion ratio predict span annotation failure?

Data: `data/processed/pairwise_error_rates.csv`, `data/processed/context_sensitivity.parquet`,
raw data (`data/raw/IdiomTranslate30.parquet`)

---

### 6. Cognate match type → translation divergence

The cognate section (Part 7, correlation map section 7) reports ρ separately for
exact and near-3 pairs but never tests whether match type *predicts* divergence.

- [ ] `match_type` (exact_4/4 vs near_3/4) → `edit_pair_mean` — Mann–Whitney U test
- [ ] Within three-way triples: does all-exact vs mixed match type predict lower divergence?

Data: `data/processed/cognate_divergence_ranking.csv`, `data/processed/triple_cognates.csv`

---

### 7. Expansion ratio as outcome

`expansion_ratio` is only used as a predictor of difficulty (ρ = +0.649). As an outcome
it is never quantified:

- [ ] `expansion_ratio` ↔ `char_len` — Part 2 states non-4-char idioms expand more, but ρ not reported
- [ ] `expansion_ratio` ↔ `stability` — do idioms with more expansive translations show more cross-strategy disagreement?
- [ ] `expansion_ratio` ↔ `slop_score` — does template use compress or expand output length?

Data: `data/raw/IdiomTranslate30.parquet`, `data/processed/semantic_consistency.csv`,
`data/processed/idiom_slop_scores.csv`

---

### 8. Multilingual template rate ↔ target language metrics

`template_rate` per target language (Part 16) is only reported as a percentage. Never
formally correlated with other per-language profile metrics.

- [ ] `template_rate` ↔ `error_rate` (per target language, n=10, Spearman ρ)
- [ ] `template_rate` ↔ `cv` (per target language, n=10)
- [ ] `template_rate` ↔ `resource` — the 3× difference (27.9% low vs 9.1% high) should be formally tested (Mann–Whitney, n=4 vs n=6)

Data: `data/processed/multilingual_template_scores.csv`, `data/processed/target_language_profile.parquet`
