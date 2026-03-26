# Part 8: Reverse Span Analysis — Translation Attractors

The analyses in Parts 3–7 ask how a given idiom gets translated. This part inverts the
question: looking across all idioms, which translation *spans* are reused as renderings for
multiple different source idioms? A span that absorbs many distinct idioms is a
**translation attractor** — a phrase in the target language that the model defaults to for
an entire class of semantically related (or superficially related) source expressions.

Spans are NFC-normalized and lowercased before counting. For each (target language, span)
pair we record how many distinct source idioms it covers and how many total times it appears.

## Attractor Statistics Overview

| Language | Spans covering ≥10 idioms | Spans covering ≥5 idioms | Max idioms per span | Resource |
|---|---|---|---|---|
| Bengali | 290 | 1,135 | 112 | Low |
| Hindi | 246 | 1,088 | 73 | Low |
| Swahili | 140 | 618 | 108 | Low |
| Spanish | 119 | 588 | 87 | High |
| French | 112 | 689 | 113 | High |
| Italian | 102 | 561 | 72 | High |
| German | 93 | 556 | 50 | High |
| English | 94 | 534 | 24 | High |
| Russian | 73 | 558 | 33 | High |
| Arabic | 72 | 408 | 66 | Low |

The most striking finding is how different English is from every other language: its top
attractor spans only 24 idioms, while French and Bengali both exceed 100. English has the
most granular rendering vocabulary — fewer idioms collapse onto the same phrase.

## Top Attractor per Language

| Language | Top attractor span | Idioms | Uses | Strategy profile |
|---|---|---|---|---|
| English | "blessing in disguise" | 24 | 83 | Creatively 60%, Author 40% |
| French | "corps et âme" | 113 | 236 | Creatively 97% |
| Spanish | "en cuerpo y alma" | 87 | 154 | Creatively 99% |
| German | "mit Leib und Seele" | 50 | 105 | Creatively 88% |
| Italian | "anima e corpo" | 72 | 124 | Creatively 99% |
| Russian | "не разлей вода" | 33 | 53 | Creatively 98% |
| Arabic | "هباءً منثوراً" | 66 | 152 | Author 55%, Creatively 45% |
| Hindi | "दिन-रात एक करके" | 73 | 159 | Creatively 65%, Author 34% |
| Bengali | "হাড়ভাঙা খাটুনি" | 112 | 224 | Creatively 47%, Author 47% |
| Swahili | "kufa na kupona" | 108 | 210 | Creatively 76%, Author 22% |

Two patterns are immediately visible. First, attractors are dominated by the **Creatively
strategy** in 8 of 10 languages — Analogy rarely appears as the dominant contributor to
any single high-frequency span. Second, Arabic ("هباءً منثوراً") is the only language
where the Author strategy has equal or greater weight (55%), reinforcing the earlier
finding that Arabic has distinctive strategy-level behaviour.

## Five Semantic Categories Drive All Attractors

The attractor spans cluster into a small set of recurring semantic categories, each
absorbing a large fraction of the East Asian idiom inventory:

**1. Wholehearted dedication / bone-breaking effort**

This is the single dominant category. French "corps et âme" ("body and soul") absorbs
113 distinct idioms — more than any other span in any language — covering the entire range
of East Asian "full effort" idioms: Chinese 全心全意 ("whole heart, whole will"), Japanese
一意専心 ("single-minded devotion"), 粉骨砕身 ("pulverise bones, crush flesh"), Korean 분골쇄신
(same meaning). The cognate phrases "en cuerpo y alma" (Spanish), "anima e corpo" (Italian),
and "mit Leib und Seele" (German) perform the same absorption function in their respective
languages — each is the canonical European rendering of the East Asian dedication idiom
cluster, and the model knows it. Bengali "হাড়ভাঙা খাটুনি" ("bone-breaking toil", 112 idioms)
and Hindi "दिन-रात एक करके" ("making day and night one", 73 idioms) play the same role for
South Asian targets: Japanese 汗馬之労, 薪水之労, 粉骨砕身 and their Korean and Chinese
cognates all funnel into these two phrases.

**2. Lucky reversal of fortune**

English "blessing in disguise" (24 idioms) is the attractor for all idioms meaning "misfortune
turns to good": Chinese 转祸为福, Japanese 塞翁失馬 (the classic "Old Man's Horse" fable),
Korean 전화위복, 원화소복, 복재적선, and a dozen more Korean idioms expressing the same concept.
Japanese 塞翁失馬 and Korean 전화위복 alone account for 25 of the 83 uses, and together they
represent two cognate idioms that have been independently assigned the same English span,
confirming the phrase's semantic precision. No other English phrase approaches this count for
this semantic category.

**3. Futility / vanishing / wasted effort**

