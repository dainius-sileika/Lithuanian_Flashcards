# Blind style survey — analysis and production decision

Data: 13 rounds, 99 images. Round 12 (hidden repeat of round 2) was recognised and left unranked → excluded; no test–retest estimate. Round 9 (minia) was submitted in its initial on-screen order; comments are consistent with that order, so it is kept at half weight. Rows analysed: 91 rankings across 12 rounds. Owner recognised `orig` in at least one round (2), so the control was only partially blind; his comments on orig ("too white / too bright / cartoony") are nevertheless consistent across all 12 rounds, including rounds where he did not say he recognised it.

Paper tone was measured on the exact images he saw (median CIE L* and b* of light, low-saturation pixels inside the red bands; b* = yellowness). Observed composition of every new image was recorded by eye before fitting (`survey_rows.json`).

## 1. Per-round results (`*` = would ship)

| R | card | orig rank | ranking |
|---|---|---|---|
| 1 | miestas | 1/8 | orig* > F4ref_g2* > F3_g2* > F4bleed_g2* > sun_old* > F4_g2 > F3_sun > F4_sun |
| 2 | gydytojas | 8/8 | F4 on 1.5* > g2_old* > F4dun_g2* > F3_g2* > F4_g2 > F3_sun > F4_sun > orig |
| 3 | eiti | 7/7 | F1_sunlow* > F4arrow_sun* > F4_sun > F3_g2 > F4_g2 > F4arrow_g2 > orig |
| 4 | suo | 6/7 | F4dun_g2* > F4_g2* > g2_old > F4_sun > F4_g2low > orig > F4_flare |
| 5 | klubas | 1/8 | orig* > F4ref_sun* > F3_sun > F4_g2 > F4ovr_g2 > F4ovr_sun > F4_sun > sun_old |
| 6 | seima | 8/8 | F2_g2* > F4_sun* > F3_sun* > F3_g2* > F4_g2b > F4_g2 > F4 on 1.5 > orig |
| 7 | paltas | 7/7 | F1_sun* > F4_sun* > F4_flare > F3_sun > F4dun_sun > F4_g2 > orig |
| 8 | pjauti | 6/8 | F4bleed_g2* > F4_g2* > sun_B* > F3_g2* > F4_sun > orig > g2_A > F4_g2low |
| 9 | minia (½ wt) | 2/7 | F3_sun* > orig* > F3_g2 > F4ref_g2 > F4_g2 > F4_sun > F4ref_sun |
| 10 | mokykla | 8/8 | F4bleed_g2* > F3_g2* > F1_g2 > F4_g2 > flare_old > F4_sun > F4_flare > orig |
| 11 | lova | 6/7 | F4dun_g2* > F4_g2* > F4_g2low* > F4_sun* > F4 on 1.5* > orig > F4_flare |
| 13 | vestuves | 7/8 | F4_g2* > F3_g2* > F4ref_sun > F4_sun > F3_sun > F4_sunb > orig > F4 on 1.5 |

**The headline:** the shipped 1.5 master is last or second-last in 9 of 12 rounds (mean normalised Borda 0.28, ship rate 0.25). It wins only miestas and klubas and places 2nd in minia — the three rounds where the new variants failed on *meaning* (klubas read as "dancing", minia variants drifted to a soup kitchen / orchard, miestas Sunburst variants put a couple in front). Orig wins when the alternatives fail the target word, never on style. The premise of the whole exercise ("recover the 1.5 look on new models") is therefore wrong: blind, he does not want the 1.5 look. He wants a darker, yellower, more worked version of what gpt-image-2 already produces.

## 2. Pooled strengths

With one rater and each new image appearing once, a Plackett–Luce fit reduces to within-round Borda; the honest pooled estimate is mean normalised Borda (0 = last, 1 = first) per attribute, with round 9 at half weight.

