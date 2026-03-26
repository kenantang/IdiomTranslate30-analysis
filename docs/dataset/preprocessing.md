# Pre-processing

## Extremely Long Translations

A small number of translations are pathologically long, caused by model generation failures.
The threshold for exclusion is **500 characters**, which lies far above the p99.99
of each strategy (Creatively: 263 chars, Analogy: 302 chars, Author: 348 chars).

**Rows removed:** 1 Creatively, 1 Analogy, 3 Author
(total 5 (row, strategy) pairs out of 906,600 rows; < 0.001%)

| Strategy | Idiom | Source | Target | Length |
|---|---|---|---|---|
| Creatively | 이율배반 | Korean | Arabic | 9,472 |
| Analogy | 風前之灯 | Japanese | Swahili | 11,821 |
| Author | 向隅而泣 | Chinese | Bengali | 572 |
| Author | 癞蛤蟆想吃天鹅肉 | Chinese | Hindi | 3,034 |
| Author | 不求甚解 | Chinese | Swahili | 1,109 |

**Failure patterns identified:**

1. **Token repetition loop** — the model begins a normal sentence and then degenerates into
   repeating a single token thousands of times before (sometimes) recovering at the very end.
   - *이율배반* (KO→Arabic, Creatively, 9,472 chars): the Korean word 불신 (distrust) repeated
     ~2,613 times mid-sentence after a normal Arabic opening.
   - *風前之灯* (JA→Swahili, Analogy, 11,821 chars): the letter "k" repeated ~5,852 times
     immediately after the first clause; the sentence resumes at the very end.

2. **Meta-response leak** — the model includes its own instruction-following framing in the output
   instead of just the translation.
   - *不求甚解* (ZH→Swahili, Author, 1,109 chars): output begins with a biography of the Swahili
     author Shaaban Robert, followed by "Hapa kuna tafsiri ya sentensi yako…" ("Here is a
     translation of your sentence…") and ends with "Je, ungependa nijaribu kutafsiri sentensi
     nyingine yoyote?" ("Would you like me to try translating any other sentence?").

3. **Runaway generation** — the model's output is semantically coherent but never converges,
   piling on additional content.
   - *向隅而泣* (ZH→Bengali, Author, 572 chars): the protagonist's name changes five times
     within a single sentence (হিমু → লিটন → শামীম → শফিক → টোকন → খোকন), suggesting the
     model could not commit and kept revising in-place.
   - *癞蛤蟆想吃天鹅肉* (ZH→Hindi, Author, 3,034 chars): the translation chains together an
     ever-growing list of Hindi proverbs (अंधा क्या चाहे, लात के देवता, धोबी का कुत्ता…)
     without settling on a single rendering.

These 5 (row, strategy) pairs represent < 0.001% of the data; their removal does not
materially affect any reported statistic. They are excluded from any translation-length
visualisations that cap the axis range.
