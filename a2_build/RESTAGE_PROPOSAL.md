# Re-staging the speech-bubble cards as pure situation pictures (Fable, 2026-10-17 — proposal only)

Owner's decisions now in force: English caption on every front (template); frames redrawn at standard widths by the builder; section name in the top band, plate number and English in the bottom band; lettering inside images only where it is part of the object. Consequence: the picture no longer has to make the words guessable. Its job is the **situation**, and it must never suggest a different phrase than the caption.

## 1. Exact count of bubble cards

| Source | Cards | Bubble type | Fate |
|---|---|---|---|
| `bubbles.py` UTTER (A1 phrase pack, incl. 2 extra keys) | 38 | one large bubble with a pictogram | re-stage |
| `bubbles.py` EXCH (A1 pack) | 14 | left-panel bubble + right-panel visible answer | re-stage as two panels **without** bubble; 4 merge into existing single cards |
| `a2_build/src/bubbles_a2.py` UTTER_A2 | 102 keys (103 entries; "Help!" twice) | one bubble with a pictogram | re-stage; 1 merge |
| Question words (`deck_builder.QUESTION_BUBBLE`, 9 A1 images rendered) | 9 (12 rows in the A2 list, all CLOZE) | "?" + pictogram bubble | **no image**; retire the 9 renders |
| A2 IMG rows whose staging has a speech bubble (`a2_staging.json`: A2-0262 ask, A2-0426 speak, A2-0803 ask) | 3 | bubble with "?" or wavy line | re-stage without bubble |
| Sentence cards with a bubble (`sentences/staging.json`: S-0014, 0017, 0018, 0026, 0051) | 5 | "?" or knot bubble | re-stage without bubble |
| `deck_builder.NOUN_STAGING` 374 *to think* | 1 | empty thought-bubble | owner's call (optional) |
| Not bubbles, keep: sign pictograms as objects (A2-1228 exit sign, A2-1273, A2-1376 WC door, 142 lytis, 143 warning silhouette), A2-0483 boiling bubbles | — | — | unchanged |

**Total phrase images affected: 154 (140 UTTER + 14 EXCH).** After 5 merges (duplicate phrases that shared a scene: *What time is it? (alt.)*, *How much is it?*, *A little*, *Please repeat*, *What does it mean?*) → **149 phrase renders + 3 IMG + 5 SENT = 157 renders**, plus 1 optional. The 9 question-word images are retired, not redrawn. Every line is in `a2_build/restage_bubbles.csv` (172 rows: ids, English, Lithuanian, old format, new format, one-line new staging, distinguishing cue, confusables, source file, render yes/no).

The 154 phrase images serve both decks: the A1 package draws its 48 phrases from the same keys, so one render per key.

## 2. (a) New staging grammar: "situation" class

Replace `utterance` / `exchange` / `question` with one class, **situation**, in three layouts:

- **Single scene (default, 149 of 157).** One calm moment in which the speech act is visible in bodies and objects: who speaks to whom, where, and the thing the phrase is about (the loaf, the empty chair, the dropped glove). No bubble, no pictogram floating in air, no lettering unless it is on a real object (a shop sign, a ticket, a clock face). Rule of thumb: if a silent film still would make the caption's meaning obvious, single scene.
- **Two panels (12).** Ask → visible answer, same two people, same scale, no bubble in either panel. Use only where the *answer* is what fixes the meaning: *Where is the toilet?* (pointing to the pictogram door), *How do you say … in Lithuanian?* (object held up → word given), *Call a doctor!* (urgent wave → telephone and ambulance), *No problem* / *You're welcome* (mishap or thanks → wave-off).
- **Three panels (1).** Setup → act → consequence. Kept only for *I need water* (empty glass → tap → drinking) as the model case; with a caption present the strip's old job (disambiguating the words) is gone, and strips cost legibility on a phone. The 3-panel idea from Reports 1–2 is therefore **withdrawn** as a default and kept as an option for sequences of time (*paskui*, *po to*) if those ever get pictures.

When each is better: single scene whenever the act is a gesture plus an object; two panels when the phrase is a question whose answer is a visible action; three panels only when the phrase itself names a sequence.

## 2. (b) Consistency check, situation ↔ target phrase

