# TODO

All correlation gap analyses from the first audit round are complete.
See `docs/analysis/part21_correlation_gaps.md` and `docs/reference/correlation_map.md`.

---

## Remaining Analysis Gaps

Identified in the second consistency audit (2026-04-03).

### A. Source-Language Effects (medium effort)

The analysis frequently conditions on target language but treats source language
as a covariate.  Dedicated source-language analyses are sparse.

- [ ] **Slop score by source language** — are Chinese, Japanese, or Korean idioms
  more template-prone in English Analogy spans?
  Data: `data/processed/idiom_slop_scores.csv` (has `source_language`)

- [ ] **Stability by source language** — do Chinese, Japanese, or Korean idioms
  show different cross-strategy semantic stability?
  Data: `data/processed/semantic_consistency.csv` (has `source_language`)

- [ ] **Expansion ratio by source language** — Part 15 OLS regression includes
  source language dummies, but per-source expansion ratio distribution has not been
  plotted or formally tested.
  Data: `data/processed/idiom_difficulty.parquet` (`exp_mean` + `source_language`)

### B. Strategy × Target Interaction Effects (medium effort)

Parts 12–18 analyse strategies and target languages separately, but the
*interaction* (does Analogy behave differently in Arabic vs English relative to
Creatively?) has not been formally tested.

- [ ] **Error rate: strategy × target interaction** — 3×10 ANOVA interaction term.
  Data: `data/processed/pairwise_error_rates.csv`

- [ ] **CV: strategy × target** — does the Author strategy show more CV variation
  across target languages than Creatively?
  Data: `data/processed/context_sensitivity.parquet`

### C. Span Position × Source Language (low effort)

Part 3 notes that Chinese and Korean sources place spans later (~0.59) than
Japanese (~0.54), but no formal test was reported.

- [ ] Kruskal–Wallis or one-way ANOVA: source language → relative span position,
  controlling for target language.
  Data: `data/processed/span_positions.parquet`

### D. JA–KO Cognate Divergence (medium effort)

The cognate divergence analysis (Parts 5, 13, 21) focuses on ZH–KO and ZH–JA
pairs.  JA–KO has 802 pairs (`koja_cognate_pairs.csv`) but no edit-distance
divergence ranking equivalent to `cognate_divergence_ranking.csv`.

- [ ] Compute per-pair edit_pair_mean for JA–KO cognate pairs and compare
  exact_4/4 vs near_3/4 (Mann–Whitney), completing the three-way analysis.
  Data: raw parquet + `data/processed/koja_cognate_pairs.csv`

---

## Definition Formalisation Gaps

### E. `jaccard_div` naming (low effort — documentation only)

The metric is named `jaccard_div` but stores Jaccard **similarity** (not
distance/diversity).  The definition has been corrected in `definitions.md`, but
the column name in all parquet files still says `jaccard_div`.  If the dataset is
ever published, consider renaming to `jaccard_sim` with a deprecation note.
(No script changes needed for the current analysis.)

### F. Semantic stability averaging (low effort — documentation only)

The `stability` definition says "averaged across available target languages per
idiom" but does not specify: are errored rows (span not in translation) included
or excluded?  The `semantic_consistency_audit.py` script should be checked and
the definition updated accordingly.
Data: `scripts/semantic_consistency_audit.py` lines ~40–70
