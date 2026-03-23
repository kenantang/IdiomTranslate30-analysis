# Methods Provenance

Tracks the origin of each analysis method used or planned for IdiomTranslate30.
For each method: the source paper, a full citation, and verbatim phrases that introduce or define it.

---

## 1. Translation Length & Expansion Ratio

**Used in:** Analysis Plan — Module 1

**Source:** Tang et al. (2024)

> Tang, Kenan, Peiyang Song, Yao Qin, and Xifeng Yan. "Creative and Context-Aware Translation of East Asian Idioms with GPT-4." *arXiv:2410.00988 [cs.CL]*, October 1, 2024. EMNLP 2024 Findings.

**Verbatim:**
> "we first generate multiple sentences containing a given idiom with GPT-4. For each of the 4 languages, we randomly sample 50 idioms and generate 10 sentences for each idiom"

> "Overall, we generate 27 translations per sentence with all prompting strategies, totalling 13,500 translations per language."

**Note:** Tang et al. measure per-idiom translation volume rather than per-sentence length ratios, but the sentence-level expansion ratio is a natural extension of the same framework — comparing how much text each strategy produces for the same source input.

---

## 2. Unique Unigrams in Spans as Diversity Proxy

**Used in:** Analysis Plan — Module 7 (Lexical Diversity)

**Source:** Tang et al. (2024)

> Tang, Kenan, Peiyang Song, Yao Qin, and Xifeng Yan. "Creative and Context-Aware Translation of East Asian Idioms with GPT-4." *arXiv:2410.00988 [cs.CL]*, October 1, 2024.

**Verbatim:**
> "We use the number of unique unigrams in the spans as a proxy for the number of different translations for each idiom."

> "the number of unique unigrams do not saturate" [as the number of translations scales up]

---

## 3. Span Extraction & Substring Containment Check

**Used in:** Analysis Plan — Module 2, Module 6

**Source:** Tang et al. (2024)

> Tang, Kenan, Peiyang Song, Yao Qin, and Xifeng Yan. "Creative and Context-Aware Translation of East Asian Idioms with GPT-4." *arXiv:2410.00988 [cs.CL]*, October 1, 2024.

**Verbatim:**
> "We extract the span in each translation that corresponds to the idiom."

> "GPT-4 was able to locate precisely the span in the translated sentence that corresponds to the idiom in the original sentence. The identified span is a substring of the translated sentence for 1994 out of 2000 Chinese-English sentence pairs."

**Note:** The substring containment check (span ⊆ translation) is the direct validity criterion stated here. Rows where this fails are annotation errors.

---

## 4. LitTER — Literal Translation Error Rate

**Used in:** Analysis Plan — Module 6 (Data Audit, literalness proxy)

**Source:** Baziotis, Mathur, and Hasler (2023)

> Baziotis, Christos, Prashant Mathur, and Eva Hasler. "Automatic Evaluation and Analysis of Idioms in Neural Machine Translation." In *Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2023)*, pages 3006–3024. *arXiv:2210.04545*, 2022.

**Verbatim:**
> "We propose literal translation error rate (LitTER), a novel metric of the frequency of literal translation errors made by a model. A literal translation error occurs if any of the words of a span in the source sentence has been wrongly translated literally in the target language."

> "Our method, is based on two key ideas. First, we use bilingual word dictionaries, which are relatively easy to obtain, to translate the words of an annotated source span into the target language, and produce blocklists with candidate literal translation errors. Then, we use the reference translations to filter the blocklists by removing those words that occur in the reference."

> "The final score is the percentage of translations that trigger the blocklist."

**Note:** The full LitTER algorithm requires bilingual dictionaries and reference translations (neither of which we have). However, the *span containment* step — checking whether source idiom characters appear verbatim inside the target span — is a reference-free adaptation of the same literalness detection logic.

---

## 5. Macro-Averaging Over Idioms

**Used in:** Analysis Plan — all modules reporting aggregate statistics

**Source:** Baziotis, Mathur, and Hasler (2023)

