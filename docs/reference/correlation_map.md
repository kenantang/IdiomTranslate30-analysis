# Correlation Map

All pairwise correlation and association analyses performed across the project,
organized by outcome variable.  Entries marked **—** had p-values reported only
as significant/non-significant in the source part without an exact figure.

---

## 1. Idiom Difficulty

*Outcome: composite difficulty score (Part 6).*  All Spearman unless noted.

| Predictor | ρ | p | Direction | Part |
|---|---|---|---|---|
| Mean expansion ratio | +0.649 | ≈ 0 | Higher expansion → harder | 6 |
| Mean within-cell CV | +0.529 | ≈ 0 | More context-sensitive → harder | 6 |
| Source: Japanese (vs Korean ref.) | +0.386 | ≈ 0 | Japanese idioms harder | 15 |
| Xinhua definition length | −0.159 | ≈ 0 | Longer definition → easier | 15 |
| In xinhua dictionary | −0.149 | ≈ 0 | Covered idioms easier | 15 |
| Is 4-character | +0.130 | ≈ 0 | Strict 4-char idioms harder | 15 |
| Character length of idiom | −0.127 | ≈ 0 | Longer idioms easier | 15 |
| Source: Chinese (vs Korean ref.) | −0.172 | ≈ 0 | Chinese idioms easier | 15 |
| In THUOCL corpus | −0.096 | ≈ 0 | Corpus-attested → easier | 15 |
| THUOCL frequency | −0.080 | < 0.001 | More frequent → easier | 6, 15 |
| Xinhua definition length | −0.088 | < 0.001 | (Part 6 estimate) | 6 |
| ZH–KO cognate membership | — | 0.44 (NS) | No effect | 6 |
| ZH–JA cognate membership | — | 0.61 (NS) | No effect | 6 |

OLS regression on exogenous features only: **R² = 0.161** (Part 15).

---

## 2. Semantic Stability (Cross-Strategy Agreement)

*Outcome: semantic stability = 1 − mean edit distance across strategies (Part 19).*
All Spearman.

| Predictor | ρ | p | Direction | Part |
|---|---|---|---|---|
| Composite difficulty | −0.526 | ≈ 0 | Harder idioms less stable | 19 |
| Xinhua definition length | +0.126 | ≈ 0 | Longer definition → more stable | 19 |
| In xinhua dictionary | +0.108 | ≈ 0 | Covered → more stable | 19 |
| Character length of idiom | +0.071 | < 0.001 | Longer idioms slightly more stable | 19 |
| In THUOCL corpus | +0.070 | < 0.001 | Corpus-attested → slightly more stable | 19 |
| THUOCL frequency | +0.049 | < 0.001 | More frequent → slightly more stable | 19 |

---

## 3. Within-Cell CV (Context Sensitivity)

*Outcome: coefficient of variation of translation length across 10 context sentences (Parts 3, 15).*

| Predictor | Method | Value | p | Direction | Part |
|---|---|---|---|---|---|
| Source sentence character length → CV (Creatively) | Spearman ρ | −0.173 | < 0.05 (all 90 source×target cells) | Longer sentence → lower CV | 15 |
| Source sentence character length → CV (Author) | Spearman ρ | −0.202 | < 0.05 (all 90 cells) | Longer sentence → lower CV | 15 |
| Source sentence character length → CV (Analogy) | Spearman ρ | −0.144 | < 0.05 (all 90 cells) | Longer sentence → lower CV | 15 |
| Source sentence word count → CV (Creatively) | Spearman ρ | −0.050 | < 0.05 | Weaker than char length | 15 |
| Source sentence word count → CV (Analogy) | Spearman ρ | −0.054 | < 0.05 | Weaker than char length | 15 |
| Source sentence word count → CV (Author) | Spearman ρ | −0.059 | < 0.05 | Weaker than char length | 15 |
| English CV vs Arabic CV distribution | KS statistic | 0.209 | 8.6 × 10⁻¹⁷⁴ | Arabic more variable | 14 |

---

## 4. Translation Length

*Outcome: translation character length (Parts 2, 3).*

| Predictor | Method | Value | p | Direction | Part |
|---|---|---|---|---|---|
| Source sentence length → translation length | Spearman ρ | 0.47–0.67 | — | Longer sentence → longer translation | 2 |
| Xinhua definition length → translation length | Spearman ρ | 0.06–0.13 | — | Richer definition → slightly longer | 2 |
| THUOCL frequency quintile → expansion ratio | Spearman ρ | −0.04 to +0.07 | — | Negligible effect | 2 |
| Source language effect on length (Creatively) | One-way ANOVA | F = 369 | 4.9 × 10⁻¹⁵⁹ | Chinese < Japanese ≈ Korean | 12 |
| Source language effect on length (Analogy) | One-way ANOVA | F = 480 | 1.1 × 10⁻²⁰⁵ | Chinese < Japanese ≈ Korean | 12 |
| Source language effect on length (Author) | One-way ANOVA | F = 461 | 1.0 × 10⁻¹⁹⁷ | Chinese < Japanese ≈ Korean | 12 |

---

## 5. Cross-Strategy Length Coupling

*All Pearson r.  Outcome: are two strategies' translation lengths correlated?*

