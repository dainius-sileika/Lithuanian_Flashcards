# Pilot Round 2 review page (2026-10-18)

Published as a private claude.ai artifact: **Pilot Round 2** — https://claude.ai/artifact/L8RAjTX84hQvouHi6kviVb

- The 14 round-2 redraws (`out_phrases_v3/round2/`) at 1024 px, each with its round-1 picture (small),
  the owner's round-1 note (`redraw_list.csv` reason_owner), earlier round-2 rolls and the QA findings.
- Controls as on the round-1 pilot page: Situation yes/nearly/no, neighbour-fail toggle, stray toggle, note;
  general notes.
- db (capabilities db + user): verdicts in collection `pilot2/<key>` (with `by` = viewer id), general notes in
  `pilot2_meta/general`.
- A section with three phone-width backs (A2-0348, A2-0362, A2-1157) showing the new usage notes.

`build_page.py <repo> <out>` regenerates `index.html` from the repo data and `template2.html`
(derived from `a2_build/review_2026-10-17/template.html`); `media/` (JPEG copies) is not committed.
