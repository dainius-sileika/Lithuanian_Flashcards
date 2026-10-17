# out_phrases_v3 — bubble-free "situation" renders (2026-10-17)

Pilot of `a2_build/PILOT_24.md`: the 24 hardest restaged phrase cards + 10 extras (9 question
words, 374 galvoti), drawn under the situation grammar (commit aa87382) by `gen.py`
(gpt-image-2.5-sunburst, medium, 1536×1024). The bubble renders in `out_phrases/`,
`out_phrases_a2/` and `out_deck_f62/374_galvoti.png` are untouched; they move to
`_superseded/` only after the owner passes the pilot. The other ~133 restaged cards are
planned (`plan.json`, 167 jobs) but NOT rendered — they wait for the owner's verdict.

Renders paid: 37 (34 first passes + 3 re-rolls: A2-0114 ×1, A2-0115 ×2; old versions in
`_rerolled/`).

## QA (`qa_v3.csv`, qa_images.py situation checks, gpt-5.6-luna)

**33 pass the hard gate, 1 FAIL.** No bubble or floating symbol in any of the 34; no lettering leak.

- FAIL **A2-0115 koks** (what kind of): the caption-blind neighbour test picks *which (kuris)*
  with a clear margin on all three renders. Three different cups in front of a customer reads as
  "which one". This is the staging, not the render — owner/Fable to re-stage koks vs kuris.
- A2-0114 kiek: first render read as the price phrase (clear); after 1 re-roll the margin is slight (WARN).
- Near-synonym WARNs (slight margin, left to the owner's neighbour toggle): Ačiū → *Thank you very
  much*; Atleiskite → *Excuse me, please…*; Ar galite man padėti? → *Could you help me, please?*;
  Nieko tokio → *it's nothing*; Nekalbu lietuviškai → *I don't understand*.
- Stray-act WARNs: Sveiki and Geros kelionės (a wave), Nėra už ką (hand on chest), Kas tas žmogus?
  (thumb-up), Kaip lietuviškai …? (pointing finger). Pseudo-text on papers: 374, A2-0352.
- Observation: most single scenes still carry 2–3 small insets, because the house-style lead
  describes insets; the situation grammar asks for one scene. Owner to judge on the page.