| group | n | Borda | ship | paper L* | paper b* |
|---|---|---|---|---|---|
| **model** gpt-image-2 | 39 | **0.62** | 0.51 | 88 | 20 |
| Sunburst | 31 | 0.50 | 0.35 | 85 | 17 |
| gpt-image-1.5 (orig + F4-on-1.5) | 16 | 0.30 | 0.31 | 93 | 13 |
| flare | 5 | 0.25 | 0.00 | 87 | 14 |
| **family** F4bleed (g2) | 3 | 0.86 | 1.00 | 78 | 21 |
| F4dun | 4 | 0.76 | 0.75 | 83 | 24 |
| F3 (both models) | 15 | 0.59 | 0.53 | 84 | 21 |
| F4 (text-only, both models) | 44 | 0.45 | 0.27 | 90 | 17 |
| shipped prompt (all models) | 17 | 0.34 | 0.29 | 90 | 13 |
| g2 × F3 | 8 | 0.66 | 0.75 | 85 | 22 |
| g2 × F4 | 19 | 0.52 | 0.32 | 92 | 19 |
| Sunburst × F4 | 17 | 0.45 | 0.24 | 88 | 16 |
| refs (images.edit) | 6 | 0.68 | 0.50 | | |
| no refs | 85 | 0.49 | 0.39 | | |
| quality low | 4 | 0.50 | 0.50 | | |
| composition float | 65 | 0.51 | 0.40 | 90 | 17 |
| composition bleed | 26 | 0.49 | 0.38 | 84 | 18 |

Top-3 rate: gpt-image-2 49 %, Sunburst 39 %, 1.5 25 %, flare 20 %. Last-place rate: gpt-image-2 3 %, Sunburst 10 %, 1.5 38 %, flare 40 %.

Regression of normalised Borda on attributes with round fixed effects (ridge, 400 round-bootstraps; 90 % CI). Only two coefficients exclude zero: **paper yellowness b\* (+0.27 per 10 units, CI +0.09…+0.39)** and **paper lightness L\* (−0.07 per 5 units, CI −0.19…−0.01)**. Everything else (model, people block, print block, bleed, refs, quality) is inside its CI once paper tone is in the model, because paper tone is colinear with family and model in this design. Treat the regression as confirmation that paper tone is the dominant measurable factor, and read the other effects from the direct contrasts below.

## 3. One-attribute contrasts (same round, same card; rank of a vs b, lower is better)

| contrast | a wins | detail |
|---|---|---|
| float vs **bleed** (g2, F4) | 0/3 | r1 6v4, r8 2v1, r10 4v1 — bleed won all three, all three bleeds ship-flagged |
| bright vs **dun** paper | 1/4 | r2 5v3, r4 2v1, r11 2v1 (g2: dun wins all), r7 2v5 (Sunburst: the dun loss was blamed on the man, "too serious and cunning, clothing fits too well", not on colour) |
| default (red) vs black arrows | 1/2 | r3 g2 5v6, Sunburst 3v2 — within noise |
| medium vs **low** quality (g2) | 3/3 | low loses every time: "too simple", "cartoony", glitches |
| text-only vs **refs** | 1/5 | refs win r1 6v2, r5 7v2, r9 5v4, r13 4v3; lose r9 Sunburst 6v7 (both failed target word) |
| klubas plain vs house-of-culture override | 1/2 | 4v5, 7v6 — no effect; the override made it "sparse"/"staged" |
| **F4 on g2** vs F4 on Sunburst | 9/12 | Sunburst won eiti, seima, paltas |
| F3 on g2 vs F3 on Sunburst | 3/5 | |
| **F3_g2** vs F4_g2 | 6/8 | F4 lost to F3 on the same model; F4's paper measured L 92 / b\* 19 vs F3's L 85 / b\* 22 |
| orig vs F4 text on 1.5 | 1/4 | the F4 text improves 1.5 in 3/4 rounds, but 1.5 stays "cartoony" |
| F4 on 1.5 vs F4 on g2 | 1/4 | |
| flare vs g2 (F4) | 1/4 | |
| seed pairs | | r6 F4_g2 6 vs F4_g2b 5; r13 F4_sun 4 vs F4_sunb 6 (owner: "chut chut too bright") |

