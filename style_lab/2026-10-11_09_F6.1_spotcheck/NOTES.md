# 09 — F6.1 production spot-check (2026-10-11)

**Why:** Fable scored the owner's F6 check (`../2026-10-10_08_F6_roll/results/analysis_fable.md`): 5 pass, 1 partial
(paper slightly too yellow), 2 fail on mechanics (insets, plausibility glitches), no style failures. Verdict: style
settled, ship to production as **F6.1** (`../2026-10-10_08_F6_roll/results/production_spec_F6_1.json`). The model
choice was left open: Sunburst won 3 of the 4 F6 rounds it was in and is 3.3x cheaper, but n = 4 and all single-subject.

**What changed in production (go_generator / deck_builder / go_settings / card_notes.json):**
- F6.1 lead + suffix, vignette and full-scene versions (`LEADS`); paper "faint yellow cast"; lone-figure gaze
  near-frontal; group gaze as a distribution.
- Dress classes: worker (caps), professional (white coat + red cross, teacher with pupils, smock), civilian (for the
  setting/weather), new **formal** (Sunday best: church, wedding, theatre, social dance).
- Inset frame consistency, explicit left/right motion strip (walk, run), plausibility rule, arrow rule.
- Per-card staging lines (`card_notes.json`, from the F6 roll + the owner's content notes: family meal not potato
  harvest, teacher with pupils, dark rye bread, no arrow at a refugee, well-sweep over a well, live hare).
- Real Lithuanian settings on 82 of 237 scene-capable cards, hand-assigned by the researcher from the location bank
  (`style_lab/research/settings_assignments.csv`; keyword auto-matching was tried first and paired a town with the
  Hill of Crosses and a park with a bog, so it is only a drafting aid now: `go_settings.suggest`).

**Run:** 30 cards never drawn in F-style, 3 strata (10 scene, 10 figure, 10 object/animal/clothing) x 2 models
(G = gpt-image-2 medium, S = gpt-image-2.5-sunburst), built through the real production path (`gen.py`). ~$1.73.
**Paper (strict):** G median L* 85.5, b* 26.9 (still above the 18–23 target); S median L* 84.0, b* 19.2 (on target).
**Decision rule (Fable):** Sunburst becomes the production model if it wins >= 60 % overall AND >= 50 % of the scene
stratum AND its glitch rate <= G's; else gpt-image-2. One model for the whole deck.
**Review:** private artifact https://claude.ai/artifact/AYbuoYm4s7qJsLb5fZXKpP (30 rounds, blind pairwise).
