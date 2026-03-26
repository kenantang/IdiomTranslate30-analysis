"""
utils.py — Shared heuristic filters for IdiomTranslate30 analysis scripts.

Every function here corresponds to a named heuristic (H1–H29) catalogued in
docs/analysis/part11_heuristics.md.  The docstring of each function states:

  • What the heuristic does and why it exists.
  • Known limitations of the heuristic approach.
  • LLM-as-a-judge (LaJ) upgrade: the exact judge prompt that could replace or
    validate this heuristic, and what the judge's output should be.
"""

from __future__ import annotations

import re
import unicodedata
from itertools import combinations
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

# ── Shared constants ───────────────────────────────────────────────────────────

LONG_THRESH: int = 500   # H20: pathologically long translation threshold (chars)
SHORT_THRESH_STRICT: int = 5   # H21: strict short-translation flag (basic_stats)
SHORT_THRESH_AUDIT: int = 10   # H21: audit short-translation flag (span_audit)
STABILITY_CV_THRESH: float = 0.08   # H24: low-CV threshold for stable translations
OUTLIER_PERCENTILE: float = 0.99   # H22: percentile cap for visualisation outliers

# ── Canonical colour palette ───────────────────────────────────────────────
# All scripts should import from here instead of defining inline hex strings.
COLOR_BLUE   : str = "#4C72B0"   # Creatively / Chinese  / High-resource / Exact-match
COLOR_ORANGE : str = "#DD8452"   # Analogy    / Japanese / Low-resource  / Near-match
COLOR_GREEN  : str = "#55A868"   # Author     / Korean
COLOR_RED    : str = "#C44E52"   # English accent / Unmatched / Error
COLOR_PURPLE : str = "#8172B2"   # Span zone – middle
COLOR_GREY   : str = "#AEB6BF"   # Neutral / secondary

STRATEGY_COLORS : list = [COLOR_BLUE, COLOR_ORANGE, COLOR_GREEN]
SOURCE_COLORS   : dict = {"Chinese": COLOR_BLUE, "Japanese": COLOR_ORANGE, "Korean": COLOR_GREEN}
RESOURCE_COLORS : dict = {"high": COLOR_BLUE, "low": COLOR_ORANGE}
COGNATE_COLORS  : dict = {"exact_4/4": COLOR_BLUE, "near_3/4": COLOR_ORANGE}
MATCH_COLORS    : dict = {"matched": COLOR_BLUE, "unmatched": COLOR_RED}


# ══════════════════════════════════════════════════════════════════════════════
# H1–H6  Span containment and classification
# ══════════════════════════════════════════════════════════════════════════════

def classify_span_match(span: str, translation: str) -> str:
    """
    Classify how (or whether) *span* is contained in *translation*.

    Returns one of:
        "ok"                      — exact substring (H1)
        "leading/trailing whitespace" — matches after strip() (H2)
        "case mismatch"           — matches case-insensitively (H3)
        "punctuation difference"  — matches after stripping Unicode P-category chars (H4)
        "off-by-one boundary"     — span[1:] or span[:-1] is in translation (H5)
        "partial word overlap"    — at least one word token in common (H6)
        "no overlap"              — none of the above

    Limitations
    -----------
    Each test is a cascading fallback; later tests are only reached when earlier
    ones fail.  The order (whitespace → case → punct → boundary → word) is
    arbitrary and may mis-classify some errors.  Space-based word tokenisation
    (H6) is uninformative for CJK scripts.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "Does the following span appear verbatim or near-verbatim in the
        translation?  Answer YES, NEAR (describe the difference), or NO."
    Use YES / NEAR as equivalent to "ok" and collapse H2–H5 into a single
    NEAR judgement with a free-text reason.  This eliminates the need for the
    cascade and handles encoding, script, and paraphrase differences uniformly.
    """
    if pd.isna(span) or pd.isna(translation):
        return "missing"
    span, translation = str(span), str(translation)

    # H1 — exact
    if span in translation:
        return "ok"

    # H2 — whitespace
    if span.strip() in translation:
        return "leading/trailing whitespace"

    # H3 — case
    if span.lower() in translation.lower():
        return "case mismatch"

    # H4 — punctuation stripped
    def _strip_punct(s: str) -> str:
        return "".join(c for c in s if not unicodedata.category(c).startswith("P"))

    if _strip_punct(span) in _strip_punct(translation):
        return "punctuation difference"

    # H5 — off-by-one boundary
    if len(span) > 2 and (span[1:] in translation or span[:-1] in translation):
        return "off-by-one boundary"

    # H6 — word overlap
    span_words = set(span.lower().split())
    trans_words = set(translation.lower().split())
    if span_words & trans_words:
        return "partial word overlap"

    return "no overlap"


