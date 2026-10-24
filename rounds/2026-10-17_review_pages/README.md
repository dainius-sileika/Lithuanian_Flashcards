# Review pages, 2026-10-17

Published as private claude.ai artifacts (verdicts saved in each artifact's db):

- **Bubble-free Pilot** — https://claude.ai/artifact/AVoEVmiY3YdLM1VvHvSE6D — the 34 pilot cards
  (`out_phrases_v3/`), PILOT_24 rubric: Situation yes/nearly/no, neighbour fail, stray act, note; general notes.
  db: `pilot/<key>`, `pilot_meta/general`.
- **A2 Additions and Fixes** — https://claude.ai/artifact/DguRLAm5r1rBuBEPuoT696 — the 43 benchmark IMG additions
  (`out_deck_a2/A2-1879…1957`) and the 5 A1 re-rolls with their before versions. db: `adds_review/<key>`,
  `adds_meta/general`.

`build_pages.py <repo> <out>` regenerates both `index.html` files from the repo data and `template.html`;
`media/` (1024 px JPEG copies of the PNGs) is not committed.
