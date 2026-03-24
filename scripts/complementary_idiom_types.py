"""Analyse complementary idiom-type datasets: sokdam, kotowaza, xiehouyu."""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import json
import urllib.request
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
EXT  = ROOT / "data/external"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")

results = {}   # dataset_name → dict of stats

# ── 1. Korean sokdam (psyche/korean_idioms) ───────────────────────────────────
print("=== Korean sokdam (psyche/korean_idioms) ===")
ko_path = EXT / "korean_idioms.parquet"
if ko_path.exists():
    ko_df = pd.read_parquet(ko_path)
    answers = ko_df["answer"].dropna()
    lens = answers.str.len()
    print(f"  Entries: {len(answers):,}")
    print(f"  Length: min={lens.min()}, median={lens.median():.0f}, max={lens.max()}")
    # Word count (space-separated)
    wc = answers.str.split().str.len()
    print(f"  Word count: mean={wc.mean():.1f}, median={wc.median():.0f}")
    # Sample
    print("  Samples:", answers.sample(5, random_state=1).tolist())
    results["KO sokdam\n(psyche/korean_idioms)"] = {
        "count": len(answers), "median_len": lens.median(), "type": "Korean"}
else:
    print("  Not found — re-downloading…")
    from datasets import load_dataset
    ds = load_dataset("psyche/korean_idioms", name="idioms", split="train",
                      trust_remote_code=True)
    ko_df = ds.to_pandas()
    ko_df.to_parquet(ko_path)
    answers = ko_df["answer"].dropna()
    lens = answers.str.len()
    results["KO sokdam"] = {"count": len(answers), "median_len": lens.median(), "type": "Korean"}

# ── 2. Japanese kotowaza (sepTN/kotowaza) ─────────────────────────────────────
print("\n=== Japanese kotowaza (sepTN/kotowaza) ===")
koto_path = EXT / "kotowaza_sepTN.json"
if not koto_path.exists():
    try:
        url = "https://raw.githubusercontent.com/sepTN/kotowaza/main/data/kotowaza.json"
        urllib.request.urlretrieve(url, koto_path)
        print("  Downloaded kotowaza.json")
    except Exception as e:
        print(f"  Download failed: {e}")
        koto_path = None

if koto_path and koto_path.exists():
    raw = json.loads(koto_path.read_text(encoding="utf-8"))
    # Can be list or dict
    if isinstance(raw, dict):
        entries = list(raw.values())
    else:
        entries = raw
    koto_df = pd.json_normalize(entries)
    print(f"  Columns: {list(koto_df.columns)}")
    print(f"  Entries: {len(koto_df)}")
    # Find the Japanese text column
    ja_col = next((c for c in koto_df.columns if "japanese" in c.lower() or "kanji" in c.lower()
                   or c in ["word","phrase","kotowaza","jp"]), None)
    if ja_col is None:
        # Try first string column
        for c in koto_df.columns:
            if koto_df[c].dtype == object:
                ja_col = c
                break
    if ja_col:
        texts = koto_df[ja_col].dropna().astype(str)
        lens  = texts.str.len()
        print(f"  Text column: '{ja_col}', samples: {texts.head(5).tolist()}")
        print(f"  Length: min={lens.min()}, median={lens.median():.0f}, max={lens.max()}")
        results["JA kotowaza\n(sepTN, n=100)"] = {
            "count": len(texts), "median_len": lens.median(), "type": "Japanese"}

# ── 3. Chinese xiehouyu (歇后语) ──────────────────────────────────────────────
print("\n=== Chinese xiehouyu ===")
xhypath = EXT / "xiehouyu.json"
XHYURLS = [
    "https://raw.githubusercontent.com/pwxcoo/chinese-xinhua/master/data/xiehouyu.json",
]
if not xhypath.exists():
    for url in XHYURLS:
        try:
            urllib.request.urlretrieve(url, xhypath)
            print(f"  Downloaded from {url}")
            break
        except Exception as e:
            print(f"  Failed {url}: {e}")

if xhypath.exists():
    xhy = pd.DataFrame(json.loads(xhypath.read_text(encoding="utf-8")))
    print(f"  Columns: {list(xhy.columns)}")
    print(f"  Entries: {len(xhy):,}")
    # riddle_part and answer_part
    if "riddle_part" in xhy.columns:
        lens = xhy["riddle_part"].str.len()
        print(f"  Riddle length: min={lens.min()}, median={lens.median():.0f}, max={lens.max()}")
        print(f"  Sample riddles: {xhy['riddle_part'].head(5).tolist()}")
        if "answer_part" in xhy.columns:
            print(f"  Sample answers: {xhy['answer_part'].head(5).tolist()}")
        results["ZH xiehouyu\n(chinese-xinhua)"] = {
            "count": len(xhy), "median_len": lens.median(), "type": "Chinese"}
    elif "riddle" in xhy.columns:
        lens = xhy["riddle"].str.len()
        results["ZH xiehouyu"] = {
            "count": len(xhy), "median_len": lens.median(), "type": "Chinese"}

# ── 4. Compare IdiomTranslate30 coverage ──────────────────────────────────────
it30_types = {
    "ZH chengyu\n(IdiomTranslate30)": {
        "count": int(df[df["source_language"]=="Chinese"]["idiom"].nunique()),
        "median_len": 4.0, "type": "Chinese"},
    "JA yojijukugo\n(IdiomTranslate30)": {
        "count": int(df[df["source_language"]=="Japanese"]["idiom"].nunique()),
        "median_len": 4.0, "type": "Japanese"},
    "KO saseong-eoro\n(IdiomTranslate30)": {
        "count": int(df[df["source_language"]=="Korean"]["idiom"].nunique()),
        "median_len": 4.0, "type": "Korean"},
}
all_results = {**it30_types, **results}

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Dataset sizes
color_map = {"Chinese": "#4C72B0", "Japanese": "#DD8452", "Korean": "#55A868"}
names  = list(all_results.keys())
counts = [v["count"] for v in all_results.values()]
colors = [color_map[v["type"]] for v in all_results.values()]
axes[0].barh(names[::-1], counts[::-1], color=colors[::-1])
axes[0].set_title("Dataset Sizes by Idiom Type", fontweight="bold")
axes[0].set_xlabel("Number of unique entries")
import matplotlib.patches as mpatches
legend_patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
axes[0].legend(handles=legend_patches, title="Language")

# Median idiom/proverb length comparison
med_lens = [v["median_len"] for v in all_results.values()]
bars = axes[1].barh(names[::-1], med_lens[::-1], color=colors[::-1])
axes[1].axvline(4, color="red", ls="--", lw=1.5, label="4 chars (chengyu/yoji/saseong)")
axes[1].set_title("Median Entry Length (chars)", fontweight="bold")
axes[1].set_xlabel("Median character count")
axes[1].legend()

fig.suptitle("IdiomTranslate30 vs Complementary Idiom-Type Datasets", fontsize=12, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "complementary_datasets.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/complementary_datasets.png")

print("\n=== Summary ===")
for name, v in all_results.items():
    print(f"  {name.replace(chr(10),' '):<45} count={v['count']:>6,}  median_len={v['median_len']:.0f}")
