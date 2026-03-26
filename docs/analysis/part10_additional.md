# Part 10: Additional Analyses

## 10.1 Per-Idiom Slop Score

For each idiom, we count what fraction of its 10 English Analogy spans fall into one of
the eight template families identified in Part 9 (weaving/thread, cosmic/star, kaleidoscope,
"trying to X" futility, dandelion/scattered, labyrinth/mirror, clockmaker precision,
castle/mist). Spans not matching any template are labelled "original."

**Overall: 12.4% of the 90,641 English Analogy spans are templated.**

| Slop score bucket | Idioms | % |
|---|---|---|
| 0% (entirely original) | 4,125 | 45.5% |
| 1–10% | 1 | 0.0% |
| 11–30% | 3,324 | 36.7% |
| 31–50% | 1,133 | 12.5% |
| >50% | 479 | 5.3% |

Almost half of all idioms never trigger a template at all. But 5.3% are heavily formulaic,
with more than half of their spans falling into a stock image. Mean slop score by source
language: Korean 0.145, Japanese 0.126, Chinese 0.111 — Korean idioms are the most
template-prone in English Analogy.

**100% slop idioms — and why:**

| Idiom | Source | Template | Explanation |
|---|---|---|---|
| 泰山北斗 | ZH/JA | cosmic_star_galaxy | "Mount Tai and North Star" — the idiom literally names a star; every Analogy span becomes "North Star" |
| 天字第一号 | ZH | cosmic_star_galaxy | "The number one under heaven" → model maps "supreme/first" to North Star imagery |
| 金科玉条 | JA | cosmic_star_galaxy | "Golden rules worth cherishing" → the model treats any fixed guiding standard as a North Star |
| 海底捞月 | ZH | trying_to_futility | "Fish the moon from the sea floor" — the idiom *is* a futility metaphor; the Analogy strategy simply re-states it |
| 水中捞月 | ZH | trying_to_futility | "Scoop the moon from water" — cognate of above; all 10 spans are "trying to catch X" |
| 班门弄斧 | ZH | trying_to_futility | "Show off an axe at Lu Ban's gate" → always rendered as "trying to teach X to Y" (a spider to spin, a nightingale to sing) |
| 千差万別 | JA | kaleidoscope | "A thousand differences, ten thousand distinctions" → the model defaults to "a kaleidoscope of X" for all variety idioms |
| 歌功颂德 | ZH | weaving_thread_tapestry | "Sing of merits and virtues" → always "wove a tapestry of verbal monuments" or similar |

The 100%-slop cases reveal a genuine semantic logic: the source idiom and the template
are *the same image* — the model is not being lazy but has correctly found that one family of
metaphors perfectly captures the idiom. The problem arises when the template is applied even
when the idiom has a richer or more specific meaning than the template can express.

**0% slop idioms** generate genuinely varied metaphors across all 10 sentences. Examples:
- 如鱼得水 (ZH, "like a fish in water") → "like a bird that found the updraft," "fit like a
  master key to a secret door," "moved like a brush rediscovering its canvas"
- 如虎添翼 (ZH, "like a tiger getting wings") → "an engine with a turbocharger," "like giving a
  high-speed train a second engine," "took on the momentum of a wildfire fueled by a sudden gale"
- 如胶似漆 (ZH, "like glue and lacquer") → "two echoes chasing a single sound," "bonded like two
  drops of rain merging on a leaf," "as seamless as two pages pressed into a single leaf"

These idioms have concrete, evocative surface imagery that invites genuinely fresh analogies
each time — unlike the "guide/standard" or "futility" idioms that collapse into a template.

---

## 10.2 Most Span-Diverse Idioms (Inverse of Part 8)

Part 8 asked which spans absorb many idioms. This section inverts the question: which
idioms generate the most distinct span forms across all 10 target languages × 3 strategies
(up to 300 spans per idiom)?

**Distribution:** mean 280.9 distinct spans out of 300, median 288, std 22.3. The
distribution is tightly left-skewed — most idioms are highly span-diverse, with the
interesting variation at the low end.

The four highest-diversity idioms are 生龙活虎, 触景生情, 前仆后继, and 固执己见 — the
four Chinese idioms that have 20 sentences each (600 total spans instead of 300). Their
raw distinct counts (581, 563, 557, 486) exceed what is possible for standard idioms.
Among standard 300-span idioms, diversity ratio of 1.0 (all 300 spans unique) is common.