> Baziotis, Christos, Prashant Mathur, and Eva Hasler. "Automatic Evaluation and Analysis of Idioms in Neural Machine Translation." *arXiv:2210.04545*, 2022.

**Verbatim:**
> "Different idioms have significantly different frequencies...However, prior work has overlooked this fact...Thus, over-represented idioms can skew the reported results and favour models that have overfitted on them. To address this, we report all of our targeted evaluation results (i.e., LitTER, APT-Eval) by macro-averaging over idioms."

**Application:** All per-strategy aggregate statistics (mean length, span ratios, divergence) should be macro-averaged over unique idioms, not micro-averaged over rows, to avoid bias from the unequal source language distribution (Chinese: 4,306 idioms vs. Korean: 2,316).

---

## 6. Span Annotation with BIO Labels

**Used in:** Analysis Plan — Module 2 (span structure)

**Source:** Zhou, Gong, and Bhat (2021)

> Zhou, Jianing, Hongyu Gong, and Suma Bhat. "PIE: A Parallel Idiomatic Expression Corpus for Idiomatic Sentence Generation and Paraphrasing." In *Proceedings of the 17th Workshop on Multiword Expressions (MWE 2021)*, pages 33–48.

**Verbatim:**
> "To specify the span of the IE in each idiomatic sentence and that of the literal paraphrase in the corresponding literal sentence, BIO labels were used; B marks the beginning of the idiom expressions (resp. the literal paraphrases), I the other words in the IE (resp. words in the literal paraphrases) and O all the other words in the sentences."

**Note:** IdiomTranslate30 stores spans as character substrings rather than BIO sequences, but the conceptual parallel is direct — the `span_*` columns are the equivalent of BIO-labelled idiom regions in the target sentence.

---

## 7. N-gram Divergence Between Parallel Sentences

**Used in:** Analysis Plan — Module 3 (strategy divergence)

**Source:** Zhou, Gong, and Bhat (2021)

> Zhou, Jianing, Hongyu Gong, and Suma Bhat. "PIE: A Parallel Idiomatic Expression Corpus for Idiomatic Sentence Generation and Paraphrasing." In *Proceedings of the 17th Workshop on Multiword Expressions (MWE 2021)*, pages 33–48.

**Verbatim:**
> "We also report the percentage of n-grams in the literal sentences which do not appear in the idiomatic sentences as a measure of the difference between the idiomatic and literal sentences."

N-gram divergence values reported (Table 3, PIE corpus):
> uni-grams: 13.86%, bi-grams: 23.60%, tri-grams: 30.19%, 4-grams: 36.51%

**Application:** Compute the percentage of n-grams in `translate_analogy` and `translate_author` that do not appear in `translate_creatively` (treating Creatively as the baseline) — a reference-free divergence measure between strategies.

---

## 8. Sentence Length Comparison Across Parallel Variants

**Used in:** Analysis Plan — Module 1, Module 5

**Source:** Zhou, Gong, and Bhat (2021)

> Zhou, Jianing, Hongyu Gong, and Suma Bhat. "PIE: A Parallel Idiomatic Expression Corpus for Idiomatic Sentence Generation and Paraphrasing." In *Proceedings of the 17th Workshop on Multiword Expressions (MWE 2021)*, pages 33–48.

**Verbatim:**
> "We notice that the parallel sentences in our dataset are comparable in terms of sentence length, while simple sentences are much shorter in the text simplification dataset. This suggests that the tasks we propose may not result in significantly shorter sentences compared to their inputs."

Corpus statistics (Table 2):
> "Idiomatic sentences: 5,170 (avg. sentence length 19.0 words); Literal sentences: 5,170 (avg. sentence length 18.5 words)."

**Application:** Compare average translation lengths across the three strategies for the same (idiom, target language) pair — analogous to Zhou et al.'s idiomatic vs. literal sentence length comparison.

---

## 9. Idiom Frequency Bucketing

**Used in:** Analysis Plan — Module 5

**Source:** Liu, Chaudhary, and Neubig (2023)

