# Sign of the Times: Evaluating the use of Large Language Models for Idiomaticity Detection

| Field | Value |
|---|---|
| **Authors** | Dylan Phelps, Thomas Pickard, Maggie Mi, Edward Gow-Smith, Aline Villavicencio |
| **Venue** | MWE-UD Workshop at LREC-COLING 2024 |
| **Year** | 2024 |
| **URL** | https://aclanthology.org/2024.mwe-1.22/ |
| **arXiv** | https://arxiv.org/abs/2405.09279 |
| **Topic** | Evaluation metrics; Multilingual idiom benchmarking |

## Abstract / Key Contribution

Systematically evaluated a range of LLMs on idiomaticity detection across three benchmarks:
SemEval 2022 Task 2a, FLUTE, and MAGPIE. Found that even GPT-4-scale models don't match
fine-tuned task-specific encoders, though performance improves with model scale. Investigated
zero-shot and few-shot prompting for idiomaticity detection.

## Methods

- Zero-shot and few-shot prompting of GPT-3.5, GPT-4, Llama-2, Flan-T5, and others
- Evaluation on three idiomaticity benchmarks
- Ablation over number of in-context examples
- Error analysis: which idiom types/lengths cause most failures

## Relevance to IdiomTranslate30

- Establishes which LLMs are reliable idiomaticity detectors — relevant if using LLM-as-judge
  evaluation on IdiomTranslate30 translations
- Prompting strategies tested here can guide how to set up automated evaluation pipelines
  for the dataset's three translation strategies
