# PLAN — one key namespace for every card (`NNNN_slug`), plate numbers and tags

Planner: Fable, 2026-10-20. Executor: Opus (nothing here is applied yet). Owner decision 2026-10-19 (verbatim):
*"Rename everything so it's consistent — content and tagging is fluid until A1 and A2 are locked down, and
everything should be as consistent as possible."* Keys and GUIDs lock once A1 and A2 are both signed off
(spec 3.3.0 §7); until then they may change, and this plan changes them once.

Deliverables in this folder: this plan, `tools/rename_keys.py` (+ `tools/keymap.py`), `dryrun_v1.txt`
(the tool's dry run on the tree as of 2026-10-20), `topic_map_v1.csv`. The map itself
(`key_map_v1.csv`) is written by `--apply`, at execution time, from the study order of that moment.

---

## 0. The scheme in two lines

Every card key is `NNNN_slug`: the card's position in the study order (A1 block 0001–1186, A2 block
1187–2433 today), zero-padded to four digits, then the ASCII-folded headword (phrases/sentences: their
first words, ≤ 4 words / 32 chars). `pav. N` = the key's number; GUID = `genanki.guid_for(key)`; the
level, kind, part of speech and topic are **tags** (`lt::level::A1`, `lt::kind::cloze`, `lt::pos::verb`,
`lt::topic::veiksmai`), never part of the key. After the lock a key never changes and new cards append
(`tools/rename_keys.py --mint "<headword>"`).

Examples from the dry run: `103_zmogus → 0001_zmogus`, `A2-0348 (Labas) → 0021_labas`,
`A2-0154 (ir) → 0105_ir`, `S-0002 → 0101_moteris_valgo_duona`, `A2-1269 → 2433_greblys`.

Counts (dry run, 2026-10-20 tree): **2,433 cards renamed** (521 base `NNN_slug`, 1,857 `A2-####`,
55 `S-####`), plus 4 merged-away ids, 31 B1 deferrals and 1 media alias carried without a number;
**65 live text files** rewritten (14,699 token replacements: 37 data/code files + 28 golden prompt files);
**1,250 tracked media files** `git mv`'d (images 520, audio 518 + 2, audio_a2 150 + 4, style/golden 28 jpg + 28 prompt files);
on the Mac about **1,500 untracked renders** (`out_deck_f62` 522, `out_deck_a2` 668, `out_phrases_v3` 233
+ `round2` 14, `out_deck_sent` 55, `out_phrases_a2` ≈150 of which few are still used) plus their
`_rerolled/` and `_superseded/` versions and the `_cloud_media/*` mirrors (1,143 files here).

---

## 1. When to run it (ordering) — the one thing that matters most

The number is the study-order position **at the moment the map is derived**. Pre-lock, the order still
moves (dep37 fix, the study-order builder's tie-breaks, future retiers). Therefore:

1. **dep37 first.** Apply `a2_build/study_order/dep37_plan.*` (5 words to A1, 26 rewords), regenerate
   `study_order.csv` with `build_study_order_v3.py`, commit. The rename tool reads that order; it does not
   care which keys dep37 touched, because it computes the map from the then-current files.
2. **Then the rename**, as the last structural change before the lock. Every later reorder before the
   lock would mean a second map (`key_map_v2.csv`, old = v1 keys) and a second media pass: supported
   (`keymap.py` follows chains), but each run costs a Mac media pass and a recorder migration, so do not
   plan on it.
3. **After the rename `study_order.csv` is the authority, not the builder.** `build_study_order_v3.py`
   breaks ties on the Fluent Forever number and on digits of the A2 id (`load_cards`, lines 296–310;
   sorts at 471/508/526), detects the FF adjective pairs by number adjacency (`pn`, 407–411, 716) and
   matches key shapes by regex (`^(\d{3}_|A2-|S-)` at 400, `^\d{3}_` at 848, `startswith("S-")` at 856).
   After the rename the A2 "number" tie-break becomes the new number, so **a regeneration is not expected
   to reproduce the order bit for bit**. The tool rewrites the builder's hand lists (SURVIVAL, CORE, DEMOTE,
   PIN_AFTER: 406 tokens) so `--audit` keeps working (checked: the audit runs on the renamed order and
   agrees except for 7 `words_used` key references the line-400 regex no longer sees — a required code
   change, §8). Pre-lock, if the order must change again, regenerate first and re-run the rename; after the
   lock, the builder is a proposal tool only and the order file is edited by hand (new cards append).

---

## 2. Critique of the direction (point by point; defaults kept unless stated)

1. **Key must not encode the level.** Agreed and stronger than stated: the key also must not encode
   the *kind* (picture/cloze/sentence) or the *list* (base/A2/sentence) — today's three families encode
   exactly that, and it is why `A1 Labas` is `A2-0348`. The only thing in the key that is a fact about the
   card is its first headword, and even that is a reading aid, not an identifier (`265_lupa` already teaches
   *lūpos*; after the lock a corrected headword keeps its slug — rule in §14).
2. **`NNNN_slug`, numbers from study order, assigned once.** Agreed, with two honest caveats. (a) "pav. 1 is
   the first card a learner meets" is true on the day of the lock and drifts afterwards: a card added later
   gets the next number but is scheduled wherever the order puts it, so after a few additions the plate
   number is a stable *name*, not the position. That is the right trade (names must not move) but say so in
   the spec. (b) The number depends on the A1/A2 split *at derivation time*: a card re-tiered after the lock
   keeps a number inside the "wrong" block. Also fine — the block boundary is history, the level lives in the
   tag and subdeck — but it means the blocks are not a guarantee, only today's picture.
   *Sentence slugs:* I chose the uniform rule (first words of the sentence: `0101_moteris_valgo_duona`)
   over a `s_` marker or the cloze target, because the key must not encode the kind (point 1) and the
   target alone (`geria`) would read as the verb card. The slug cap (4 words / 32 chars) keeps file names
   sane; collisions (31 pairs share a slug, e.g. two *žemė*, two *aukštas*) are legal — the number is the id.