**Most span-locked idioms (lowest distinct count among standard idioms):**

| Idiom | Source | Distinct spans / 300 | Ratio | Why locked |
|---|---|---|---|---|
| 总而言之 | ZH | 81 | 0.27 | "In summary" — each language has a fixed translation: "kwa ufupi," "خلاصة القول," "kurzum," "одним словом," "alles in allem," "en somme," "en resumen" |
| 有朝一日 | ZH | 108 | 0.36 | "Someday" — every language converges on its word for "one day": "eines Tages," "un giorno," "siku moja," "настанет день," "un jour," "algún día" |
| 久而久之 | ZH | 122 | 0.41 | "Over time" — similar: "со временем," "au fil du temps," "mit der Zeit" |
| 무혈혁명 | KO | 123 | 0.41 | "Bloodless revolution" — translates transparently across all languages |
| 질의응답 | KO | 129 | 0.43 | "Question and answer" — each language has a fixed phrase: "maswali na majibu," "preguntas y respuestas," "Fragerunde," "Q&A session" |
| 无名英雄 | ZH | 132 | 0.44 | "Unsung hero" — English phrase is canonical, other languages use their own fixed equivalent |
| 자연도태 (JA: 自然淘汰) | JA | 133 | 0.44 | "Natural selection" — a scientific term with no figurative variation possible |

The pattern is sharp: the most span-locked idioms are not metaphorical classical expressions
but **functional/discourse particles or modern concepts** — "in summary," "someday," "over
time," "bloodless revolution," "Q&A," "natural selection." These have a single correct
translation in every language and no room for analogical variation. The locking is not
a model failure but a reflection of semantic concreteness: when there is only one right
answer, all strategies and all sentences converge on it.

Per-strategy breakdown confirms this: for 总而言之, Creatively, Analogy, and Author all
produce similar counts of distinct spans (41, 39, 33) — the locking is strategy-independent,
not a Creatively/Author alignment artifact.

---

## 10.3 Template vs Surface Diversity Reconciliation

Part 3 reported that 92.1% of English Analogy cells (one idiom × one target language ×
10 sentences) have all-different spans across their 10 sentences, implying genuine
sentence-level diversity. Part 9 shows that the Analogy strategy heavily reuses templates.
These appear contradictory. This section reconciles them.

**Surface diversity is high.** 91.5% of the 9,062 English Analogy cells have all 10 spans
lexically unique (no two spans are identical tokens). This confirms Part 3.

**But template diversity is much lower:**

| Distinct templates used in one cell of 10 spans | Idioms |
|---|---|
| 1 (only "original" or only one named template) | 4,131 |
| 2 | 3,682 |
| 3 | 1,119 |
| 4 | 120 |
| 5 | 10 |

The typical cell uses only 1–2 distinct image families across 10 sentences.

**The key finding:** of the 8,288 cells where all 10 surface spans are unique (91.5%),
**41.3% (3,425 cells) use only one named slop template** — meaning the model generates 10
lexically different spans that are all structurally the same image. Examples:

- [ZH] 一叶障目，不见泰山 → template=weaving, spans: "a single speck of dust to eclipse the
  entire sun" / "allow a passing ripple to swallow the entire ocean" / "obsessed with a
  single loose thread while the entire tapestry unravels unnoticed" — 10 unique surfaces,
  all within the weaving frame
- [ZH] 一人得道，鸡犬升天 → template=cosmic, spans: "when one person climbs to the stars, even
  their garden weeds are pulled up to heaven" / "a single star rising pulls its entire
  constellation into the heavens" — 10 unique surfaces, all celestial metaphors
- [ZH] 千差万別 → template=kaleidoscope: "a kaleidoscope of clashing and harmonizing cultures"
  / "a kaleidoscope of a billion shifting fragments" — 10 unique spans, all kaleidoscopes

**Conclusion:** The 92% all-different-surface-span rate from Part 3 substantially overstates
actual diversity. Nearly half the idioms that appear surface-diverse are in fact template-locked
at the structural level — the model is generating *parameter variations* within a fixed image
(different objects for the dandelion to scatter, different things to be woven into a cable)
rather than exploring genuinely different analogical frames.

