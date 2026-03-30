# Part 13: Extended Cognate Analysis

Part 5 establishes pairwise cognate links between ZH–KO (543 pairs), ZH–JA (468 pairs),
and JA–KO (802 pairs) separately.  Two questions were left unanswered: do any idioms form
a **three-way cognate triple** across all three source languages simultaneously, and which
**specific cognate pairs** produce the most (or least) similar translations across target
languages?

---

## 13.1 Three-Way Cognate Detection

A three-way triple is defined as a tuple (zh_idiom, ja_idiom, ko_idiom) where:

1. (zh, ja) appears in the ZH–JA pairwise table, and
2. (zh, ko) appears in the ZH–KO pairwise table, and
3. (ja, ko) also appears in the JA–KO pairwise table.

This is more restrictive than simply finding a ZH idiom with both a JA and a KO cognate —
the Japanese and Korean counterparts must also be linked to *each other*.

| Metric | Count |
|---|---|
| ZH–KO pairs  | 543 (293 exact_4/4) |
| ZH–JA pairs  | 468 (266 exact_4/4) |
| JA–KO pairs  | 802 (548 exact_4/4) |
| Three-way triples | **231** |
| All-exact triples (exact_4/4 across all three links) | **95** |

**231 idioms form verified three-way cognate triples** — far more than might be expected
given the pairwise set sizes.  95 of these are all-exact: the same four CJK characters
appear verbatim in all three writing systems (accounting for simplified/traditional
divergence in ZH–JA).

Sample triples spanning multiple match types:

| ZH | JA | KO | ZH–JA | ZH–KO |
|---|---|---|---|---|
| 一刻千金 | 一刻千金 | 일각천금 | exact_4/4 | exact_4/4 |
| 一字千金 | 一字千金 | 일자천금 | exact_4/4 | exact_4/4 |
| 一张一弛 | 一張一弛 | 일장일이 | exact_4/4 | exact_4/4 |
| 一丘之貉 | 一丘之貉 | 일구지학 | exact_4/4 | near_3/4  |
| 一刀两断 | 一刀両断 | 일도양단 | near_3/4  | near_3/4  |

These triples represent the most densely shared layer of the East Asian classical idiom
tradition — compounds that migrated from classical Chinese into both Japanese and Korean
and were preserved with minimal phonological or orthographic drift.

**Divergence comparison:**
The mean inter-strategy edit distance for triple idioms is **0.605**, identical to the
overall ZH–KO pairwise mean (also 0.605).  Being a three-way cognate does not make a
concept *easier to translate consistently* — it simply means the surface forms are shared,
not that the underlying semantics are more transparent or that the model treats them
differently.

![triple_cognate_overlap](../figures/triple_cognate_overlap.png)

---

## 13.2 Low-Divergence Cognate Pair Ranking

For each of the 537 ZH–KO cognate pairs with divergence data, we average the mean
inter-strategy edit distance across ZH and KO source translations to obtain a
`edit_pair_mean` score.  Lower scores indicate that both the Chinese and Korean versions
of the idiom produce *consistent* translations (low within-strategy variation) across all
10 target languages.

**10 most convergent pairs** (edit_pair_mean closest to 0):

| ZH | KO | Match type | ZH edit | KO edit | Pair mean |
|---|---|---|---|---|---|
| 班门弄斧 | 반문농부 | exact_4/4 | 0.536 | 0.390 | 0.463 |
| 缘木求鱼 | 연목구어 | exact_4/4 | 0.511 | 0.439 | 0.475 |
| 金科玉律 | 금과옥조 | near_3/4  | 0.482 | 0.501 | 0.491 |
| 南柯一梦 | 남가일몽 | exact_4/4 | 0.544 | 0.457 | 0.501 |
| 大逆不道 | 대역무도 | near_3/4  | 0.605 | 0.417 | 0.511 |
| 对牛弹琴 | 대우탄금 | exact_4/4 | 0.480 | 0.542 | 0.511 |

**10 most divergent pairs** (edit_pair_mean furthest from 0):

| ZH | KO | Match type | ZH edit | KO edit | Pair mean |
|---|---|---|---|---|---|
| 肝胆相照 | 간담상조 | near_3/4 | 0.688 | 0.688 | 0.688 |
| 功亏一篑 | 공휴일궤 | near_3/4 | 0.610 | 0.761 | 0.685 |
| 朝秦暮楚 | 조진모초 | exact_4/4 | 0.705 | 0.648 | 0.676 |
| 千差万别 | 천차만별 | exact_4/4 | 0.591 | 0.759 | 0.675 |
| 神出鬼没 | 신출귀몰 | exact_4/4 | 0.634 | 0.708 | 0.671 |

The most convergent pairs share a property: they have **clear, culturally portable
narrative images**.  班门弄斧/반문농부 ("showing off woodworking to Lu Ban, master
carpenter") and 对牛弹琴/대우탄금 ("playing lute to a cow") have concrete, universally
comprehensible scenes that the model renders consistently.  In contrast, the most
divergent pairs tend to be more abstract or culturally specific: 肝胆相照 ("liver and
gallbladder facing each other" — deep mutual trust) and 朝秦暮楚 ("serving Qin in the
morning, Chu in the evening" — fickleness) require cultural commentary that varies across
translations.

The scatter below shows **ZH edit distance vs KO edit distance** for all 537 pairs,
coloured by match type.  Pairs cluster near the diagonal (ρ ≈ 0.38–0.55 from Part 5),
confirming that an idiom that produces variable translations in Chinese also tends to
produce variable translations in Korean — the source of difficulty is largely
concept-level, not language-specific.

![cognate_divergence_distribution](../figures/cognate_divergence_distribution.png)
