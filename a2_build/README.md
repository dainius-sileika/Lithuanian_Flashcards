> **SUPERSEDED by docs/DESIGN_SPEC_CURRENT.md on 2026-10-19** — kept as history; where this file and the code disagree, the code and the spec are right.

# a2_build — the A2 list, built 2026-10-11 (Fable), updated the same day for the owner's decisions

Rebuild with `python3 a2_build/src/build_a2.py` (reads the decision modules in `src/`; stress lookups came from
caches in `~/a2work/` on this Mac — without them new rows lose pron/pres3/past3).

## Files

| file | what |
|---|---|
| `deck_fixes.csv` | 95 proposed corrections to the shipped 520 (key, field, old, new, source, confidence, note) |
| `deck_fixes_applied.csv` | the 27 field changes actually made (16 high-confidence rows) to `master_wordlist.csv` / `cards_anki.csv` |
| `a2_wordlist.csv` | **1,709 new cards** (520 → 2,229). Queue columns + `source, freq_rank, route, check, example_lt, example_en, pres3, past3` |
| `a2_staging.json` | 369 staging lines for the hard IMG rows, keyed by id (same shape as `card_notes.json`) |
| `src/` | the decisions as code: `queue_overrides.py`, `official_overrides.py`, `additions.py`, `lettering.py` (card_text per the lettering decision), `examples_*.py` (cloze sentences), `staging_*.py` (subject phrases + staging), `bubbles_a2.py` (phrase-card bubbles, merged into `bubbles.py`) |
| `build_warnings.txt` | empty = every pron strips back to its headword, every cloze has a sentence, every IMG row has a subject |

## Done today outside this folder (all uncommitted, for review)