3. **Plate number = key number.** Agreed. Verified CSS/field-only: `card_frame._frame()` renders
   `pav. {{number}}` / `{{Number}}` from the note field (card_frame.py 150, 221); `build_apkg.plate_number()`
   fills the field; the image prompts forbid any lettering or numbers and require the header/footer bands
   blank (go_generator.py 321–345); the standard frame crops the drawn frame off anyway. **No image has a
   number baked in** — nothing to list. The "drawn" frame (`--frame drawn`) also takes `{{number}}` from the
   field (build_apkg.FRONT/BACK).
4. **GUIDs.** `genanki.guid_for(key)` everywhere (build_apkg 452/468/509/646). After the rename every GUID
   changes once; v3.0 is delete-and-reimport anyway, and no package with the new keys has been published.
   `tools/verify_apkg.py --against` must learn the map (§8) or it will report 2,433 "changed GUIDs".
5. **Tags.** Agreed; scheme in §6 with the full category → topic table (`topic_map_v1.csv`). One pushback:
   I keep the raw `category` column in the data files and the Anki `category` field as they are, and put
   the *unified* topic in the tag. Rewriting the category values themselves would touch the drawing grammars
   (`go_grammars.route(category, …)`, `CAT2CLASS`, `NOUN_GRAMMARS` — all in the style lock) and the study-order
   lanes (`LANE`) for no gain in the deck. The duplicates the owner saw (Job/Jobs, Phrases/Formulas/Greetings)
   collapse in the tag and in the section label, which is what a learner sees. Candidate follow-up, not in
   this plan: put the topic slug in the Category field and shrink `card_frame.SECTIONS` to 20 one-to-one rows.
6. **One map, aliases forever.** Agreed. `a2_build/rename/key_map_v1.csv` (never edited, never deleted) +
   `tools/keymap.py` (`canonical()`, `aliases()`, `lookup()`) for everything that reads history by key.
   Pushback on "everything that references keys must move together": **history must not be rewritten.**
   Ledgers, gen logs, QA sheets, build manifests, round folders, reports, the spec history and the archive
   keep their old names, and the map is how they are read. Rewriting a ledger would falsify the record of
   what was rendered under which name; rewriting `build_reports/builds/v3.0_A1.json` would make the manifest
   of a shipped package disagree with the package. The tool's `--verify` therefore distinguishes LIVE
   (rewritten), GENERATED (rebuilt) and HISTORY (untouched) and fails on anything unclassified.