def span_is_contained(span: str, translation: str) -> bool:
    """
    Return True if *span* is an exact substring of *translation* (H1).

    This is the primary span-validity check used in span_audit.py.

    Limitations
    -----------
    Case-sensitive and byte-exact.  A span with a trailing space or different
    Unicode normalisation form will return False even if visually identical.

    LLM-as-a-judge upgrade
    ----------------------
    Subsumed by classify_span_match(): use the LaJ prompt there and treat
    YES / NEAR as True.
    """
    if pd.isna(span) or pd.isna(translation):
        return False
    return str(span) in str(translation)


# ══════════════════════════════════════════════════════════════════════════════
# H7  Span position zone binning
# ══════════════════════════════════════════════════════════════════════════════

def span_position_zone(rel_start: float) -> str:
    """
    Map a relative span start position in [0, 1] to a named zone.

    Returns "beginning" (< 1/3), "middle" (1/3 – 2/3), or "end" (> 2/3).
    Returns "unknown" for NaN input.

    Parameters
    ----------
    rel_start : float
        len(span_prefix) / (len(translation) - len(span)), clamped to [0, 1].

    Limitations
    -----------
    Bin boundaries at 1/3 and 2/3 are arbitrary.  There is no linguistic
    motivation; a span at 0.32 and one at 0.36 fall into different zones.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "In the following sentence the idiom translation appears at the marked
        position.  Is it in: (a) a topic or fronted position, (b) the main
        predicate, (c) a clause-final or parenthetical position, or (d) elsewhere?
        Answer (a)–(d) with a one-line reason."
    This gives syntactically grounded zones independent of character offsets.
    """
    if pd.isna(rel_start):
        return "unknown"
    if rel_start < 1 / 3:
        return "beginning"
    if rel_start <= 2 / 3:
        return "middle"
    return "end"


def compute_relative_start(span: str, translation: str) -> float:
    """
    Return the relative start position of *span* within *translation*.

    Defined as start_offset / (len(translation) - len(span)).
    Returns NaN if span is not found or occupies the entire translation.
    """
    if pd.isna(span) or pd.isna(translation):
        return float("nan")
    span, translation = str(span), str(translation)
    start = translation.find(span)
    if start == -1:
        return float("nan")
    denom = len(translation) - len(span)
    return start / denom if denom > 0 else 0.0


# ══════════════════════════════════════════════════════════════════════════════
# H8  Text normalisation for span deduplication
# ══════════════════════════════════════════════════════════════════════════════

_STRIP_PUNCT_CHARS = ".,!?;:'\""


def normalize_span(span: str) -> str:
    """
    Normalise a span string for use as an aggregation key (H8).

    Steps:
        1. Strip leading/trailing whitespace.
        2. Apply Unicode NFC normalisation.
        3. Lowercase.
        4. Strip a fixed set of boundary punctuation characters.

    Limitations
    -----------
    NFC does not handle compatibility equivalences (e.g. full-width Latin
    letters used in Japanese contexts).  NFKC would cover these but risks
    over-normalising Arabic ligatures and some Indic conjuncts.  The
    punctuation strip list is hard-coded to ASCII punctuation only.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "Are these two translation spans semantically equivalent renderings of
        the same source idiom, or are they meaningfully different?
        Answer SAME or DIFFERENT with a one-line reason."
    This replaces character-level normalisation with semantic equivalence,
    collapsing typographic variants and minor paraphrase in one pass.
    """
    if pd.isna(span):
        return ""
    s = str(span).strip()
    s = unicodedata.normalize("NFC", s)
    s = s.lower()
    s = s.strip(_STRIP_PUNCT_CHARS)
    return s


# ══════════════════════════════════════════════════════════════════════════════
# H9  OpenCC simplified-to-traditional conversion
# ══════════════════════════════════════════════════════════════════════════════