> Liu, Emmy, Aditi Chaudhary, and Graham Neubig. "Crossing the Threshold: Idiomatic Machine Translation through Retrieval Augmentation and Loss Weighting." In *Proceedings of EMNLP 2023*, pages 15027–15044. *arXiv:2310.07081*.

**Verbatim:**
> "We examine the frequency of each idiom within OpenSubtitles as a proxy for its overall frequency in the training data, and bucket idioms into quintiles based on their occurrence frequency in source text."

> "As idioms become more frequent, the quality of translations increases."

> "This indicates that like in the synthetic experiments, there may be strong frequency effects on translation quality of idioms."

**Application:** Each idiom in IdiomTranslate30 appears exactly 200 times (fixed by design). However, within the 20 context sentences per idiom per language pair, we can study whether sentence-level context length or lexical context diversity (number of unique surrounding words) correlates with span length or strategy divergence.

---

## 10. Heuristic Literal-vs-Idiomatic Labelling via Keyword Matching

**Used in:** Analysis Plan — Module 6

**Source:** Dankers, Lucas, and Titov (2022)

> Dankers, Verna, Christopher G. Lucas, and Ivan Titov. "Can Transformer be Too Compositional? Analysing Idiom Processing in Neural Machine Translation." In *Proceedings of ACL 2022*, pages 3608–3626.

**Verbatim:**
> "The translations are labelled heuristically. In the presence of a literal translation of at least one of the idiom's keywords, the entire translation is labelled as a word-for-word translation, where the literal translations of keywords are extracted from the model and Google translate. When a literally translated keyword is not present, it is considered a paraphrase."

Distribution data (Table 1):
> "The vast majority of literal PIEs indeed result in word-for-word translations. The subset of figurative samples results in more paraphrases, but 76% is still a word-for-word translation, dependent on the language."

**Application:** A simplified version — check whether any character n-gram from the source idiom (romanised or transliterated) appears verbatim in the target span — serves as a reference-free literalness flag within each translation strategy.

---

## 11. Multi-Dimensional Figurative Translation Evaluation Framework

**Used in:** Analysis Plan — background framing for Module 1

**Source:** Wang, Zhang, Wu, Loakman, Huang, and Lin (2024)

> Wang, Shun, Ge Zhang, Han Wu, Tyler Loakman, Wenhao Huang, and Chenghua Lin. "MMTE: Corpus and Metrics for Evaluating Machine Translation Quality of Metaphorical Language." In *Proceedings of EMNLP 2024*, pages 11343–11358.

**Verbatim:**
> "Our evaluation protocol is designed to estimate four aspects of MT: Metaphorical Equivalence, Emotion, Authenticity, and Quality. In doing so, we observe that translations of figurative expressions display different traits from literal ones."

> "Approximately 20% of metaphorical expressions are found to be translated without proper correspondence to the intended metaphorical meaning (non-equi)."

> "BERTScore struggles to distinguish the performance between metaphorical and literal translations. This limitation may be due to the methods relying on contextual embeddings and cosine similarity struggles to capture the subtle semantic differences inherent in metaphorical language."

**Application:** This framework motivates analysing IdiomTranslate30 along structurally analogous axes using only the data itself: Equivalence → span containment; Authenticity → length ratio and lexical diversity; without LLM judges or reference translations.

---

## 12. Inter-Strategy Agreement via Statistical Testing

**Used in:** Analysis Plan — Module 1, Module 3

**Source:** Liu, Chaudhary, and Neubig (2023)

> Liu, Emmy, Aditi Chaudhary, and Graham Neubig. "Crossing the Threshold: Idiomatic Machine Translation through Retrieval Augmentation and Loss Weighting." In *Proceedings of EMNLP 2023*, pages 15027–15044.

**Verbatim:**
> "We evaluate the statistical significance of the results through a one-tailed permutation test."

> "Agreement (Krippendorff's α) in both cases was moderately high (French α=0.5754, Finnish α=0.6454)."

**Application:** Use non-parametric tests (Wilcoxon signed-rank) to test whether differences in translation length and span length between strategies are statistically significant — consistent with Liu et al.'s use of permutation tests over language-pair comparisons.
