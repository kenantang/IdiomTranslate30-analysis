# Part 4: Cross-Lingual Patterns

Having characterised how the model translates a given idiom into a given language, we now ask
how much the *choice* of target language matters — and whether language family membership
explains shared vocabulary across translations of the same idiom.

## Cross-Lingual Consistency

The coefficient of variation (CV) of translation length *across* the 10 target languages per
idiom, computed on per-language means (aggregated over the 10 context sentences first):

| Strategy | Mean CV |
|---|---|
| Creatively | 0.108 |
| Analogy | 0.115 |
| Author | 0.165 |

Author shows substantially higher cross-lingual inconsistency (CV 0.165) than the other
two strategies, suggesting its stylistic framing is more sensitive to which target language
is used. This is driven largely by a resource gap: high-resource target languages (English,
French, German, Spanish, Italian, Russian) produce significantly longer translations than
low-resource ones (Arabic, Bengali, Hindi, Swahili), with the gap largest for Author
(~30 chars mean difference, Mann-Whitney p ≈ 0).

> **Note (bug fix):** an earlier version computed CV over raw rows, conflating within-language
> sentence variance with between-language variance, inflating CV by 63–110%. The values
> above are corrected.

![cv_by_resource_level](../figures/cv_by_resource_level.png)
![span_heatmap](../figures/span_heatmap.png)

## Cross-Target Language Word Overlap

The cross-lingual consistency analysis shows that translation *length* varies across target languages. We now ask whether *vocabulary* is shared across languages for the same idiom — specifically whether language family predicts shared words.

For each (idiom, strategy), the vocabulary across all 10 sentences is aggregated per target
language (word-set union), then pairwise Jaccard is computed across all 45 language pairs.
Pairs are classified as within-family or between-family.

| Strategy | Within-family Jaccard | Between-family Jaccard |
|---|---|---|
| Creatively | 0.021 | 0.002 |
| Analogy | 0.019 | 0.001 |
| Author | 0.017 | 0.001 |

Within-family overlap is **14–19× higher** than between-family overlap. Between-family Jaccard
has a median of exactly 0.000, confirming near-complete absence of shared vocabulary across
unrelated language families in idiom translations. The Romance triad dominates within-family
overlap: Spanish–Italian (0.041) > French–Spanish (0.033) > French–Italian (0.022). Germanic
pairs score lower (English–German 0.010), reflecting English's greater lexical divergence from
German. Critically, the source language (Chinese, Japanese, Korean) has no detectable effect
on the pattern — cross-target overlap is entirely a property of the target languages.

![cross_target_overlap](../figures/cross_target_overlap.png)