- **`cards_anki.csv` / `master_wordlist.csv`**: the 16 high-confidence fixes applied (gen_sg of #249; headwords of #379/385/427/431; 11 stress fills). Your uncommitted gender edits untouched. Log: `deck_fixes_applied.csv`. Medium/low rows (minià, taikà, kortẽlė, datà, lė̃tas, seklùs, jì, jū̃s, jiẽ, svãras, the duplicates, levels, #371) wait for you.
- **batonas** added: `master_wordlist.csv` #531 (Food, A1, pron batònas from kirtis.info — no Wiktionary entry), `card_notes.json` key `531_batonas` (pale wheat loaf, golden scored crust, dark rye behind for contrast), and a `cards_anki.csv` row **inserted directly after 182_duona**. `build_apkg.py` adds notes in `cards_anki.csv` row order and Anki's new-card order follows note creation, so that row position is the study order — no code change needed. The row has no image yet; the builder skips imageless rows, so it is harmless until the picture exists.
- **`build_apkg.py`** extended (not a parallel builder): reads `A2_LIST` (default `a2_build/a2_wordlist.csv`; `A2_LIST=""` skips). IMG/PHRASE rows → the existing GO note once an image exists in `images_a2/`, `out_phrases/`, `out_deck_a2/` or `images/` (`<id>.webp|png|jpg`); CLOZE/PAIR rows → new native cloze note type **"Lietuvių GO Cloze"** (`{braces}` in `example_lt` become `{{c1::…}}`; front = sentence with the blank + English hint; back = headword, stress, gender, forms, gloss, audio from `audio_a2/<id>.mp3` when present). Tags: level, route, phase. `APKG_OUT=path` chooses the output file. Dry run: 930 cloze notes + 48 phrase images → a valid 7 MB .apkg (`~/a2work/test_a2.apkg`); the full build was not run so `Lietuviu_Flashcards.apkg` is untouched.
- **`bubbles.py`** now merges `a2_build/src/bubbles_a2.py` (104 new UTTER entries: greetings, politeness, transactions, signs, clock times). **`gen_phrases.py`**: `A2_LIST=a2_build/a2_wordlist.csv python3 gen_phrases.py 8 60` renders the list's PHRASE rows; default behaviour unchanged. No images generated.
- `anki/templates.md` documents the cloze note type.

## Decisions taken (your questions 1–5; you review later)

1. **Size**: kept all 1,709 incl. the 137 deferred (P-K last). 520 + 1,709 = 2,229 cards ≈ 1,950 lemmas, top of the CEFR A2 band.
2. **Anachronisms**: modern-tech words stay cloze (*internetas, el. paštas, planšetė, bankomatas, pica*); nothing of 1981 to draw.
3. **Weekdays/months**: pictures, now with declared lettering — the week strip carries the heads `Pr An Tr Kt Pn Št Sk` and the numeral; the month page carries the numeral, `1981` and the weekday row. Cloze alternative kept in each row's note.
4. **#371 eiti (go)**: proposed retarget → važiuoti left for you (deck_fixes, medium); the list keeps A2-1445 važiuoti (ids now frozen in id_map.csv). If you take the retarget, drop A2-1445.
5. **Re-base SWAPs** accepted as drafted (čekis, grynieji pinigai, sąskaita, persikelti, klaidingas, nuovada, pirmiausia, pagaliau).

**Lettering** (owner, 2026-10-11): 97 rows now declare `card_text` — exact Lithuanian strings, never the target word; prices in litai (`2 Lt 40 ct`). It brought 11 words back from cloze to picture (*nuolaida, čekis, sąskaita, meniu, adresas, tvarkaraštis, pažymys, laipsnis, kilometras, gramas, litras*) and added **litas** (A2-1772). *euras* went to cloze (prices are litai). Signs whose text would be the target (*KASA, PAŠTAS, TAKSI, KAVINĖ*) stay wordless; signs that are the phrase itself (*draudžiama, atidaryta*) are pictogram bubbles.

## 1. Deck fixes (`deck_fixes.csv`) — see above; unchanged list, 16 applied.

## 2. The list (`a2_wordlist.csv`)

Sources: queue 831 (of 984: 139 dup-flagged rows resolved — 8 kept as distinct senses; 16 P-E pattern cards dropped per the re-base; broken rows dropped, e.g. *kainoskaitė* is not a word); official VU list 680 (every IMG/CLOZE/PHRASE/PAIR/SWAP route of the triage, blank `owner_decision` taken as acceptance, ~80 routes changed with the reason in `notes`); frequency core 132 (*daryti, ieškoti, net, nei, kol, beveik, turbūt, irgi, meilė, pilis, vėliava…*); added 66 (dative/accusative pronouns, nationalities, ordinals 6–12, *makaronai, gira, šortai, dantų pasta, litas*, clock-time phrases).

| phase | name | rows | IMG | CLOZE | PAIR | PHRASE |
|---|---|---:|---:|---:|---:|---:|
| P-A | A1 completion | 94 | 77 | 17 | – | – |
| P-B | Function words & core verbs | 258 | – | 258 | – | – |
| P-C | A2 topical | 95 | 37 | 58 | – | – |
| P-D | Phrases & formulas | 194 | – | 40 | – | 154 |
| P-F | Vocabulary expansion | 266 | 132 | 134 | – | – |
| P-H | Official-list pictures | 254 | 254 | – | – | – |
| P-I | Official-list cloze & aspect pairs | 275 | 4 | 260 | 11 | – |
| P-J | Frequency core additions | 136 | 43 | 70 | 23 | – |
| P-K | Deferred (off-list, low frequency) | 137 | 78 | 59 | – | – |
| | **total** | **1,709** | **625** | **896** | **34** | **154** |

Level: 614 A1 / 1,095 A2 (queue tags kept; official rows A1 if top-1,000 and not administrative, or basic by hand list).

**Routes.** ~270 queue rows IMG→CLOZE: abstract nouns, speech-act and mental verbs, relative adjectives, extended family, lettering-only concepts, modern tech, and the time nouns (*laikas, valanda, diena…*: a clock reads as *laikrodis*). 40 P-D/P-G phrases became cloze: the discourse markers (*Beje, Deja, Mano nuomone…*) and the 20 grammar-pattern sentences (*Anksčiau {gyvendavau} Kaune*), which cloze on the form they teach. Reasons sit in `notes` row by row.

**Cloze rows** (896 + 34 pairs) carry `example_lt` with the target in {braces} and `example_en`. I wrote them; a native read is still the gate.

**Stress** (new rows): 379 Wiktionary = kirtis.info, 69 Wiktionary only, 396 kirtis.info only (rule engine — candidates), 102 multiword assembled per word, 27 not found (-ai adverbs), 7 `DISAGREE` (*šita, alkanas, vokas, alergija, pusryčiauti, kaltas, rimtas*). Queue fixes folded in: bè, ikì, mažaĩ, ekonòmika, registrãcija, pirmãdienis (Wiktionary's pirmadiẽnis contradicts kirtis and the other six weekdays), encoding (spìnta, keĩsti, ìš), `meniu` gen_sg, *būti skolingas*, *auliniai batai*, *nuobodu*.

**Grammar forms**: gender from Wiktionary else by ending; gen_sg rule-derived and marked; adjective feminines by rule; pres3/past3 from Wiktionary for 80 of 343 verbs — the rest say `principal parts: NOT FOUND`.

## 3. Staging

All 625 IMG rows have a `subject_phrase_EN`; 369 have a full staging line (every verb, place, building, person/role, contrast adjective, event, time, number, lettered card, and anything with a deck neighbour). Plain objects, foods, animals and clothes got the subject phrase only — the F6.1 grammars carry those; write a line only after a first roll fails. Numbers: numeral + counted set. Compass set as one rose. Nationalities cloze; *Lietuva* a map with the tricolour and three city names.

## 4. Still open for you

- Native read of `example_lt` (930 sentences) — or sample 50.
- `DISAGREE` (7) and `NOT FOUND` (27 stress, 263 verb parts) rows.
- Question words A2-0108…0117 are cloze in the list but already have bubble images in `out_phrases/`; either route works — say which.
- The medium/low deck fixes and #371.
- Audio for the new cards (`audio_a2/<id>.mp3`), and the IMG renders (other agent) into `images_a2/`.

## Owner checklist
- [ ] Accept/revert the 27 applied field changes (`deck_fixes_applied.csv`) and decide the medium/low rows.
- [ ] Review batonas (#531) staging; render it with the A1 re-render.
- [ ] Skim `card_text` on the 97 lettered rows (strings must be exactly right; qa_images reads them back).
- [ ] Sample the cloze sentences; then `python3 build_apkg.py` (A2 rows ride along) and import.