def build_s2t_converter():
    """
    Build and return an OpenCC simplified-to-traditional converter (H9).

    Returns None if opencc is not installed.

    Limitations
    -----------
    OpenCC s2t is a heuristic character-by-character substitution that does
    not resolve ambiguous simplified characters (e.g. 发 → 發 vs 髮).

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following simplified Chinese idiom and traditional Chinese / Japanese
        idiom look similar.  Are they the same idiom (same meaning and origin),
        cognates (related but diverged), or coincidentally similar?
        Answer SAME, COGNATE, or COINCIDENTAL with a one-line reason."
    This handles the ambiguity that character-level normalisation cannot.
    """
    try:
        import opencc
        return opencc.OpenCC("s2t")
    except ImportError:
        return None


def simplified_to_traditional(text: str, converter=None) -> str:
    """
    Convert a simplified Chinese string to traditional using OpenCC (H9).

    If *converter* is None, a fresh one is built (slow for bulk use — pass a
    pre-built converter instead).  Returns *text* unchanged if opencc is not
    available.
    """
    if converter is None:
        converter = build_s2t_converter()
    if converter is None:
        return text
    return converter.convert(text)


# ══════════════════════════════════════════════════════════════════════════════
# H10  kHangul Unihan lookup with hanja fallback
# ══════════════════════════════════════════════════════════════════════════════

def build_kHangul_map(unihan_readings_path: Path) -> Dict[str, str]:
    """
    Parse Unihan_Readings.txt and return a dict mapping CJK char → first
    kHangul reading (H10, layer 1).

    Limitations
    -----------
    Many CJK characters have multiple Korean readings depending on context.
    This function always takes the first listed reading without considering
    which is appropriate for the given idiom.

    LLM-as-a-judge upgrade
    ----------------------
    See char_to_hangul() below.
    """
    kh_map: Dict[str, str] = {}
    for line in unihan_readings_path.read_text(encoding="utf-8").splitlines():
        if "\tkHangul\t" not in line:
            continue
        parts = line.split("\t")
        ch = chr(int(parts[0][2:], 16))
        first = parts[2].split()[0].split(":")[0]
        kh_map[ch] = first
    return kh_map


def char_to_hangul(
    ch: str,
    kh_map: Dict[str, str],
    s2t_converter=None,
) -> Optional[str]:
    """
    Map a single CJK character to its Sino-Korean Hangul reading using a
    three-layer fallback (H10):

        Layer 1 — Direct Unihan kHangul lookup.
        Layer 2 — Convert simplified → traditional (OpenCC), then kHangul.
        Layer 3 — hanja library substitution mode.

    Returns None if all layers fail.

    Limitations
    -----------
    The first-reading-only rule in Layer 1 produces incorrect forms for idioms
    where a character's secondary reading applies.  Layer 3 uses a "substitution"
    mode that may return the wrong syllable for ambiguous characters.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following Chinese idiom is compared with the following Korean idiom.
        Do they share the same classical Chinese etymological origin and core
        meaning, even if they differ in one or more characters?
        Answer YES (same origin), PARTIAL (related but semantically diverged),
        or NO (coincidental similarity), with a one-line reason."
    This makes the cognate decision at the idiom level, bypassing per-character
    transliteration entirely.
    """
    # Layer 1
    if ch in kh_map:
        return kh_map[ch]
    # Layer 2
    trad = simplified_to_traditional(ch, s2t_converter)
    if trad != ch and trad in kh_map:
        return kh_map[trad]
    # Layer 3
    try:
        import hanja as hanja_lib
        result = hanja_lib.translate(ch, "substitution")
        if result and len(result) == 1 and is_hangul_syllable(result):
            return result
    except Exception:
        pass
    return None


def idiom_to_hangul_tuple(
    idiom: str,
    kh_map: Dict[str, str],
    s2t_converter=None,
) -> Tuple[Optional[str], ...]:
    """
    Translate a 4-character CJK idiom to a tuple of Hangul syllables (H10).

    Entries are None where transliteration failed.  Callers should skip idioms
    with any None entry for exact/near-3 cognate matching.
    """
    return tuple(char_to_hangul(c, kh_map, s2t_converter) for c in idiom)


# ══════════════════════════════════════════════════════════════════════════════
# H11  CJK / Hangul / Latin character classification
# ══════════════════════════════════════════════════════════════════════════════

