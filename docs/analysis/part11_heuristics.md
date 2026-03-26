# Part 11: Heuristic String Matching — Catalogue, Limitations, and LLM-as-a-Judge Upgrades

Every quantitative finding in this report rests on some form of string matching. This section
catalogues every heuristic matching choice made across all analysis scripts, explains exactly
what each heuristic does and where it breaks down, and proposes a concrete LLM-as-a-judge
(LaJ) prompt that could replace or validate each one. The goal is to give future researchers
a clear picture of which numbers are robust and which should be treated as lower-bound
estimates pending a higher-quality evaluation pass.

Heuristics are grouped into eight categories that recur across multiple scripts.

---

## 11.1 Span Containment and Localisation

These heuristics answer the question *"Is the annotated span actually present in the
translation?"* They are used in `span_errors.py`, `span_audit.py`, and `span_position.py`
and underpin the span-error rates reported in Part 1.

### H1 — Exact substring match (`span in trans`)

**What it does.** Python's `in` operator tests whether the span string is a contiguous
substring of the translation string. This is the primary span-validity check.

**Limitation.** The check is case-sensitive and byte-exact. A span annotation of `"North
Star"` will fail against a translation containing `"north star"`, and a span containing a
trailing space will fail against one without. Both are annotation artefacts, not genuine
mismatches. In practice, roughly 3–5% of apparently "missing" spans are recoverable by the
softer checks below.

**LLM-as-a-judge upgrade.** Prompt a judge with the translation and the span and ask:
*"Does the following span appear verbatim or near-verbatim in the translation? Answer YES,
NEAR (explain the difference), or NO."* Use YES/NEAR as a pass for validity purposes. This
removes the need for any of H2–H5 below: the judge handles whitespace, capitalisation,
punctuation, and encoding in a single pass.

---

### H2 — Whitespace-stripped match (`span.strip() in trans`)

**What it does.** Strips leading and trailing whitespace from the span before the substring
test. Applied as a fallback when H1 fails.

**Limitation.** Only removes outer whitespace. A span with an internal double space
(`"blessing  in disguise"`) still fails against the single-spaced translation.

**LLM-as-a-judge upgrade.** Subsumed by the H1 upgrade above.

---

### H3 — Case-insensitive match (`span.lower() in trans.lower()`)

**What it does.** Lowercases both strings before the substring test.

**Limitation.** Lowercasing is locale-unaware in Python's default `str.lower()`. For
Turkish, the dotted-İ / dotless-ı distinction means `"İdiom".lower()` ≠ `"idiom"`. The
dataset contains no Turkish target language, but future extensions should be aware of this.

**LLM-as-a-judge upgrade.** Subsumed by H1 upgrade.

---

### H4 — Punctuation-stripped match

**What it does.** Removes all characters whose Unicode category starts with `"P"`
(punctuation), then tests substring containment. Applied as a third fallback.

**Limitation.** Unicode category `P` classifies characters as punctuation based on their
codepoint assignment, not their function in a particular script. Some Arabic diacritics and
Hebrew vowel points are not in category `P` but function as punctuation-like modifiers.
Conversely, some ideographic characters are assigned punctuation categories. For the
Latin-script majority of this dataset the heuristic is reliable, but Arabic and Hindi spans
may be affected.

**LLM-as-a-judge upgrade.** Subsumed by H1 upgrade.

---

### H5 — Off-by-one boundary match (`span[1:] in trans or span[:-1] in trans`)

**What it does.** Tests whether dropping the first or last character of the span produces a
match. Guards against spans that include or exclude a boundary character (e.g., a closing
quote or a period that happens to be attached to the span in the annotation).

**Limitation.** Only checks one-character truncations from each end. A span missing two
boundary characters, or differing at an internal position, is not caught. The guard on
`len(span) > 2` prevents degenerate 1–2 character spans from trivially matching.

**LLM-as-a-judge upgrade.** Subsumed by H1 upgrade; the judge can handle arbitrary
boundary differences.

---

### H6 — Word-overlap check (word-set intersection)

**What it does.** Splits both span and translation on whitespace, lowercases, and checks
whether any word appears in both sets. Used as a last-resort signal: if zero overlap exists,
the span is likely completely wrong.

**Limitation.** Space-based tokenisation produces incorrect tokens for German compounds
(`"Lebensweisheit"` will not match component words), agglutinative languages (Turkish,
Finnish), and languages without inter-word spaces (Chinese, Japanese, Thai). For
CJK-language spans this heuristic always returns zero overlap and therefore provides no
information.

