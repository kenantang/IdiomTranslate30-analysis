"""Build Japanese yojijukugo reference list from Wiktionary."""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import re
import json
import gzip
import urllib.request
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils import is_4char_cjk_idiom, is_yojijukugo_tagged

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
EXT  = ROOT / "data/external"
PROC = ROOT / "data/processed"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
ja_idioms = set(df[df["source_language"]=="Japanese"]["idiom"].unique())
print(f"IdiomTranslate30 Japanese idioms: {len(ja_idioms):,}")

# ── Source 1: Wiktionary Japanese yojijukugo category dump ───────────────────
# Use the Kaikki.org English Wiktionary JSON dump, which includes Japanese entries
# with part-of-speech and category annotations.
KAIKKI_PATH = EXT / "kaikki_ja_yoji.jsonl"

if not KAIKKI_PATH.exists():
    print("Fetching Wiktionary entries for Japanese 四字熟語 via kaikki.org…")
    # kaikki.org provides pre-extracted per-language JSON
    url = "https://kaikki.org/dictionary/Japanese/kaikki.org-dictionary-Japanese.json"
    tmp = EXT / "_ja_wikt_tmp.json"
    try:
        urllib.request.urlretrieve(url, tmp)
        # Filter to yojijukugo: exactly 4 CJK characters, tagged as 四字熟語 or idiom
        results = []
        with open(tmp, encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                word = entry.get("word", "")
                if not is_4char_cjk_idiom(word):   # H12: 4-char CJK filter
                    continue
                # Check for yojijukugo tag  (H15)
                is_yoji = is_yojijukugo_tagged(entry)
                gloss = "; ".join(
                    g for s in senses for g in s.get("glosses", []) if g
                )
                results.append({"word": word, "is_yoji_tagged": is_yoji, "gloss": gloss})
        tmp.unlink(missing_ok=True)
        yoji_df = pd.DataFrame(results).drop_duplicates("word")
        print(f"  4-char CJK entries found: {len(yoji_df):,}")
        print(f"  Tagged as yojijukugo/idiom: {yoji_df['is_yoji_tagged'].sum():,}")
        yoji_df.to_json(KAIKKI_PATH, orient="records", lines=True, force_ascii=False)
        print(f"  Saved {len(yoji_df)} entries → {KAIKKI_PATH.name}")
    except Exception as e:
        print(f"  Wiktionary fetch failed: {e}")
        yoji_df = pd.DataFrame(columns=["word","is_yoji_tagged","gloss"])
else:
    print("Wiktionary cache found, loading…")
    yoji_df = pd.read_json(KAIKKI_PATH, lines=True)
    print(f"  {len(yoji_df):,} entries loaded")

# ── Source 2: GitHub yojijukugo lists ────────────────────────────────────────
# Try a few known small public lists to supplement
EXTRA_URLS = [
    ("https://raw.githubusercontent.com/ikegami-yukino/yojijukugo/main/yojijukugo.txt",
     EXT / "yojijukugo_ikegami.txt"),
]
extra_words = set()
for url, path in EXTRA_URLS:
    if not path.exists():
        try:
            urllib.request.urlretrieve(url, path)
            print(f"Downloaded {path.name}")
        except Exception as e:
            print(f"Could not download {path.name}: {e}")
    if path.exists():
        words = [w.strip() for w in path.read_text(encoding="utf-8").splitlines() if w.strip()]
        extra_words.update(words)
        print(f"  {path.name}: {len(words)} entries")

# Combine all 4-char CJK words from all sources
all_yoji = set(yoji_df["word"].tolist()) | extra_words
print(f"\nCombined yojijukugo reference: {len(all_yoji):,} unique entries")

# ── Overlap with IdiomTranslate30 ─────────────────────────────────────────────
overlap     = ja_idioms & all_yoji
not_in_ref  = ja_idioms - all_yoji
ref_not_in  = all_yoji  - ja_idioms

print(f"\nIdiomTranslate30 JA ∩ reference: {len(overlap):,} / {len(ja_idioms):,} "
      f"({len(overlap)/len(ja_idioms)*100:.1f}%)")
print(f"IdiomTranslate30 JA not in reference: {len(not_in_ref):,}")
print(f"Reference not in IdiomTranslate30: {len(ref_not_in):,}")

print("\nSample matched:", list(overlap)[:10])
print("Sample unmatched (IT30 only):", list(not_in_ref)[:10])

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Venn-style bar
venn_data = pd.Series({
    f"IT30 only\n({len(not_in_ref):,})": len(not_in_ref),
    f"Both\n({len(overlap):,})": len(overlap),
    f"Ref only\n({len(ref_not_in):,})": len(ref_not_in),
})
venn_data.plot(kind="bar", ax=axes[0], color=["#4C72B0","#55A868","#DD8452"], width=0.6)
axes[0].set_title("Japanese Yojijukugo Coverage\n(IdiomTranslate30 vs Wiktionary+GitHub)",
                  fontweight="bold")
axes[0].set_ylabel("Unique idiom count")
axes[0].tick_params(axis="x", rotation=0)

# Source breakdown
source_data = {
    "Wiktionary (4-char CJK)": len(yoji_df),
    "Wiktionary (yoji-tagged)": int(yoji_df["is_yoji_tagged"].sum()),
    "GitHub lists": len(extra_words),
    "Combined": len(all_yoji),
    "IdiomTranslate30": len(ja_idioms),
}
pd.Series(source_data).plot(kind="barh", ax=axes[1], color="#4C72B0")
axes[1].set_title("Source Sizes", fontweight="bold")
axes[1].set_xlabel("Count")
fig.tight_layout()
fig.savefig(FIG / "japanese_yoji_coverage.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/japanese_yoji_coverage.png")

# Save reference list
ref_df = pd.DataFrame({"word": sorted(all_yoji)})
ref_df["in_IT30"] = ref_df["word"].isin(ja_idioms)
ref_df.to_csv(EXT / "japanese_yojijukugo_reference.csv", index=False)
print(f"Saved → data/external/japanese_yojijukugo_reference.csv ({len(ref_df):,} entries)")
