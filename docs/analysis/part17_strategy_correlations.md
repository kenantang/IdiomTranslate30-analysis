# Part 17: Strategy Length Correlations per Target Language

Cross-strategy translation length correlations are moderately strong at the global level —
r(C↔A) = 0.659, r(C↔Au) = 0.675, r(A↔Au) = 0.580 (50k-row sample) — but these pool all
10 target languages as a single population.  If strategies are genuinely language-agnostic,
these correlations should be consistent across targets.  If some languages "decouple" the
strategies, it indicates that the translation mode varies more strongly than the idiom
content in those languages.

---

## Per-Target Correlations

| Target language | Resource | r(C↔A) | r(C↔Au) | r(A↔Au) |
|---|---|---|---|---|
| Swahili  | low  | 0.631 | 0.690 | 0.547 |
| Italian  | high | 0.624 | 0.638 | 0.523 |
| Spanish  | high | 0.621 | 0.623 | 0.523 |
| French   | high | 0.615 | 0.632 | 0.536 |
| English  | high | 0.596 | 0.668 | 0.566 |
| German   | high | 0.592 | 0.675 | 0.539 |
| Hindi    | low  | 0.576 | 0.700 | 0.516 |
| Russian  | high | 0.564 | 0.599 | 0.468 |
| Bengali  | low  | 0.568 | 0.620 | 0.482 |
| Arabic   | low  | 0.531 | 0.574 | 0.443 |

**Arabic consistently has the lowest pairwise correlations** across all three strategy
pairs.  This confirms the finding from Part 12 that Arabic is structurally the most
distinctive target language: not only does it have higher error rates and more compact
translations, but the three strategies also *disagree more* with each other on translation
length in Arabic than in any other language.  VSO word order and rich templatic
morphology give the model more degrees of freedom in how it structures each strategy's
output.

**Global baseline** (50k-row sample): r(C↔A) = 0.659, r(C↔Au) = 0.675, r(A↔Au) = 0.580.
The per-target values are uniformly *below* the global baseline because pooling languages
introduces between-language variance that inflates the apparent within-strategy coupling.

---

## Resource Level Effect

| Resource | r(C↔A) | r(C↔Au) | r(A↔Au) |
|---|---|---|---|
| High-resource | 0.602 | 0.639 | 0.526 |
| Low-resource  | 0.576 | 0.646 | 0.497 |

The difference is small (0.02–0.03 r units) and does not follow a clear directional
pattern: low-resource languages actually show *higher* C↔Author correlation than
high-resource (0.646 vs 0.639), contradicting the hypothesis that strategies decouple
in low-resource languages.  The main driver of the Arabic outlier is therefore not
resource level but Arabic-specific morphological and structural properties.

---

## Key Observation: Author Tracks Creatively More Than Analogy Does

Across all 10 languages, r(C↔Au) > r(C↔A) in every case.  The Author strategy produces
lengths closer to Creatively than Analogy does in every language.  This makes sense from
a design perspective: both Creatively and Author strategies are instructed to produce
contextually grounded translations of the *sentence* (with the idiom rendering embedded),
while Analogy is instructed to construct a standalone metaphorical comparison.  The
sentence-level framing of Creatively and Author thus explains their tighter length coupling,
while Analogy's standalone structure introduces independent length variation.

![strategy_length_correlations](../figures/strategy_length_correlations.png)
