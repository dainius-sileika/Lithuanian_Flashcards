# 07 — F5 confirmation run (2026-10-10, night)

**Why:** Fable's analysis of the owner's blind survey (06) recommended F5 (vignette) and F5D (full detailed scene) on
gpt-image-2 medium, to be confirmed on 15 fresh cards before the remaining ~1,000.
**Arms (29 images, `img/`, `plan.json`, generator `gen.py`, full prompts in `gen_log.jsonl`):**
- A: all 15 cards, gpt-image-2, F5 (F5D for miestas, mokykla, turgus, pjauti); per-card staging notes for
  gydytojas (red cross), minia (dense crowd), eiti (whole-figure motion strip).
- B: eiti, paltas, minia, vestuves, miestas with the three reference masters (images.edit; layout/legibility only).
- C: eiti, paltas on Sunburst (proportion fallback).
- L: seima, vestuves, gydytojas, minia, valgyti, paltas, miestas with a sourced Lithuanian people block (F5L/F5DL,
  `f5L_prompts.json`) from Fable's research `lithuanian_appearance_research_fable.md` (VLE/Česnys 1952–55 survey,
  Tarakanova/Terentyeva/Cheboksarov 1956, Coon 1939, Deniker 1900, NatGeo 1976 map; 1975–85 everyday dress).
**Paper tone (`paper_tone.json`, Fable's method):** arm A in the target band (L* 80–87, b* 20–28) on only 3/15 —
yellowness on target, lightness low (63–78). The method reads scene pixels as paper on full-bleed cards, so it
overstates darkness there; eiti and karas are visibly darker tan. Fable's criterion 2 therefore fails as measured.
**Review:** private artifact https://claude.ai/artifact/6hbrmeL7vhv4ceskbKD1tL (same tool as 06), 15 rounds,
orig blinded in every round; source `web/index.html`, `web/rounds.json`, key `web_key.json`.