Arabic "هباءً منثوراً" ("scattered as dust", from Quranic Arabic, 66 idioms) absorbs the
entire range of "effort that came to nothing" idioms: Chinese 一盘散沙 ("loose sand", unity
impossible), 付之东流 ("cast to the east-flowing river"), Korean 도로무익 and 풍비박산
("scattered to the four winds"), Japanese 乱離骨灰. The Swahili attractor "kupaka rangi
upepo" ("painting the wind", 34 idioms) plays the same role but specifically for the
Analogy strategy — it is one of the rare cases where Analogy dominates a high-frequency
span (44 of 48 uses). The model apparently reaches for this vivid Swahili idiom when
inventing analogies for futile actions.

**4. Inseparability / close companionship**

Russian "не разлей вода" ("inseparable as water that won't pour apart", 33 idioms) absorbs
the full range of "close friends" and "inseparable pair" idioms from all three source
languages. English "kindred spirits" (23 idioms) and "kith and kin" target similar idioms.
Swahili "chanda na pete" ("finger and ring", 62 idioms) and "kufa na kupona" ("die or
survive together", 108 idioms) both function as inseparability attractors — the latter
pulling in an enormous range of commitment, sacrifice, and solidarity idioms from all three
source languages.

**5. Extreme contrast / polar difference**

English "worlds apart" (23 idioms) and "bolt from the blue" (17 idioms) serve two sub-categories:
"worlds apart" absorbs Chinese 天壤之别 ("sky–earth difference"), Japanese 雲泥万里 ("cloud–mud
distance"), Korean 천양지차, and similar extreme-contrast idioms; "bolt from the blue" absorbs
the CJK cognate cluster 晴天霹雳 / 청천벽력 / 青天霹靂 ("thunderbolt from a clear sky"),
appearing 23 times for those three cognates alone. Swahili "mbingu na ardhi" ("sky and earth",
43 idioms) and Hindi "आकाश-पाताल" ("sky–underworld", 45 idioms for आकाश-पाताल एक कर दिया)
cover the same semantic field in their respective languages.

## English Is the Most Discriminating Target Language

The contrast between English (max 24 idioms per span) and French or Bengali (max 112–113)
is not merely a scale difference — it reflects a qualitative difference in how the model
handles these languages. English has a richer and more varied stock of conventional
idiomatic phrases: "the talk of the town," "trial and error," "in a league of its own,"
"a drop in the ocean," "burning the midnight oil," "silver tongue," and dozens more each
absorb 12–17 idioms. No single phrase dominates because the idiom vocabulary is wide enough
to distribute the load.

For French, Spanish, Italian, and German, the "body and soul" phrase family is so
semantically central and so well-known that it dominates: the model reaches for "corps et
âme" whenever a source idiom connotes dedication or complete commitment, regardless of
whether the source idiom is about writing until dawn, risking one's life, or working
without rest. The result is that 113 distinct CJK idioms — each with a slightly different
nuance — collapse onto a single French phrase that only captures the broadest
"wholehearted" reading.

For Bengali and Swahili, the attractor dominance is even greater. Bengali "হাড়ভাঙা খাটুনি"
absorbs 112 idioms across all three source languages, meaning the model is effectively
rendering roughly 5% of all source idioms in the dataset with one Bengali phrase whenever
Bengali is the target. This is partly a vocabulary-depth problem (the model's Bengali idiom
range is narrower) and partly a morphological one: Bengali's complex script system produces
the highest span annotation error rate in the dataset (6.8%), and some of the 112 "distinct
idioms" using this span may reflect annotation variants of the same underlying Bengali phrase
rather than genuinely independent choices.

The Analogy strategy is largely **attractor-resistant**: for almost every language, the top
attractor is driven overwhelmingly by the Creatively strategy. Analogy is designed to
generate fresh analogies for each idiom, and it does so even when Creatively defaults to
the same phrase. The exception is Swahili "kupaka rangi upepo" (painting the wind), where
Analogy is responsible for 92% of uses — the model has identified this Swahili expression
as an effective analogical frame for futility and applies it consistently in analogy mode.

## Cognate Attractor Alignment

A notable structural finding: for the CJK cognate clusters identified in Part 5, the model
assigns the *same* English attractor span to all three source languages. Chinese 晴天霹雳,
Korean 청천벽력, and Japanese 青天霹靂 all receive "bolt from the blue" in English (7, 8, and
8 uses respectively). Chinese 大材小用 / Japanese 大器小用 / 牛刀割鶏 all receive "using a
sledgehammer to crack a nut" (9, 9, and 9 uses). The model has correctly identified these
as cognate clusters and applied the same English equivalent consistently. This attractor
convergence across sources is actually *correct* behaviour — unlike the "blessing in
disguise" case, where many semantically distinct Korean idioms have been collapsed because
the model could not find finer-grained English distinctions between them.