**LLM-as-a-judge upgrade.** *"The following span was annotated as the translation of an
idiom within the following sentence. Do any words or morphemes in the span appear in the
sentence, even in a different inflected or compound form? Answer YES or NO with a one-line
reason."*

---

### H7 — Span position zone binning (`pd.cut` into beginning / middle / end)

**What it does.** Computes the character offset of the span within the translation, divides
by translation length, and bins the resulting value into three equal-width zones using
`pd.cut([-.001, 1/3, 2/3, 1.001])`.

**Limitation.** Equal-width zones at 1/3 and 2/3 are arbitrary. There is no linguistic
motivation for these boundaries. A span at position 0.32 and one at 0.36 are classified into
different zones despite being adjacent. Meaningful zones might instead be defined
syntactically (sentence-initial before the main verb, clause-final after the main verb, etc.)
or pragmatically.

**LLM-as-a-judge upgrade.** *"In the following sentence, the idiom translation appears at
the marked location. Is the idiom translation syntactically in: (a) a topic or fronted
position, (b) the main predicate, (c) a clause-final or parenthetical position, or (d)
somewhere else? Answer with (a), (b), (c), or (d) and a one-line reason."* This gives
linguistically grounded position labels rather than thirds-of-a-string.

---

## 11.2 Text Normalisation

These heuristics are used to make strings comparable before counting or matching. They appear
in `reverse_span_analysis.py` and `cognate_comparison_extended.py`.

### H8 — NFC normalisation + punctuation stripping for span deduplication

**What it does.** Applied in `reverse_span_analysis.py` before computing attractor counts:
each span undergoes `unicodedata.normalize("NFC", x.strip()).lower().strip(".,!?;:'\"")`
before being used as a grouping key.

**Limitation.** NFC (Canonical Decomposition followed by Canonical Composition) handles the
most common multi-codepoint representations of combining characters. However, NFC does not
handle compatibility equivalences (e.g., the full-width Latin letters used in Japanese
contexts, `Ａ` vs `A`). NFKC would cover these but risks over-normalising Arabic ligatures
and some Indic conjuncts that are semantically distinct. The punctuation strip list is
hard-coded to `.,!?;:'"` and will miss other common terminators (e.g., `…`, `—`, `「」`,
Arabic `؟`).

**LLM-as-a-judge upgrade.** Use a judge to decide whether two spans with different surface
forms are the same rendering of the same idiom: *"Are these two translation spans semantically
equivalent renderings of the same source idiom, or are they meaningfully different? Answer
SAME or DIFFERENT with a one-line reason."* This replaces character-level normalisation with
semantic equivalence, collapsing variants that differ only in typography, word order, or
minor paraphrase.

---

### H9 — OpenCC simplified-to-traditional conversion for cognate matching

**What it does.** In `cognate_comparison_extended.py`, Chinese idioms from the simplified
script source dictionary are converted to traditional script using OpenCC's `s2t` converter
before comparison against Japanese kanji forms.

**Limitation.** OpenCC `s2t` is a heuristic character-by-character substitution that does
not model character ambiguity (one simplified character can map to multiple traditional
characters depending on context). For example, 发 can become 發 (to emit) or 髮 (hair)
depending on the idiom, and the wrong choice would cause a false non-match with a Japanese
form that uses 髮. OpenCC attempts disambiguation via word-level rules but is not perfect.

**LLM-as-a-judge upgrade.** *"The following simplified Chinese idiom and traditional Chinese
/ Japanese idiom look similar. Are they the same idiom (same meaning and etymological origin),
cognates (related but diverged in meaning), or coincidentally similar in form? Answer SAME,
COGNATE, or COINCIDENTAL with a one-line reason."* This handles the ambiguity that
character-level normalisation cannot.

---

### H10 — kHangul Unihan lookup with hanja library fallback

**What it does.** In `cognate_comparison_extended.py`, CJK characters in Chinese idioms are
transliterated to their Korean Sino-Korean (Hangul) readings using the Unicode Unihan
database `kHangul` field. Characters missing from Unihan fall back to the `hanja` Python
library using substitution mode, with validation that the result is a single Hangul syllable.

**Limitation.** Many CJK characters have multiple Korean readings depending on context (e.g.,
樂 is 악 *ak* in music contexts and 낙 *nak* in pleasure contexts). The heuristic always
takes the first listed reading from Unihan without considering which reading is appropriate
for the given idiom. This can produce incorrect Sino-Korean forms for idioms where a
character's secondary reading applies, causing a genuine cognate to be missed or a
non-cognate to be falsely matched.

