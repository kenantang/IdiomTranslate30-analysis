# Part 9: Analogy Strategy Slop Patterns

The Analogy strategy is designed to generate a fresh metaphor or analogy for each
source idiom, rather than supplying a direct translation or authorial stylisation.
Because this strategy must invent rather than recall, it is the most prone to repeating
a stock repertoire of "poetic-sounding" images — a class of output sometimes called
*LLM slop*: formulaic metaphors that appear varied on the surface but share identical
underlying templates. This part documents those templates per target language.

## English: Eight Recurring Templates

The 90,641 English Analogy spans are dominated by a small set of structural templates.
Listed by how many distinct source idioms each covers:

**1. Weaving / thread / tapestry (3,580 spans / 2,049 idioms)**

The single largest template family. The model reaches for weaving imagery whenever it
needs to express unity, effort, fragility, or gradual accumulation. Surface forms vary
widely but the underlying frame is always the same: individual threads → single cable
for solidarity idioms; a single loose thread unravelling the whole tapestry for fragility;
weaving one thread at a time for patient progress. Examples:
- *"This disaster taught the villagers how to weave their separate threads into a single,
  unbreakable cable against the storm"* (for 风雨同舟, "in the same boat through wind and
  rain")
- *"Family members should weave their individual threads into a single unbreakable cable
  to pull through the storms of life together"* (for 和衷共济, "cooperate in common
  purpose")
- *"a single loose thread can unravel the entire tapestry"* (for fragility / sudden collapse
  idioms)
- *"trying to weave a ladder out of smoke"* / *"trying to weave a net out of moonlight"*
  (futility sub-template)

**2. Cosmic / star / galaxy (2,411 spans / 1,556 idioms)**

Star imagery is deployed for three distinct semantic functions: the North Star as a
fixed guiding principle, catching or reaching for stars as a futility or impossibility
frame, and galaxy/constellation as a scale metaphor for magnitude. Examples:
- *"North Star"* / *"moral north star"* / *"North Star's anchor"* (for guidance,
  exemplar, or beacon idioms — 금과옥조, 泰山北斗, etc.)
- *"a single star burning in a sunless void"* (for isolation or standing alone idioms)
- *"with the precision of a master watchmaker tuning a galaxy"* (precision + cosmic
  elaboration combined)
- *"catching a falling star in a jar"* / *"catching a falling star in a thimble"*
  (futility sub-frame)

**3. Kaleidoscope (619 spans / 327 idioms)**

"A kaleidoscope of X" is the model's default Analogy span for complexity, contradiction,
variety, or instability. The template is nearly formulaic — the word "kaleidoscope"
appears with a following noun almost every time — and the elaboration adds adjectives
("shifting," "shattered," "smoky," "restless") without changing the underlying image:
- *"a kaleidoscope of clashing convictions"* (for contradiction idioms)
- *"a kaleidoscope of blossoms"* (for variety or richness idioms)
- *"a kaleidoscope of shifting mirrors"* / *"a kaleidoscope of shattered mirrors"*
  (compound slop: kaleidoscope + mirrors combined)
- *"a kaleidoscope of smoke and mirrors"* (triple compound)

**4. "Trying to X" futility templates (912 spans / 430 idioms)**

A highly productive construction where the Analogy span always begins with "trying to"
followed by a physically impossible action. The actions vary but draw from a stock of
about a dozen base images: harvesting moonlight, weaving something from smoke or moonlight,
extinguishing a forest fire with a teardrop, catching clouds with a butterfly net, filling
a canyon with pebbles, mapping a labyrinth in the dark. Examples:
- *"trying to harvest moonlight in a bucket"* (for daydreaming / wishful thinking idioms)
- *"trying to extinguish a forest fire with a single teardrop"* / *"trying to quench
  a forest fire with a single teardrop"* (for futile-effort idioms)
