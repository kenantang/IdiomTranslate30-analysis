# Part 1: Data Quality

Before examining translation content, we characterise annotation quality. Each row contains
model-generated span annotations marking where the idiom rendering appears in the translation.
These are the primary quality concern since they are not human-verified.

## Span Annotation Audit

| Check | Creatively | Analogy | Author |
|---|---|---|---|
| Missing span | 19 (0.002%) | 19 (0.002%) | 24 (0.003%) |
| Span not contained in translation | 21,549 (2.38%) | 18,258 (2.01%) | 18,421 (2.03%) |
| Span longer than translation | 329 | 420 | 271 |
| Span equals raw idiom | 155 | 188 | 124 |
| Degenerate translation (= source) | 0 | 0 | 1 |

**5.80% of rows (52,608) carry at least one flag**, almost entirely driven by span-not-in-translation
cases (~2% per strategy). A filtered version can be produced from `data/audit/anomalies.csv`.
The 2% rate motivates a closer look at what these cases actually represent.

![flag_rates](../figures/flag_rates.png)

## Span Error Classification

Breakdown of the ~58k flagged rows:

| Category | Creatively | Analogy | Author |
|---|---|---|---|
| Partial word overlap | 16,495 | 14,618 | 14,138 |
| Off-by-one boundary | 1,731 | 1,320 | 1,477 |
| No overlap | 1,613 | 1,009 | 1,363 |
| Case mismatch | 1,267 | 981 | 1,064 |
| Punctuation difference | 435 | 326 | 363 |
| Leading/trailing whitespace | 8 | 4 | 16 |

**~77% are partial word overlap** — the span shares at least one word with the translation but
is not a contiguous substring, most likely because the model paraphrased the idiom across
non-adjacent words. These are annotation artefacts safe to retain for most analyses. The ~7%
"no overlap" cases (≈3,985 flagged pairs across three strategies) are the only ones that warrant
filtering for span-dependent tasks. All analyses below treat flagged rows as-is unless otherwise noted.

![span_error_types](../figures/span_error_types.png)