**LLM-as-a-judge upgrade.** *"The following Chinese idiom is compared with the following
Korean idiom. Both may be Sino-Korean in origin. Do they share the same classical Chinese
etymology, and would a native Korean speaker likely recognise them as related? Answer YES,
POSSIBLY, or NO with a one-line explanation citing the etymological relationship."*

---

## 11.3 Script and Character Classification

These heuristics detect what script a character or string belongs to. They appear in
`unmatched_chinese.py`, `japanese_yojijukugo.py`, `cognate_comparison_extended.py`, and
`difficulty.py`.

### H11 — CJK character detection by Unicode range

**What it does.** Checks whether a character's codepoint falls in the CJK Unified Ideographs
block (`U+4E00`–`U+9FFF`) or CJK Extension A (`U+3400`–`U+4DBF`). Used to identify
Chinese/Japanese characters in spans and idioms.

**Limitation.** Unicode assigns CJK characters to eight extension blocks
(A–H), the Compatibility Ideographs block (`U+F900`–`U+FAFF`), and several supplementary
plane blocks (`U+20000`–`U+3134F`). The scripts only check two of these blocks. Rare
characters in Extensions B–H (used in classical texts and personal names) would be missed.
In practice this affects fewer than 0.1% of idioms in this dataset but could matter for
highly classical Japanese or rare Chinese idioms.

**LLM-as-a-judge upgrade.** *"What writing system does the following character or string
belong to: Simplified Chinese, Traditional Chinese, Japanese Kanji, Korean Hanja, or mixed?
Answer with the most specific label and note if the character appears in multiple systems."*
This provides a semantically meaningful label rather than a codepoint range answer.

---

### H12 — 4-character idiom filter

**What it does.** Filters idioms to exactly 4 characters (by Python `len()`) to select
Chinese chengyu and Japanese yojijukugo. Used in `japanese_yojijukugo.py`,
`cognate_comparison_zhko.py`, `cognate_comparison_extended.py`, and `difficulty.py`.

**Limitation.** `len()` counts Unicode code points, not grapheme clusters. A 4-character
idiom that uses a character stored as a surrogate pair (e.g., some CJK Extension B
characters) would count as 5. Additionally, not all Classical Chinese idioms are 4
characters: three-character idioms (三字格, e.g., 拦路虎, 莫须有) and six-character idioms
(e.g., 醉翁之意不在酒) are culturally significant but excluded by this filter. The filter
also excludes Japanese yojijukugo that include kana (e.g., 大和撫子 at 5 characters if the
hiragana is retained).

**LLM-as-a-judge upgrade.** *"Is the following idiom a traditional four-character Chinese
chengyu or Japanese yojijukugo? If it is a related multi-character fixed expression that
would conventionally be treated similarly, also say YES. Answer YES or NO with a one-line
reason."* This replaces the hard length filter with a conventionality judgement.

---

### H13 — Hangul syllable range detection

**What it does.** Checks whether a character falls in the Hangul Syllables block
(`U+AC00`–`U+D7A3`) to validate Korean transliterations. Used in
`cognate_comparison_extended.py`.

**Limitation.** The Hangul Syllables block covers the 11,172 precomposed syllables used in
modern Korean. It does not cover Hangul Jamo (`U+1100`–`U+11FF`), the combining consonants
and vowels used for Old Korean, or the Hangul Compatibility Jamo (`U+3130`–`U+318F`). A
Sino-Korean reading stored as decomposed Jamo would fail this validation and be silently
discarded, reducing cognate recall.

**LLM-as-a-judge upgrade.** Subsumed by H10 upgrade above.

---

### H14 — Japanese column auto-detection by column name

**What it does.** In `complementary_idiom_types.py`, the script tries to find the column
containing Japanese text by checking if the column name contains `"japanese"`, `"kanji"`, or
is one of a hard-coded list (`"word"`, `"phrase"`, `"kotowaza"`, `"jp"`). Falls back to the
first object-dtype column.

**Limitation.** Column names in external datasets are unpredictable. A dataset that stores
the Japanese text in a column named `"headword"` or `"expression"` would cause the fallback
to trigger, potentially selecting the wrong column (e.g., a definition column instead of the
idiom column). The fallback does no content validation.

**LLM-as-a-judge upgrade.** Not applicable in the typical sense; this is a structural
parsing heuristic. Instead, validate by sampling: *"The following 5 cell values are from a
column named '{col}'. Is this column likely to contain Japanese idiom text (kanji/kana
expressions), or is it some other type of content? Answer IDIOMS or OTHER."* Run this on the
top 5 candidate columns and select the one scored IDIOMS with the highest confidence.

