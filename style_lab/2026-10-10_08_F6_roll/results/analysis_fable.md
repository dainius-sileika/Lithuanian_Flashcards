# F6 roll (08) — scoring and production decision

34 images, 14 rounds, blind, orig in every round. Arms: A = F6/F6D gpt-image-2 medium; A2 = second seed of A (minia, mokytojas); Y = F6y/F6Dy (one notch warmer paper); C = Sunburst with the F6 text (eiti, duona, lėtas, paltas). Paper measured with the strict estimator (`style_lab/tools/papertone2.py`, `paper_tone_strict.json`).

## 1. Scoring against the 7 pass criteria (`next_roll_design_fable.json`)

| # | criterion | result | verdict |
|---|---|---|---|
| 1 | better paper arm ship-flagged >= 12/14; orig below it everywhere | A ticked 11/14 (+ senelė "perfect" with the box unticked = 12); Y 10/14 (+1). Best-of-A/Y shipped on **14/14**. Orig **last in 14/14**. | **PASS** (A alone is on the line; its two misses are plausibility glitches, not style) |
| 2 | strict paper median L* 83–90 / b* 20–26, fewer dark/bright words | A: median L* **85.5** (77.5–87.5), b* **25.7** (23.3–31.6). Y: L* 85.5 (81.5–89.5), b* 27.5 (18.9–30.7). Lightness in band for both; yellowness over the band on 6/14 A and 9/14 Y. Words: "tad brighter" x2 (senelė, both arms), "could be a bit lighter" x1 (Y eiti); zero "too dark". Owner's new anchor: **C_366_eiti = 85.5 / 18.2**, "the amount of yellow we should aim for". | **PARTIAL** — lightness solved; yellowness one notch high. Retune to L* 85–88 / b* 18–23. Y (warmer) lost 5–9 to A, so the warmer wording is dropped. |
| 3 | zero head-position comments on multi-person A/Y cards; minia shipped in >= 1 of 3 draws | Minia A shipped ("most varied... doesn't feel weird"), A2 shipped; Y "too many facing away". Seima, vestuvės ("over the shoulder is a nice touch"), mokytojas, senelė, pirkti: no gaze comments. Single-figure: paltas A/Y "slightly less away", C "too far away". | **PASS** for groups; single-figure gaze needs one notch toward frontal (done in F6.1). |
| 4 | zero duplicate-inset comments; eiti strip alternates; lėtas hare awake | eiti: C and Y "two right foot forward" — the staging line did not hold; vestuvės: one inset with a different frame; lėtas A: hare "looks dead". | **FAIL** (3 cards) |
| 5 | target word identifiable on all 14 incl. fresh | All identifiable; Y karas arrow "pointing at the boy" is an arrow-target error, not a subject error. | **PASS** |
| 6 | no "doesn't look Lithuanian/USSR" on A/Y; >= 2 positive | Zero negatives on A/Y. Positives: seima Y "right kind of beautiful", mokytojas A2 "handsome actors", lėtas C "best target language"; bažnyčia/namas accepted as Lithuanian scenes. The owner now asks for *more* Lithuanian setting (2/3–3/4 of cards in real places): a request for the next layer, not a complaint. | **PASS** |
| 7 | zero proportion/glitch on single-figure cards | Proportions: **zero** complaints across 34 images (third run in a row since the wording fix). Physical plausibility: A eiti table in doorway, A namas hanging well-sweep, Y namas sweep without a well, A duona spoon behind hook, Y duona "just spoons", A lėtas dead hare = **5–6 of 28 A/Y images (~20 %)**. | proportions **PASS**; plausibility **FAIL** (new category) |

**Score: 5 of 7 pass, 1 partial; both failures are content mechanics (insets, plausibility), none is style.** Orig is beaten 14/14 and the owner's general verdict is "very good set... still minor adjustments".

## 2. Verdict: ship to production

No further style roll. Three runs have converged: paper lightness, people, proportions, gaze distribution, composition (F6/F6D) and the Lithuanian block are settled and stable across seeds (A vs A2 are rank neighbours on both cards). What remains is (a) a one-notch yellow retune, (b) a single-figure gaze notch, (c) content-mechanics rules that belong in go_generator's rule blocks rather than in another style experiment, and (d) the per-card setting line the researcher is building. These go in as **F6.1** and are checked in the 30-card production spot-check, which also settles the model question.

Expected production QA load: ~20 % re-rolls for plausibility/inset mechanics, falling as the new rule blocks bite. That is within the spec's "bias hard, then catch the misses" model.

## 3. Arm comparison

- **A vs Y:** 9–5 to A on rank; A also took both minia draws and karas. Y won seima (a more everyday woman) and pirkti/eiti narrowly. The warmer paper bought nothing; drop it.
- **A vs A2 (seed noise):** minia 1–2, mokytojas 1–3 with A2 "handsome actors, good copy". Rank neighbours; the gaze distribution is stable across seeds.
- **C (Sunburst):** 1st in 3/4 (eiti, duona, lėtas) with the strongest praise of the run; 3rd on paltas for gaze. Its paper (85.5 / 18–25) is the owner's anchor. Its bands render a brighter scarlet than gpt-image-2's dark red.
- **orig:** last 14/14, "old copy" x12.

## 4. Model decision: not decidable on n = 4; settle it in the spot-check