- *"trying to weave a parachute after leaping from the plane"* (for too-late remedies)
- *"trying to fill a bucket with a fork"* / *"trying to halt a landslide with a toothpick"*
- *"trying to catch lightning in a paper bag"* / *"trying to bottle a thunderstorm"*

**5. Scattered like dandelion seeds (367 spans / 268 idioms)**

The phrase "scattered like dandelion seeds caught in a sudden gale" (and variants with
"sudden gale" → "gale", or "dandelion seeds" → "a dandelion") is the model's canonical
Analogy for dispersal, dissolution, collapse, and disorder idioms:
- *"the crowd scattered like dandelion seeds caught in a sudden gale"* (for 一哄而散,
  "scatter with a shout")
- *"the merchandise vanished from the shelves like dandelion seeds caught in a sudden
  gale"* (for 一扫而空, "swept clean in one stroke")

**6. Labyrinth of mirrors (107 spans / 79 idioms)**

Confusion, deception, and self-referential complexity idioms consistently attract
mirror-labyrinth imagery: "a labyrinth of shifting mirrors," "a labyrinth of jagged glass,"
"wandering through a forest of mirrors." Unlike the Spanish version below (see Cross-Language
section), English uses this template sparingly — it ranks well below the top clusters.

**7. Precision of a master clockmaker (306 spans / 190 idioms)**

Used for all precision, meticulousness, and expert craft idioms. The template is always
the same form: *"with the precision of a master [craftsman]"* where the craftsman is
almost always a clockmaker or watchmaker:
- *"she navigated the company out of its nosebleed with the surgical precision of a master
  clockmaker"* (for 精明强干)
- *"despite his youth, he already navigates life with the sharp precision of a master
  clockmaker in a field of sundials"* (same idiom, different sentence)

**8. Castle / palace built of mist or smoke (83 spans / 47 idioms)**

A dedicated template for ephemerality, hollow promises, and illusory achievement:
- *"castle built of morning mist"* / *"palace carved from mountain mist"*
- *"a castle built on a foundation of mist"* (for 好高骛远, 空中楼阁, etc.)
- *"as hollow as a drum made of smoke"*

## Romance Languages: The Mirror Labyrinth Dominates

French, Spanish, and Italian all share a dramatically stronger attachment to the
mirror-labyrinth image than English does. Spanish is the most extreme case.

**Spanish (404 spans / 275 idioms)** — the labyrinth-of-mirrors template is the single
most distinctive Analogy pattern in Spanish, appearing in forms such as:
- *"un laberinto de espejos empañados"* (a labyrinth of fogged mirrors, 18 uses)
- *"laberinto de espejos rotos"* (broken mirrors, 10 uses)
- *"un laberinto de espejos líquidos"* (liquid mirrors, 6 uses)
- *"un laberinto de espejos sin salida"* (mirrors with no exit, 7 uses)

Spanish also uniquely escalates the clockmaker precision template by adding cosmic
elaboration — a pattern not seen in English:
- *"con la precisión de un relojero de estrellas"* (with the precision of a clockmaker
  of stars, 10 uses)
- *"con la precisión de un relojero de nubes"* (clockmaker of clouds, 9 uses)
- Appeared for idioms like 百无一失 and 训练有素, where English uses plain
  "master clockmaker" but Spanish invents a poetic qualifier for the object being
  measured

Spanish also has a **brújula (compass) cluster**: "brújula de cristal" (crystal compass,
15 uses), "brújula de fuego" (fire compass), "brújula de seda" (silk compass) — all used
for idioms about moral principles, reliable guides, or fixed standards.

**French** mirrors the Spanish patterns with its own variants:
- *"un labyrinthe de miroirs déformants"* (distorting mirrors, 11 uses)
- *"une boussole affolée au milieu d'un orage magnétique"* (a compass going haywire in
  a magnetic storm) for disorientation idioms — a vivid image also adopted in German
  and Spanish
- *"la ferveur d'une racine perçant le granit"* (the fervor of a root piercing granite,
  12 uses) for perseverance idioms
