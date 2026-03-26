# Figures

## 1. Fig1 Language Distribution

![fig1_language_distribution.png](../figures/fig1_language_distribution.png)

Distribution of rows across source (left) and target (right) languages. Target languages are perfectly balanced (~90,660 rows each), while Chinese contributes nearly half the source sentences.

## 2. Fig2 Idiom Coverage

![fig2_idiom_coverage.png](../figures/fig2_idiom_coverage.png)

Number of unique idioms per source language. Chinese has the largest inventory (4,306), followed by Japanese (2,440) and Korean (2,316).

## 3. Fig3 Translation Length Violin

![fig3_translation_length_violin.png](../figures/fig3_translation_length_violin.png)

Violin plot of translation lengths (characters) for each strategy on a 50k-row sample. Inner lines show quartiles. Analogy and Author strategies tend to produce longer translations than the Creatively strategy.

## 4. Fig4 Length By Target Language

![fig4_length_by_target_language.png](../figures/fig4_length_by_target_language.png)

Median character count of each translation strategy grouped by target language. Languages with complex scripts (e.g., Arabic, Bengali, Hindi) tend to have shorter character counts despite equivalent semantic content.

## 5. Fig5 Sentence Length By Source

![fig5_sentence_length_by_source.png](../figures/fig5_sentence_length_by_source.png)

Density histogram of source sentence lengths by language. All three languages show a similar unimodal distribution peaking around 25–30 characters, consistent with the dataset's design of short, idiom-carrying sentences.

## 6. Fig6 Span Length By Strategy

![fig6_span_length_by_strategy.png](../figures/fig6_span_length_by_strategy.png)

Box plots of the character length of the idiom span identified within each translation. The Analogy strategy produces noticeably longer spans, suggesting more elaborate idiomatic substitutions.

## 7. Fig7 Missing Spans

![fig7_missing_spans.png](../figures/fig7_missing_spans.png)

Count of missing span annotations per source language and strategy. Missingness is very low overall (<25 rows) and concentrated in Chinese rows.