---

### H15 — Yojijukugo tag detection by substring

**What it does.** In `japanese_yojijukugo.py`, entries in a Wiktionary-derived dictionary
are classified as yojijukugo by checking whether `"四字熟語"` or `"yojijukugo"` (case-
insensitive) appears in their tag fields.

**Limitation.** Wiktionary tagging is community-maintained and inconsistent. Many genuine
yojijukugo are tagged as simply `"idiom"` without the specific yojijukugo tag. The script
supplements with H12 (4-character filter) but the combined recall is still incomplete:
expressions tagged as `"proverb"` or `"phrase"` that happen to be 4-character chengyu-derived
forms are excluded.

**LLM-as-a-judge upgrade.** *"Is the following Japanese expression conventionally classified
as a yojijukugo (四字熟語) — a fixed four-character compound with a culturally established
meaning? Answer YES, BORDERLINE (explain), or NO."* Apply to any 4-character entry not
already tagged.

---

## 11.4 Analogy Template Classification

### H16 — Regex template matching for 8 named slop patterns

**What it does.** In `analogy_deep_analysis.py`, each English Analogy span is matched
against 8 compiled regular expressions. The first matching pattern wins; unmatched spans are
labelled `"original"`. The patterns and their intent are:

| Template name | Pattern (simplified) | Target expressions |
|---|---|---|
| `weaving_thread_tapestry` | `weav\|tapestry\|unravel\|loom\|stitch\|woven` | Thread / fabric metaphors |
| `cosmic_star_galaxy` | `\bstar\b\|\bgalaxy\b\|\bcosmic\b\|\bconstellation\b\|\bnorth star\b` | Astronomical metaphors |
| `kaleidoscope` | `kaleidoscope` | Kaleidoscope image |
| `trying_to_futility` | `^trying to ` | Futility frames starting with "trying to" |
| `dandelion_scattered` | `dandelion\|scattered.*gale` | Dandelion / scattered-seeds image |
| `labyrinth_mirror` | `labyrinth\|hall of mirror\|forest of mirror` | Maze / reflection image |
| `clockmaker_precision` | `clockmaker\|watchmaker\|precision of a master` | Precision craftsman image |
| `mist_smoke_castle` | `castle.*(?:mist\|smoke\|fog)\|built of.*(?:mist\|smoke)` | Insubstantial castle image |

**Limitation.** The patterns were derived by manual inspection of English Analogy spans and
are necessarily incomplete. Several known limitations:

- **Coverage gap.** Templates were identified from English outputs only. Templates in
  non-English languages (e.g., Russian abstract-noun patterns, Arabic dust/immortality poles)
  are not captured. The `"original"` label absorbs all unmatched spans including other
  recurring templates not yet named.
- **Order dependency.** The first-match rule means a span matching multiple patterns is
  assigned only to the first one. For example, a span like `"a north star in a tapestry of
  stars"` would be classified as `weaving_thread_tapestry` (matched first) rather than
  `cosmic_star_galaxy`.
- **Lexical brittleness.** `kaleidoscope` is a single-word exact match; `"kaleidoscopic"`
  would not match. The `trying_to_futility` pattern requires the phrase at the start of the
  span; a span like `"like trying to..."` would not match.
- **No semantic generalisation.** A span like `"like a needle in an infinite loom"` would
  match `weaving_thread_tapestry` but so would a span that genuinely uses weaving as a
  culturally appropriate analogy rather than cliché. The regex cannot distinguish authentic
  use from slop.

**LLM-as-a-judge upgrade.** This is the highest-value LLM upgrade in the entire pipeline.
Prompt a judge with the source idiom, its literal meaning, and the Analogy span, then ask:

*"The following span is the model's Analogy-strategy translation of a CJK idiom. Classify it
into one of these categories:*
*(a) Weaving / thread / tapestry image*
*(b) Cosmic / star / galaxy / north-star image*
*(c) Kaleidoscope image*
*(d) Futility frame ('trying to X', 'like trying to X')*
*(e) Dandelion / scattered-seeds image*
*(f) Labyrinth / hall-of-mirrors image*
*(g) Clockmaker / watchmaker precision image*
*(h) Insubstantial castle / castle of mist image*
*(i) Another recurring LLM cliché — name it*
*(j) Culturally grounded or original image*

*Answer with the letter and a one-line justification. If (i), name the template."*