---

## 10.4 Source-Language Differential for Slop Templates

Different source languages pull the English Analogy strategy toward different template
families at a statistically significant level (χ²=321.5, df=14, p=3.8×10⁻⁶⁰).

| Template | Chinese | Japanese | Korean | Max/min ratio |
|---|---|---|---|---|
| cosmic_star_galaxy | 2.05% | **4.05%** | 3.35% | **2.0×** |
| weaving_thread_tapestry | 6.11% | 6.06% | **8.34%** | 1.4× |
| mist_smoke_castle | 0.07% | 0.11% | **0.20%** | **3.0×** |
| trying_to_futility | **1.11%** | 0.60% | 0.78% | 1.9× |
| labyrinth_mirror | 0.30% | 0.37% | **0.43%** | 1.4× |
| kaleidoscope | **0.63%** | 0.71% | 0.61% | 1.2× |
| clockmaker_precision | 0.34% | 0.29% | **0.45%** | 1.6× |
| dandelion_scattered | **0.46%** | 0.43% | 0.32% | 1.4× |

**Cosmic/star is a Japanese-specific bias (2.0×).** Japanese idioms attract twice as much
North-Star/galaxy imagery as Chinese idioms. The driver is a cluster of Japanese idioms
about eminence and guiding standards — 泰山北斗, 金科玉条, 眼中之人, 不朽不滅 — which
overlap with the North Star concept. Chinese has some of these (天字第一号, 金科玉律) but
fewer that match the "supreme exemplar" frame.

**"Trying to X" futility is a Chinese-specific bias (1.9×).** Chinese idioms attract
nearly twice as much futility-template imagery as Japanese. The driver is a cluster of
Chinese idioms that are themselves futility metaphors: 海底捞月, 水中捞月, 缘木求鱼
("climb a tree to catch fish"), 抱薪救火 ("carry kindling to put out a fire") — idioms
where the source image directly invites a "trying to do the impossible" restatement.

**Mist/smoke/castle is a Korean-specific bias (3.0×).** Korean idioms are three times
more likely than Chinese idioms to attract the ephemerality template. This likely reflects
a Korean-idiom cluster around impermanence and hollow pretension that does not have as
strong a representation in the Chinese or Japanese subsets.

**Weaving/thread is highest for Korean (8.34% vs ~6% for ZH/JA)**, reflecting Korea's
larger inventory of solidarity and unity idioms that map naturally onto the "weaving
individual threads into a single cable" frame.

---

## 10.5 Cultural Reference Portability

Across 90,641 Analogy spans spanning all 10 target languages, 42 span strings appear
verbatim in 3 or more target languages. These fall into two structurally distinct categories.

**Category A: CJK terms the model refuses to translate (romanisation pass-through)**

The most striking cross-language spans are *not* well-known cultural references but
highly specific Japanese religious, historical, or philosophical terms that the model
simply romanises rather than translating — identically, across all 6 Latin-script languages:

| Term | Idiom | Languages | Romanised form |
|---|---|---|---|
| 尊皇攘夷 (Sonnō Jōi, "revere emperor, expel barbarians") | JA | 6 | "Sonno Joi" |
| 只管打坐 (Shikantaza, "just sitting" — Zen meditation) | JA | 6 | "shikantaza" |
| 廃仏毀釈 (Haibutsu kishaku, 19th-c. Buddhist suppression) | JA | 6 | "haibutsu kishaku" |
| 和敬清寂 (Wa-kei-sei-jaku, tea ceremony principles) | JA | 6 | "wakeiseijaku" |
| 本地垂迹 (Honji suijaku, Shinto-Buddhist doctrine) | JA | 6 | "honji suijaku" |

"Shikantaza" achieves 31 uses across 6 languages — the model writes "Practicing Shikantaza"
(EN), "le shikantaza" (FR), "Das reine Sitzen im Shikantaza" (DE), "shikantaza" (IT/SW/ES).
The pattern reveals that when the model encounters an extremely specific classical Japanese
term with no natural equivalent in a target language, it falls back on romanisation — and
applies this fallback uniformly across all 6 Latin-script languages. "Shikantaza" is not
an analogy for 只管打坐; it is 只管打坐, untranslated.