def is_cjk_char(c: str) -> bool:
    """
    Return True if *c* is a CJK unified ideograph (H11).

    Checks Unicode name for "CJK" as primary test; falls back to the two most
    common codepoint ranges (U+4E00–U+9FFF and U+3400–U+4DBF).

    Limitations
    -----------
    Only the two most common CJK blocks are checked in the fallback.  Extension
    blocks B–H and the Compatibility Ideographs block are missed, affecting
    roughly < 0.1 % of classical idiom characters.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "What writing system does the following character belong to: Simplified
        Chinese, Traditional Chinese, Japanese Kanji, Korean Hanja, or mixed?
        Answer with the most specific label."
    This provides a semantically meaningful label rather than a codepoint answer.
    """
    name = unicodedata.name(c, "")
    if "CJK" in name:
        return True
    cp = ord(c)
    return 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF


def is_cjk_string(text: str) -> bool:
    """Return True if every character in *text* is a CJK ideograph (H11)."""
    return bool(text) and all(is_cjk_char(c) for c in text)


def is_hangul_syllable(c: str) -> bool:
    """
    Return True if *c* is a precomposed Hangul syllable (U+AC00–U+D7A3) (H13).

    Limitations
    -----------
    Does not cover Hangul Jamo (U+1100–U+11FF) used for Old Korean, or Hangul
    Compatibility Jamo (U+3130–U+318F).

    LLM-as-a-judge upgrade
    ----------------------
    Subsumed by the char_to_hangul() LaJ upgrade.
    """
    return "\uAC00" <= c <= "\uD7A3"


def is_latin_char(c: str) -> bool:
    """
    Return True if *c* is a basic ASCII Latin letter (U+0041–U+007A) (H11).

    Limitations
    -----------
    Does not include extended Latin characters with diacritics or accents.
    """
    return "\u0041" <= c <= "\u007A"


def char_script_type(c: str) -> str:
    """
    Classify a single character as "CJK", "Hangul", "Latin", or "other" (H11).

    Used in unmatched_chinese.py for character-level script profiling.
    """
    if is_cjk_char(c):
        return "CJK"
    if is_hangul_syllable(c):
        return "Hangul"
    if is_latin_char(c):
        return "Latin"
    return "other"


# ══════════════════════════════════════════════════════════════════════════════
# H12  4-character CJK idiom filter
# ══════════════════════════════════════════════════════════════════════════════

def is_4char_cjk_idiom(text: str) -> bool:
    """
    Return True if *text* is exactly 4 CJK characters (H12).

    Used to select chengyu / yojijukugo / 사자성어 from a larger vocabulary.

    Limitations
    -----------
    Uses Python len(), which counts Unicode code points rather than grapheme
    clusters.  Characters stored as surrogate pairs (e.g. some CJK Extension B
    codepoints) will be counted as 2, causing a 4-character idiom to be
    rejected.  Also excludes legitimate 3- and 6-character classical forms.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "Is the following Japanese / Chinese / Korean expression conventionally
        classified as a yojijukugo or chengyu — a fixed four-character compound
        with a culturally established meaning?  If it is a related multi-character
        fixed expression that would conventionally be treated similarly, also say
        YES.  Answer YES or NO with a one-line reason."
    This replaces the hard length filter with a conventionality judgement.
    """
    return len(text) == 4 and is_cjk_string(text)


# ══════════════════════════════════════════════════════════════════════════════
# H14  Japanese column auto-detection
# ══════════════════════════════════════════════════════════════════════════════

_JP_COLUMN_HINTS = {"word", "phrase", "kotowaza", "jp"}


def detect_japanese_column(df: pd.DataFrame) -> Optional[str]:
    """
    Heuristically identify which column of *df* contains Japanese idiom text (H14).

    Priority:
        1. Column whose name contains "japanese" or "kanji" (case-insensitive).
        2. Column whose name is one of a fixed hint set.
        3. First object-dtype column as a last resort.

    Returns the column name, or None if the DataFrame is empty.

    Limitations
    -----------
    Relies entirely on column names without inspecting cell contents.  A dataset
    that stores Japanese text in a column named "headword" or "expression" will
    fall through to the first object-dtype fallback, which may be wrong.

    LLM-as-a-judge upgrade
    ----------------------
    For each candidate column, sample 5 values and prompt:
        "The following 5 cell values are from a column named '{col}'.  Is this
        column likely to contain Japanese idiom text (kanji / kana expressions),
        or some other content?  Answer IDIOMS or OTHER."
    Select the column answered IDIOMS with highest confidence.
    """
    for col in df.columns:
        name_lower = col.lower()
        if "japanese" in name_lower or "kanji" in name_lower:
            return col
        if col in _JP_COLUMN_HINTS:
            return col
    for col in df.columns:
        if df[col].dtype == object:
            return col
    return None


