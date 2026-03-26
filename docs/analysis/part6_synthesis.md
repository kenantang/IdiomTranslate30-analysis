# Part 6: Synthesis

This analysis integrates findings from all preceding parts into a single per-idiom
difficulty score, allowing us to identify which properties make an idiom hard to translate and
whether external signals (frequency, dictionary coverage, cognate status) predict this difficulty.

## Idiom-Level Difficulty Composite

Four normalised (0–1) components are averaged equally into
a composite difficulty score for each of the 8,949 idioms:

1. **Cross-strategy divergence** — strategies disagree more on harder idioms
2. **Expansion ratio** — harder idioms require more elaboration
3. **Context sensitivity** — harder idioms produce more variable translations
4. **Cross-target dissimilarity** — harder idioms share less vocabulary across related languages

**Correlates of difficulty (Chinese idioms):**

| Correlate | Spearman ρ | p |
|---|---|---|
| Mean expansion ratio | +0.649 | < 10⁻³⁰⁰ |
| Mean CV (context sensitivity) | +0.529 | < 10⁻³⁰⁰ |
| THUOCL frequency rank | +0.081 | 1.8×10⁻⁶ |
| Xinhua definition length | −0.088 | 1.4×10⁻⁸ |

Expansion ratio and context sensitivity dominate — an idiom is hard to translate if it requires
verbose, variable output. Frequency rank has a small positive effect (rarer idioms are slightly
harder), consistent with the finding above that THUOCL-unmatched idioms produce longer
translations. Longer xinhua definitions correlate weakly with *lower* difficulty: idioms that
dictionaries explain at length may be semantically clearer and therefore easier for the model
to render consistently.

**Cognate membership does not predict difficulty** (ZH–KO: p = 0.44; ZH–JA: p = 0.61). Sharing
a character form with a cognate in another language does not make an idiom easier to translate —
difficulty is driven by cultural interpretability and semantic transparency, not shared script.
(Note: the ZH–JA set includes the 113 trivial dictionary duplicates; excluding them does not
change the result.)

**4-character Chinese idioms are harder than non-4-character ones** (mean 0.529 vs 0.499,
p < 10⁻²⁰). Multi-clause proverbs are more self-explanatory in their surface form — they
state their meaning explicitly, leaving less for the model to interpret and elaborate.

**Hardest idioms** (top examples): 推荐让能, 强奸民意, 文恬武嬉 — culturally specific
concepts with no direct equivalents in most target languages. Note: the top two are also the
zero-sentence idioms identified in the Data Edge Cases section; their inflated difficulty
scores are artefacts of hallucinated translations rather than genuine idiom complexity.

**Easiest idioms**: 海底捞月 (fishing the moon from the sea), 一箭双雕 (one arrow two eagles),
晴天霹雳 (thunderbolt from clear sky) — highly imageable universal metaphors that map cleanly
to stable conventional equivalents across all 10 target languages.

The contrast between the extremes is most readable in English. The easiest Chinese idiom
开山祖师 ("the founding patriarch who opens the mountain") receives consistent, natural
renderings across all three strategies — "founding patriarch," "the bedrock mountain from
which all subsequent peaks were quarried," "founding sire and first progenitor" — all
centering on the same concept of originator or pioneer with minor stylistic variation. The
hardest genuine Chinese idiom 文恬武嬉 ("civil officials at ease, military officials at
play," describing political decay through complacency) actually elicits a *mistranslation*
in one strategy: Creatively produces "dual mastery of the brush and the blade," which
renders the idiom as a positive quality rather than a critique of negligence. Analogy
similarly produces "a rare harmony of the silken brush and the iron fist," still reading
the idiom as virtuous balance. Only Author captures the intended connotation: "mild in
letters and merry in arms" — an archaic framing that hints at decadence. This is not a
failure of elaboration but of interpretation: the model defaults to the most salient
surface reading (civil + martial = balanced scholar-warrior) and misses the negative
political context.

For Japanese, the easiest idiom 騎虎之勢 ("riding a tiger's momentum") maps directly
onto the English proverb "riding a tiger," so all three strategies stay close to that
template: "riding a tiger and can't jump off" / "strapped to a rocket mid-ascent"
(an updating of the image) / "bestride the tiger's back, wherefrom I cannot light
without mine own destruction." The hardest Japanese idiom 面誉不忠 ("praising to one's
face, disloyal in the heart") produces highly divergent surface metaphors — "a honeyed
tongue and a hollow heart" / "a marble facade held up by rotting timber" / "fawning
praise and faithless treachery" — none of which share any words, though they all target
the same semantic of surface praise masking disloyalty.

Korean shows the same pattern. The easiest idiom 약방감초 ("licorice in a medicine
shop," meaning an indispensable constant presence) maps readily to English via a shift
of domain: "the indispensable glue that holds our team together" / "the golden thread
woven into every fabric of our team" / "the very herb that seasons every pot" — varied
metaphors but all encoding indispensability clearly. The hardest Korean idiom 화복무문
("fortune and misfortune have no fixed gate," meaning outcomes are determined by one's
own actions) requires unpacking a philosophical concept for which English has no compact
equivalent, and the three strategies take very different paths: "fortune and misfortune
are but shadows cast by one's own hand" / "misfortune and fortune are but two sides of
the same wind" / "fortune and woe have no fixed gate" (a near-literal rendering that
sacrifices naturalness for fidelity).

![difficulty](../figures/difficulty.png)
