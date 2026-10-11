# F6.1 spot-check (09) — model decision and F6.2

30 cards never drawn in F-style, 3 strata x 2 models (G = gpt-image-2 medium, S = gpt-image-2.5-sunburst medium), blind pairwise through the real production path. Winner first; ship ticks G 26/30, S 28/30; neither shipped on gatvė and mokykla.

## 1. Decision rule applied

| test | threshold | result | verdict |
|---|---|---|---|
| S wins overall | >= 60 % | **19/30 = 63 %** | pass |
| S wins scene stratum | >= 50 % | **7/10** (figure 6/10, object 6/10) | pass |
| S glitch rate <= G's | hard glitches | **S 3/30 vs G 4/30** | pass |
| (finish defects, not in the rule) | | S 4 (highlights x3, backdrop figures x1) vs G 1 (duplicate faces) | S worse; addressed by F6.2 (a), (d), (e) |

Glitch tally from the owner's comments.
G hard glitches (4): pacientas "beds merge"; maitinti "no well for the lever"; tėvas "logic off, ratios, track ends at an odd place, booth out of scale"; laikrodis clock hands identical (mechanical). G finish/composition (1): turgus "two seller women exactly the same, uncanny".
S hard glitches (3): sriuba "cut-in-half bowl, shape wrong"; pjauti "glitch in inset 2"; maitinti "well is buggy". S finish/composition (4): karve "shiny, woman has highlights"; maitinti "slightly too shiny"; mokykla teacher inset "a little shiny"; policininkas "standing on a background".
Shared failures (both models, staging not model): gatvė reads as plaza; mokykla reads as a house; dainuoti insets show conductor hands; pacientas both actors at camera (S) / beds merge (G).

Paper: S median strict L* 84.0 / b* 19.2 = the owner's anchor (C_366_eiti 85.5/18.2) without any retune; G 85.5 / 26.9, still above the 18-23 target and drawing "chut chut dark / brighter paper" on 6 cards (sriuba, teatras, kunigas, ūkis, policininkas, arklys, maitinti). The S "dark outliers" (teatras 60.5, tėvas 60.5, policininkas 66.5, dirbti 66.5, mokykla 63.5) are all full-scene images where the paper fraction is 0.1-0.27 and the estimator picked scene fill; I checked teatras, tėvas, policininkas and dirbti by eye: the visible margins are the normal light cream. Not a paper problem. The owner's one G colour compliment (vairuoti, 85.5/25.6 "a good shade, better than the dark dark, better than the light") sits inside S's natural range on lightness; his seven "slightly brighter colour is good" comments are all on S.

Other S evidence: 1st in 3/4 F6 rounds; 28 ship ticks vs 26; "feeling is right/correct" x3; correct proportions on every F5/F6/F6.1 draw. Cost $0.0135 vs $0.044 (520 cards: ~$7 vs ~$23), ~2x faster.

**Production model: gpt-image-2.5-sunburst, quality medium, 1536x1024**, under one condition: the matte amendment must be verified on the first 30 production cards. If 3 or more of 30 show specular highlights on skin, hair or metal after F6.2, test quality=high on 10 of them before falling back to gpt-image-2. One model for the whole deck; add "deep, dark brick-red" to BARS_RULE so Sunburst's scarlet bands match the shipped dark red.

## 2. F6.2 amendments (drop-in text in `F6_2_amendments.json`, with the assembly position of each)

(a) **Matte finish.** Lead: "dead-matte gouache fills with soft shading on every surface"; suffix: "dead-matte offset print ... flat tone on skin, hair, cloth and metal". New `MATTE_RULE` after PLAUSIBILITY_RULE: every surface dead-matte as absorbent offset paper prints it; skin, hair, fabric, leather, metal, glass, water, polished wood carry flat ink tone and one soft shadow tone only.
(b) **Two main actors.** Lead gaze sentence rewritten to cover group / two main figures / lone figure; new `GAZE_PAIR_RULE` after the dress class: of two main figures one faces the viewer, the other looks at the task, the first figure or into the scene.
(c) **Main image carries the word.** New `MAIN_MEANING_RULE` after the staging/setting group: the main picture alone makes the word obvious; the subject is the largest, most central element in its most recognisable form and defining action; insets only support. Both composition sentences now say "large and central". This is also the first principle of the staging guide, because the three failures (gatvė, mokykla, šokti) were staging/setting problems as much as prompt problems: the Setting line (a Kaunas boulevard; a wooden manor school) took the picture over.
(d) **Distinct faces.** "each person a different individual" in the lead; new `DISTINCT_FACES_RULE` after the dress class.
(e) **Integration.** `SETTING_GUARD` replaced: people stand inside the place, feet on its ground, scaled to doors/furniture/vehicles, same flat light, setting continuing behind and between them.
(f) **Mechanical.** `PLAUSIBILITY_RULE` rewritten WITHOUT named props: the F6.1 text's example "a well-sweep stands over its timber well-head" primed a well onto maitinti on both models. Wells are now described only in the staging of cards about wells or farmsteads; the global rule keeps generic clauses (hanging things on racks/hooks, clear doorways, furniture on the floor, usable grips, machines whole and scaled to people, resting animals alive). Clock: staging line for 246_laikrodis with three insets at clearly different times. Verbs: a default inset note for verbs outside MOTION_STRIP_ROWS (defining detail close-up, second angle, result) so the generic 3-frame strip stops appearing on non-locomotion verbs (dainuoti).
(g) **Paper.** No wording change for Sunburst; it is on the anchor. Bands darkened (BARS_RULE colour words). Lead is 261 words after trimming "as in a documentary photograph" and the surface list (moved to MATTE_RULE).

## 3. Staging lines delivered (in the JSON `staging_lines` and `staging_guide.md`)
027_gatvė (roadway, centre line, zebra, kerbs, traffic as the subject), 036_mokykla (long rows of identical windows, flagpole, entrance steps with a stream of satchel children, bell, schoolyard), 411_dainuoti (open mouths and songbooks; insets replace the strip), 408_šokti (couple in full motion, skirt flaring, feet mid-step; a three-phase dance-step strip), plus 246_laikrodis, 430_maitinti, 114_pacientas, 050_turgus.

## 4. Open items
- Verify matte on the first 30 production cards (condition above).
- MAIN_MEANING_RULE vs Setting lines: expect fewer setting takeovers; if a place card still reads as its setting, the fix is the staging line, not the lead.
- Lead length 261 words: stable so far (F6 216, F6.1 254 both performed); if print texture thins, cut the physiognomy clause first.
- The owner's "slightly busy in detail, acceptable" on ūkis: watch full-scene cards for overcrowding; MAIN_MEANING_RULE's "large and central" should help.