# ══════════════════════════════════════════════════════════════════════════════
# H15  Yojijukugo tag detection
# ══════════════════════════════════════════════════════════════════════════════

def is_yojijukugo_tagged(entry: dict) -> bool:
    """
    Return True if a Wiktionary/Kaikki entry is tagged as yojijukugo (H15).

    Checks for 四字熟語 or "yojijukugo" in top-level categories/tags and in
    per-sense tags/categories.  Also accepts "idiom" in sense-level tags.

    Limitations
    -----------
    Wiktionary tagging is community-maintained and inconsistent.  Many genuine
    yojijukugo are tagged only as "idiom" or "proverb" without the specific
    yojijukugo tag, reducing recall.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "Is the following Japanese expression conventionally classified as a
        yojijukugo (四字熟語)?  Answer YES, BORDERLINE (explain), or NO."
    Apply to any 4-character entry not already tagged, to recover missed entries.
    """
    tags_flat = str(entry.get("categories", "")) + str(entry.get("tags", ""))
    senses = entry.get("senses", [])
    sense_tags = " ".join(
        str(s.get("tags", "")) + str(s.get("categories", "")) for s in senses
    )
    return (
        "四字熟語" in tags_flat
        or "四字熟語" in sense_tags
        or "yojijukugo" in tags_flat.lower()
        or "idiom" in sense_tags.lower()
    )


# ══════════════════════════════════════════════════════════════════════════════
# H16  Analogy template classification
# ══════════════════════════════════════════════════════════════════════════════

ANALOGY_TEMPLATES: Dict[str, str] = {
    "weaving_thread_tapestry": r"weav|tapestry|unravel|single.*cable|loom|stitch|woven",
    "cosmic_star_galaxy":      r"\bstar\b|\bgalaxy\b|\bcosmic\b|\bconstellation\b|\bnorth star\b|\bcelestial\b",
    "kaleidoscope":            r"kaleidoscope",
    "trying_to_futility":      r"^trying to ",
    "dandelion_scattered":     r"dandelion|scattered.*gale|gale.*scatter",
    "labyrinth_mirror":        r"labyrinth|hall of mirror|forest of mirror",
    "clockmaker_precision":    r"clockmaker|watchmaker|precision of a master",
    "mist_smoke_castle":       r"castle.*(?:mist|smoke|fog)|palace.*(?:mist|smoke|fog)|built of.*(?:mist|smoke)|carved.*(?:mist|smoke)",
}

# Pre-compile for performance
_COMPILED_TEMPLATES = {
    name: re.compile(pattern, re.IGNORECASE)
    for name, pattern in ANALOGY_TEMPLATES.items()
}


def classify_analogy_template(span: str) -> str:
    """
    Classify an English Analogy-strategy span into one of 8 named slop templates
    or "original" if none match (H16).

    Matching is first-match: a span matching multiple patterns is assigned only
    to the first matching template in ANALOGY_TEMPLATES insertion order.

    Limitations
    -----------
    - Templates were derived from English outputs only; non-English slop patterns
      are not captured.
    - First-match order creates ambiguity for spans that match multiple templates.
    - Single-word patterns (e.g. "kaleidoscope") will miss inflected forms.
    - The "trying_to_futility" pattern requires the phrase at the start of the span.
    - Cannot distinguish authentic use of a metaphor from cliché.

    LLM-as-a-judge upgrade  (highest-value upgrade in the pipeline)
    ----------------------
    Prompt:
        "The following span is an Analogy-strategy translation of a CJK idiom.
        Classify it as one of:
          (a) Weaving / thread / tapestry image
          (b) Cosmic / star / galaxy / north-star image
          (c) Kaleidoscope image
          (d) Futility frame ('trying to X')
          (e) Dandelion / scattered-seeds image
          (f) Labyrinth / hall-of-mirrors image
          (g) Clockmaker / watchmaker precision image
          (h) Insubstantial castle / castle-of-mist image
          (i) Another recurring LLM cliché — name it
          (j) Culturally grounded or original image
        Answer with the letter and a one-line justification."
    Category (i) surfaces new templates that the regex approach misses entirely.
    """
    for name, pattern in _COMPILED_TEMPLATES.items():
        if pattern.search(span):
            return name
    return "original"