- *"sculpter des nuages de fumée"* (sculpting clouds of smoke, 8 uses) for futility

**Italian** shares the mirror labyrinth template and introduces a distinctive variant:
- *"tessitore di nubi"* (weaver of clouds, 13 uses) — the Analogy strategy maps the
  English "master weaver" template onto an Italian variant that makes the object of
  weaving cosmic: clouds, constellations, dew, destinies
- *"mungere le nuvole"* / *"mungere il vento"* (milking the clouds / milking the wind,
  11 uses combined) — an Italian futility idiom the model applies broadly to any
  "wasted effort" source idiom
- *"costanza di una goccia che scava il granito"* (constancy of a drop that carves
  granite, 11 uses) — the "water carves stone" perseverance metaphor

## German: The Magnetic Storm Compass

German Analogy is dominated by compass and magnetic-storm imagery rather than mirror
labyrinths. The most frequent high-count Analogy span is:
- *"wie ein Kompass in einem Magnetsturm"* (like a compass in a magnetic storm, 12 uses)
  — for all confusion, disorientation, and loss-of-direction idioms
- *"wie ein Kompass ohne Nadel"* (a compass without a needle, 7 uses) — same template,
  different sub-image
- *"wie ein Kompass, der seinen Nordpol verloren hat"* (a compass that has lost its
  North Pole, 3 uses)

German also uses *"ein einzelnes Sandkorn in einer endlosen Wüste"* (a single grain of
sand in an endless desert, 9 uses) for insignificance and isolation idioms — the German
equivalent of the English "drop in the ocean" template.

## Russian: Abstract Nouns and Physical Impossibilities

Russian Analogy shows a distinctive preference for **single abstract nouns** as the
Analogy span, rather than elaborate metaphorical phrases. The top spans include:
"нерешительность" (indecision, 17 uses), "высокомерие" (arrogance, 14 uses),
"бесстыдство" (shamelessness, 12 uses), "бездействие" (inaction, 9 uses). For Russian,
the Analogy span names the semantic concept rather than constructing an image around it.

When Russian does use extended metaphors, they follow a futility template reminiscent of
the English "trying to" cluster:
- *"вычерпать море решетом"* (bail out the sea with a sieve, 6 uses) — the Russian
  idiomatic expression for futility, applied to idioms about wasted effort and
  contradiction
- *"усидеть на двух разъезжающихся льдинах"* (to sit on two ice floes drifting apart,
  8 uses) — used for idioms about irreconcilable contradiction

## Arabic: The Dust and the Immortality Poles

Arabic Analogy clusters around two opposite poles — total dissolution and eternal life:
- *"الخلود"* (immortality, 21 uses) absorbs all longevity, legacy, and timelessness
  idioms: 長生不死, 不老不死, 불로장생, 永生不滅 — every CJK "eternal life" cluster funnels
  into this single Arabic word
- *"كمن يطارد خيط دخان في مهب الريح"* (like chasing a thread of smoke in the wind,
  6 uses) — futility framed with dust/smoke imagery drawn from Classical Arabic registers
- *"نحت الجبال بقطرات الندى"* (carving mountains with dewdrops, 6 uses) — perseverance
  through impossibly gradual effort

Arabic is also notable for using *"سحابة صيف عابرة"* (a passing summer cloud, 8 uses)
for all fleeting, ephemeral, and short-lived idioms — a direct Arabic equivalent of the
"castle built of morning mist" template in English.

## Hindi and Bengali: Mapping onto Existing Target-Language Idioms

Hindi and Bengali Analogy works differently from the European languages: instead of
inventing novel metaphorical phrases, the model tends to map source idioms onto
**existing idioms in the target language**. The result is that the Analogy spans are
often established Hindi or Bengali figurative expressions rather than original creations.

**Hindi top Analogy spans:**
- *"पलक झपकते ही"* (in the blink of an eye, 40 uses) — a fixed Hindi idiom applied to
  all speed, suddenness, and instantaneity source idioms
