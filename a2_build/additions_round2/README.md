# Additions round 2 — redraws from the owner's 2026-10-17 review

Plan only. No picture was rendered and no data file was changed. The executor applies this folder.

## Files

- `redraw_list.csv` — 15 cards (14 A2 additions + 338 pėda): key, Lithuanian, English, the new staging line (main + insets, in the `card_notes.json` / `a2_staging.json` sentence form: "Main picture: … ; the X is the subject. Insets: a; b; c."), `edit_or_reroll`, the owner's note verbatim, and a planner note.
- `order_adjacency.csv` — 10 PIN_AFTER proposals for `build_study_order_v2.py` (mama after motina, tėtis after tėvas, and the family / top-bottom / cloze pairs).

## How the executor applies it

1. **Staging lines.** The A2 addition cards (A2-1879…1957) have no staging line today — they render from `subject_phrase_EN` plus the class inset menu, which is why the model chose the insets itself. Put each `new_staging` into `a2_build/a2_staging.json` `notes[key]` (the adapter inserts it after the Subject sentence). For `338_peda` the line goes into `card_notes.json` `notes["338_peda"]`, and `master_wordlist.csv` #338 `card_text` gains the doorframe numerals (see the planner note).
2. **Edit vs re-roll.** `edit_or_reroll` names the primary path. "edit" = the gpt-image edit endpoint (`client.images.edit`) with the existing PNG (`out_deck_a2/<key>.png`, or `images/338_peda.webp` → PNG) as the input image and a mask that is transparent only over the inset box(es) named, opaque everywhere else; the prompt is the house lead + that inset's sentence from `new_staging` + `NO_TEXT_RULE` + `ANATOMY_RULE` (and `ANATOMY_PROPS_RULE` once pilot round 2 lands). `go_generator.py` has no edit path yet; a small script `a2_build/additions_round2/edit_inset.py` is the place for it (not written here — the executor owns the code). Inset boxes are the ruled frames in the right-hand column of every 1536×1024 render; read their pixel bounds off the PNG before masking. QA the edited card with `qa_images.py` like any re-roll. If the edit changes anything outside the mask, or fails twice, fall back to the full re-roll with the same staging line — the "keep as rendered" clauses in the staging describe the current picture so the re-roll stays close.
3. **Rules in force.** Pilot round 2's CONVERSATION_GAZE, PANEL_CONTINUITY and ANATOMY/PROPS are assumed; the staging lines name hands where a gesture depends on them and say "the same mother/father/coach" where insets share a figure. 338 keeps `flag="imperial"`.
4. **Likeness.** A2-1917 (pilot) is also a Part B likeness card (Darius and Girėnas, 1933) — render it after the precedent/likeness segments exist (`a2_build/historical/implementation/`), not before.
5. **Study order.** Add the `order_adjacency.csv` rows to `PIN_AFTER` in `build_study_order_v2.py` (`{"pinned_key": "after_key"}`; the scheduler already supports several pins and holds a pinned card until its anchor is placed, then puts it immediately after). Rebuild `study_order.csv` and check the family cards sit in pairs.

## Owner decisions still open

- A2-1915: the painting on the gallery wall is proposed as Čiurlionis's *Karalių pasaka* (1909). "Between Worlds" is the title of the 2022–23 Dulwich exhibition, not of a painting; *Rex* (1909) is the alternative. See the planner note in `redraw_list.csv`.
- A2-1898 / A2-1899: mama and tėtis are pinned *after* motina and tėvas. If he wants the everyday word first, the pin is reversed (note in `order_adjacency.csv`).

## Cost

15 cards: 9 edits (≈ $0.02–0.04 each at edit pricing, unverified) + 6 re-rolls (≈ $0.0135 each), with QA ≈ $0.10 per card: well under $2 even with a second attempt on every card.