Category (i) would surface new templates that the regex approach misses entirely, producing a
data-driven template inventory rather than a manually hypothesised one.

---

## 11.5 Similarity and Distance Metrics

These heuristics quantify how similar two strings or string sets are. They appear in
`cognate_comparison_zhko.py`, `context_sensitivity.py`, `cross_target_overlap.py`, and
`difficulty.py`.

### H17 — Word-set Jaccard similarity

**What it does.** Splits texts on whitespace, lowercases, and computes
`|A ∩ B| / |A ∪ B|` over the resulting word sets. Used to measure:
- Translation similarity within a group (context_sensitivity.py, Part 3)
- Cross-language translation vocabulary overlap (cross_target_overlap.py, Part 4)
- One component of the composite difficulty score (difficulty.py, Part 6)
- Cognate translation similarity (cognate_comparison_zhko.py, Part 5)

**Limitation.** Word-set Jaccard has four well-known failure modes in this dataset:
1. **Inflection blindness.** `"runs"` and `"running"` are treated as different words; two
   translations that use the same verb in different tenses score lower than they should.
2. **Composition blindness.** German compounds are atomic in this metric; `"Lebensweisheit"`
   and `"Lebensklugheit"` share no tokens despite sharing a morpheme.
3. **Order insensitivity.** Jaccard ignores word order entirely; a translation and its
   reversal receive a perfect score of 1.0.
4. **CJK inapplicability.** Japanese, Chinese, and Korean use no inter-word spaces; the
   "word-set" for a CJK string is its individual characters, making the metric a character
   overlap score rather than a word overlap score.

**LLM-as-a-judge upgrade.** *"The following two translations are for the same source idiom.
On a scale of 0–4, how semantically similar are they? 0 = completely different meaning,
1 = loosely related, 2 = similar theme, 3 = nearly synonymous, 4 = essentially identical
meaning. Answer with just the number."* Averaged over all sentence pairs within a cell, this
replaces word-level Jaccard with semantic similarity, handling inflection, composition,
paraphrase, and non-space-delimited scripts simultaneously.

---

### H18 — Normalised Levenshtein edit distance

**What it does.** In `cognate_comparison_zhko.py`, the character-level Levenshtein distance
between two translations is divided by the length of the longer string to produce a
normalised dissimilarity in [0, 1].

**Limitation.** Character-level edit distance treats every character substitution as equal-
cost regardless of semantic similarity. Substituting `"moon"` for `"sun"` costs 4 edits at
the character level despite being semantically close; substituting `"moon"` for `"star"` also
costs 4 edits despite being somewhat similar. The metric is sensitive to translation length:
short translations have coarser granularity.

**LLM-as-a-judge upgrade.** Subsumed by H17 upgrade; semantic similarity scoring makes
character-level edit distance redundant for the task of comparing cognate translations.

---

### H19 — Codepoint-array near-3 cognate matching

**What it does.** In `cognate_comparison_zhko.py` and `cognate_comparison_extended.py`,
4-character idioms are encoded as integer tuples of Unicode codepoints and compared via
vectorised matrix operations. "Exact" match requires all 4 codepoints to match; "near-3"
match requires exactly 3 of 4 codepoints to match (i.e., exactly one character differs).

**Limitation.** Near-3 is a structural approximation to cognate distance. It treats
character identity as binary (match / no match) and codepoint distance as irrelevant — a
one-codepoint difference between characters that look nearly identical (simplified vs
traditional variant, e.g., 为 vs 為) counts the same as a substitution of a completely
unrelated character. More importantly, semantically equivalent idioms that share meaning but
differ in two or more characters (e.g., 一日千秋 and 一日三秋, where 千 vs 三 is
semantically meaningful) are excluded from the near-3 category but would be real cognates.

**LLM-as-a-judge upgrade.** *"The following two CJK idioms come from different source
languages (e.g., Chinese and Japanese, or Chinese and Korean). Do they share the same
classical Chinese etymological origin and core meaning, even if they differ in one or more
characters? Answer YES (same origin), PARTIAL (related but semantically diverged), or NO
(coincidental similarity), with a one-line reason citing the meaning of each."*

---

## 11.6 Numeric Thresholds and Filters

These heuristics apply hard-coded numeric cutoffs. They appear in multiple scripts and
determine which rows are included in or excluded from aggregations.

### H20 — Pathologically long translation filter (> 500 characters)

