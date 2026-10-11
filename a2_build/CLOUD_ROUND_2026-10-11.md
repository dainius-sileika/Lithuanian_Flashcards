# Cloud round, 2026-10-11 (Fable, branch cloud-2026-10-11, from 1deea06)

Everything is committed locally on the branch; nothing pushed; no file overwritten or deleted.

## 1. Genders — decided
`review_genders_2026-10-10.csv` now carries `verdict`, `agrees_with_proposed`, `cards_anki_now`, `source`, `decided`.
All 63 proposed genders are right: 52 confirmed on en.wiktionary (the `lt-noun|m/f` or declension template, cited per row), 11 by morphology where Wiktionary has no entry (-ystė, -imas, -a/-ė nouns; karštis m. because gen. karščio, not *karšties; Dievas/Žemė from their declension templates). No change to `cards_anki.csv` was needed.

## 2. Identity and order
- **GUIDs**: `build_apkg.py` derives every note GUID from the permanent key (`genanki.guid_for("001_suo")`, `("A2-0108")`, `("S-0001")`), never from row position or content; model ids (1607392913 picture, 1607392914 cloze) and deck ids (2059400112/3) are constants. Verified: two builds → identical GUID sets (2,075 notes). Documented in the file header. Caveat recorded there: a row moved between note types cannot update in place.
- **Study order**: new `build_study_order.py` → `study_order.csv` (2,285 rows: 428 A1 deck, 93 A2-tagged deck cards, 1,709 A2 list, 55 sentence cards). `build_apkg.py` sets each note's new-card position (`due`) from it. Design: units of ~36 cards mixing people, food, verbs, home, adjectives, places, body, nature…; hand-picked core at the head of each group (the frequency list is press/legal and would have put *asmuo* second); adjective antonym pairs adjacent; colours one run; same-word confusables ≥60 apart (eiti/eiti, aukštas/aukštas …); batonas pinned right after duona (positions 5–6); administrative/abstract words demoted. A2: deck's A2 cards, then the list phase by phase (P-A and P-D keep file order, the rest category-mixed); sentence cards right after the last of their words.
- **Users updating an existing deck**: Anki updates the notes but does not move cards already in the collection. Fix on their side: Browse → select *Lietuvių Flashcards* → sort by the Key field (or add the Number column) → select all → Cards → Reposition (start 1, step 1). Stated in `build_apkg.py` and `anki/templates.md`.

