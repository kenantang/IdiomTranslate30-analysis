# Data Dependencies

The analysis scripts rely on several external data sources beyond the main
`IdiomTranslate30.parquet` file. All external files are stored under `data/external/`.
Most are fetched automatically on first run; one (**Unihan**) must be downloaded manually.

---

## Summary

| File | Destination | Acquisition | Used by |
|---|---|---|---|
| `IdiomTranslate30.parquet` | `data/raw/` | Manual | All scripts |
| `Unihan_Readings.txt` | `data/external/` | **Manual** | `cjk_cognates.py`, `cognate_comparison_extended.py` |
| `chinese_xinhua.json` | `data/external/` | Auto (GitHub) | `external_coverage.py`, `unmatched_chinese.py`, `complementary_idiom_types.py` |
| `THUOCL_chengyu.txt` | `data/external/` | Auto (GitHub) | `external_coverage.py` |
| `kaikki_ja_yoji.jsonl` | `data/external/` | Auto (kaikki.org) | `japanese_yojijukugo.py` |
| `yojijukugo_ikegami.txt` | `data/external/` | Auto (GitHub) | `japanese_yojijukugo.py` |
| `korean_idioms.parquet` | `data/external/` | Auto (HuggingFace) | `external_coverage.py`, `complementary_idiom_types.py` |
| `kotowaza_sepTN.json` | `data/external/` | Auto (GitHub) | `complementary_idiom_types.py` |
| `xiehouyu.json` | `data/external/` | Auto (GitHub) | `complementary_idiom_types.py` |
| `chid_wordlist.txt` | `data/external/` | Auto (GitHub) | `unmatched_chinese.py` |

---

## Manual Downloads

### Unihan Database (`Unihan_Readings.txt`)

**Required by:** `cjk_cognates.py`, `cognate_comparison_extended.py`

The Unicode Consortium's Unihan database maps CJK codepoints to their per-language
readings. The scripts use the `kHangul` field to transliterate Chinese characters into
their Sino-Korean (Hangul) pronunciation for cognate matching.

**Download steps:**

1. Go to [https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip](https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip)
2. Extract the zip — it contains several `.txt` files
3. Copy `Unihan_Readings.txt` to `data/external/Unihan_Readings.txt`

```bash
curl -O https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip Unihan.zip Unihan_Readings.txt -d data/external/
rm Unihan.zip
```

The file is ~25 MB uncompressed. The scripts also reference `Unihan_Variants.txt` (present
in `data/external/`) which can be extracted from the same zip if needed:

```bash
unzip Unihan.zip Unihan_Variants.txt -d data/external/
```

---

## Auto-Downloaded Sources

These files are fetched automatically by the relevant script on first run and cached in
`data/external/`. If the cache exists, the download is skipped.

### chinese-xinhua (`chinese_xinhua.json`)

**Source:** [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) on GitHub

A community-maintained Chinese idiom dictionary with ~30,000 chengyu entries, each
containing the word form, pinyin, explanation, and example sentence.

**Used for:** Coverage analysis (which IT30 Chinese idioms are in this dictionary),
definition-length correlation with translation length, and character-level length
distribution comparisons.

**Auto-fetched by:** `external_coverage.py`

```
https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data/idiom.json
→ data/external/chinese_xinhua.json
```

---

### THUOCL Chengyu Frequency List (`THUOCL_chengyu.txt`)