**What it does.** In `context_sensitivity.py`, `cross_target_overlap.py`, `difficulty.py`,
and `generate_report.py`, translations longer than 500 characters are set to `NaN` before
analysis. This removes rows where the model appears to have produced a refusal, an
explanation, or a hallucinated continuation rather than a translation.

**Limitation.** The threshold of 500 characters is arbitrary. A legitimate Swahili or German
translation with extensive compounding could plausibly exceed 500 characters. Conversely, a
500-character English output that is mostly the model explaining its reasoning would not be
caught if it is exactly 500 characters. There is no inspection of content — a very long but
genuine translation is discarded alongside model failures.

**LLM-as-a-judge upgrade.** *"The following text is supposed to be a translation of a
Chinese / Japanese / Korean idiom used in a sentence. Does it look like a genuine translation
output, or does it look like a model refusal, an explanation, or a failure to translate?
Answer TRANSLATION or FAILURE with a one-line reason."* This replaces the length threshold
with a content-based quality gate, allowing long but genuine translations to be retained.

---

### H21 — Short translation filter (< 5 or < 10 characters)

**What it does.** `basic_stats.py` flags translations shorter than 5 characters;
`span_audit.py` flags them below 10 characters as potentially degenerate.

**Limitation.** Chinese and Japanese translations can be legitimately very short (a single
character or word). A 3-character Japanese translation of a concise idiom might be perfectly
valid. The language-agnostic threshold conflates script density differences: a 6-character
Japanese translation carries more information than a 6-character English one.

**LLM-as-a-judge upgrade.** Subsumed by H20 upgrade; the FAILURE category handles short
non-translations as well as long ones.

---

### H22 — Expansion ratio outlier filter (99th percentile)

**What it does.** In `translation_length.py`, the top 1% of expansion ratios are removed
before visualisation to prevent the histogram from being dominated by a long tail.

**Limitation.** The 99th percentile cutoff removes the same proportion of data from every
language regardless of that language's tail distribution. Hindi and Bengali, which have
higher median expansion ratios than European languages, have a heavier right tail; the same
percentile removes more substantive data from those languages.

**LLM-as-a-judge upgrade.** Not required for visualisation purposes; this is a display
choice rather than an analytical decision. A more principled alternative is to use per-
language 99th percentiles rather than a corpus-wide one, which requires no LLM.

---

### H23 — Span-to-translation ratio validity filter (≤ 1.0)

**What it does.** In `span_analysis.py`, span/translation character-length ratios greater
than 1.0 are removed on the grounds that a span cannot be longer than the translation
containing it.

**Limitation.** Ratios slightly above 1.0 can occur due to encoding differences between the
span string and the translation string (e.g., a span stored with a smart quote that was
normalised away in the translation). Discarding these without inspection may hide systematic
encoding bugs.

**LLM-as-a-judge upgrade.** For any span with ratio > 1.0, prompt: *"The following span is
annotated as appearing within this translation but appears to be longer than the translation.
Is there an obvious encoding or character difference that would explain this, or does the span
genuinely not appear in the translation? Answer ENCODING ARTEFACT or GENUINE MISMATCH with a
one-line reason."*

---

### H24 — Context sensitivity low-CV threshold (< 0.08)

**What it does.** In `extract_examples.py`, idioms with a cross-sentence coefficient of
variation below 0.08 are selected as examples of "stable" (context-insensitive) translation
behaviour.

**Limitation.** CV < 0.08 means the standard deviation of translation lengths is less than
8% of the mean. This is a proxy for stability: if translations are all the same length, they
are likely the same text. But an idiom could have 10 different-length translations that are
all semantically identical, producing a high CV but no context sensitivity; conversely, all
10 could be the same length but with different word choices.

**LLM-as-a-judge upgrade.** *"The following 10 translations were produced for the same idiom
in 10 different context sentences. Do they appear to be essentially the same translation used
repeatedly, or does the translation genuinely vary with context? Answer STABLE, MODERATE
VARIATION, or CONTEXT-SENSITIVE with a one-line reason."* This measures semantic stability
directly rather than proxying it through length variance.

---

### H25 — Doubled idiom detection (count = 20)

**What it does.** In `generate_report.py`, groups of (source language, idiom, target
language) with exactly 20 sentences are flagged as erroneously duplicated entries (expected:
10).

**Limitation.** The expected count of 10 and the anomalous count of 20 are hard-coded. Any
other count anomaly (e.g., 11 or 15 sentences) would not be detected. The detection also
does not verify whether the two blocks of 10 are independent runs vs duplicated rows.

**LLM-as-a-judge upgrade.** Not applicable; this is a count-based data integrity check that
requires no semantic judgement.

