# Part 15: Context Complexity, Difficulty Prediction & Typological Span Analysis

Three analyses that link *input properties* (source sentence complexity, idiom
features, target-language typology) to *translation behaviour* (output consistency,
difficulty scores, span position).

---

## 15.1 Sentence Complexity → Output Consistency

Part 3 shows that within-cell CV varies across idiom–target pairs, but does not ask
*why*.  One candidate: longer or more complex source sentences may supply richer
context that either constrains the model (lower CV, more consistent) or opens up more
paraphrase options (higher CV, more variable).

We merge mean source sentence length (characters and word count per idiom) with per-cell
CV from `context_sensitivity.parquet` and compute Spearman ρ for each
(source × target × strategy) combination (90 cells total).

| Strategy | Mean ρ (sentence length → CV) | Mean ρ (word count → CV) |
|---|---|---|
| Creatively | **−0.173** | −0.050 |
| Analogy    | **−0.144** | −0.054 |
| Author     | **−0.202** | −0.059 |

**All 90 (source × target × strategy) cells show a statistically significant negative
correlation** between source sentence length and within-cell CV (p < 0.05 in all 90 cells).

The direction is consistent and interpretable: **longer source sentences produce *more*
consistent translations** (lower CV).  This supports the "context constrains" hypothesis:
when the model is given more textual information about how the idiom is used, it locks
onto a narrower range of translation options.  Word count is a weaker predictor than
character count, suggesting that sentence density (more characters per word, as in longer
compounds) matters more than raw word number.

The Author strategy shows the strongest effect (ρ = −0.202), consistent with its
register-sensitive mandate — longer, richer sentences provide stronger stylistic cues
that the model exploits to produce a more targeted formal register.

The heatmap below shows mean ρ by source language × strategy (left panel) and by target
language (right panel).  Chinese idioms show slightly stronger length→CV correlation
than Japanese or Korean, possibly because Chinese source sentences are shorter on average,
making the sentence-length gradient within the Chinese set more informative.

![sentence_complexity_cv](../figures/sentence_complexity_cv.png)

---

## 15.2 Difficulty Prediction Model

Part 6 computes a composite difficulty score per idiom but reports only pair-wise
Spearman correlations with individual features.  Here we rank all available features
simultaneously and fit an OLS regression to quantify their combined explanatory power.

### Feature correlations with difficulty

| Feature | Spearman ρ | Direction |
|---|---|---|
| `src_ja` (Japanese source) | **+0.386** | Japanese idioms are harder |
| `src_zh` (Chinese source)  | −0.172 | Chinese idioms are easier |
| `def_len` (xinhua definition length) | −0.159 | Better-documented idioms are easier |
| `in_xinhua` (in xinhua dict) | −0.149 | Dictionary-covered idioms are easier |
| `is_4char` (exactly 4 chars) | +0.130 | Strictly 4-char idioms are harder |
| `char_len` (character count) | −0.127 | Longer idioms are easier |
| `in_thuocl` (in THUOCL corpus) | −0.096 | Corpus-attested idioms are easier |
| `thuocl_freq` (corpus frequency) | −0.080 | More frequent idioms are easier |

**OLS R² = 0.161** — these exogenous features account for 16.1% of difficulty variance.
The remainder is captured by the behavioural features already embedded in the difficulty
score itself (divergence, expansion ratio, CV, Jaccard).

### Interpretation

The dominant predictor is **source language identity**: Japanese idioms are substantially
harder than Korean (reference), which are substantially harder than Chinese.  This is not
a demographic artefact — it aligns with Part 2's finding that 82% of Japanese idioms in
IT30 are absent from Wiktionary (vs 4.4% for Chinese), confirming that the Japanese
inventory skews toward obscure, classical yojijukugo that the model treats as semantically
opaque.

Among content features, **dictionary coverage beats frequency** (ρ of in_xinhua=−0.149
vs thuocl_freq=−0.080), suggesting that having a standard definition matters more than
how often an idiom is used in modern text.  The positive coefficient for `is_4char`
might appear counterintuitive, but it reflects that the rare non-4-char Chinese idioms
(8.6% of the Chinese inventory) tend to be multi-clause proverbs with more explicit
literal content, which are actually easier to translate.

![difficulty_regression](../figures/difficulty_regression.png)

---

## 15.3 Span Position × Linguistic Typology

Part 3 observes that Bengali places idiom spans earlier (median rel_start ≈ 0.478) than
Italian (0.609), but the difference is not explained.  Annotating each target language
with its **word order** (SVO/SOV/VSO) and **morphological complexity** (low/medium/high)
allows a typological explanation.

### Median relative span position by typology

| Word order | Creatively | Analogy | Author |
|---|---|---|---|
| SVO | 0.567 | 0.598 | 0.542 |
| VSO | 0.560 | 0.576 | 0.562 |
| SOV | 0.456 | 0.472 | 0.474 |

| Morphology | Creatively | Analogy | Author |
|---|---|---|---|
| Low    | 0.569 | 0.607 | 0.546 |
| Medium | 0.486 | 0.508 | 0.493 |
| High   | 0.566 | 0.579 | 0.546 |

| Script | Creatively | Analogy | Author |
|---|---|---|---|
| Latin    | 0.570 | 0.605 | 0.545 |
| Cyrillic | 0.552 | 0.560 | 0.525 |
| Arabic   | 0.560 | 0.576 | 0.562 |
| Indic    | 0.456 | 0.472 | 0.474 |

**SOV languages (Bengali and Hindi) place the idiom span earlier** — roughly 0.09–0.12
relative units earlier than SVO languages — across all three strategies.  This is
consistent with the head-final structure of SOV languages: the predicate (which often
carries the idiomatic content) appears before the verb and objects, pulling the
rendering toward the middle of the sentence rather than the final position favoured in
SVO languages.

**Morphological complexity** shows a non-monotonic pattern: medium-complexity languages
(Bengali, Hindi) produce the lowest rel_start values, while both low-complexity (EN, FR,
ES, IT) and high-complexity (RU, AR, SW) languages produce similar, higher values.  The
morphological pattern is thus driven by the coincidence of medium morphology and SOV
order in the Indic languages rather than morphological complexity itself.

The Spearman correlation between morphological complexity (coded 0/1/2) and rel_start
is **ρ = −0.038, p ≈ 0** — statistically significant given the large sample but
practically negligible in magnitude, confirming that word order (SOV vs SVO/VSO) is the
more useful typological predictor.

![typology_span_heatmap](../figures/typology_span_heatmap.png)