- *"पत्थर की लकीर"* (a line etched in stone, 20 uses) — used for permanence,
  irreversibility, and fixed commitment idioms; itself a Hindi idiom meaning an
  unchangeable decree
- *"पारस पत्थर"* (the philosopher's stone, 13 uses) — for transformation and
  value-unlocking idioms: the Sanskrit alchemical concept maps onto any source idiom
  about turning something ordinary into something precious
- *"उतार-चढ़ाव"* (ups and downs, 23 uses) — applied broadly to all change and
  fluctuation idioms; a common Hindi expression itself

**Bengali top Analogy spans:**
- *"আকাশকুসুম কল্পনা"* (sky-flower imagination, 21 uses) — Bengali idiom for an
  impossible dream or idle fantasy, applied to all wishful thinking and unrealistic
  aspiration source idioms
- *"অগণিত"* (countless/innumerable, 31 uses) — a single adjective span applied to
  magnitude and abundance idioms
- *"অবিনশ্বর"* (imperishable, 27 uses) — immortality and permanence idioms
- *"একই মুদ্রার এপিঠ-ওপিঠ"* (two sides of the same coin, 10 uses) — for duality and
  inseparability idioms; itself a standard Bengali/Hindi phrase

The pattern is structural: where English invents "dandelion seeds caught in a gale" or
"trying to weave a net out of moonlight," Hindi substitutes "in the blink of an eye" or
"a line etched in stone" — the model is translating by idiom-substitution rather than
metaphor-invention. This likely reflects the model having absorbed a richer stock of
conventional idiom-level figurative mappings for Hindi and Bengali through training.

## Swahili: Vernacular Idioms as Analogy Templates

Swahili Analogy shares the Hindi/Bengali substitution pattern but with its own
distinctive idiom inventory, producing a set of highly vivid vernacular images:

- *"kupaka rangi upepo"* (painting the wind, 44 Analogy uses) — the dominant futility
  image; "you are painting the wind" for any idiom meaning a completely pointless effort
- *"kumpigia mbuzi gitaa"* (playing guitar to a goat, 13 uses) — for idioms about wasted
  wisdom on an unreceptive audience (pearls before swine equivalents): 对牛弹琴,
  馬耳東風 (horse's ear to the east wind), 마이동풍 all map here
- *"kutumia mzinga wa kivita kuua mbu"* (using a tank to kill a mosquito, 12 uses) —
  for overkill and disproportionate force idioms: 大材小用, 牛刀割鶏, 杀鸡焉用牛刀
  (why use an ox knife to slaughter a chicken?)
- *"kujaribu kukamua maziwa kwenye jiwe"* (trying to milk a stone, 10 uses) — for
  impossible-extraction futility idioms

Swahili's Analogy spans are all culturally grounded proverbs or folk sayings rather
than invented images. The model knows these Swahili expressions and deploys them
systematically as analogical frames.

## A Cross-Language Attractor: The Hongmen Banquet

One historical reference appears as an Analogy span in six languages — the Chinese
Hongmen Banquet (鸿门宴 / 鴻門之会), a famous 206 BCE feast that was actually a planned
assassination attempt by Xiang Yu against Liu Bang. The model uses this event as an
analogy for any idiom involving a trap disguised as hospitality, treacherous social
situations, or hidden danger:

| Language | Span | Uses |
|---|---|---|
| Swahili | "karamu ya Hongmen" | 16 |
| French | "banquet de Hongmen" | 14 |
| Italian | "banchetto di Hongmen" | 14 |
| Spanish | "Banquete en Hongmen" | 13 |
| German | "Bankett von Hongmen" | 12 |
| English | "Hongmen Banquet" | 7 |

Swahili uses this reference most frequently (16 uses), which is unexpected — it is a
specifically Chinese historical event with no particular resonance in Swahili cultural
tradition. This suggests the model has latched onto it as a universally available "trap
disguised as hospitality" analogy template, deploying it across all target languages
regardless of whether the reference would be culturally legible to a native reader.