---

## 11.7 Aggregation and Scoring Design Choices

### H26 — Equal-weight composite difficulty score

**What it does.** In `difficulty.py`, four min-max-normalised components — span diversity,
expansion ratio, cross-sentence CV, and cross-target Jaccard inverted — are averaged with
equal weights to produce an idiom-level difficulty score.

**Limitation.** Equal weighting implies that span diversity, translation length volatility,
context sensitivity, and cross-language vocabulary diversity contribute equally to
translation difficulty. There is no empirical basis for this assumption. A principal
component analysis would reveal whether these four metrics actually load on a single
underlying dimension or represent multiple independent difficulty axes.

**LLM-as-a-judge upgrade.** *"How difficult do you expect the following CJK idiom to be to
translate accurately into European and Afro-Asiatic target languages? Rate difficulty on a
scale of 1 (straightforward: meaning is transparent, has common equivalents) to 5 (very hard:
culturally specific, no standard equivalent, requires creative invention). Provide a one-line
reason citing the main source of difficulty (cultural specificity, figurative opacity,
register mismatch, etc.)."* This provides a human-interpretable ground-truth difficulty
rating that can be used to validate whether the composite score is measuring the right thing.

---

### H27 — High/low resource language binary classification

**What it does.** In `crosslingual_consistency.py` and `cross_target_overlap.py`, the 10
target languages are partitioned into high-resource (English, French, German, Spanish,
Italian, Russian) and low-resource (Arabic, Hindi, Bengali, Swahili) based on a hard-coded
membership list.

**Limitation.** "High-resource" and "low-resource" are relative terms that depend on the
task and the metric. Arabic has substantial NLP resources for Modern Standard Arabic but far
fewer for dialectal variants; Russian has excellent resources for Cyrillic text but may have
weaker transliteration tools; Swahili is better-resourced than many African languages but
less so than European ones. The binary split ignores within-group variation and the specific
task (idiom translation) for which resource availability may not follow general NLP rankings.

**LLM-as-a-judge upgrade.** Not a string matching heuristic; this is a categorical
classification. A richer alternative is to treat resource level as a continuous variable
derived from quantitative proxies (e.g., number of Wikipedia articles, size of available
parallel corpora, mBERT representation quality) rather than a binary label.

---

### H28 — Language family classification

**What it does.** In `cross_target_overlap.py`, each target language is assigned to a
language family (Germanic, Romance, Slavic, Semitic, Indo-Aryan, Bantu) and language pairs
are classified as within-family or between-family for the vocabulary overlap analysis.

**Limitation.** The language family assignment uses classical linguistic taxonomy, which may
not predict translation behaviour well. The relevant similarity for this dataset is not
genetic but typological: French and Spanish share word order, case system, and extensive
vocabulary, making within-Romance overlap high; but English and French (Germanic vs Romance)
also share enormous vocabulary through the Norman Conquest, making between-family overlap
potentially as high as within-family for some idiom types.

**LLM-as-a-judge upgrade.** Not a string matching heuristic. A more informative grouping
would use corpus-derived vocabulary overlap between the target languages directly, rather than
linguistic family.

---

### H29 — Idiom length bucketing (3, 4, 5, 6, 7+)

**What it does.** In `idiom_morphology.py`, idioms are bucketed by character count into five
groups (≤3, 4, 5, 6, 7+). Character count is computed by Python `len()`.

**Limitation.** Character count conflates length in distinct ways across the three source
scripts. A 4-character Japanese idiom (yojijukugo) is a tightly lexicalised classical form
with a specific cultural role; a 4-character Korean idiom may or may not be a chengyu-derived
form; a 6-character Chinese idiom may be a compound proverb rather than a fixed phrase. The
same bucket contains idioms with very different structural and cultural properties.

**LLM-as-a-judge upgrade.** *"How would you classify the following CJK idiom by form: (a)
4-character classical compound (chengyu/yojijukugo/사자성어), (b) proverb or saying (with
verb phrase), (c) compound noun or fixed collocation, (d) loan phrase or loanword, (e) other?
Answer with (a)–(e) and a one-line reason."* This produces a linguistically meaningful
categorisation independent of surface character count.

---

## 11.8 Summary Table

The table below consolidates all 29 heuristics identified above, their primary scripts, the
class of limitation they share, and whether an LLM-as-a-judge upgrade is available.