## 3. Glosses
- `482_storas` english → **fat** (cards_anki.csv). master_wordlist.csv (image agent's file) still says *thick* — please mirror.
- `265_lupa` → **lūpos / lips**, F pl, gen. lūpų, pron lū́pos (Wiktionary lūpa (1), plural lū́pos); key and GUID unchanged. The human take `audio/265_lupa.mp3` still says the singular paradigm → re-record (listed for the owner). master_wordlist.csv row 265 to mirror (lithuanian_TARGET lūpos, english lips, gender F pl).

## 4. Sentences — `a2_build/sentences/`
Decision in `design.md`: picture + Lithuanian cloze on the front (no English), full sentence + English + headword forms + sentence audio on the back — the FF rule holds, the owner's "English with the Lithuanian on the answer side" is adopted, and the blank makes the card gradable (a picture alone admits many true sentences). Target ~150 for A2; `sentences.csv` = first 55 (35 from A1 deck words), `staging.json` = one line each. `build_apkg.py` builds them (cloze model gained an `Image` field; tag SENT; keys S-####); `build_study_order.py` slots each after its last word.

## 5. Recording — the owner records
`python3 build_recorder.py A2` → `recorder_A2.html` (tracked) + `a2_build/recording_list.csv`: 2,694 takes in study order — every A2 headword with its forms (file `<id>.mp3`), the example sentence of every cloze row (`<id>_s.mp3`), the 55 sentence cards (`S-####.mp3`). Phone layout (big buttons, grid hidden, "go to take"), takes persist in the browser, **Export new takes** ships one ZIP per batch and remembers what went. Takes come out as webm/m4a; convert to mp3 into `audio_a2/` (ffmpeg) — build_apkg picks them up by name. Single self-contained HTML, 593 KB.

## 6. Package
`build_apkg.py`: writes `Lietuviu_Flashcards_v<APKG_VERSION>.apkg` (default v2.0) and never overwrites (suffix -1, -2 …); A1 images from `A1_IMAGE_DIRS` (default `out_deck_f62,images` — F6.2 first, 1.5 masters as fallback); A2 from `A2_IMAGE_DIRS` (default `out_deck_a2,out_phrases_a2,images_a2,out_phrases`); sentence images from `SENT_IMAGE_DIRS`. Test build here with `A1_IMAGE_DIRS=_cloud_media/f62,images A2_IMAGE_DIRS=_cloud_media/a2,_cloud_media/phrases`: 2,130 notes (1,145 picture incl. 521 A1 + 624 A2; 930 A2 cloze; 55 sentence cloze), 1,665 media files, every `src=`/`[sound:]` reference resolves, all names ASCII, due 1…2285, GUIDs identical across builds, 214 MB (near the 250 MB AnkiWeb cap — audio for A2 will push it over; split or downscale later). 155 A2 picture rows had no image yet in `_cloud_media`. The test package is gitignored and not shipped.

## 7. Carried over from the Mac round (not done here)
- **A1 re-roll list** (card_notes.json is the image agent's file — proposed lines below, for it to paste):
  - `084_tevai`: "A mother and father side by side; the father near-frontal with eyes just past the viewer, the mother turned to the child and holding its hand; the child looks up at her. Arrows above both adults."
  - `088_brolis`: "Two brothers shoulder to shoulder; the taller one near-frontal, the younger turned toward him and tugging his sleeve, looking up at his face. Arrow above one of them."
  - `097_prezidentas`: "The man president at the podium speaking toward the hall with a raised hand; the woman president seated at the side table signing a document, head bent to the page, so only one figure faces out."
  - `054_kosmosas`: "Main picture: deep space — a dark star field with the Milky Way, a ringed planet and a crescent moon, a plain white rocket with a small tricolour on its fin climbing on a column of flame; the star field is the subject. Insets: a telescope on a tripod; an astronaut in a plain white suit floating; the Earth as a blue disc."
  - `517_jie`: "Main picture: a speaker in the foreground at the left edge pointing with the whole arm at a group of five people standing together across a yard, the bold arrow from the pointing hand to the group; the group is the subject, seen whole and at a little distance, talking among themselves. Insets: the same group boarding a bus; the group at a table."
  - `387_mokytis`: "Main picture: a young woman at a desk with an open textbook and an exercise book, pencil moving, lips moving as she repeats, a dictionary and a lamp; the studying is the subject. Insets: a hand underlining a line; flash cards fanned on the desk; the same woman reciting with eyes closed."
  - `378_zudyti`: drop the inset "a mousetrap sprung" (1.6.1 decision: the fly-swat only); keep the rolled newspaper and the swatted fly.
  - `312_oras`: done in `deck_builder.py` NOUN_STAGING 312 — lungs inset replaced by a bicycle pump and washing in the wind.
  - `134_doleris`: options for the owner — (a) declare `card_text` "ONE DOLLAR" (a banknote is lettering by definition; English, so against the rule's spirit); (b) retarget #134 → **litas** (A2-1772 then merges into it; period-true) or → **euras** (learner's reality); (c) keep wordless with the portrait oval as a plain shape (current). Recommendation: (b) litas.
- Azure TTS for A2: dropped — the owner records.

## Open for the owner
- Mirror the two gloss changes into master_wordlist.csv (image agent's file).
- Re-record 265 lūpos.
- Confirm the study-order design (first 40 positions: žmogus, vyras, moteris, vanduo, duona, batonas, pienas, kava, valgyti, gerti, eiti, dirbti, miegoti, matyti, sakyti, telefonas, stalas, kėdė, didelis/mažas, naujas/senas, gražus/bjaurus, karštas/šaltas, miestas, namas, gatvė, galva, ranka, koja, saulė, lietus, sniegas, autobusas, šuo, batai, mokytojas, gydytojas, kompiuteris, grupė …).
- Choose the doleris option.
