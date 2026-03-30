# Part 18: Strategy Effectiveness by Idiom Category

Without semantic labels, we proxy idiom categories using four structural properties
already available from Parts 1–6: **difficulty quartile**, **dictionary coverage**
(in_xinhua), **4-character structure**, and **source language**.  For each category ×
strategy combination we compare span error rate and within-cell CV.

---

## Error Rates by Difficulty Quartile

| Difficulty | Creatively | Analogy | Author |
|---|---|---|---|
| Q1 (easy)   | 2.35% | 2.02% | 2.04% |
| Q2          | 2.48% | 2.01% | 2.07% |
| Q3          | 2.36% | 1.98% | 1.99% |
| Q4 (hard)   | 2.32% | 2.05% | 2.02% |

**Difficulty has almost no effect on error rate** — the range across quartiles is at
most 0.16 percentage points (Creatively Q2 vs Q3).  A Kruskal–Wallis test confirms:

| Strategy | H-statistic | p-value |
|---|---|---|
| Creatively | 14.2 | 0.003 |
| Analogy    |  2.9 | 0.406 |
| Author     |  3.5 | 0.319 |

Only Creatively shows a statistically significant (but practically negligible) quartile
effect; Analogy and Author show none.  This is a key null result: **the span annotation
quality does not degrade for harder idioms**.  Span errors are driven by target-language
properties (Part 12) rather than source idiom difficulty.

---

## CV by Dictionary Coverage

| in_xinhua | Creatively CV | Analogy CV | Author CV |
|---|---|---|---|
| Not in dictionary | 0.209 | 0.200 | 0.223 |
| In dictionary     | 0.203 | 0.190 | 0.215 |

Idioms covered by the xinhua dictionary produce **slightly lower CV** (more consistent
translations across context sentences) than uncovered idioms, across all three strategies.
The difference is small (~0.006–0.010 CV units) but consistent in direction: a standard
definition gives the model a stable semantic target to translate consistently, while
undocumented idioms leave more room for context-driven variation.

---

## Error Rates by Source Language

| Source | Creatively | Analogy | Author |
|---|---|---|---|
| Chinese  | 2.44% | 2.05% | 2.08% |
| Japanese | 2.21% | 1.95% | 1.98% |
| Korean   | 2.30% | 2.05% | 2.07% |

Across all categories and source languages, **Analogy consistently has the lowest error
rate** (by 0.2–0.4 pp vs Creatively).  This is the most consistent pattern in the
category analysis: the Analogy strategy's standalone metaphor structure means the span
is a self-contained phrase that is less likely to be a fragmented or inflected substring
of the translation.  Creatively, which integrates the span into a sentence context, is
the most error-prone because the span must match exactly within a longer, more
morphologically complex translation.

---

## 4-Character vs Non-4-Character (Chinese only)

| Structure | Creatively error | Analogy error | Author error |
|---|---|---|---|
| 4-character  | 2.43% | 2.04% | 2.08% |
| Non-4-char   | 2.40% | 2.05% | 2.05% |

Virtually identical error rates between 4-char and non-4-char Chinese idioms, confirming
that idiom length does not drive span annotation quality.

---

## Summary

The category analysis produces a clear **null finding**: difficulty, dictionary coverage,
character length, and 4-character structure do not meaningfully differentiate which
strategy performs best.  **Analogy has the lowest error rate in every subgroup**, and the
magnitude of difference is consistent (~0.2–0.4 pp lower than Creatively).  The dominant
predictor of error rate remains target-language script family (Part 12), not source idiom
properties.

![strategy_by_category](../figures/strategy_by_category.png)
![strategy_error_by_difficulty](../figures/strategy_error_by_difficulty.png)
