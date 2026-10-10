# 06 — blind ranked survey (2026-10-10)

**Why:** the owner: "sometimes it's hard to intellectually determine this" — infer his real preference and
its criteria from blind rankings rather than from descriptions.
**Design:** by Fable (`survey_design.json`, generator `build_survey_design.py`): 13 rounds, 7–8 variants each,
the shipped 1.5 master (`orig`) blinded in every round as control, round 12 = unflagged repeat of round 2
(test–retest), two same-settings duplicates (`F4_g2b_seima`, `F4_sunb_vestuves`) to measure seed noise.
New prompt family **F4** (F2 print paragraph + F3 people block, pale bright cream paper, cut-out vignette) and
one-attribute edits: F4dun (paper), F4bleed (composition), F4arrow (black arrows); one klubas subject override
(house-of-culture hall); reference-image variants (images.edit with the three favourites); gpt-image-1.5 + F4 to
separate model from prompt; quality low; flare.
**New images:** 53 in `new/` (`gen_new.py`, log with full prompt text in `gen_log.jsonl`).
**Presentation:** `make_rounds.py` re-encodes every image (orig included) through one resize+JPEG pipeline,
shuffles positions and letters per round → `rounds/round_NN.jpg`. **`survey_key.json` is the unblinding key.**
**Owner's answers / analysis:** to be added (`responses.txt`, `analysis.md`).

**Web survey (replaces the chat sheets):** published as a private artifact
https://claude.ai/artifact/AW382atWR4BJXuVLgkuAh6 — drag-to-rank per round, "would ship" toggle, a comment per
image, autosaving to the artifact's database (`responses/r01`…`r13`, `responses/general`). Source in `web/index.html`,
images `web/img/<opaque id>.jpg` (same 1200x800 re-encode for every variant), public round data `web/rounds.json`,
unblinding key `web_key.json` (opaque id → variant). The chat sheets in `rounds/` and `survey_key.json` are superseded.

## Owner's results (2026-10-10, evening)
Raw answers `results/owner_raw_responses.zip`; unblinded `results/owner_unblinded.json`. Round 12 (hidden repeat)
was recognised and left unranked; round 9 came back in its initial order (comments consistent with it).
Analysis by Fable: `results/analysis_owner_fable.md` (+ `survey_rows_measured.json` with measured paper L*/b*,
`analyse.py`). Headline: blind, the owner ranks the shipped 1.5 master last or second-last in 8 of 12 rounds
("too bright / too white / cartoony") — the target is no longer the 1.5 look. Yellower dun paper is the strongest
predictor (winners L* 80–86, b* 21–27); detail + nostalgic feeling beats pure GO; full-bleed beat floating 3/3;
quality low lost 3/3; heavy-feature people wording caused proportion errors and "more handsome" requests;
gpt-image-2 medium is the best model; flare had zero ships. Next prompt candidates F5 (vignette) and F5D
(detailed full scene): `results/f5_candidates.json`; 15-card confirmation plan in the analysis.

## Standalone survey for friends
`standalone/GO_style_survey.html` (12.6 MB, self-contained, offline; same 99 images and opaque ids, order
re-shuffled per respondent; progress kept in the browser; end screen saves `go-survey-<name>.json` or copies
the same text). Put returned files in `results/friends/` and run `results/ingest_friends.py` to unblind.
`standalone/template.html` is the source (images, rounds and SortableJS 1.15.2 are inlined at build time).