Each row carries `distinguishing_cue` and `confusables`. The QA pass (existing `qa_images.py`, one extra question) asks of every render:
1. **Caption fit**: does the scene show the situation named by the English caption? (fail → re-roll)
2. **Neighbour test**: could this scene equally illustrate one of the listed confusables in our own deck? The distinguishing cue must be present and visible at phone size: time of day for *Labas rytas / Laba diena / Labas vakaras* (sun height, lamps); one person casual vs a group formal for *Labas / Sveiki*; crossed fingers + exam folder vs train + suitcase for the two *good luck* cards; the purse or wallet for every price phrase; the bowed head only on apologies, never on thanks; a thumb-up only on *I'm fine / all good / well done*.
3. **No stray speech act**: no handshake unless the phrase is a meeting phrase, no wave unless parting, no raised palm unless greeting or stopping, no pointing finger unless the phrase points.
4. **Lettering**: none, except on objects where the owner's rule allows it (signs, clock faces, tickets, a phrasebook cover). The target phrase must never appear.
5. **Register**: clothes and setting match tu/jūs (teenagers at a school gate for *Iki*, a man in a hat on a trolleybus for *Atleiskite*).
Pairs that share a scene deliberately (*How are you?* / *I'm fine*; *What is your name?* / *My name is…*; *window seat* / *aisle seat*) are drawn as the same scene from the asker's and the answerer's side, so the learner sees the exchange across two cards without a two-panel image.

## 2. (c) Question words without the "?" bubble

The 12 question-word rows are already CLOZE in the A2 list. Without the bubble there is nothing for a picture to carry (kur/kada/kodėl are not depictable without a pictogram, which is exactly what is being removed). Proposal: **no image**; the cloze front shows the gapped sentence with the English caption in the bottom band ("where") and the hint on tap; the back shows the word, stress and audio. The 9 rendered bubble images move to `_superseded/` per the version rule. If the owner wants a picture for the unit's look, one shared "asking" scene (a visitor with a map and a passer-by) can serve all 12 as a section illustration, not as a cue.

## 2. (d) The list

`a2_build/restage_bubbles.csv` — one line per card. Columns: ids, english, lithuanian, old_format, new_format, new_staging, merge_with, distinguishing_cue, confusables, source_file, render.

## 2. (e) Cost and order

- 157 renders × $0.0135 = **$2.12**; at the observed ~40% re-roll rate ≈ **$3.0**; QA vision pass ≈ $1.5. **Under $5 all-in.** With the 112 renders for the proposed additions (`benchmark_en/PROPOSAL_additions.md`) the whole phrase/addition pass stays **under $10**. The owner's "top up" is for time, not money: ~270 renders at 4 workers is about an hour and a half of pipeline time plus QA.
- Order: (1) owner approves grammar and the merge list; (2) prompt-rule changes below, dry-run three prompts; (3) render the 14 two-panel + 10 hardest single scenes first as a pilot (greetings set, thanks/apology set, price set), QA with the neighbour test; (4) render the rest; (5) retire old renders to `_superseded/`; (6) 3 IMG + 5 SENT last; (7) then the additions under the same grammar.

## 2. (f) Prompt-rule changes

- `go_grammars.py`: add `situation` (single), `situation_2` (two panels, "no bubble in either panel"), keep `sequence` for the one strip; mark `utterance`, `exchange`, `question` as retired (keep the text for provenance, remove from `NOUN_GRAMMARS` selection). Add to `NO_INSET_CLASSES`.
- `bubbles.py` / `bubbles_a2.py`: superseded by a new `situations.py` keyed by English gloss → (format, scene, cue, confusables), generated from `restage_bubbles.csv`; UTTER/EXCH kept only for history.
- `gen_phrases.py`: drop `QMARK`, `is_question` branching and `exact_text`; always `text=False`; stop passing `exclude=target` (naming the forbidden word primes it; the NO_TEXT_RULE already covers it); route by format from `situations.py`; question-word rows skipped (no image).
- `go_generator.py` `NO_TEXT_RULE`: delete the sentence that licenses symbols inside bubbles ("a bubble may contain a drawn picture or symbol…") and the "speech bubbles must stay free…" clause; add one positive sentence: "No speech bubbles, thought bubbles or floating symbols of any kind; meaning is carried by people, gestures, objects and setting." Keep the declared-`card_text` path for object lettering (signs, prices, clock digits).
- `deck_builder.py`: `QUESTION_BUBBLE` / `QUESTION_BY_GLOSS` retired; `SEQUENCE_BY_GLOSS` kept for *I need water* only; NOUN_STAGING 374 optional edit.
- `qa_images.py`: add the neighbour test (reads `confusables` + `distinguishing_cue`), and a "no bubble present" check.
- Builder/template: the caption band supplies the English; the top band the section ("VIII skyrius · frazės"); plate numbers continue the existing numbering.

## 3. Decisions the owner must make
1. Approve the single-scene default and withdrawal of 3-panel strips (keep for *I need water* only).
2. Approve the 5 merges (one image for duplicate phrases) and the 9 question-word images being retired with no replacement.
3. *to think* (374): is an empty thought-bubble a "word bubble"? (I say keep the bubble: it is the conventional object for thinking and contains nothing.)
4. Sign lettering: the *open / forbidden / allowed* sign cards — allow the Lithuanian word on the sign object (it is the target word) or keep pictogram-only signs? The current rule ("never the target word") says pictogram-only; I recommend keeping that.
5. Pilot first (24 renders, one evening) or straight through (157)?
