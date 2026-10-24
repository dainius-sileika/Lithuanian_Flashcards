# Historical places and figures — implementation plan

Plan only (2026-10-17/18). Nothing rendered, no data or generator file changed. Follows the owner's decisions on `../REPORT_historical_places_figures.md`: all 26 places adopted; "surroundings, but try faces as best you can"; president = Adamkus as he looked in office (1998–2003, 2004–2009), anachronism accepted; Vytis / Cross of Vytis allowed; tram kept; hospital → 1939 Kaunas Clinics and Maironis bronze → 1928 Freedom Statue approved; six-render test approved.

## Files, in the order the executor applies them

1. `location_bank_additions.json` — 12 new entries for `style_lab/research/location_bank.json` (`go_settings.assign()` raises on an unknown `location_id`, so merge these first). Each place is described by features; none is named in the prompt.
2. `settings_rows.csv` — 29 rows for `style_lab/research/settings_assignments.csv` in its format (`key,location_id,mode,why`): the 26 places (incl. the two swaps), plus three optional rows (112, A2-1326, 138) marked OPTIONAL. Three of the 26 (A2-0654, A2-1347, A2-1370) were moved to the B1 pack on 2026-10-17; their rows are marked DEFERRED and apply when that pack ships.
   - Two pipeline facts the executor must know: (a) `deck_builder.prepare_settings` skips the bank line for any A1 place card whose note starts "Main picture:" — 035, 047, 048, 055 — so for those the place is written into the staging line itself; (b) `out_deck_a2/a2_adapter.py` passes `setting=""` for every A2 card. Either change its two calls to `setting=db.SETTINGS.get(key, "")` after `prepare_settings`, or rely on the staging lines, which already carry the place. The settings rows are still worth adding: they keep re-rolls stable and record the assignment.
3. `staging_rows.csv` — 38 rows: the staging line that actually reaches the prompt for every place, swap and likeness card (`file` says whether it goes into `card_notes.json` or `a2_build/a2_staging.json`), with what each line carries.
4. `RULES_precedent_likeness.md` — exact text: `PRECEDENT_RULE`, `LIKENESS_RULE`, where they go in `_prompt_openai`, and the emblem rule. The emblem text is given twice: as the replacement `FLAG_RULE` the owner asked for, and in the recommended executable form (`FLAG_RULES["emblem"]`, routed to the named cards only until T4/T5 pass).
5. `likeness_cards.csv` — 12 rows: every card that gets a figure or a named work, the person, the period, the feature sentence that fills `{features}`, the vetting reference into `../historical_likenesses.md`, the precedent description, the staging source, caveats. Every feature sentence is marked UNVERIFIED where it comes from photographs rather than a read text: the executor checks each against the portrait on the cited vle.lt page before fixing the words.
6. `test_plan.csv` — the six approved renders (T1 plane, T2 author, T3 basketball, T4 court + Cross of Vytis, T5 president = Adamkus + Vytis, T6 Freedom Statue control), each with its staging source, what the owner checks and the expected outcome. Judge with the PILOT_24 rubric: the word first, style second, "does the reference land" third. A render passes only if the word is still guessable.

## Stop rules

- If T5 is refused by the API, record it and fall back to the president card as staged now (anonymous), with the Seimas block inset and the emblem — the owner said anachronisms are acceptable, not that a refusal should be fought.
- If the Vytis garbles on T5 but the Cross holds on T4, keep the Cross in the emblem text and drop the knight sentence.
- If T1 and T2 pass on the word but no face lands, the likeness segment is kept (it costs nothing and the owner asked to try) and the ledger records the attempt.

## Cost

Test 6 × $0.0135 ≈ $0.08, with QA ≈ $0.14. Full application afterwards: 26 places + 3 swaps/optional + 9 likeness cards ≈ 38 renders × 3 tries ≈ $1.55, QA ≈ $1.10. Three deferred cards are excluded until B1.

## Owner decisions still open

- 138 komanda: may the football team become the 1939 basketball champions? (Optional row; drop it if not.)
- A2-0792 writer: Sruoga (proposed) or Binkis (already on 123) or Vaižgantas (cassock risk).
- The optional likenesses (113 Basanavičius, A2-0782 Gustaitis, 122 Čiurlionis): render after T1–T6, or skip.