# ══════════════════════════════════════════════════════════════════════════════
# H17  Word-set Jaccard similarity
# ══════════════════════════════════════════════════════════════════════════════

def word_jaccard(text_a: str, text_b: str) -> float:
    """
    Compute word-set Jaccard similarity between two strings (H17).

    Tokenises by splitting on whitespace after lowercasing.  Returns 0.0 if
    both sets are empty.

    Limitations
    -----------
    - Inflection-blind: "runs" and "running" are different tokens.
    - Composition-blind: German compounds share no tokens with their components.
    - Order-insensitive: a translation and its reversal score 1.0.
    - CJK inapplicable: no inter-word spaces, so each character becomes a token.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following two translations are for the same source idiom.  On a
        scale of 0–4, how semantically similar are they?
        0 = completely different, 1 = loosely related, 2 = similar theme,
        3 = nearly synonymous, 4 = essentially identical meaning.
        Answer with just the number."
    Averaged over all pairs, this replaces Jaccard with semantic similarity and
    handles inflection, composition, paraphrase, and CJK simultaneously.
    """
    a_words = set(str(text_a).lower().split())
    b_words = set(str(text_b).lower().split())
    union = a_words | b_words
    return len(a_words & b_words) / len(union) if union else 0.0


def mean_pairwise_jaccard(texts: Sequence) -> float:
    """
    Compute the mean Jaccard similarity over all C(n,2) pairs in *texts* (H17).

    Non-null values are used; returns NaN if fewer than 2 valid texts are given.

    Limitations
    -----------
    Same as word_jaccard().  High mean Jaccard can indicate either genuine
    consistency or surface-level repetition of the same phrase.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following N translations were produced for the same idiom across
        different context sentences.  Do they appear to be essentially the same
        translation used repeatedly, or does the translation genuinely vary with
        context?  Answer STABLE, MODERATE VARIATION, or CONTEXT-SENSITIVE with a
        one-line reason."
    This measures semantic stability directly, not via length or lexical overlap.
    """
    valid = [str(t) for t in texts if pd.notna(t)]
    if len(valid) < 2:
        return float("nan")
    scores = [word_jaccard(a, b) for a, b in combinations(valid, 2)]
    return float(np.mean(scores))


# ══════════════════════════════════════════════════════════════════════════════
# H18  Normalised Levenshtein edit distance
# ══════════════════════════════════════════════════════════════════════════════

def normalized_levenshtein(a: str, b: str) -> float:
    """
    Compute normalised character-level Levenshtein distance between *a* and *b*
    (H18), divided by max(len(a), len(b)).

    Returns 0.0 if both strings are empty.  Requires the *rapidfuzz* package.

    Limitations
    -----------
    Character-level edit distance treats every substitution as equal-cost
    regardless of semantic distance.  The metric is coarser for short strings.

    LLM-as-a-judge upgrade
    ----------------------
    Subsumed by the word_jaccard() LaJ upgrade; semantic similarity scoring
    makes character-level edit distance redundant for cognate translation
    comparison.
    """
    from rapidfuzz.distance import Levenshtein
    max_len = max(len(a), len(b))
    return Levenshtein.distance(a, b) / max_len if max_len else 0.0


# ══════════════════════════════════════════════════════════════════════════════
# H20  Pathologically long translation filter
# ══════════════════════════════════════════════════════════════════════════════

def filter_long_translations(
    df: pd.DataFrame,
    cols: Sequence[str],
    threshold: int = LONG_THRESH,
) -> pd.DataFrame:
    """
    Set translation cells longer than *threshold* characters to NaN (H20).

    This removes model generation failures (token repetition loops, runaway
    generation, meta-response leaks) before length-sensitive analyses.

    Parameters
    ----------
    df        : DataFrame to modify (a copy is returned).
    cols      : Translation column names to filter.
    threshold : Maximum allowed character length (default 500).

    Limitations
    -----------
    The threshold is arbitrary.  A legitimate verbose translation in an
    agglutinative language could exceed 500 characters.  No content inspection
    is performed: a long but genuine translation is discarded.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following text is supposed to be a translation of a CJK idiom used
        in a sentence.  Does it look like a genuine translation, or a model
        refusal, explanation, or failure to translate?
        Answer TRANSLATION or FAILURE with a one-line reason."
    This replaces the length threshold with a content-based quality gate,
    allowing long genuine translations to be retained.
    """
    df = df.copy()
    for col in cols:
        mask = df[col].str.len() > threshold
        df.loc[mask, col] = np.nan
    return df