7. **Recorder.** Agreed; §10. Migration is a *move* inside IndexedDB (clip + `said:` meta re-keyed, a
   `migrated:` meta left behind), never a delete. The ingest side needs a small script (none exists today —
   ingest is a prose procedure in `build_recorder.py`'s docstring): §10.3.
8. **Computed, not hand-listed.** Done: `tools/rename_keys.py` derives everything from `study_order.csv` +
   the three card lists at run time; dry run by default; `--apply`; `--apply-media`; `--verify`; `--mint`.
9. **Directory layout.** Keep the folders, rename the files. A `media/img` + `media/audio` layout would be
   tidier but touches `A1_IMAGE_DIRS`/`A2_IMAGE_DIRS`/`SENT_IMAGE_DIRS`, every `gen.py` (`OUT`, `_rerolled`),
   `golden_set.py`, `_cloud_media` mirrors, the `.gitignore` patterns, the review pages and the owner's
   Proton folder structure — all for an aesthetic gain, on the same day as a 2,700-file rename. Not worth
   the risk now; after the lock it can be done as its own small, verifiable move.

---

## 3. The scheme, precisely

- **Key** `^\d{4}_[a-z][a-z0-9_]*$`. Number = `order` column of `study_order.csv` at derivation. Slug =
  `rename_keys.slug(headword)`: first form before `/`, parentheses dropped, cloze braces dropped, lower-case,
  NFD and combining marks removed (stress marks, ą č ę ė į š ų ū ž → a c e e i s u u z), words joined by
  `_`, at most 4 words and 32 characters (whole words only), `x` if nothing is left.
  Headword source: `cards_anki.csv lithuanian`, `a2_wordlist.csv lithuanian_TARGET`, `sentences.csv lt`.
- **Take keys** (recorder, audio): `<key>` for the word, `<key>_s` for the example sentence; media
  `<key>.mp3`, `<key>_s.mp3`, `<key>.png|webp|jpg`, cropped copies `<key>_sf<v>.jpg`, versions
  `_rerolled/<key>.r<n>.png`, golden `<key>.jpg` + `<key>.prompt.txt`.
- **Not numbered**: merged-away ids (`merged_keys.csv`, 4) — carried in the map as `status=merged` with
  `note=merged into <old> -> <new>`; B1 deferrals (31) — `status=deferred`, keep their old id in
  `deferred_B1.csv` (a promoted row gets `--mint`); media alias `265_lupos` → same new key as `265_lupa`.
- **New cards after the lock**: `tools/rename_keys.py --mint "<headword>"` = max number in use + 1 + slug;
  the card is appended to `study_order.csv` wherever the owner schedules it; its key never moves.
- **Re-tier / re-word after the lock**: the key stays, including a slug that no longer matches the
  headword. Only the number is identity; the slug is a label frozen at lock time.
- **A second pre-lock rename** (if ever): `--apply` again writes `key_map_v2.csv` (old = v1 keys);
  `keymap.canonical()` follows the chain.

---

## 4. Plate numbers

`build_apkg.plate_number()` becomes `str(int(key[:4]))` for every note type; the `number`/`Number`
field holds it. Numbers are shown unpadded (`pav. 21`, as today's `pav. 1001`). The band logic and CSS
are unchanged; the `Number` field is display-only so this is not a schema change. The old scheme
(A1 1–531 by wordlist number, A2 1001+, sentences 4001+) goes to history in the spec changelog.

The Fluent Forever row number survives as a **data join only**: `master_wordlist.csv` `#` (the generator
tables `VERB_STAGING`, `NOUN_STAGING`, `FORMAL_ROWS` … are keyed by it) and `cards_anki.csv` `number`.
It is no longer shown anywhere. Recommended (small, grep-able, §8): rename that column `number → ff_no`
in `cards_anki.csv` so nobody reads it as the plate again.

---

## 5. GUIDs

Unchanged mechanism: `guid = genanki.guid_for(key)`. The rename changes every GUID once, pre-lock. The
first package built after the rename is a fresh import for every user (already the v3.0 policy). At the
lock, keys and GUIDs freeze: the spec rule becomes "a key, hence a GUID, never changes after the lock;
a card that changes meaning keeps its key; a card that would change note type is a new card".
Verification of the renamed build against the pre-rename build goes through the map (§12).

---

## 6. Tags and topics

Today: A1 picture notes `[level]`; A2-list notes `[level, route, phase-without-dash]` (e.g. `A1 CLOZE PA`);
sentence notes `[level, "SENT"]`. The frame CSS keys section overrides off `data-tags~="PHRASE"` and
`~="SENT"` (`card_frame.ROUTE_SECTIONS`, `section_css()`, template attribute `data-tags="{{Tags}}"`).

**Proposed scheme** — four hierarchical tags per note, all lower-case except the CEFR level:

| tag | values | source |
|---|---|---|
| `lt::level::A1` / `A2` | the subdeck | `level` column (cards_anki / a2_wordlist / sentences) |
| `lt::kind::picture` / `phrase` / `cloze` / `sentence` | note kind | cards_anki → picture; route IMG → picture, PHRASE → phrase, CLOZE and PAIR → cloze; sentences.csv → sentence |
| `lt::pos::noun` / `verb` / `adjective` / `adverb` / `pronoun` / `numeral` / `preposition` / `conjunction` / `question` | part of speech of the headword; **omitted** for phrases and sentences | `type`: N, V, A, ADV, P, NUM, PREP, CONJ, Q (a2_wordlist); master_wordlist `type` N/V/A/P joined by FF number for A1 base rows |
| `lt::topic::<slug>` | one of the 20 section slugs below | `category` → `a2_build/rename/topic_map_v1.csv` (sentences → `sakiniai`) |

The phase tag (`PA` … `PL`) is dropped: it records which planning batch a row came from, which is
provenance, not a study attribute (it stays in the CSV). The route tag is replaced by `kind`. PAIR rows
are two-blank clozes; the data keeps `route=PAIR`.

**Topics = the 20 Lithuanian sections of the top band**, ASCII-slugged, so the tag and the running head
always agree: `zmones, gyvunai, vietos, transportas, namai, maistas, drabuziai, kunas_ir_sveikata, gamta,
darbas_ir_mokykla, visuomene, spalvos_ir_medziagos, skaiciai_ir_laikas, veiksmai, savybes,
daiktai_ir_savokos, jausmai_ir_nuomones, pagalbiniai_zodziai, frazes, sakiniai`. The full mapping of the
53 category values in use (with row counts per source and the merges — Job + Jobs + Work & school +
Work & culture → X; Phrases + Formulas + Greetings + Politeness + Basics + Getting by + Transactions +
Core/Extended patterns + Functions → XIX; Color + Materials → XII, etc.) is `topic_map_v1.csv`. Two
findings from building it: **`Functions` (67 PHRASE rows) is not in `card_frame.SECTIONS`** — it only gets
its label through the PHRASE override; add it to XIX explicitly. And **`Nouns` is 385 rows** (a quarter of
the A2 list) under XVI *daiktai ir sąvokos* — a part-of-speech bucket wearing a topic's clothes. The tag
scheme makes this visible (`lt::pos::noun` + `lt::topic::daiktai_ir_savokos`); re-topicking those rows by
hand is content work for the A2 sign-off, not for this plan.

**Implementation sketch (build_apkg.py)**
```python
TOPIC = {r["category"]: r["topic"] for r in csv.DictReader(open("a2_build/rename/topic_map_v1.csv"))}
POS = {"N": "noun", "V": "verb", "A": "adjective", "ADV": "adverb", "P": "pronoun", "NUM": "numeral",
       "PREP": "preposition", "CONJ": "conjunction", "Q": "question"}
def tags_for(level, kind, pos_code, category):
    t = [f"lt::level::{level}", f"lt::kind::{kind}", f"lt::topic::{TOPIC[category]}"]   # KeyError = unmapped category: fail the build
    if pos_code in POS: t.insert(2, f"lt::pos::{POS[pos_code]}")
    return t
```
`card_frame.ROUTE_SECTIONS = {"lt::kind::phrase": "XIX", "lt::kind::sentence": "XX"}` (the `~=` attribute
selector matches a whitespace-separated token and `::` inside a quoted CSS string is legal; Anki fills `{{Tags}}`
with the space-separated tag string, and hierarchical `::` tags are supported since Anki 2.1.45 — the executor confirms
the rendered label on the frame preview before the release). `card_frame.section_of()` mirrors it. The APKG_LEVELS
filter and the deck routing already use the `level` column, not the tag.

**Style-lock impact**: `SECTIONS` (adding Functions), `ROUTE_SECTIONS` and `section_css()` are lock items
(`tools/style_lock.py` 172–175), so the tag change is a spec **minor** release with a lock update — the
same release that adds §12 (§14). `GO_FIELDS`/`CLOZE_FIELDS` do not change: no schema change.

---

## 7. Inventory — every file and field that carries a key

Classes: **LIVE** = rewritten by `rename_keys.py --apply` (whole-token replacement, longest key first, with a
non-alphanumeric boundary on both sides so `001_suo` also matches in `001_suo.mp3`, `001_suo_s`,
`001_suo_sf2.jpg` and never inside `0001_suo`); **GEN** = regenerated by its own tool afterwards;
**CODE** = hand change by the executor (§8); **HIST** = untouched, read through `keymap.py`.

| path | class | key fields / what | notes |
|---|---|---|---|
| `study_order.csv` | LIVE | `key` (also the source of the numbers) | regenerate *before* the rename, not after (§1) |
| `cards_anki.csv` | LIVE | `key`, `image_file` | `number` keeps the FF row (rename column to `ff_no`, §8) |
| `master_wordlist.csv` | LIVE | gains column `key` after `#` (blank for the 10 superseded colours and 11 category-multi rows) | `#` unchanged |
| `a2_build/a2_wordlist.csv` | LIVE | `id` | |
| `a2_build/sentences/sentences.csv` | LIVE | `id`, `words_used` (keys, space-separated), `image_key` | |
| `a2_build/merged_keys.csv` | LIVE | `merged_into` → new; `id` stays the merged-away old id (no new key) | |
| `a2_build/id_map.csv` | LIVE | `id`, `merged_into` | becomes the registry of current keys; the 4 merged ids stay old |
| `a2_build/deferred_B1.csv` | HIST (by design) | `id` old | `status=deferred` in the map; `--mint` on promotion |
| `audio_source.tsv` | LIVE | `key`, `file` path | |
| `a2_build/context_notes.csv` | LIVE | `key` | |
| `a2_build/study_order/retag_A1.csv`, `retier_v3.csv` | LIVE | `key` | inputs of `--apply-retier` |
| `a2_build/study_order/recording_order_v3.csv` | GEN | `key` | `build_study_order_v3.py` |
| `a2_build/study_order/dep37_plan.{csv,md}`, `check_dep37_plan.py` | HIST | | applied before the rename (§1) |
| `a2_build/recording_list.csv`, `recorder_A2.html` | GEN | `take`, `file_name`, `dest`; the page's WORDS | `build_recorder.py A2` |
| `a2_build/audio/recorder_A2_afb2ebe2_script.json` | LIVE | per-key script of the 2026-10-12 sheet | read by `build_recorder.deck_takes()` for stale detection |
| `a2_build/restage_bubbles.csv` | LIVE | `ids` (incl. the bare FF number `374` → `0218_galvoti`, column-aware) | then regenerate `situations.py` |
| `situations.py` | LIVE + GEN | `ids`, `BY_ID` | rewritten *and* regenerable (`a2_build/src/build_situations.py`) |
| `a2_build/a2_staging.json`, `card_notes.json`, `a2_build/sentences/staging.json` | LIVE | JSON keys | staging read by the generators |
| `a2_build/historical/implementation/likeness_args.json` | LIVE | `cards` keys, `active` | read by `historical.py` |
| `style_lab/research/settings_assignments.csv` | LIVE | `key` | read by `go_settings.assign()` |
| `a2_build/stress_58_resolved.csv`, `a2_build/deck_fixes.csv` | LIVE | `id` / `key` | reference data still consulted |
| `style/golden/manifest.csv`, `style/golden/*.prompt.txt`, `style/golden/README.md`, `style/golden/<key>.jpg` | LIVE (+ git mv) | `key`; prompt files' `key:`/`file:` lines | |
| `review_desk/items.json` | LIVE | prose with keys | the owner's live task page |
| `build_apkg.py` | LIVE + CODE | `IMAGE_ALIAS`, `plate_number`, tags, comments | §8 |
| `build_study_order_v3.py` | LIVE + CODE | SURVIVAL, CORE, DEMOTE, PIN_AFTER (406 tokens); regexes at 400/848/856 | §8 |
| `deck_builder.py` | LIVE + CODE | `DIRECTION_FREE_ROWS` A2 ids, docstring; key derivation at 1254 | §8 |
| `frame_crop.py` (`SIDE_OVERRIDES`), `frame_preview.py` (`DEFAULT_KEYS`), `qa_images.py` (docstrings + `card_id`) | LIVE (+ CODE for qa_images) | | |
| `out_phrases_v3/gen.py` (PILOT list), `out_deck_sent/gen.py`, `out_deck_a2/a2_adapter.py`, `a2_build/src/build_situations.py` | LIVE | hand lists / comments | |
| `card_frame.py`, `anki/templates.md`, `a2_build/RECORDING_GUIDE.md` | LIVE + CODE | example keys in prose; `ROUTE_SECTIONS` | |
| `build_recorder.py` | CODE | no literal keys; `startswith("S-")` at 595; migration + KEY_MAP (§10) | |
| `tools/verify_apkg.py` | CODE | `startswith("S-")` at 104; `--key-map` for GUID comparison | |
| `tools/golden_set.py` | CODE | `ledger_row(key)` → `keymap.lookup` | reads ledgers (HIST) by key |
| `a2_build/src/apply_benchmark.py`, `a2_build/src/build_a2.py` | HIST | mint `A2-####` ids | **retired**: the list has been edited directly since 2026-10-11 (rounds 3–6); a re-run would regress it. Move to `_archive/deprecated/` in the same commit |
| `wordlist_a2_pending.csv`, `accents_todo_kirtis.csv`, `a2_rebase/*` | HIST | inputs of the retired builder | |
| `out_*/ledger.csv`, `gen_log.jsonl`, `plan.json`, `cards.csv`, `qa_*.csv`, `picks.jsonl`; `~/a2_work/*`, `~/f62_work/*` on the Mac | HIST | append-only generation records | new rows after the rename carry new keys; readers use `keymap.lookup` |
| `build_reports/**` (manifests, `v3.0_A1_keys.tsv`, frame_bands/flags, hand_scan) | HIST / GEN | | frame csvs are rewritten by the next build |
| `a2_build/round3..6/`, `rollout*/`, `pilot_round2/`, `additions_round2/`, `hand_fixes/`, `phrase_additions/`, `review_2026-10-17/`, `historical/` (except likeness_args), `data_checks/`, `benchmark_en/`, `backs_audit/`, `a1_redo/`, `audio/reconciliation_*`, `audio/backfill_audio_source.py` | HIST | | review pages' HTML references old media names — they are history pages |
| `CHANGELOG.md`, `VERSIONS.md`, `docs/VERSIONS.md`, `docs/spec_history/*`, `a2_build/*.md` plans and reports, `a2_build/README.md`, `a2_build/sentences/design.md` | HIST | | `docs/DESIGN_SPEC_CURRENT.md` is edited by hand in the spec release (§14), not by regex |
| `_archive/**`, `style_lab/**` (except settings_assignments.csv) | HIST | | |
| media: `images/*.webp` (520), `audio/*.mp3` (518 + `_superseded` 2), `audio_a2/*.mp3` (150 + `_superseded` 4), `style/golden/*.jpg` + `*.prompt.txt` (28 + 28) | git mv | | hash-checked, logged in `media_log_key_map_v1_tracked.tsv` |
| media on the Mac only: `out_deck_f62/`, `out_deck_a2/`, `out_phrases_v3/`, `out_phrases_v3/round2/`, `out_deck_sent/`, `out_phrases_a2/`, `images_a2/`, `out_phrases/`, `images_sent/` (if present) and each one's `_rerolled/`, `_superseded/`; `_cloud_media/{f62,a2,phrases}/` | `--apply-media` | `<key>[.r<n>].png` etc. | §9 |
| `_apkg_media/` (transcode cache, `.src` sidecars) | delete | | regenerated by the next build; stale sidecars under old names would just be ignored, but clear it so the media hash is clean |

`--verify` enforces this table: every tracked text file outside HIST that still carries one of the map's
old keys fails; a file in none of the three classes fails as UNCLASSIFIED (found on the test run and
fixed: golden prompts, dep37, the tools themselves).

---

## 8. Code changes the executor makes in the same commit as `--apply`

1. **build_apkg.py** — `plate_number(key)` → `str(int(key[:4]))` for all note types (drop the A2-/S-
   branches and the `a1_number` argument; the A1 loop passes `plate_number(k)` instead of `r['number']`);
   delete `IMAGE_ALIAS` and its two lookups (the alias file is renamed to the key); `tags_for()` as §6 for
   the three `add_note` sites; read `type` for A1 rows via master `#` (or add a `type` column to
   `cards_anki.csv` — simpler, recommended). Update the IDENTITY comment block (lines 197–216).
2. **build_study_order_v3.py** — line 400 regex → `^\d{4}_`; `--apply-retier`: master rows by the new
   `key` column (848–853) instead of `int(k[:3])`; 856 sentence keys by membership in `SENTENCES`, not
   `startswith("S-")`; `load_cards` A2 "number" → keep as a tie-break but document that it is the key
   number now. Add a header note: the order file is authoritative after the rename (§1).
3. **deck_builder.py** — line 1254 `key = f"{n:03d}_{slug(...)}"` → `key = r["key"]` (fail loudly if
   blank for an eligible row); docstring examples.
4. **qa_images.py** — `card_id()`: prefer `key` for every source (master now has one); drop the
   numeric-prefix fallbacks at 203, 363, 585 (they would mis-join `0151_…` with FF `#151`).
5. **card_frame.py** — `ROUTE_SECTIONS` keyed by the new tags; add `"Functions"` to XIX; `section_of()`.
6. **build_recorder.py** — §10 (KEY_MAP in the page, `migrateKeys()`, export mapping); line 595 kind
   by the WORDS `kind` field, not `startswith('S-')`.
7. **tools/verify_apkg.py** — `--key-map FILE`: when comparing `--against` an older package, map its
   keys through the file before the GUID/field comparison, and report "GUIDs changed as mapped: N" instead
   of failing; line 104 kind detection by note type/tag.
8. **tools/golden_set.py** — `ledger_row(key)`: try `key`, then `keymap.aliases(key)`.
9. **tools/ingest_takes.py** (new, §10.3).
10. **cards_anki.csv** column `number → ff_no` and the four readers (`build_apkg` A1 loop, `build_study_order_v3`
    `load_cards`, `qa_images.card_id`, `build_recorder` "number" display → show the key number).
11. Retire `a2_build/src/build_a2.py`, `apply_benchmark.py` and the `A2-####` minting to
    `_archive/deprecated/a2_src_2026-10/` with a README line pointing at `--mint`.
12. `.gitignore`: nothing new (the media logs under `a2_build/rename/` are committed; `recorder*.html`
    stays ignored).
13. **Spec release** (§14): prose first, then `tools/spec_release.py --bump minor --note "Keys, plate
    numbers and tags: one NNNN_slug namespace, hierarchical tags (spec §12)"` — this also updates the style lock
    for the `SECTIONS`/`ROUTE_SECTIONS` change. The pre-commit hook will otherwise refuse the commit.

---

## 9. Media method

**Tracked media** (1,250 files): `git mv` inside `--apply`, each file sha1-checked before and after, logged
to `a2_build/rename/media_log_key_map_v1_tracked.tsv` (old_path, new_path, bytes, sha1, method). Done in
the **scratch clone outside Proton** (`~/work/repo` in the Mac VM, or the cloud clone), committed and
pushed from there. Proton Drive is never the place where `.git` is written during a 1,300-file operation —
it has rolled `.git` back and produced "Edit conflict" copies before.

**Untracked renders** (Mac only, ≈1,500 + versions + mirrors): after `git pull` into the Proton working
copy, **pause Proton Drive sync**, then
```
python3 tools/rename_keys.py --apply-media out_deck_f62 out_deck_a2 out_phrases_v3 out_phrases_v3/round2 \
    out_deck_sent out_phrases_a2 images_a2 out_phrases images_sent _cloud_media/f62 _cloud_media/a2 _cloud_media/phrases
```
which renames in place (`os.rename`, same filesystem, atomic per file; the `_rerolled/` and `_superseded/`
subfolders of each dir are included), refuses if any destination already exists, hash-checks each file,
writes `a2_build/rename/media_log_key_map_v1_<host>_<date>.tsv`, and is idempotent (a second run says
"nothing to rename"). Then `--verify` (the full media check only means something here), commit the log,
resume sync. Why in place rather than copy-then-archive: a rename never touches the bytes (the hash check
proves it), the log makes it reversible line by line, and a copy would double 5–6 GB inside a sync folder
that is already the fragile part. Nothing is deleted; nothing old-named is left (verify fails on leftovers).
`~/a2_work/` and `~/f62_work/` ledgers stay as they are (HIST).

Fallback if Proton misbehaves during the pause: the log + the map allow `--apply-media` to be re-run on
whatever is still old-named; a conflict copy (`… (Edit conflict).png`) does not match the media regex and
is reported by `ls`, not touched.

---

## 10. The recorder

### 10.1 What exists
`recorder_A2.html` (regenerated by `build_recorder.py A2`) keeps clips in IndexedDB `lt_recorder_A2_afb2ebe2`
(`DECK_SHEET_ID`, fixed forever): store `clips` (take key → Blob), store `meta` (`said:<key>`,
`superseded:<key>:<ms>`, `exported` = list of keys). Take keys are `<key>` and `<key>_s`. Export writes a
ZIP of `<key>.<ext>` + `manifest.tsv` (key, dest, level, status, said, english, file).

### 10.2 Migration inside the regenerated page (build_recorder.py)
- Embed `KEY_MAP = __KEY_MAP__`: old take key → new take key for every `renamed`/`alias` row of
  **every** map in `a2_build/rename/key_map_v*.csv` (both `<k>` and `<k>_s`), composed through the chain
  (`keymap.canonical`). ≈4,900 entries, ~150 KB — fine next to the 1 MB page.
- `migrateKeys()` runs in `start()` right after `openDB()` and **before** `setAsideStale()`:
  for each key `k` in `storeKeys('clips')` with `KEY_MAP[k]`: if no clip exists under the new key, `putClip(new,
  blob)`, copy `said:k` → `said:new`, `putMeta('migrated:'+k, {to:new, at:Date.now()})`, then `delClip(k)` (a move:
  the take lives on under its new name — this is the superseded rule's "never delete a take", not a deletion);
  if a clip already exists under the new key (recorded after the rename), the old one goes to
  `superseded:<k>:<ms>` with its `said` (and is exported under `superseded/`), never dropped. Then rename the
  members of `meta.exported` through the map. `superseded:<old>:<ms>` entries are left as they are; the export
  code maps `p[1]` through `KEY_MAP` for the folder name so they come out as `superseded/<new>.<ms>.<ext>`.
- Report in `storeInfo`: "N takes carried over from the old card keys."
- Stale check: `setAsideStale()` compares `said:` stamps, which are words, not keys — unaffected; the legacy
  per-key script (`recorder_A2_afb2ebe2_script.json`) is LIVE-rewritten so `legacy.get(t["key"])` still matches.
- Test before handing over: open the regenerated page in a browser profile that has the current DB with a
  dummy clip under an old key (the executor can record one in the current page first), confirm the clip
  appears under the new key, then "Export all" and check the ZIP names and `manifest.tsv`.

### 10.3 Ingest of exported ZIPs (new `tools/ingest_takes.py`)
Owner ZIPs may predate the rename (old file names) or follow it. The script reads `manifest.tsv`, maps
`key` through `keymap.canonical()` (so `A2-0348.webm` lands as `audio_a2/0021_labas.mp3`), takes `dest`
from the **current** `a2_build/recording_list.csv` by the canonical key (never from the manifest: the manifest's
`dest` may be stale), converts with `ffmpeg … -codec:a libmp3lame -q:a 4`, moves a replaced take to
`<dir>/_superseded/<key>.<ms>.mp3`, and appends `key  human  <dest>  <said>` to `audio_source.tsv` (the `said`
column from the manifest). Clips under `off_list/` and `superseded/` are copied to `_archive/takes/<zip-stem>/`
with their manifest rows and are not shipped. Idempotent per ZIP (skip when `dest` already has the same
sha1 as the converted clip would have had — or simply when `audio_source.tsv` already has the key with
`source=human` and matching `said`).

---

## 11. Runbook (executor)

Preconditions: dep37 applied and `study_order.csv` regenerated and committed; `git status` clean; the current
A1 package `Lietuviu_Flashcards_v3.0_A1.apkg` and its manifest exist as the "before" baseline; the owner has
pressed **Export all** in the recorder once (belt — the migration is the braces).

In `~/work/repo` (outside Proton), on `main`:
1. `git pull`; `python3 tools/rename_keys.py --dry-run --out a2_build/rename/dryrun_v1_exec.txt`; read the
   GUARDS block (must be empty) and the counts; compare with `dryrun_v1.txt` (same families, same file list;
   numbers may differ after dep37).
2. `python3 tools/rename_keys.py --apply` — writes `key_map_v1.csv`, rewrites 65 files, `git mv`'s 1,250
   files, runs `--verify` (expect only the five GENERATED warnings).
3. Code changes §8 (1–12). `python3 a2_build/src/build_situations.py` (regenerates `situations.py`);
   `python3 build_study_order_v3.py --audit study_order.csv` (dependency figures equal to the pre-rename audit —
   1,979 uses / 43 forward today; a difference means a missed shape regex); `python3 build_recorder.py A2`;
   `rm -rf _apkg_media`.
4. Spec: edit `docs/DESIGN_SPEC_CURRENT.md` (§14 text; fix the examples in §6/§7 that read `001_suo`,
   `A2-0108`; the merges line reads both names), then `python3 tools/spec_release.py --bump minor --note …`.
5. `python3 tools/rename_keys.py --verify` (zero FAIL, zero WARN now). `GO_ALLOW_STYLE_DRIFT` must **not** be
   needed — if the gate complains, the lock update in step 4 was skipped.
6. Build: `APKG_LEVELS=A1 APKG_VERSION=3.1 python3 build_apkg.py` (A2 too if it is being built at this point);
   `python3 tools/verify_apkg.py <new> --against Lietuviu_Flashcards_v3.0_A1.apkg --key-map a2_build/rename/key_map_v1.csv`
   — same note count (1,186 A1), every old key maps to a note, fields identical except `key`/`Key`, `number`/
   `Number`, media names and tags, GUIDs changed exactly as mapped, media count equal (1,424 for A1), package
   under 250 MB. `python3 frame_preview.py <new>` for a visual spot check of `pav. N` on five cards incl. one
   sentence card. Commit ("Rename: one NNNN_slug key namespace, plate numbers from the key, lt:: tags
   (spec 3.4.0, key_map_v1)"), `git push origin HEAD:main`, `git push --tags`.
7. Proton working copy: pause sync → `git pull` → `--apply-media …` (§9) → `--verify` → commit the media log →
   push → resume sync. Clear `_apkg_media/` there too.
8. Hand the owner: the new `recorder_A2.html` (the IndexedDB name is unchanged, takes carry over), the
   review-desk note (it is LIVE-rewritten), and the AnkiWeb update as a delete-and-reimport.

Rollback: the map and the two media logs are a complete, line-by-line inverse; `git revert` of the commit
restores every tracked file and tracked media name; `--apply-media` has no inverse flag by design (run the
log backwards with a 5-line script if ever needed — it is tab-separated old/new).

---

## 12. Verification (what "done" means)

- `rename_keys.py --verify`: every `key`/`id` in the ten live data files is `NNNN_slug` (merged/deferred ids
  excepted); no tracked LIVE/GEN text file carries any old key; no file under an old name in any media dir;
  every renamed card has an image where the build looks and audio where the data says it has one; no
  UNCLASSIFIED file.
- `build_study_order_v3.py --audit`: identical figures to the pre-rename audit.
- `verify_apkg.py --key-map`: note-for-note equality with the baseline package modulo key/number/tags/media
  names; GUID delta = exactly the map.
- `build_recorder.py A2` output: the same take count as before the rename (2,849 today, minus whatever the
  owner has recorded), every `dest` under a new name; `recording_list.csv` has no old key.
- Browser: the migrated DB shows the recorded count unchanged; an export's `manifest.tsv` carries new keys.
- `golden_set.py --status`: 28 present (through the alias lookup).
- `git grep -E '(^|[^A-Za-z0-9])(A2-[0-9]{4}|S-[0-9]{4}|[0-9]{3}_[a-z])' -- ':!_archive' ':!build_reports' ':!docs/spec_history' …`
  as an independent cross-check of `--verify`'s own regex (the exclusions are the HIST prefixes).

---

## 13. Risks, honestly ranked

1. **Order drift between derivation and lock** (§1). Mitigation: rename last; order file authoritative
   afterwards; a second map is possible but expensive. Residual: medium.
2. **Proton Drive during the untracked media rename** — the one step that cannot be redone from git.
   Mitigation: sync paused, in-place rename, per-file hash + log, idempotent re-run, conflict copies
   detectable. Residual: low-medium; the log makes any mess reversible.
3. **Shape-dependent code I did not find.** The grep for `startswith("A2-")`, `[:3]`, `split("_")[0]`,
   `\d{3}_` across live code found the eight places in §8; `--verify` catches literal leftovers but not logic.
   Mitigation: the audit/build/recorder equality checks in §12 are behavioural, not textual. Residual: low.
4. **Recorder migration bug losing a take.** Mitigation: move-not-delete, `migrated:` trail, owner's Export
   all before the switch, executor test with a dummy clip. Residual: low.
5. **History rewritten by accident** (someone "helpfully" sed-ing a ledger). Mitigation: the class table in
   the tool and this plan; `keymap.py` makes the old names usable so there is no temptation. Residual: low.
6. **Style lock / spec gate refuses the build** because the tag/section change was not released. Mitigation:
   step 4 before step 6; never `GO_ALLOW_STYLE_DRIFT=1`. Residual: nil if the runbook is followed.
7. **`id_map.csv` semantics**: after the rename it is a registry of current keys with four old merged ids; the
   retired builder would have minted `A2-####` again. Mitigation: archive the builder (§8.11). Residual: nil.

---

## 14. Proposed spec text — new section (minor bump → 3.4.0)

Insert after §7 (renumbering is not needed if it is appended as **§12** after §11; recommended: §12 so
existing cross-references stay valid). Also change in §6: "Plate numbers are one sequence …" → "Plate
numbers are the key's number (§12)"; in §7: the examples `001_suo`, `A2-0108` → their new keys (take them
from `key_map_v1.csv`), and the merges line: "A2-1187 (Sudie) → A2-0354 (Viso gero, now `0047_viso_gero`) …".

> ## 12. Keys, plate numbers and tags (2026-10-20; `tools/rename_keys.py`, `a2_build/rename/`)
> - **One key namespace.** Every card key is `NNNN_slug`: a four-digit number and the ASCII-folded headword
>   (phrases and sentences: their first words, ≤ 4 words / 32 characters; `rename_keys.slug`). The number is
>   the card's study-order position when the key was minted (`study_order.csv`, A1 block then A2 block at the
>   rename of 2026-10); the slug is a reading aid, not an identifier — two cards may share one, and it is never
>   re-derived when a headword is corrected.
> - **Keys do not encode the level, the kind, the list or the batch.** Those are tags (below) and the subdeck.
> - **Lock.** Keys, and with them GUIDs (`genanki.guid_for(key)`), are frozen once A1 and A2 are both signed
>   off. After the lock a key never changes or is reused; a card that changes meaning keeps its key; a card
>   that would change note type is a new card. **New cards append:** `tools/rename_keys.py --mint "<headword>"`
>   gives max number in use + 1 and the slug; the card is scheduled wherever the order puts it, so after
>   additions the number is a stable name, not a position.
> - **History of names.** Every earlier name of a card (`001_suo`, `A2-0348`, `S-0001`, media aliases) is in
>   `a2_build/rename/key_map_v<N>.csv` (append-only; never edited or deleted). Append-only records (ledgers,
>   gen logs, QA sheets, build manifests, reports, the spec history) are never rewritten; they are read through
>   `tools/keymap.py` (`canonical`, `aliases`, `lookup`). Live data carries the current key only.
> - **Media names follow the key**: `<key>.png|webp|jpg`, `<key>.mp3`, `<key>_s.mp3` (example sentence),
>   `<key>_sf<v>.jpg` (cropped copy), `_rerolled/<key>.r<n>.png`, `style/golden/<key>.jpg` + `.prompt.txt`.
>   Recorder take keys are `<key>` and `<key>_s`; the recorder page carries the key map and re-keys stored
>   clips on start (move, never delete); `tools/ingest_takes.py` maps exported file names the same way.
> - **Plate number.** `pav. N` in the bottom band is the key's number, for every note type
>   (`build_apkg.plate_number`), rendered from the `number`/`Number` field by the frame CSS; no picture carries
>   a number. The Fluent Forever row (`master_wordlist.csv` `#`, `cards_anki.csv` `ff_no`) is a data join only
>   and is not shown. (Until 3.3.0: A1 1–531 by wordlist row, A2 1001+, sentences 4001+.)
> - **Tags.** Four hierarchical tags per note: `lt::level::A1|A2`; `lt::kind::picture|phrase|cloze|sentence`;
>   `lt::pos::noun|verb|adjective|adverb|pronoun|numeral|preposition|conjunction|question` (words only);
>   `lt::topic::<section slug>` — one of the twenty top-band sections, ASCII-slugged (`zmones` … `sakiniai`),
>   from `a2_build/rename/topic_map_v1.csv` (category → topic; an unmapped category fails the build). The
>   section label in the top band is chosen by the Category field, overridden to XIX/XX by `lt::kind::phrase`
>   / `lt::kind::sentence` (`card_frame.ROUTE_SECTIONS`). The former `route` and `phase` tags are retired.
> - **Tooling.** `tools/rename_keys.py` (dry run by default; `--apply`, `--apply-media`, `--verify`, `--mint`)
>   is the only way keys are renamed; `--verify` fails on any old key outside history, on unclassified files
>   and on media missing under the new name.

Changelog line: `3.4.0 — 2026-10-xx. §12 added: one NNNN_slug key namespace (numbers from the study order at
the rename, slugs from the headword), plate number = key number for all note types, hierarchical lt:: tags
with the 20-section topic map, key history in a2_build/rename/key_map_v1.csv; SECTIONS gains Functions,
ROUTE_SECTIONS keyed by lt::kind tags (owner decision 2026-10-19 "rename everything so it's consistent").`

---

## 15. What the owner must decide (kept minimal — he delegated this)

1. **Timing only:** confirm "dep37 first, then the rename as the last pre-lock change" (§1). If he would
   rather rename now and accept a possible `key_map_v2` later, the tool supports it; the cost is one more
   Mac media pass and recorder migration.
2. Nothing else. The sentence-slug rule (first words), the tag vocabulary, "history is not rewritten",
   "folders stay, files move", `number → ff_no`, retiring `build_a2.py`: all defaulted here with reasons;
   any of them can be reversed before `--apply` at the cost of a line in the tool.
