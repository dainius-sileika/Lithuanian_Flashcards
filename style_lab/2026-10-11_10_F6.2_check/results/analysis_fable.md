# F6.2 render check (10) — GO / NO-GO for the full re-render

30 cards (the 09 spot-check set) re-rendered on gpt-image-2.5-sunburst, medium, 1536x1024, with F6.2 as implemented (matte lead + MATTE_RULE, MAIN_MEANING_RULE, DISTINCT_FACES_RULE, GAZE_PAIR_RULE, new SETTING_GUARD, prop-free PLAUSIBILITY_RULE, dark bands, VERB_INSET_DEFAULT, card_notes staging for the 09 failures). Inspected at full resolution (`results/look/f62_*.jpg`, crops).

## (a) Matte condition — PASS
Skin and hair: flat tone on every face I checked (minia x2 crowds, mokytojas, pacientas nurse, kunigas, policininkas pair, menininkas, sriuba insets, vairuoti). Metal and glass: policeman's baton, telephone bakelite, clock rim, truck mirror all read as flat ink with one shadow tone. Borderline sheen on 2 objects where a printed illustration would also show it: batai (toe-cap gloss of polished leather) and obuolys (one small apple highlight). 0 of 30 on skin/hair/metal; the 09 complaint ("THIS DECK HAS A GENERAL HIGHLIGHT ISSUE", karve woman, maitinti well, mokykla inset) is gone on the same cards. Threshold was >= 3/30 to trigger quality=high; no test needed.

## (b) Hard glitches — 2 of 30, both staging-level, none model-level
- **183_sriuba**: the "cut-in-half bowl" is back (second bowl sliced open showing soup inside). Cause: the food class grammar sentence "Draw it whole, with a cut or sliced view beside it" is applied to a liquid dish. Fix below (staging line for sriuba; a note for go_grammars).
- **046_teatras**: the stage set carries a heraldic banner with a bird device on a red field, close to a state eagle. FLAG_RULE covers national emblems, not stage props. Fix below (staging line: plain painted backdrop, no banners). Also: this interior card received an EXTERIOR Setting line (Laisvės alėja boulevard), which the model pushed into an inset; harmless here but see settings note.
Everything from the 09 list is now right: eiti corridor clear; laikrodis three insets at three different times; maitinti has no well; pacientas one patient as subject with the nurse looking at the patient (a second occupied bed is visible behind, acceptable); tėvas funicular car and track plausible; policininkas pair standing in the street among the cars; turgus stallholders distinct in age, build and headscarf; pjauti insets are two saw strokes with opposite arrows plus the result.

## (c) Main picture carries the word — PASS on the five failures
gatvė: roadway with centre line, zebra, Zhiguli, Ikarus, kerbs — reads "street". mokykla: two storeys of identical windows, flagpole, entrance steps with a stream of satchel children, bell, football goal — reads "school". šokti: woman spun out, skirt flaring, feet mid-step, band and tables behind — reads "dance". dainuoti: choir of six with open mouths and songbooks, notes in the air — reads "sing". stotis: station building with clock, platform, green locomotive and carriages, passengers with suitcases — reads "station". No remaining card in the 30 fails the two-second test; teatras, ligoninė, turgus, ūkis, bažnyčia-type scenes are all unambiguous.

## (d) House rules — PASS
Two-main-figure gaze: pacientas (patient to viewer, nurse to patient), policininkas (one to viewer, one to traffic), menininkas (one to viewer, one at the easel), mokytojas (one to class, one at board). Distinct faces: minia (two seeds), turgus, dirbti, dainuoti, teatras audience — varied age, hair, build. Setting integration: policininkas and tėvas now stand in their places at the right scale. Clock: three different times. Lithuanian detail without prompting conflict: koplytstulpis roadside shrine on ūkis and arklys, Vilnius cathedral behind kunigas, log granary on pjauti, troba-type houses on namas/ūkis.

## (e) Paper — PASS
Strict median L* 85.5 / b* 18.9 (target 85–88 / 18–23). Object/figure cards 84.5–89.5 / 16–22. Lower readings (ūkis 77.5/6.3, teatras 77.5, gatvė 78.5/12, turgus 82.5/12, kunigas 84.5/9.6) are full-scene images where the estimator measured scene fill (paper fraction 0.1–0.35); their visible margins are the normal light cream. No "too dark" or "too white" card in the set. (`results/paper_tone_strict.json`.)

## Verdict: **GO** for the ~520-card re-render on Sunburst/F6.2
No prompt or rule change. Three staging corrections go into card_notes before the run (text in `card_notes_existing_proposed.json`):
1. `183_sriuba` — full steaming bowl as the subject, spoon in it, rye bread beside; insets ladle-from-pot, canteen eaters, a second kind of soup. (Grammar note for later: the food "cut or sliced view" clause should apply only to solid foods; liquids and dishes get "served in its bowl or on its plate". Not needed for this run since the staging line overrides it.)
2. `046_teatras` — plain painted landscape backdrop and red curtains, no banners or heraldry on the stage set.
3. `430_maitinti` — the card_notes line (hens) contradicts VERB_STAGING 430 (mother spoon-feeding a baby, "feeding PEOPLE"); the render followed VERB_STAGING, which is right (lesinti = birds, šerti = livestock). Replace the note with a people-feeding line. The wordlist subject phrase for 430 still says "scattering grain to chickens"; leave the CSV alone tonight but it should be corrected in the next wordlist edit.

Two process notes for the run:
- `go_settings.assign(..., skip=set(CARD_NOTES))` suppresses the Setting line on every card that has a staging note. With the proposed notes covering ~200 cards, that would remove most of the owner's "real Lithuanian place 2/3 of the time". Change the skip to the `_settings_embedded` list in the proposed JSON (keys whose note already names the place) so the bank line still appends after the note everywhere else; the notes are written to tolerate it ("... is the subject; the buildings of the setting stand behind").
- Setting mode: teatras shows an exterior Setting line attached to an interior main. `settings_assignments.csv` has a `mode` column (exterior / interior / inset); the engine should prefix interior-mode and inset-mode lines ("Through the window: ...", "In one inset: ...") so a bank entry can never redraw an interior card as a street. One-line change in go_settings; if not done tonight, QA will catch the few cases.

Expected QA load: with style settled and the mechanics rules in place, this set shows 2/30 staging glitches and 0 style complaints; budget ~10 % re-rolls over the 520.
