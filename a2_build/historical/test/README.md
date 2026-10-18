# Historical six-render test (A4, 2026-10-18)

Review page **Historical Test** (private artifact, db `histtest`, notes `histtest_meta/general`):
https://claude.ai/artifact/HyXgC3WshJceyH4JXBHBDr — the six renders beside the shipped card, the plan's judging
questions per render (yes / partly / no) and OK / Redo. **A5 (roll-out) waits for the owner's verdict.**

## Applied
- `go_generator.py`: `PRECEDENT_RULE`, `LIKENESS_RULE` (text of RULES_precedent_likeness.md §1), `FLAG_RULE_EMBLEM`
  registered as `FLAG_RULES["emblem"]` (§3b; the default `FLAG_RULE` is unchanged), `precedent=` / `likeness=`
  through `_prompt_openai` / `build_prompt` / `generate`, inserted after the setting block (§2).
- `historical.py` + `implementation/likeness_args.json`: per-card values; only the keys in `active` (the six test
  cards) reach a prompt. `deck_builder.build_call` and `a2_adapter.build_call_a2` add them; `FLAG_OVERRIDE` 35, 97 = emblem.
- `style_lab/research/location_bank.json` +12 entries; `settings_assignments.csv` +20 rows (OPTIONAL and DEFERRED rows
  of settings_rows.csv left out: 112, 138, A2-0667, A2-1326, A2-1357, A2-0654, A2-1347, A2-1370).
- Staging for the six test cards only (card_notes.json 012, 035, 097, 123; a2_staging.json A2-1297, A2-1769).
- Face words checked against the Wikipedia/Commons portraits (vle.lt portraits not reachable as images here) and
  corrected: Adamkus no spectacles, broad open face; Darius broad square face, Girėnas narrower oval face (the draft had
  them reversed); Binkis wears a tie. The precedent for A2-1297 no longer names the hall. 035 also carries the hand-scan gavel fix.

## Prompt diff
`implementation/prompt_diff_2026-10-18.txt`: all 1,400 production prompts rebuilt before and after; exactly 8 change —
the six test cards plus 106_zaidejas and 107_sirgalius (their new State Stadium settings rows, as the plan intends:
"106/107 by the bank"). 048 and 055 do not change: their notes start "Main picture:", so their place comes with the A5 staging.
No sentence or situation prompt changes.

## Renders and QA
`render_test.py` renders into this folder (the shipped pictures are untouched); `test_ledger.csv` records prompt,
likeness and refusals. T5 was **accepted** by the API. QA (`qa_histtest.csv`, with --limbs): 0 FAIL, 2 PASS, 4 WARN
(guess wording; 123 tiny garbled text on the pages; 097 read cold as "Lithuania" — the flags and the Vytis dominate).