**Category B: Western cultural references deployed cross-linguistically**

| Reference | Languages | Source idioms | Typical span |
|---|---|---|---|
| Hongmen Banquet | 7 (all except Arabic/Bengali/Hindi) | 2 | "Banquet at Hongmen" / "Banquet de Hongmen" |
| Natural selection | 5 (European only) | 7 | "natural selection" / "sélection naturelle" / "natürliche Auslese" |
| Gordian knot | 3 (EN, IT, ES) | 25 | "Gordian knot tied with smoke" |
| Prodigal son | 3 (EN, FR, IT) | 1 | "prodigal son" / "fils prodigue" |

The Hongmen Banquet appears in 7 languages (absent only from Arabic, Bengali, Hindi — the
languages with non-Latin scripts where the reference would require transliteration). Natural
selection is restricted to the 5 European languages with substantial science vocabulary in
the model's training data. The Gordian knot spans 25 different source idioms in 3 languages —
the model uses it generically for any "intractable tangle" idiom.

---

## 10.6 Bathos: Prosaic Analogy Spans for Classical Idioms

A small but consistent fraction of Analogy spans are not analogies at all — they are simple
labels: single abstract nouns, technical terms, or mundane two-word phrases that name the
concept rather than create an image for it.

**Bathos rate by target language (% of all Analogy spans):**

| Language | Bathos rate | Top bathos spans |
|---|---|---|
| Bengali | 0.20% | অগণিত (countless), বারবার (again and again), অবিনশ্বর (imperishable) |
| English | 0.18% | "immortality", "self-reliance", "day and night", "Q&A session" |
| Hindi | 0.19% | बार-बार (again and again), अमरता (immortality), अजीबोगरीब (peculiar) |
| German | 0.14% | "beispiellos" (unprecedented), "Fragerunde" (Q&A), "Unermüdlich" (tireless) |
| Russian | 0.12% | "нерешительность" (indecision), "высокомерие" (arrogance), "бесстыдство" (shamelessness) |
| Spanish | 0.11% | "una y otra vez" (again and again), "la inmortalidad" |
| French | 0.11% | "l'immortalité", "métabolisme", "séance de questions-réponses" |
| Swahili | 0.10% | "maswali na majibu" (Q&A), "mchana na usiku" (day and night) |
| Italian | 0.10% | "l'immortalità", "metabolismo", "botta e risposta" (Q&A) |
| Arabic | 0.11% | "الخلود" (immortality), "مراراً وتكراراً" (again and again), "التردد" (indecision) |

Bathos rates are low (~0.1–0.2%) but consistent across all languages. Three semantic
clusters produce bathos across the most languages:

**1. Immortality / eternal life** — the idiom cluster 不老不死 / 長生不死 / 불로장생 /
영생불멸 (eternal youth, eternal life) produces "immortality" / "l'immortalité" /
"l'immortalità" / "الخلود" / "अमरता" in 7 languages simultaneously. These are the most
cross-linguistically bathetic idioms in the dataset: the concept is so concrete that
the Analogy strategy simply names it rather than inventing a metaphor for it.

**2. Q&A terminology** — 질의응답 (KO) and 質疑応答 (JA) both produce "Q&A session" /
"Fragerunde" / "séance de questions-réponses" / "maswali na majibu" / "domande e risposte"
in 7 languages. These idioms literally mean "question and answer," so every strategy in
every language defaults to that phrase.

**3. Repetition and persistence** — 屡次三番, 再三再四, 夜以继日 (ZH) and their cognates
produce "again and again" / "day and night" / "बार-बार" / "বারবার" / "une et encore une"
across up to 7 languages. Idioms meaning "repeatedly" or "without rest" have so clear a
gloss that no analogy improves on it.

**Russian is structurally different** from the other languages in this analysis. While all
languages produce some bathos, Russian's top bathos spans (нерешительность, высокомерие,
бесстыдство, бездействие) are not conventional labels for the source idiom's meaning —
they are Russian *character concepts* applied to CJK idioms about hesitation and arrogance.
This confirms the finding from Part 9: Russian Analogy deliberately names the psychological
concept rather than creating an image, which makes it look like "bathos" by the labelling
criterion but is actually a distinct translation philosophy specific to Russian.