**Seed noise floor:** identical settings moved 1 rank (seima) and 2 ranks (vestuves; the second seed came out measurably brighter, so part of that gap is paper, not luck). Any contrast of ≤2 ranks is not evidence. Contrasts that clear the floor: bleed (r10: 3 ranks), dun paper (r2: 2 ranks, r4/r11 top vs 2nd with "toss-up" comment — marginal but consistent 3/3 on g2), refs (r1: 4, r5: 5), quality low (r8: 6), orig vs the field (5–7 ranks, 9 rounds).

## 4. Stated criteria vs revealed weights

Comment themes (regex-coded, n = 91 comments) with the mean Borda of the images they were written on:

| theme | n | Borda | ship | paper L* / b* |
|---|---|---|---|---|
| "feeling / nostalgia / beautiful" | 33 | 0.52 | 0.39 | 88 / 18 |
| proportions / glitch / uncanny | 21 | 0.50 | 0.29 | |
| "GO" (as praise) | 18 | 0.63 | 0.50 | |
| wants more yellow/cream | 17 | 0.57 | 0.47 | 89 / 17 |
| cartoony / simple / plain / flat | 17 | 0.30 | 0.18 | 92 / 15 |
| too bright / too white | 10 | 0.24 | 0.10 | 91 / 13 |
| detail (as praise) | 8 | 0.73 | 0.88 | 85 / 20 |
| handsome (wanted or praised) | 8 | 0.59 | 0.50 | |
| target word | 8 | 0.65 | 0.50 | |
| American / Western / 1990 | 3 | 0.19 | 0.33 | |
| cap / cross | 4 | 0.74 | 1.00 | |

Where stated and revealed agree:
- **Yellow.** He said it 17 times; the measurement says it is the single strongest predictor. The images he called "too bright/white" average L\* 91 / b\* 13; the winners average L\* 84 / b\* 22. He even ranked F4dun_g2_suo first while calling it "a bit too yellow": his verbal threshold for "too yellow" sits *above* his revealed optimum. Target paper: L\* 80–86, b\* 21–27 (F3_g2, F4dun, F4bleed levels). Orig sits at L\* 93–95, b\* 10–13, which is why it loses.
- **Detail + feeling beats pure GO.** Every variant he praised as "true/perfect GO" but "simple/cartoony/lacks feeling" (g2_A, F4_g2low ×3, F4-on-1.5 ×3, orig) landed in the bottom third. "Detail" as praise has the highest ship rate of any theme (0.88). His own general note ("true GO falls 1–3, nostalgia feeling and palette trump pure GO") is borne out — but note it is a post-hoc description of rankings he had just made.
- **Proportions and AI errors disqualify.** 21 comments; they cost gpt-image-2 the three rounds it lost to Sunburst (eiti, paltas, and the mokykla/seima "proportions off" variants). gpt-image-2 draws single full-length figures with long legs or large heads under the F3/F4 "thick-set bodies" instruction; Sunburst draws bodies correctly.

