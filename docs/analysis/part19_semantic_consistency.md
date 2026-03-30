# Part 19: Semantic Consistency Audit

True semantic faithfulness requires human reference translations.  As a practical
substitute, we use **cross-strategy span agreement** as a proxy for semantic stability:
if all three strategies independently produce similar span phrasings for an idiom, the
concept is likely semantically unambiguous and the model's renderings are stable.
Wide cross-strategy divergence indicates semantic uncertainty or cultural opacity.

**Stability score** = 1 − mean(edit_CA, edit_CAu, edit_AAu), averaged across available
target languages per idiom.  Higher = more semantically stable.

---

## Distribution of Stability

| Metric | Value |
|---|---|
| Mean stability | 0.389 |
| Std deviation  | 0.044 |
| Minimum        | 0.183 |
| Maximum        | 0.661 |

The distribution is narrow (std = 0.044), indicating that most idioms cluster in a
moderate-stability band rather than splitting into two distinct easy/hard groups.

By source language:

| Source | Mean stability |
|---|---|
| Chinese  | 0.394 |
| Korean   | 0.387 |
| Japanese | 0.382 |

Chinese idioms are marginally more stable — consistent with their higher xinhua coverage
and lower difficulty scores in Part 6.  Japanese is least stable, again reflecting the
IT30 Japanese inventory's skew toward obscure yojijukugo.

---

## What Predicts Stability?

| Feature | Spearman ρ | Interpretation |
|---|---|---|
| difficulty     | **−0.526** | Harder idioms → less stable semantics |
| def_len        | +0.126 | Longer xinhua definitions → more stable |
| in_xinhua      | +0.108 | Dictionary-covered idioms are more stable |
| char_len       | +0.071 | Longer idioms are marginally more stable |
| in_thuocl      | +0.070 | Corpus-attested idioms are slightly more stable |
| thuocl_freq    | +0.049 | Higher frequency → marginally more stable |

**Difficulty is by far the strongest predictor** (ρ = −0.526, p ≈ 0).  This is
expected — idioms that produce variable translations (high difficulty) by definition
have strategies that diverge from each other.  The feature independence here is limited:
stability is partially definitional.  More useful are the exogenous predictors: having
a xinhua definition (ρ = +0.108) and a longer definition (ρ = +0.126) both independently
predict stability, confirming that well-documented idioms produce more consistent
renderings.

---

## Most Stable Idioms (Semantically Convergent)

| Source | Idiom | Stability | Notes |
|---|---|---|---|
| Korean   | 명경지수 | 0.661 | "Clear mirror, still water" — serene clarity; universal image |
| Chinese  | 以眼还眼，以牙还牙 | 0.636 | Biblical "eye for an eye"; cross-cultural recognition |
| Korean   | 반문농부 | 0.610 | Cognate of 班门弄斧; portable carpenter metaphor |
| Japanese | 三日天下 | 0.607 | "Three-day reign" — brief power; historically grounded |

The most stable idioms share a characteristic: they have **culturally portable,
visually concrete imagery** or **cross-cultural equivalents** (biblical phrases,
universal natural imagery).  The model converges on the same rendering across strategies
because there is little interpretive ambiguity.

---

## Most Unstable Idioms (Semantically Divergent)

| Source | Idiom | Stability | Notes |
|---|---|---|---|
| Chinese  | 威风凛凛 | 0.183 | "Impressive might" — abstract; many possible renderings |
| Japanese | 和魂洋才 | 0.216 | "Japanese spirit, Western learning" — culturally specific |
| Chinese  | 推荐让能 | 0.230 | Zero-sentence idiom (see Part 14) |
| Chinese  | 强奸民意 | 0.233 | Zero-sentence idiom (see Part 14); politically sensitive |
| Japanese | 竜蟠虎踞 | 0.239 | "Dragon coiling, tiger crouching" — abstract power metaphor |

Two of the top five most unstable idioms are the **zero-sentence anomalies** from
Part 14 (推荐让能, 强奸民意), confirming that those idioms' instability is partly
artefactual — translations without context sentences are less constrained and more
variable.  The remaining unstable idioms are genuinely semantically ambiguous: abstract
Sino-Japanese compounds whose meaning cannot be conveyed by a single canonical phrase.

---

## Stability by Target Language

| Target | Resource | Stability |
|---|---|---|
| Swahili  | low  | **0.469** |
| Hindi    | low  | 0.421 |
| German   | high | 0.386 |
| French   | high | 0.385 |
| Spanish  | high | 0.378 |
| Arabic   | low  | 0.377 |
| Bengali  | low  | 0.375 |
| Italian  | high | 0.373 |
| English  | high | 0.365 |
| Russian  | high | **0.356** |

**Swahili produces the highest cross-strategy consistency** (0.469), and **Russian the
lowest** (0.356).  This is surprising given Russian is a high-resource language.  One
explanation: Russian's rich morphology means the three strategies each produce a
differently inflected form of the same span phrase, which reduces edit-distance similarity
even when the semantic content is identical.  Swahili's high consistency may reflect
the model's narrower vocabulary for Swahili, forcing all three strategies toward the same
small set of renderings — effectively a high-template-rate language (Part 16 finds
Swahili has moderate template rates) where consistency comes from limited options rather
than semantic clarity.

![semantic_consistency_distribution](../figures/semantic_consistency_distribution.png)
![semantic_stability_features](../figures/semantic_stability_features.png)