| ID | Heuristic | Primary script(s) | Limitation class | LaJ available? |
|---|---|---|---|---|
| H1 | Exact substring match | span_errors.py, span_audit.py | Encoding sensitivity | Yes — semantic containment judge |
| H2 | Whitespace-stripped match | span_errors.py | Subsumed by H1 | Subsumed by H1 |
| H3 | Case-insensitive match | span_errors.py | Subsumed by H1 | Subsumed by H1 |
| H4 | Punctuation-stripped match | span_errors.py | Unicode category imprecision | Subsumed by H1 |
| H5 | Off-by-one boundary match | span_errors.py | One-edit only | Subsumed by H1 |
| H6 | Word-overlap check | span_errors.py | Space-tokenisation, no morphology | Yes — morpheme overlap judge |
| H7 | Span position zone binning | span_position.py | Arbitrary 1/3–2/3 boundary | Yes — syntactic position judge |
| H8 | NFC + punctuation stripping | reverse_span_analysis.py | NFKC gap, incomplete strip list | Yes — semantic equivalence judge |
| H9 | OpenCC s2t conversion | cognate_comparison_extended.py | Character ambiguity | Yes — etymological cognate judge |
| H10 | kHangul lookup + hanja fallback | cognate_comparison_extended.py | First-reading only | Yes — Sino-Korean cognate judge |
| H11 | CJK Unicode range check | unmatched_chinese.py, difficulty.py | Missing Extension B–H blocks | Yes — script classification judge |
| H12 | 4-character length filter | japanese_yojijukugo.py, cognate scripts | Surrogate pairs, non-4-char forms | Yes — yojijukugo/chengyu judge |
| H13 | Hangul syllable range check | cognate_comparison_extended.py | Misses decomposed Jamo | Subsumed by H10 |
| H14 | Japanese column name detection | complementary_idiom_types.py | Unpredictable column names | Yes — content-sampling classifier |
| H15 | Yojijukugo tag substring | japanese_yojijukugo.py | Incomplete Wiktionary tags | Yes — yojijukugo identification judge |
| H16 | 8-template regex classifier | analogy_deep_analysis.py | English-only, first-match, lexical brittleness | Yes — highest-value upgrade; multi-class + open-set judge |
| H17 | Word-set Jaccard similarity | context_sensitivity.py, cross_target_overlap.py, difficulty.py | Inflection / composition / CJK blindness | Yes — semantic similarity scorer (0–4) |
| H18 | Normalised Levenshtein distance | cognate_comparison_zhko.py | Character ≠ semantic distance | Subsumed by H17 |
| H19 | Codepoint near-3 cognate matching | cognate scripts | Binary match, misses 2-char cognates | Yes — etymological origin judge |
| H20 | Long translation filter (> 500 chars) | context_sensitivity.py, cross_target_overlap.py, difficulty.py, generate_report.py | Arbitrary threshold, discards long genuine translations | Yes — TRANSLATION vs FAILURE judge |
| H21 | Short translation filter (< 5–10 chars) | basic_stats.py, span_audit.py | Script-density blindness | Subsumed by H20 |
| H22 | 99th percentile expansion outlier | translation_length.py | Same percentile across languages | No (display choice only) |
| H23 | Span ratio > 1.0 filter | span_analysis.py | Encoding artefacts disguised as errors | Yes — encoding artefact vs mismatch judge |
| H24 | Low-CV stability threshold (< 0.08) | extract_examples.py | Length CV ≠ semantic stability | Yes — semantic stability judge |
| H25 | Doubled idiom count (= 20) | generate_report.py | Other count anomalies undetected | No (count check only) |
| H26 | Equal-weight difficulty score | difficulty.py | Unvalidated equal weighting | Yes — intrinsic difficulty rating judge |
| H27 | High/low resource binary split | crosslingual_consistency.py, cross_target_overlap.py | Binary over-simplification | No (continuous proxies preferred) |
| H28 | Language family classification | cross_target_overlap.py | Genetic ≠ typological similarity | No (corpus overlap preferred) |
| H29 | Idiom length buckets (≤3, 4, 5, 6, 7+) | idiom_morphology.py | Character count ≠ idiom type | Yes — idiom form classifier |

The heuristics in the highest-risk tier for analytical validity are **H16** (template
classification), **H17** (Jaccard-based semantic similarity), **H19** (cognate matching),
**H20** (translation quality filtering), and **H26** (difficulty scoring). These five
heuristics directly determine which findings are reported as the core results in Parts 3, 5,
6, 9, and 10. An LLM-as-a-judge pass over a random 10% sample for each of these five would
provide a calibration check sufficient to establish confidence intervals around the headline
numbers without re-running the full pipeline.