### Global (across all languages)

| Pair | r (50k sample) | Part |
|---|---|---|
| Creatively ↔ Author | 0.675 | 17 |
| Creatively ↔ Analogy | 0.659 | 17 |
| Analogy ↔ Author | 0.580 | 17 |

### Per Target Language

| Target | Resource | r(C↔A) | r(C↔Au) | r(A↔Au) | Part |
|---|---|---|---|---|---|
| Swahili  | low  | 0.631 | 0.690 | 0.547 | 17 |
| Italian  | high | 0.624 | 0.638 | 0.523 | 17 |
| Spanish  | high | 0.621 | 0.623 | 0.523 | 17 |
| French   | high | 0.615 | 0.632 | 0.536 | 17 |
| English  | high | 0.596 | 0.668 | 0.566 | 17 |
| German   | high | 0.592 | 0.675 | 0.539 | 17 |
| Hindi    | low  | 0.576 | 0.700 | 0.516 | 17 |
| Bengali  | low  | 0.568 | 0.620 | 0.482 | 17 |
| Russian  | high | 0.564 | 0.599 | 0.468 | 17 |
| Arabic   | low  | 0.531 | 0.574 | 0.443 | 17 |

### Per Span Length (cross-strategy span correlations)

| Pair | r range (across target languages) | Part |
|---|---|---|
| Creatively span ↔ Analogy span | 0.22–0.29 | 3 |

---

## 6. Span Position

*Outcome: relative span position `rel_start` (Parts 3, 15).*

| Predictor | Method | Value | p | Direction | Part |
|---|---|---|---|---|---|
| Morphological complexity (low/med/high) → rel_start | Spearman ρ | −0.038 | ≈ 0 (sig., negligible effect) | Medium morphology → earlier position | 15 |

Typological groupings (median rel_start, see Part 15 tables for full breakdown):

| Word order | Analogy rel_start | Author rel_start | Creatively rel_start |
|---|---|---|---|
| SVO | 0.598 | 0.542 | 0.567 |
| VSO | 0.576 | 0.562 | 0.560 |
| SOV | 0.472 | 0.474 | 0.456 |

---

## 7. Cognate Span Similarity

*Outcome: span length or edit distance for cognate pairs.*

| Variable pair | Method | Value | p | Part |
|---|---|---|---|---|
| ZH span length ↔ KO span length (exact 4/4 pairs) | Spearman ρ | 0.48–0.55 | — | 5, 13 |
| ZH span length ↔ KO span length (near 3/4 pairs) | Spearman ρ | 0.38–0.53 | — | 5, 13 |
| ZH edit distance ↔ KO edit distance (all ZH–KO pairs) | Spearman ρ | 0.38–0.55 | — | 13 |
| Mean edit: three-way triples vs all ZH–KO pairs | — | 0.605 vs 0.605 | — | 13 |

---

## 8. Span Annotation Quality (Error Rate)

*Outcome: span containment error rate (Parts 1, 12, 18).*  Statistical tests.

| Predictor | Method | Key result | Part |
|---|---|---|---|
| Difficulty quartile → error rate (Analogy) | Kruskal–Wallis | H = 2.9, p = 0.41 (NS) | 18 |
| Difficulty quartile → error rate (Author) | Kruskal–Wallis | H = 3.5, p = 0.32 (NS) | 18 |
| Difficulty quartile → error rate (Creatively) | Kruskal–Wallis | H = 14.2, p = 0.003 (sig., negligible effect) | 18 |
| Zero-sentence vs normal rows (Creatively length) | Mann–Whitney U | p = 1.3 × 10⁻⁴⁰ | 14 |
| Zero-sentence vs normal rows (Analogy length) | Mann–Whitney U | p = 3.5 × 10⁻¹⁹ | 14 |
| Zero-sentence vs normal rows (Author length) | Mann–Whitney U | p = 4.3 × 10⁻²² | 14 |

---

## 9. Dictionary Coverage & Translation Behaviour

*Outcome: translation or span properties as a function of dictionary coverage (Part 2).*

| Variables | Method | Value | Direction | Part |
|---|---|---|---|---|
| Matched vs unmatched THUOCL idioms → translation length | t-test | p ≈ 0 | Rarer idioms produce longer translations (THUOCL matched: 102.6 vs unmatched: 113.7 chars, Creatively) | 2 |

---

## 10. Source Language Template Bias

*Outcome: template family distribution in English Analogy spans (Part 10).*

| Variables | Method | Value | p | Part |
|---|---|---|---|---|
| Source language → template family distribution | χ² | 321.5 (df = 14) | 3.8 × 10⁻⁶⁰ | 10 |

Directional biases: Japanese → cosmic/star (2×), Chinese → futility (1.9×), Korean → mist/castle (3×).

---

## 11. Cross-Target Vocabulary Overlap

*Outcome: vocabulary sharing across target languages for the same idiom (Part 4).*

| Variable pair | Method | Key result | Part |
|---|---|---|---|
| Same language family pairs vs cross-family | Jaccard comparison | Within-family (e.g. FR–ES–IT) higher Jaccard than cross-family | 4 |
| Span Jaccard C↔A ↔ dominant span fraction | Spearman ρ | 0.903 | 7 |