Where stated and revealed diverge:
- **"1.5 is still best."** This was the brief's founding premise and the owner's explicit verdict before the survey. Blind, the 1.5 master is last or second-last in 9/12 rounds, and his comments on it are uniformly "too bright / too white / cartoony / too happy / over the top". Either the earlier verdict was an attachment to the shipped deck rather than a style preference, or seeing the F3/F4 batch moved his taste. The practical consequence is the same: the 520 shipped cards are *not* the target, and the remaining ~1,000 should not try to match them. Whether the 520 should eventually be re-rolled is his call; the data say he would rank most of them low against F5.
- **"Looks Western / American."** Stated as the main failure mode of the new models in the brief. In the rankings it appears in only 3 comments (sun_old klubas ×2, F4_sun klubas), all confined to the klubas card. Sunburst's broader losses are described as "feeling off", "flat / bland", "too bright", "high contrast" — a *finish* complaint, not an *ethnicity-of-the-people* complaint. The F3 people block fixed the Western read everywhere except klubas, where the subject itself (dancing hall + evening) carries it.
- **"Men should be austere but soviet-handsome."** F3/F4 asked for "broad plain faces, heavy features, thick-set bodies" and over-delivered: 8 comments ask for "chut chut more handsome", and the two best-liked people cards (F2_g2 seima, g2_old gydytojas) are the ones *without* the heavy-feature instruction. Revealed preference: plain clothes and composure, yes; heavy faces and thick bodies, no.
- **Float vs bleed.** Stated: "floating-on-paper preferred if the people are right." Revealed: bleed won 3/3 against its floating twin, all three ship-flagged, and he asked to save the prompt. A confound: the bleed images are also darker (L\* 78) and yellower, so part of the bleed win is paper coverage. Still, the stated preference should not be taken at face value.
- **House-of-culture override for klubas.** My hypothesis, not his; it did nothing. The klubas problem is target-word legibility ("looks like dancing"), which the shipped-prompt orig and the ref-image variant solved by showing the *hall* (stage, bar, entrance inset) rather than the dancers.

## 5. Model-level findings

