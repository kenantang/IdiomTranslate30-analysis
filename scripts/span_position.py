"""
Span position within translation.

For each row where the span is a contiguous substring of the translation,
compute:
  relative_start = span_start_char / (translation_len - span_len)
    → 0.0 = span begins at the very start
    → 1.0 = span begins at the very end (last possible position)

Rows where span is NOT found in translation are excluded (uses audit logic).

Outputs:
  data/processed/span_positions.parquet
  figures/span_position.png
"""
import matplotlib
matplotlib.use("Agg")
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from utils import span_position_zone, compute_relative_start, LONG_THRESH

ROOT = Path(__file__).parent.parent
PROC = ROOT / "data/processed"
FIG  = ROOT / "figures"
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

TCOLS  = ["translate_creatively", "translate_analogy", "translate_author"]
SCOLS  = ["span_creatively",      "span_analogy",      "span_author"]
LABELS = ["Creatively", "Analogy", "Author"]

print("Loading data…")
df = pd.read_parquet(ROOT / "data/raw/IdiomTranslate30.parquet")

# ── Compute span start offsets ─────────────────────────────────────────────
print("Computing span positions…")
pos_rows = []
for tc, sc, lbl in zip(TCOLS, SCOLS, LABELS):
    # Filter: translation not too long, span not null
    mask = (df[tc].str.len() <= LONG_THRESH) & df[sc].notna() & df[tc].notna()
    sub  = df[mask].copy()

    # Compute relative start and filter to rows where span is found
    sub["_tlen"] = sub[tc].str.len()
    sub["_slen"] = sub[sc].str.len()
    sub["rel_start"] = [
        compute_relative_start(s, t)
        for s, t in zip(sub[sc], sub[tc])
    ]

    # Keep only rows where span is found (rel_start is not NaN)
    found = sub[sub["rel_start"].notna()].copy()
    found["_start"] = [t.find(s) if isinstance(s, str) and isinstance(t, str) else -1
                       for t, s in zip(found[tc], found[sc])]
    found["position_zone"] = found["rel_start"].map(span_position_zone)
    found["strategy"] = lbl
    pos_rows.append(found[["source_language","target_language","idiom","strategy",
                            "_tlen","_slen","_start","rel_start","position_zone"]]
                    .rename(columns={"_tlen":"tlen","_slen":"slen","_start":"abs_start"}))

positions = pd.concat(pos_rows, ignore_index=True)
positions.to_parquet(PROC / "span_positions.parquet", index=False)
print(f"Saved {len(positions):,} rows → data/processed/span_positions.parquet")

# ── Summary ────────────────────────────────────────────────────────────────
print("\n=== Span position zone distribution (% of rows with span found) ===")
for lbl in LABELS:
    sub = positions[positions.strategy==lbl]
    vc  = sub["position_zone"].value_counts(normalize=True).sort_index() * 100
    print(f"  {lbl:<14}  beginning={vc.get('beginning',0):.1f}%  "
          f"middle={vc.get('middle',0):.1f}%  end={vc.get('end',0):.1f}%")

print("\n=== Mean relative start by source language (Creatively) ===")
sub_c = positions[positions.strategy=="Creatively"]
print(sub_c.groupby("source_language")["rel_start"].mean().round(3).to_string())

print("\n=== Mean relative start by target language (Creatively) ===")
print(sub_c.groupby("target_language")["rel_start"].mean().sort_values().round(3).to_string())

# ── Figures ────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(17, 10))

# Row 0: KDE of relative start per strategy × source language
for ax, lbl in zip(axes[0], LABELS):
    sub = positions[positions.strategy==lbl]
    for src, color in zip(["Chinese","Japanese","Korean"],
                           ["#4C72B0","#DD8452","#55A868"]):
        data = sub[sub.source_language==src]["rel_start"].dropna()
        data.plot.kde(ax=ax, label=src, color=color, bw_method=0.15)
    ax.axvline(1/3, ls="--", color="grey", lw=0.8, alpha=0.6)
    ax.axvline(2/3, ls="--", color="grey", lw=0.8, alpha=0.6)
    ax.set_xlim(0, 1); ax.set_ylim(bottom=0)
    ax.set_title(f"Span Relative Start Position\n({lbl})", fontweight="bold")
    ax.set_xlabel("Relative start (0=beginning, 1=end)")
    ax.set_ylabel("Density"); ax.legend(fontsize=8)
    ax.text(1/6, ax.get_ylim()[1]*0.95, "begin", ha="center", fontsize=8, color="grey")
    ax.text(1/2, ax.get_ylim()[1]*0.95, "mid",   ha="center", fontsize=8, color="grey")
    ax.text(5/6, ax.get_ylim()[1]*0.95, "end",   ha="center", fontsize=8, color="grey")

# Row 1 left: Zone bar chart per strategy
ax = axes[1, 0]
zone_pct = (positions.groupby(["strategy","position_zone"])
            .size().unstack(fill_value=0)
            .apply(lambda r: r/r.sum()*100, axis=1))
zone_pct[["beginning","middle","end"]].plot(kind="bar", ax=ax, width=0.6,
    color=["#4C72B0","#DD8452","#55A868"])
ax.set_title("Position Zone Distribution\nby Strategy", fontweight="bold")
ax.set_ylabel("% of rows"); ax.set_xlabel("")
ax.tick_params(axis="x", rotation=0); ax.legend(fontsize=8)

# Row 1 middle: Mean relative start by target language (Creatively)
ax = axes[1, 1]
tgt_means = (sub_c.groupby("target_language")["rel_start"].mean().sort_values())
ax.barh(tgt_means.index, tgt_means.values, color="#4C72B0")
ax.axvline(tgt_means.mean(), ls="--", color="red", lw=1, label=f"mean={tgt_means.mean():.2f}")
ax.set_title("Mean Relative Span Start\nby Target Language (Creatively)", fontweight="bold")
ax.set_xlabel("Relative start position")
ax.legend(fontsize=8)

# Row 1 right: Span length vs position scatter (sample, Creatively)
ax = axes[1, 2]
samp = sub_c[["slen","tlen","rel_start","source_language"]].dropna().sample(
    min(5000, len(sub_c)), random_state=42)
samp["span_frac"] = samp["slen"] / samp["tlen"]
for src, color in zip(["Chinese","Japanese","Korean"], ["#4C72B0","#DD8452","#55A868"]):
    s = samp[samp.source_language==src]
    ax.scatter(s["rel_start"], s["span_frac"], alpha=0.15, s=4, color=color, label=src)
ax.set_title("Span Position vs Span Fraction\n(Creatively, sample)", fontweight="bold")
ax.set_xlabel("Relative start position")
ax.set_ylabel("Span length / translation length")
ax.legend(fontsize=8)

fig.suptitle("Idiom Span Position Within Translation", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(FIG / "span_position.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print("\nSaved → figures/span_position.png")