def is_pathologically_long(text: str, threshold: int = LONG_THRESH) -> bool:
    """Return True if *text* exceeds *threshold* characters (H20)."""
    return pd.notna(text) and len(str(text)) > threshold


# ══════════════════════════════════════════════════════════════════════════════
# H21  Pathologically short translation filter
# ══════════════════════════════════════════════════════════════════════════════

def is_pathologically_short(text: str, threshold: int = SHORT_THRESH_STRICT) -> bool:
    """
    Return True if *text* is shorter than *threshold* characters (H21).

    Thresholds used in the pipeline:
        5  chars — basic_stats.py (strict flag)
        10 chars — span_audit.py (audit flag)

    Limitations
    -----------
    Character count is language-agnostic.  A 3-character Japanese translation
    may be perfectly valid (CJK characters are semantically dense).  The same
    threshold applied to English and Japanese conflates script density differences.

    LLM-as-a-judge upgrade
    ----------------------
    Subsumed by the is_pathologically_long() LaJ upgrade; the FAILURE category
    covers both very long and very short non-translations.
    """
    if pd.isna(text):
        return False
    return len(str(text)) < threshold


# ══════════════════════════════════════════════════════════════════════════════
# H22  Percentile-based outlier filter for visualisation
# ══════════════════════════════════════════════════════════════════════════════

def filter_percentile_outliers(
    series: pd.Series,
    q: float = OUTLIER_PERCENTILE,
) -> pd.Series:
    """
    Return *series* with values above the *q*-th percentile removed (H22).

    Used to prevent extreme outliers from dominating visualisation axes.

    Parameters
    ----------
    series : Numeric pandas Series.
    q      : Upper quantile cutoff (default 0.99).

    Limitations
    -----------
    A corpus-wide percentile removes the same proportion from every subgroup.
    Languages with heavier right tails (e.g. Hindi, Bengali) lose more
    substantive data than others at the same percentile.

    LLM-as-a-judge upgrade
    ----------------------
    Not applicable — this is a display choice rather than an analytical
    decision.  A more principled alternative is to compute per-subgroup
    percentiles, which requires no LLM.
    """
    cutoff = series.quantile(q)
    return series[series < cutoff]


# ══════════════════════════════════════════════════════════════════════════════
# H23  Span-to-translation ratio validity filter
# ══════════════════════════════════════════════════════════════════════════════

def is_valid_span_ratio(span: str, translation: str) -> bool:
    """
    Return True if len(span) / len(translation) ≤ 1.0 (H23).

    A span cannot be longer than the translation containing it, so ratios
    above 1.0 indicate annotation errors or encoding mismatches.

    Limitations
    -----------
    Ratios slightly above 1.0 can arise from encoding differences between the
    span and translation strings (e.g. smart quotes normalised away in the
    translation).  These are discarded without content inspection.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following span is annotated as appearing within this translation but
        appears longer than the translation.  Is there an obvious encoding or
        character difference that explains this, or does the span genuinely not
        appear in the translation?
        Answer ENCODING ARTEFACT or GENUINE MISMATCH with a one-line reason."
    """
    if pd.isna(span) or pd.isna(translation):
        return False
    tl = len(str(translation))
    return tl > 0 and len(str(span)) / tl <= 1.0


# ══════════════════════════════════════════════════════════════════════════════
# H24  Low-CV stability threshold
# ══════════════════════════════════════════════════════════════════════════════

def is_stable_translation_group(
    cv: float,
    threshold: float = STABILITY_CV_THRESH,
) -> bool:
    """
    Return True if a group's coefficient of variation is below *threshold* (H24).

    Used in extract_examples.py to select idioms whose translations are stable
    across context sentences (low context-sensitivity).

    Parameters
    ----------
    cv        : Coefficient of variation of translation lengths across sentences.
    threshold : Upper CV bound for "stable" (default 0.08).

    Limitations
    -----------
    Length CV is a proxy for semantic stability.  Ten translations of equal
    length but with different word choices would be classified as stable.
    Conversely, identical translations with one longer variant would be flagged
    as unstable.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "The following N translations were produced for the same idiom in N
        different context sentences.  Are they essentially the same translation
        used repeatedly, or does the translation genuinely vary with context?
        Answer STABLE, MODERATE VARIATION, or CONTEXT-SENSITIVE with a one-line
        reason."
    This measures semantic stability directly rather than via length variance.
    """
    return pd.notna(cv) and cv < threshold