- **gpt-image-2 is the production model.** Best mean Borda (0.62), best ship rate (0.51), 3 % last-place rate, and it follows composition instructions (floats when asked, bleeds when asked). Its one weakness is body proportions on single full-length figures (eiti, paltas, children in mokykla) — three of its four same-card losses to Sunburst.
- **Sunburst** is a credible fallback for single-figure cards (it won eiti and paltas outright, with correct proportions and caps) but ignores composition instructions, drifts "flat/bland", and failed the target word on minia twice. Reference images pull it back toward the chart layout (F4ref_sun_vestuves and F4ref_sun_klubas both floated / read correctly).
- **Flare** lost 4/5 with 0 ships ("bright, too simple", airbrush face, leg glitch). Drop.
- **gpt-image-1.5 with the new text** is "bang on GO" to him (lova #5 ship, gydytojas #1) but "cartoony" on people cards. Not a production option anyway (removed 1 Dec).
- **Quality low** loses 3/3. Stay at medium.
- **Reference images** (3 masters via images.edit) win 4/5 and lift Sunburst most. Worth an arm in the confirmation run; note the masters themselves are now low-ranked, so the benefit is layout/legibility, not palette.

## 6. What the data cannot say

- No test–retest: the repeat was recognised. Per-round rank differences of ≤2 are within the seed-noise floor and the attribute effects at that size (arrows, override, F3-vs-F4 on most cards) are undetermined.
- One rater, 12 rounds, ~65 distinct variants, each new image seen once: the attribute effects are confounded with per-image luck except where the same contrast repeated 3+ times (bleed, dun, low quality, g2-vs-Sunburst).
- The paper-tone effect is estimated from images whose tone was *not* independently controlled (only 4 dun/bright pairs); the optimum range above is interpolated from winners, not from a dose–response test.
- Partial unblinding of orig means its ranking carries some bias; the direction of that bias is unknown (he could be punishing the familiar or protecting it; his comments suggest the former was not happening).
- The owner's "beautiful" criterion is not operationalised; "detail" and "feeling" are the nearest coded proxies.

## 7. Production recommendation

**Model:** gpt-image-2, quality medium, 1536×1024. Sunburst only as a per-card re-roll fallback for single full-length-figure cards if F5 on gpt-image-2 still shows proportion errors in the confirmation run.

**Lead:** `F5` (full text in `f5_candidates.json`), which is F4 with the survey's corrections:
1. Paper: "warm yellowed dun paper" (the F4dun wording won 3/3 on g2; F4's "pale bright cream" is what made F4 lose to F3 on the same model).
2. People: "correct natural body proportions; austere, regular, plainly handsome faces; calm closed mouths; gaze resting slightly off the viewer" replacing "broad plain faces, heavy features, thick-set bodies". Keeps plain clothes, side-parted hair, headscarf.
3. "Working men in flat cloth caps" in the lead; also change `FIGURE_DRESS["worker"]` from "caps or bareheaded" to caps.
4. Composition: vignette with surroundings sketched in and fading to the paper — between F4's bare cut-out and F4bleed's full picture, because he ship-flagged both and praised "detail and feeling".
5. Suffix carries black arrows/callouts (cheap, consistent with the spec's charcoal callouts; the contrast was within noise).
6. "Soft shading" instead of "one soft shadow tone" (he found F4dun's shading "a bit much" but F3's "bang on"; the overshoot was in the darker variants, so the word stays mild).

**Sibling `F5D`** ("detailed soviet art aesthetic", the prompt he asked to save): identical except the composition sentence asks for a full edge-to-edge scene. Use it for place and workplace-scene cards (miestas, mokykla, turgus, workshop verbs); F5 for objects, clothing, persons, single-figure verbs.

**Where each content rule belongs:**
- Global lead (F5): paper tone, proportions, plainly handsome / austere, gaze off-viewer, caps on working men, black arrows.
- `FIGURE_DRESS["worker"]`: caps always.
- Per-card staging (deck_builder NOUN_STAGING / VERB_STAGING), not the lead: red cross on the hospital façade (ligoninė, gydytojas insets); klubas shown as the *hall* (stage, bar, entrance inset) with dancers secondary; minia as a dense standing crowd filling the frame (the two F4 minia failures were staging drift, not style); eiti motion-strip insets as whole standing/walking figures rather than legs only; hospital/clinic interiors with a visible red-cross kit.
- Guessability gate stays in human QA; the survey shows it decides rounds when style is close (miestas, klubas, minia).

## 8. Confirmation plan (15 cards, before the ~1,000)

Cards (spread across classes, including the survey failures):
- Places (F5D): 024_miestas, 036_mokykla, 050_turgus
- Workshop/worker verbs (F5D): 405_pjauti; single-figure verbs (F5): 366_eiti, 376_valgyti
- People (F5): 113_gydytojas (with cross staging), 090_seima, 108_minia (crowd staging), 137_vestuves
- Clothing/object/animal (F5): 066_paltas, 211_lova, 001_suo
- Abstract/other (F5): 147_karas, 454_letas

Arms: all 15 on gpt-image-2 medium (A). Five of them (eiti, paltas, klubas-substitute minia, vestuves, miestas) also as a B arm with the 3 reference masters via images.edit, and eiti + paltas also on Sunburst F5 (C) as the proportion fallback. ~25 images, under $1.

Owner review: blind, same web tool, 2–3 variants per card plus the shipped orig as control; ranking + ship flag + comment.

Pass criteria (all must hold):
1. ≥ 11/15 arm-A cards ship-flagged, and orig ranked below arm A on ≥ 10/15.
2. Measured paper tone on every arm-A image within L\* 80–87, b\* 20–28 (the winners' band). Outside it → adjust the paper words before the run, not after.
3. Zero "proportions/glitch" comments on the single-figure cards (eiti, valgyti, paltas). If any, route single-figure classes to Sunburst F5 (arm C) and check C passed on those cards.
4. Target word identifiable on all 15 without the label (the guessability gate), in particular minia and the place cards under F5D.
5. Both F5 and F5D accepted on at least one card each, otherwise collapse to the one that passed.
If refs (arm B) beat arm A on ≥ 4/5, make references the production default for Sunburst fallbacks only; on gpt-image-2 keep text-only unless B wins ≥ 4/5 there too (cost and pipeline complexity).

## Files
- `survey_rows.json` — the 91 analysed rows with attributes, observed composition, measured paper L\*/b\*.
- `analyse.py` — the analysis script (Borda, groups, contrasts, regression, paper tone).
- `f5_candidates.json` — F5 and F5D full text.