**Source:** [thunlp/THUOCL](https://github.com/thunlp/THUOCL) on GitHub

THU Open Chinese Lexicon — a corpus-derived frequency list for Chinese words including
a chengyu subset. Entries are tab-separated `word\tfrequency` pairs.

**Used for:** Frequency quintile analysis — whether corpus frequency of a chengyu
predicts translation length or difficulty score.

**Auto-fetched by:** `external_coverage.py`

```
https://raw.githubusercontent.com/thunlp/THUOCL/master/data/THUOCL_chengyu.txt
→ data/external/THUOCL_chengyu.txt
```

---

### Kaikki / Wiktionary Japanese Entries (`kaikki_ja_yoji.jsonl`)

**Source:** [kaikki.org](https://kaikki.org/dictionary/Japanese/)

Kaikki.org provides pre-parsed JSON dumps of Wiktionary entries by language. The script
downloads the full Japanese entry dump (~200 MB), filters to 4-character CJK entries
tagged as 四字熟語 or `yojijukugo`, and caches only those entries as a JSONL file.

**Used for:** Japanese yojijukugo coverage analysis — what fraction of IT30 Japanese
idioms appear in Wiktionary with a yojijukugo tag.

**Auto-fetched by:** `japanese_yojijukugo.py`

```
https://kaikki.org/dictionary/Japanese/kaikki.org-dictionary-Japanese.json
→ filtered and saved as data/external/kaikki_ja_yoji.jsonl
```

!!! note
    The full download is ~200 MB. The filtered cache (`kaikki_ja_yoji.jsonl`) is much
    smaller (~2 MB). The raw download is not kept.

---

### ikegami-yukino Yojijukugo List (`yojijukugo_ikegami.txt`)

**Source:** [ikegami-yukino/yojijukugo](https://github.com/ikegami-yukino/yojijukugo) on GitHub

A plain-text list of yojijukugo compiled from several Japanese reference sources.
Used as a secondary reference list alongside Wiktionary.

**Auto-fetched by:** `japanese_yojijukugo.py`

```
https://raw.githubusercontent.com/ikegami-yukino/yojijukugo/main/yojijukugo.txt
→ data/external/yojijukugo_ikegami.txt
```

---

### Korean Idioms Dataset (`korean_idioms.parquet`)

**Source:** [psyche/korean_idioms](https://huggingface.co/datasets/psyche/korean_idioms) on HuggingFace

A HuggingFace dataset of Korean idioms (속담, sokdam — Korean proverbs and sayings).
Requires the `datasets` package (`pip install datasets`).

**Used for:** Korean idiom coverage analysis and complementary idiom type comparison.

**Auto-fetched by:** `external_coverage.py`, `complementary_idiom_types.py`

```python
load_dataset("psyche/korean_idioms", name="idioms", split="train")
→ data/external/korean_idioms.parquet
```

---

### sepTN Kotowaza (`kotowaza_sepTN.json`)

**Source:** [sepTN/kotowaza](https://github.com/sepTN/kotowaza) on GitHub

A JSON dataset of Japanese kotowaza (proverbs / sayings) with meanings and examples.
Used to compare IT30's Japanese idiom inventory against a proverb-focused reference.

**Auto-fetched by:** `complementary_idiom_types.py`

```
https://raw.githubusercontent.com/sepTN/kotowaza/main/data/kotowaza.json
→ data/external/kotowaza_sepTN.json
```

---

### Chinese Xiehouyu (`xiehouyu.json`)

**Source:** [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua) on GitHub

Xiehouyu (歇后语) are two-part allegorical sayings — a distinct form from chengyu.
Used to measure whether IT30's Chinese idioms overlap with this complementary category.

**Auto-fetched by:** `complementary_idiom_types.py`

```
https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data/xiehouyu.json
→ data/external/xiehouyu.json
```

---

### CHID Wordlist (`chid_wordlist.txt`)

**Source:** [chujiezheng/ChID-Dataset](https://github.com/chujiezheng/ChID-Dataset) on GitHub

The Chinese Idiom Dataset (ChID) wordlist — a list of chengyu used in a cloze-test NLP
benchmark. Used to check how many of IT30's unmatched Chinese idioms (those not in
chinese-xinhua) appear in this NLP benchmark corpus.

**Auto-fetched by:** `unmatched_chinese.py`

```
https://raw.githubusercontent.com/chujiezheng/ChID-Dataset/master/wordList.txt
→ data/external/chid_wordlist.txt
```

---

## Python Package Dependencies

### Non-standard packages (must be installed separately)

| Package | Used by | Install |
|---|---|---|
| `rapidfuzz` | `cognate_comparison_zhko.py`, `cognate_comparison_extended.py`, `strategy_divergence.py` | `pip install rapidfuzz` |
| `opencc-python-reimplemented` | `cjk_cognates.py`, `cognate_comparison_extended.py` | `pip install opencc-python-reimplemented` |
| `hanja` | `cjk_cognates.py`, `cognate_comparison_extended.py` | `pip install hanja` |
| `scikit-learn` | `english_and_resource_profile.py` | `pip install scikit-learn` |
| `statsmodels` | `english_and_resource_profile.py` | `pip install statsmodels` |
| `datasets` | `external_coverage.py`, `complementary_idiom_types.py` | `pip install datasets` |
| `mkdocs-material` | docs only | `pip install mkdocs mkdocs-material` |

To install all non-standard packages at once:

```bash
pip install rapidfuzz opencc-python-reimplemented hanja scikit-learn statsmodels datasets mkdocs mkdocs-material
```

### Standard packages (assumed present)

| Package | Used by |
|---|---|
| `pandas` | All scripts |
| `numpy` | All scripts |
| `matplotlib` | All scripts that generate figures |
| `seaborn` | All scripts that generate figures |
| `scipy` | `analogy_deep_analysis.py`, `cjk_cognates.py`, `cognate_comparison_zhko.py`, `cognate_comparison_extended.py`, `crosslingual_consistency.py`, `difficulty.py`, `english_and_resource_profile.py`, `external_coverage.py`, `idiom_morphology.py`, `lexical_diversity.py`, `span_analysis.py`, `translation_length.py` |
| `pyarrow` | All scripts reading/writing `.parquet` files |