# ══════════════════════════════════════════════════════════════════════════════
# H27  High / low resource language classification
# ══════════════════════════════════════════════════════════════════════════════

RESOURCE_LEVEL: Dict[str, str] = {
    "English": "high",
    "French":  "high",
    "German":  "high",
    "Spanish": "high",
    "Italian": "high",
    "Russian": "high",
    "Arabic":  "low",
    "Bengali": "low",
    "Hindi":   "low",
    "Swahili": "low",
}

HIGH_RESOURCE_LANGS = frozenset(l for l, r in RESOURCE_LEVEL.items() if r == "high")
LOW_RESOURCE_LANGS  = frozenset(l for l, r in RESOURCE_LEVEL.items() if r == "low")


def resource_level(language: str) -> str:
    """
    Classify a target language as "high" or "low" resource (H27).

    Returns "unknown" for languages not in the mapping.

    Limitations
    -----------
    The binary split is hard-coded and ignores within-group variation.  Arabic
    has substantial resources for Modern Standard Arabic but far fewer for
    dialectal variants.  The classification is not task-specific.

    LLM-as-a-judge upgrade
    ----------------------
    Not a string-matching heuristic.  A more principled alternative is to treat
    resource level as a continuous variable derived from quantitative proxies
    (e.g. number of Wikipedia articles, size of parallel corpora) rather than
    a binary label.
    """
    return RESOURCE_LEVEL.get(language, "unknown")


# ══════════════════════════════════════════════════════════════════════════════
# H28  Language family classification
# ══════════════════════════════════════════════════════════════════════════════

LANGUAGE_FAMILIES: Dict[str, str] = {
    "English": "Germanic",
    "German":  "Germanic",
    "French":  "Romance",
    "Spanish": "Romance",
    "Italian": "Romance",
    "Russian": "Slavic",
    "Arabic":  "Semitic",
    "Bengali": "South Asian",
    "Hindi":   "South Asian",
    "Swahili": "Bantu",
}


def language_family(language: str) -> str:
    """
    Return the classical linguistic family of a target language (H28).

    Returns "unknown" for languages not in the mapping.

    Limitations
    -----------
    Classical genetic taxonomy may not predict translation behaviour.  English
    and French share extensive vocabulary (Norman Conquest) despite being in
    different families, making within-family overlap potentially misleading.

    LLM-as-a-judge upgrade
    ----------------------
    Not a string-matching heuristic.  A more informative grouping would use
    corpus-derived vocabulary overlap between target languages directly, rather
    than linguistic family membership.
    """
    return LANGUAGE_FAMILIES.get(language, "unknown")


def language_pair_relation(lang_a: str, lang_b: str) -> str:
    """
    Return "within-family" or "between-family" for a pair of target languages (H28).
    """
    fa, fb = language_family(lang_a), language_family(lang_b)
    if "unknown" in (fa, fb):
        return "unknown"
    return "within-family" if fa == fb else "between-family"


# ══════════════════════════════════════════════════════════════════════════════
# H29  Idiom length bucketing
# ══════════════════════════════════════════════════════════════════════════════

_BUCKET_ORDER = ["≤3", "4", "5", "6", "7+"]


def idiom_length_bucket(idiom: str) -> str:
    """
    Map an idiom to a character-length bucket: ≤3, 4, 5, 6, or 7+ (H29).

    Limitations
    -----------
    Character count conflates structurally distinct idiom types.  A 4-character
    Japanese yojijukugo and a 4-character Korean modernism belong to the same
    bucket despite very different cultural roles.  The bucket boundaries are
    arbitrary.

    LLM-as-a-judge upgrade
    ----------------------
    Prompt:
        "How would you classify the following CJK idiom by form:
        (a) 4-character classical compound (chengyu / yojijukugo / 사자성어),
        (b) proverb or saying (with a verb phrase),
        (c) compound noun or fixed collocation,
        (d) loan phrase or loanword,
        (e) other?
        Answer (a)–(e) with a one-line reason."
    This gives a linguistically meaningful categorisation independent of surface
    character count.
    """
    n = len(idiom)
    if n <= 3:
        return "≤3"
    if n <= 6:
        return str(n)
    return "7+"


BUCKET_ORDER: list = _BUCKET_ORDER
