"""Characterise the 189 Chinese idioms not in chinese-xinhua."""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import json
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils import char_script_type, is_cjk_char

ROOT = Path(__file__).parent.parent
FIG  = ROOT / "figures"
EXT  = ROOT / "data/external"
PROC = ROOT / "data/processed"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

df       = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")
meta     = pd.read_parquet(PROC / "idiom_metadata.parquet")
xinhua   = pd.DataFrame(json.loads((EXT / "chinese_xinhua.json").read_text(encoding="utf-8")))
xinhua_set = set(xinhua["word"])

unmatched = meta[~meta["in_xinhua"]]["idiom"].tolist()
matched   = meta[ meta["in_xinhua"]]["idiom"].tolist()
print(f"Unmatched: {len(unmatched)}, Matched: {len(matched)}")

# ── Character-length breakdown ────────────────────────────────────────────────
um = pd.Series([len(i) for i in unmatched], name="length")
m  = pd.Series([len(i) for i in matched],   name="length")
print("\nUnmatched length distribution:")
print(um.value_counts().sort_index().to_string())
print("\nMatched length distribution (% of each length):")
print(m.value_counts().sort_index().to_string())

# ── Script composition — are they traditional/simplified/mixed? (H11-H13) ─────
def idiom_profile(idiom):
    types = [char_script_type(c) for c in idiom]
    return pd.Series(types).value_counts().to_dict()

unmatched_df = pd.DataFrame({"idiom": unmatched})
unmatched_df["length"]      = unmatched_df["idiom"].str.len()
unmatched_df["all_CJK"]     = unmatched_df["idiom"].apply(
    lambda i: all(is_cjk_char(c) for c in i))
unmatched_df["has_non_CJK"] = ~unmatched_df["all_CJK"]

print(f"\nUnmatched — all-CJK chars: {unmatched_df['all_CJK'].sum()} / {len(unmatched_df)}")
print(f"Unmatched — contains non-CJK: {unmatched_df['has_non_CJK'].sum()}")
non_cjk = unmatched_df[unmatched_df["has_non_CJK"]]["idiom"].tolist()
if non_cjk:
    print("  Non-CJK examples:", non_cjk[:10])

# ── Check against CHID word list ──────────────────────────────────────────────
chid_path = EXT / "chid_wordlist.txt"
if not chid_path.exists():
    import urllib.request
    try:
        url = "https://raw.githubusercontent.com/chujiezheng/ChID-Dataset/master/wordList.txt"
        urllib.request.urlretrieve(url, chid_path)
        print("\nDownloaded CHID wordlist.")
    except Exception as e:
        print(f"\nCHID wordlist unavailable: {e}")
        chid_path = None

if chid_path and chid_path.exists():
    chid_words = set(chid_path.read_text(encoding="utf-8").splitlines())
    in_chid = [i for i in unmatched if i in chid_words]
    print(f"\nUnmatched ∩ CHID: {len(in_chid)} / {len(unmatched)}")
    if in_chid:
        print("  Examples found in CHID:", in_chid[:10])

# ── Translation-length comparison: unmatched vs matched ───────────────────────
TCOLS  = ["translate_creatively","translate_analogy","translate_author"]
LABELS = ["Creatively","Analogy","Author"]
df_zh  = df[df["source_language"]=="Chinese"].copy()
df_zh["group"] = df_zh["idiom"].apply(
    lambda i: "unmatched" if i in set(unmatched) else "matched")
print("\nMean translation length — matched vs unmatched (xinhua):")
for tc, lbl in zip(TCOLS, LABELS):
    m_mean  = df_zh[df_zh["group"]=="matched"  ][tc].str.len().mean()
    um_mean = df_zh[df_zh["group"]=="unmatched"][tc].str.len().mean()
    print(f"  {lbl:<14} matched={m_mean:.1f}  unmatched={um_mean:.1f}")

# ── Figure ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

# Idiom length distribution comparison
len_df = pd.DataFrame({
    "Matched":   pd.Series([len(i) for i in matched]).value_counts().sort_index(),
    "Unmatched": um.value_counts().sort_index(),
}).fillna(0)
len_df.iloc[:12].plot(kind="bar", ax=axes[0], color=["#4C72B0","#C44E52"], width=0.7)
axes[0].set_title("Character Length: Matched vs\nUnmatched in chinese-xinhua", fontweight="bold")
axes[0].set_xlabel("Idiom length (chars)")
axes[0].set_ylabel("Count of unique idioms")
axes[0].tick_params(axis="x", rotation=0)

# Translation length box
tlen_melt = pd.melt(
    df_zh[["group"] + TCOLS].rename(columns=dict(zip(TCOLS, LABELS))),
    id_vars=["group"], var_name="Strategy", value_name="Length"
)
tlen_melt["Length"] = tlen_melt["Length"].apply(
    lambda x: len(str(x)) if pd.notna(x) else None)
tlen_melt = tlen_melt.dropna()
sns.boxplot(data=tlen_melt, x="Strategy", y="Length", hue="group",
            palette={"matched":"#4C72B0","unmatched":"#C44E52"},
            flierprops=dict(marker=".", alpha=0.2), ax=axes[1])
axes[1].set_title("Translation Length: Matched vs\nUnmatched Chinese Idioms", fontweight="bold")
axes[1].set_ylabel("Character count")
axes[1].set_ylim(0, 400)
axes[1].legend(title="xinhua coverage")
fig.tight_layout()
fig.savefig(FIG / "unmatched_chinese.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("Saved → figures/unmatched_chinese.png")

# Save unmatched list
unmatched_df.to_csv(ROOT / "data/audit/unmatched_chinese_idioms.csv", index=False)
print("Saved → data/audit/unmatched_chinese_idioms.csv")
