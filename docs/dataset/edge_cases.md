# Zero-Length Source Sentences

Three idioms account for all 300 zero-length source sentences (100 rows each, covering all 10
target languages × 10 sentence slots):

| Idiom | Language | Root cause |
|---|---|---|
| 强奸民意 | Chinese | Content policy refusal |
| 推荐让能 | Chinese | Extremely obscure classical idiom |
| 공휴일궤 | Korean | Extremely rare classical idiom |

**强奸民意** (qiángjian mínyì, "to violate the public will") contains 强奸 (qiángjian = rape).
The sentence generation pipeline almost certainly refused to produce Chinese context sentences
containing this character sequence, leaving the sentence field empty for all 100 rows.

**推荐让能** (tuījiàn ràng néng, "recommend the worthy, yield to the capable") is an extremely
rare classical Chinese idiom. The model could not generate plausible context sentences for it.

**공휴일궤** is the Korean (Hangul) form of the Sino-Korean idiom 功虧一簣 (lit. "one basket of
earth short of completing the mound" → "to fail at the very last step"). Its Chinese counterpart
**功亏一篑** is present in the dataset and has normal sentence coverage; only the Korean rendering
was affected, suggesting the Korean sentence generator did not recognise this archaic form.

## Failure patterns in the translations

Because the sentence field is empty but translations were still generated, these 300 rows exhibit
four distinct model failure modes:

**1. Prompt leak (Creatively strategy only, 14–30% of rows per idiom)**

The `translate_creatively` field contains the raw translation prompt instead of a translation.
Examples:
- Swahili: *"Tafadhali tafsiri sentensi ifuatayo kutoka Kikorea kwenda Kiswahili kwa ubunifu:"*
  ("Please translate the following sentence from Korean to Swahili creatively:")
- Spanish: *"Por favor, traduce la siguiente oración del coreano al español de forma creativa"*
- Bengali: contains the request for the Chinese sentence to be provided

Prompt leaks occur **exclusively in the Creatively strategy** and are concentrated in Bengali and
Swahili (6–10/10 rows). English, French, German, Italian, and Russian show zero leaks, likely
because these languages' instruction-following prompts are structured differently by the pipeline.

**2. Literary hallucination (Author strategy, model defaults to famous openings)**

Without a source sentence, the Author strategy — prompted to write in the style of a famous
author in the target language — anchors on the most salient literary text in its training data:

| Target | Recurring hallucination | Source |
|---|---|---|
| Spanish | *"En un lugar de la Mancha, de cuyo nombre no quiero acordarme…"* (6–7× per idiom) | Don Quixote |
| Russian | *"Все счастливые семьи похожи друг на друга…"* (8× for 공휴일궤) | Anna Karenina |
| French | *"L'abîme appelle l'abîme"* / *"Hélas ! quel sombre abîme…"* | Victor Hugo |
| Italian | *"Quel ramo del lago di Como…"* | I Promessi Sposi |
| English | *"Stay thy course, and harken to my plea"* (Shakespearean pastiche) | — |

This is a classic **mode collapse to salient training data** when the conditioning signal (source
sentence) is absent. The two Chinese idioms share 9 identical Author-strategy translations,
confirming these are pure fallback outputs unrelated to the idiom.

**3. Poetic hallucination (Analogy strategy)**

The Analogy strategy generates elaborate unrelated metaphors in the target language (e.g. Arabic
*"أنتِ كالبحر في عمق أسراره"* — "You are like the sea in the depths of its secrets"). Outputs
are almost entirely unique (99/100 per idiom), confirming unconstrained generation.

**4. Meta-response spans**

A large fraction of span annotations for these rows contain the model's own explanation of the
mismatch rather than an actual span:
- 强奸民意: 72–88% meta-response spans depending on strategy (highest of the three)
- 推荐让能: 39–64% meta-response spans
- 공휴일궤: 7–16% meta-response spans

Example (span_creatively for 공휴일궤, English): *"The Korean idiom 공휴일궤 (功虧一簣) means
'to fail at the last step'… However, looking at your provided Arabic translation… there is no
span that corresponds to the idiom."*

强奸民意 produces the most meta-responses because the model also recognises — even when it does
generate a translation — that the content is inconsistent with the sensitive idiom, making it
refuse to extract a span in the majority of cases.

## Impact on downstream analyses

These 300 rows (0.033% of the dataset) have undefined expansion ratios (division by zero) and
completely uninformative translations. The difficulty composite correctly identifies
强奸民意 (difficulty 0.901) and 推荐让能 (difficulty 0.842) as the two hardest Chinese idioms —
their high scores are driven entirely by the pathological variance in these failed translations,
not by genuine idiom difficulty. These three idioms should be **excluded from any analysis
that relies on sentence content or translation fidelity**.

---

# Data Edge Cases

## Idioms with 20 Sentences per Target Language

The dataset is nominally structured as 10 context sentences per (idiom, target language). However,
4 Chinese idioms appear with **20 sentences** per target language (200 rows per
idiom instead of the standard 100):

| Idiom | Language | Sentences per target |
|---|---|---|
| 前仆后继 | Chinese | 20 |
| 固执己见 | Chinese | 20 |
| 生龙活虎 | Chinese | 20 |
| 触景生情 | Chinese | 20 |

These idioms contain mostly unique sentences — within-group sentence-level duplicates exist for
固执己见 (1 dup) and 触景生情 (3 dups) across some target languages.
All analysis scripts handle variable group sizes correctly by taking means across all available
sentences before aggregation.