For Sunburst: 3/4 first places with the run's warmest comments; paper is the anchor without any retune; correct proportions on every F5/F6 draw; $0.0135 vs $0.044 (about $7 vs $23 for the 520 re-render) and ~2x faster.
Against: the four C cards were all single-subject (one man, a loaf, a tortoise, a coat), exactly the card type Sunburst was always good at. Its earlier losses were on multi-person and scene cards (full-bleed drift, "flat / bland", klubas Western, minia target-word drift) and on gaze (paltas, this roll). Its band colour differs visibly from gpt-image-2's, so the deck cannot mix models.

Decision rule (`production_spec_F6_1.json -> model_decision`): dual-render the 30-card spot-check on both models ($1.73 total), stratified 10 multi-person/scene (F6.1D), 10 single-figure, 10 objects/animals/clothing; blind pairwise with ship flags. Sunburst becomes the production model if it wins >= 60 % overall **and** >= 50 % of the multi-person/scene stratum **and** its plausibility-glitch rate is no worse; otherwise gpt-image-2. Whichever wins renders all 520 and everything after. If Sunburst wins, add "deep dark brick-red" to BARS_RULE and re-measure paper on its first 30.

My prior: 55/45 that Sunburst passes, because F6's fully specified text has removed the reasons it used to fail; the multi-person stratum is the real test.

## 5. F6.1 (full text in `production_spec_F6_1.json`)

Changes vs F6:
1. Paper: "light aged cream paper with a **faint** yellow cast" (was "soft"), lead and suffix. Target strict L* 85–88 / b* 18–23 (anchor C_366_eiti).
2. Lone-figure gaze: "a lone figure stands near-frontal, face turned only a little, eyes just past the viewer's shoulder", beside the unchanged group distribution.
3. Clothes "chosen for the setting and occasion" (bažnyčia in worker-blues).
4. Suffix: insets "all in the same ruled frame"; black arrows kept. Plausibility and arrow rules live in their own blocks (below) rather than the suffix, to keep the lead from growing further. Lead is 254 words (F6 was 216); if the spot-check shows diluted print texture, shorten the physiognomy sentence first.
5. Setting hook: a per-card `Setting:` line after the staging line, filled from the researcher's bank (format and guard in the spec); roughly 2/3–3/4 coverage as the owner asked; for object cards the setting goes in an inset so it never competes with the target word.

## 6. go_generator rule-block replacements (text in the spec)

- **FIGURE_DRESS**: worker (caps always); professional (white coat + small red cross on kit or clinic; teacher with pupils present; shop assistant in white smock); civilian (dressed for setting and weather); **new `formal`** class (Sunday best) with a routing note for bažnyčia, vestuvės and other occasion cards.
- **INSET_RULE**: same thin ruled frame for all insets; each a clearly different moment, object or angle.
- **MOTION_STRIP_RULE** (new, strip verbs only): three explicit phases: feet together; LEFT foot forward with right arm forward; RIGHT foot forward with left arm forward.
- **PLAUSIBILITY_RULE** (new): every object complete, attached and in working order; well-sweep over its well-head; utensils on a rack or hooks; doorways clear; furniture on the floor; tools in a usable grip; a sleeping animal visibly alive, curled, eyes closed, ears relaxed.
- **ARROW_RULE** (new, arrow cards only): arrows and callouts in black ink point only at the subject the card teaches or its direction of motion.
- All positive phrasing; zero negations in the new blocks.

## 7. Text policy (pilot, in the spec)

NO_TEXT_RULE stays in production. Pilot 20 cards x 2 renders through the existing `_exact_text_rule(spec, exclude)` with a researcher-compiled whitelist (card, exact string, style, source): board arithmetic and curriculum-true formulas for 1981 (7 x 8 = 56, S = v t, F = m a, H2O, NaCl), shop/hospital/bread signs in uppercase Lithuanian, two or three interwar book spines (ALTORIŲ ŠEŠĖLY, METAI, DĖDĖS IR DĖDIENĖS), a masthead, an address block. Lithuanian only, diacritics required (ą č ę ė į š ų ū ž), at most two strings per card, the target word still never written. **Open owner decision:** currency on price tags in a free-Lithuania 1981 (Lt/ct vs rubles), left blank until he decides. QA gate: vision-model read-back must equal the whitelisted string exactly, diacritics included; zero stray lettering; owner checks period plausibility. Lift the rule per card *class* only at >= 90 % exact across the 40 pilot renders with 0 stray-text cards; everything else stays wordless.

## 8. Content notes (in the spec)

seima = everyday meal at the kitchen table as the main picture, potato gathering demoted to an inset; mokytojas = teacher(s) with three or four pupils at desks, board with simple true arithmetic or a diagram; duona = dense dark rye loaf, near-black crust, dark crumb, no white loaf on the card; batonas = its own card with a long pale wheat loaf; karas = drop the arrow, or point it at the burning village/soldier column; namas = sweep standing over a timber well-head; lėtas = hare running in the inset, any resting hare clearly asleep; vestuvės = identical inset frames; eiti = motion-strip rule + clear corridor; paltas = lone figure near-frontal; bažnyčia = formal dress class.

## 9. Settled / still open

Settled: model-family behaviour under F6 text; paper lightness; the Lithuanian people block; proportions; group gaze distribution; F6/F6D composition split; black arrows; orig retired as a reference ("old copy" x12).
Open: yellowness one notch (F6.1 retune, verify on the spot-check); gpt-image-2 vs Sunburst (dual-render spot-check); plausibility/inset rules' effect (spot-check glitch rate vs this roll's ~20 %); text pilot; setting-bank coverage; currency decision.
