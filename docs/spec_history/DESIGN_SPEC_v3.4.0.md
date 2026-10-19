<!-- FROZEN copy of docs/DESIGN_SPEC_CURRENT.md at spec version 3.4.0 (2026-10-20). Do not edit; the live spec is docs/DESIGN_SPEC_CURRENT.md, the lock style/STYLE_LOCK.json. -->
# Lietuvių Flashcards — current design spec (de facto)

**Spec version 3.4.0** · dated 2026-10-20 · style lock `style/STYLE_LOCK.json` · history `docs/spec_history/`

This is the one authoritative statement of the design parameters the pipeline
actually uses today. Every line is sourced to the code (file + constant) or to a dated owner decision;
when a doc and the code disagree, the code and the most recent owner decision win
(`docs/SPEC_RECONCILIATION_2026-10-19.md` lists the disagreements found). Older specs
(`_archive/docs/GO_STYLE_SPEC.md`, `ROADMAP.md`, `VERSIONS.md`, the `a2_build/*.md` plans) are history.
Read this file first in a new session; change the code, then this file, in the same commit.

## 1. Image engine
- **Model / quality / size:** `gpt-image-2.5-sunburst`, quality `medium`, 1536×1024 (ratio 4:3).
  `go_generator.OPENAI_MODEL` (env `GO_IMAGE_MODEL`), `OPENAI_QUALITY`, `OPENAI_SIZES["4:3"]`;
  `deck_builder.RATIO = "4:3"`. Z-Image-Turbo (`ZIMAGE_SPACE`) exists as a fallback path and is not used.
  Cost basis used in plans: ≈ $0.0135 a render, QA ≈ $0.01–0.07 a card.
- **House style F6.2** (2026-10-11, blind owner surveys `style_lab/2026-10-10_06..08`, spot-check 09):
  two leads differing only in composition — `CONCEPT_LEAD` (vignette: subject on bare light paper,
  surroundings fading out) and `CONCEPT_LEAD_SCENE` (full scene edge to edge, places/crowds,
  `deck_builder.FULL_SCENE_ROWS`) — each closed by its `STYLE_SUFFIX*`. 1981 Lithuanian civil-defence
  training album, brush-ink outlines, dead-matte gouache, four-colour offset, aged cream paper
  (paper target L* 85–88, b* 18–23, `style_lab/tools/papertone2.py`). The gpt-image-1.5 lead is kept
  only as `LEGACY_CONCEPT_LEAD_1_5` for reading old ledgers.
- **People:** ordinary Lithuanians of 1981, correct proportions, distinct individuals
  (`DISTINCT_FACES_RULE`). **Hair** (lead text, owner 2026-10-11): women blond or light-brown; the
  younger lean, hair mostly straight, now and then faintly waved or styled; older women in the usual
  everyday range — plain, pinned back or set, *occasionally* curled, or under a cotton headscarf; curls are
  one option, never a rule. Men side-parted or cropped, some moustached, working men in flat caps.
- **Dress classes** `go_generator.FIGURE_DRESS`: `worker` (blue-grey work clothes, flat caps, black
  kirza boots), `professional` (white coat + small red cross, teacher with pupils, white smock, plain
  service uniform), `civilian` (default for nouns and places since 1.7.1), `formal` (Sunday best;
  `deck_builder.FORMAL_ROWS`). Per-card routing in `deck_builder` (NOUN_STAGING, OVERRIDE_CLASS) and
  the `card_notes.json` staging lines.
- **Gaze (house):** varied natural angles; in a group one or two face the viewer, eyes just past the
  shoulder; of two main figures only one; a lone figure near-frontal (`_HOUSE_GAZE_LEAD`, `GAZE_PAIR_RULE`).
- **Standing rules on every card:** `BARS_RULE` (plain dark brick-red bands top and bottom, thin border,
  nothing crosses them), `NO_CUTAWAY_RULE`, `ANATOMY_RULE` (five fingers; `ANATOMY_PROPS_RULE` on situation
  cards), `PLAUSIBILITY_RULE`, `MATTE_RULE`, `MAIN_MEANING_RULE` (the main picture alone carries the word),
  `ARROW_RULE`, `SETTING_GUARD`, `NO_STRAY_FIGURE`. With insets: `INSET_RULE` (2–3, same thin ruled frame,
  each a clearly different moment), `INSET_MEANING_RULE` (an inset never votes for a neighbouring word),
  `PANEL_CONTINUITY_RULE` (deck-wide since 2026-10-17: repeated scenes keep people, clothes, positions and
  fixtures). Walking/running: `MOTION_STRIP_RULE` (`deck_builder.MOTION_STRIP_ROWS`).
- **Direction of movement** (owner 2026-10-19, "Yes, as drafted" — `a2_build/round4/answers.md` §4; spec 3.1.0):
  `DIRECTION_RULE` — when the **main figures** walk, run, ride, drive or carry something from one place to another
  they travel from the viewer's LEFT toward the RIGHT, the way a page is read; figures who stand, sit or talk are not
  affected, and it **applies to the main actors only, never to background figures** (owner: "it applies only to the
  main actors in the image, not background"). Routing `go_generator.direction_applies()`: on for motion-strip cards
  and for cards whose subject or staging carries a verb of motion; **off** for `deck_builder.DIRECTION_FREE_ROWS`
  (cards whose meaning is a side or a direction: 425 sukti, A2-0995 dešinėje, A2-0958 Kairėje, A2-2005, A2-1506/1526,
  A2-1689/1690, A2-1047/0959 tiesiai, A2-0405/1638/1680 grįžti/pareiti, A2-0423, A2-1061/1062, A2-1084, A2-1878,
  A2-0212), for two-panel `situation_2` cards, and for any staging that names a side itself in capitals (LEFT/RIGHT —
  the staging wins). Callers pass `direction=False` for the free rows (`deck_builder.build_call`,
  `a2_adapter.build_call_a2`, `gen_phrases.build_situation_call`). **New renders only:** no card is re-rolled for
  this rule ("No need to retcon old cards").
- **Real places** (F6.1): a `Setting:` line from `go_settings.assign()` —
  `style_lab/research/settings_assignments.csv` over `style_lab/research/location_bank.json`
  (free Lithuania, 1981; anachronisms tolerated where the GO theme holds — owner, Oct 2026).

## 2. Lettering and emblems
- **No text by default** (`NO_TEXT_RULE`). Lettering is allowed **only** where a row declares it in its
  `card_text` column (`master_wordlist.csv`: 22 A1 rows; `a2_build/a2_wordlist.csv`: 98 rows), rendered
  through `go_generator._exact_text_rule()` (unconditional spec, the target word excluded), and
  **verified by QA rule 3** (`qa_images.py`: every quoted string must read back exactly). Prices are in
  **litai** (`"2 Lt 40 ct"`), never roubles. Glyph cards (letter/consonant/vowel) use `GLYPH_RULE`.
- **Posters, playbills and signs** (owner 2026-10-19, round 4): when a picture shows a poster, playbill or
  sign, it shows a **real period Lithuanian work** — a film, play or the like that a free Lithuania of 1981
  could plausibly show (no Soviet-convention titles) — with its title **declared** in the row's `card_text`
  and **read back exactly by QA rule 3**. Blank posters and empty frames are avoided. First uses: A2-1191
  *šiaip sau* — `"VELNIO NUOTAKA"` (Žebriūnas, 1974); A2-1360 *spektaklis* — `"MILŽINO PAUNKSMĖ"` (Sruoga,
  1932) (`a2_build/round4/answers.md`, appendix).
- **Emblems:** default `FLAG_RULE` — at most a small tricolour, not on every card, no heraldry.
  `FLAG_RULES["eu"]` / `["imperial"]` on the measurement cards 334–339 (`deck_builder.FLAG_OVERRIDE`).
  `FLAG_RULES["emblem"]` (Cross of Vytis / Vytis allowed) is routed to **097 prezidentas only**
  (`FLAG_OVERRIDE.update({97: "emblem"})`, "President card only (as now)" — owner 2026-10-19) and is
  **dormant**: in round 4 the owner put the shipped 097 picture back (an anonymous president, no likeness,
  no Vytis), so **no shipped card shows a Vytis**; the allowance acts only on a future 097 re-roll. 035
  teismas carries the **flag, not the Cross** (owner 2026-10-19). Columns of Gediminas and every other
  badge stay out.

## 3. Historical precedents and likenesses (2026-10-18/19)
- `PRECEDENT_RULE` evokes a real Lithuanian thing by features only (never a name or plaque);
  `LIKENESS_RULE` asks for a named face at a named period on listed cards only. Per-card values:
  `historical.py` reading `a2_build/historical/implementation/likeness_args.json` (`active`:
  012 lėktuvas = the Lituanica with Darius and Girėnas, 035 teismas, A2-1297, A2-1769, 113 gydytojas,
  122 menininkas (Čiurlionis), A2-0782, 138 komanda (1939 team); 123 autorius and **097 prezidentas**
  kept as shipped and inactive — 097's Adamkus test render was withdrawn by the owner in round 4,
  2026-10-19). 26 real A2 places adopted (`a2_build/historical/real_places.md`, `settings_rows.csv`);
  round 4 reverted four of the roll-out's place rows at the owner's word (106, 107 State Stadium,
  A2-1326 post-office inset, A2-0085 railway station hall — rows marked REVERTED). Rules text: `a2_build/historical/implementation/RULES_precedent_likeness.md`
  (applied; the code is the truth).

## 4. Situation grammar (bubble-free phrase cards, 2026-10-17)
- Every former speech-bubble card is routed by `situations.py` (GENERATED by
  `a2_build/src/build_situations.py` from `a2_build/restage_bubbles.csv`; never hand-edited) to one of
  three layouts: `situation` (one calm scene), `situation_2` (two panels, ask → visible answer, same two
  people), `sequence` (the one three-panel strip). `generate(..., situation=True)` swaps `NO_TEXT_RULE`
  for `NO_TEXT_RULE_SITUATION` + `NO_BUBBLE_RULE`; **no bubbles, no "?"**, no `exclude` word.
- **Conversation gaze:** rows with `gaze == "conversation"` get `CONVERSATION_GAZE_RULE` in place of the
  three house gaze sentences (speakers look at each other, nobody at the viewer); non-speaking situation
  rows keep the house gaze. Situation cards use `ANATOMY_PROPS_RULE`.
- **Insets stay** on single-scene cards for beauty (owner, Oct 2026) and are bound by
  `PANEL_CONTINUITY_RULE` where they repeat the scene.
- Production drivers: `out_phrases_v3/gen.py` (imports `gen_phrases.build_situation_call`);
  renders in `out_phrases_v3/` (pilot round 1 + roll-out) and `out_phrases_v3/round2/` (pilot round 2).
  The replaced bubble pictures are in `_archive/recent_versions/` (moved 2026-10-19).

## 5. QA gate
- `qa_images.py`, model `gpt-5.6-luna` (`MODEL`, env `GO_QA_MODEL`), cache `_qa/qa_cache.json` keyed by
  file hash. Checks: no undeclared lettering (target word = hard FAIL), blind guessability, declared text
  read back exactly; **round-2 checks** (`FIT_PROMPT`: speakers' gaze on conversation cards, two-panel
  continuity, limb ownership and held props; `NEIGHBOUR_PROMPT`: no vote for a neighbouring word);
  `--limbs` gives every non-situation card the limb/prop call too (`LIMBS_PROMPT`, 2026-10-18 hand-scan).
  Since 3.1.0 `FIT_PROMPT` also asks which way the main moving figures travel ("direction"); right-to-left on a card
  that got `DIRECTION_RULE` is a **WARN**, never a FAIL.
  Rule in force: generate → QA → review page → owner confirms → commit/push.

## 6. Card front and back (v2.1 "standard bands", `card_frame.py`, `anki/frame_standard.css`)
- The drawn frame is cropped off a copy of each picture (`frame_crop.py`, `FRAME_CROP_VERSION = "2"`;
  sources never written; failures → `build_reports/frame_flags.csv`) and redrawn in CSS at one width.
- **Top band:** Lithuanian section label `"N skyrius · <label>"` from `card_frame.SECTIONS` (I žmonės … XX
  sakiniai; XVI *daiktai ir sąvokos*, XVIII *pagalbiniai žodžiai* — owner 2026-10-19), chosen by the
  note's Category field and `ROUTE_SECTIONS` tags (`lt::kind::phrase` → XIX frazės, `lt::kind::sentence` → XX
  sakiniai; §12). `Functions` belongs to XIX.
- **Bottom band:** `pav. N` · leader · **English caption** (the `english` / `Gloss` field). Plate numbers
  are the key's number (§12; `build_apkg.plate_number`: `0021_labas` → pav. 21), for every note type.
- **Cloze fronts hide the English caption** (`.sf-cloze-front .sf-en { visibility: hidden }`); the
  cloze sentence sits on a paper panel inside the frame (or under the picture on sentence cards).
- **Back (default since 2026-10-18):** `card_frame.proposed_backs("thumb")` + `anki/back_proposed.css`
  — thumbnail picture, word, stressed `pron`, audio, gender, forms, gloss, then the **usage line**
  (field `usage`/`Usage`, from `a2_build/context_notes.csv`, confidence high/medium/owner-approved,
  `build_apkg.USAGE_CONFIDENCE`). **Adjectives** show both forms as `didelis ♂ · didelė ♀`
  (`build_apkg.adjective_forms`). `--back current` and `--frame drawn` keep the older looks reachable.
- **Typography:** Brygada 1918 regular/italic/bold throughout, shipped as media `fonts/_Brygada1918-*.ttf`
  (`card_frame.FONT_FILES`); PT Serif / Old Standard TT retired to `fonts/_superseded/`.
- **Note types:** "Lietuvių GO" (`GO_FIELDS`, 14 fields incl. `usage`) and "Lietuvių GO Cloze"; model ids
  and deck ids never change; GUIDs are `genanki.guid_for(key)` and change only with a key (§12: once, at the
  rename of 2026-10-20, then frozen at the A1+A2 lock). Decks: `Lietuvių Flashcards::A1` / `::A2`.

## 7. Content and data
- A1 base: `cards_anki.csv` (521 cards, built from `master_wordlist.csv` + `card_notes.json` staging; its
  `ff_no` column is the Fluent Forever row, a data join only). A2 list: `a2_build/a2_wordlist.csv` (first built
  by `build_a2.py`, edited directly since 2026-10-11; the builder is retired to `_archive/deprecated/a2_src_2026-10/`;
  `a2_build/id_map.csv` registers the current keys). Sentences: `a2_build/sentences/sentences.csv`. Keys: §12.
- **Image resolution order** (`build_apkg.A1_IMAGE_DIRS` / `A2_IMAGE_DIRS` / `SENT_IMAGE_DIRS`, first hit wins):
  A1 `out_phrases_v3, out_deck_f62, images`; A2 `out_phrases_v3/round2, out_phrases_v3, out_deck_a2,
  out_phrases_a2, images_a2, out_phrases`; sentences `out_phrases_v3, out_deck_sent, images_sent`.
  `images/` holds the 1.x WebP masters as the A1 fallback; the pre-F6.2 PNGs are in `_TO_DELETE/out_deck/`.
- **Merges** (owner 2026-10-19, `a2_build/merged_keys.csv`): A2-1187 Sudie → A2-0354 Viso gero (now
  `0047_viso_gero`, back note), A2-1149 atsargiai → A2-0385 Atsargiai! (`0344_atsargiai`), A2-1944 → A2-1995
  (`2221_kaip_rasoma`), A2-1958 → A2-1991 (`1727_man_labiau_patinka_arbata`). The absorbed id stays reserved
  under its old name (`id_map.csv` `merged_into`; `status=merged` in the key map). **B1 deferrals:** 31 rows in
  `a2_build/deferred_B1.csv`, out of the A2 build.
- **Prašom + infinitive** (owner 2026-10-18, `a2_build/PRASOM_SWITCH_2026-10-18.md`): the four postposed
  *prašau* phrases (`0521_prasom_pakartoti`, `0565_prasom_uzrasyti`, `0203_prasom_kalbeti_leciau`,
  `1029_prasom_sestis`; formerly A2-0902/0903/0375/1166) and two cloze examples now read *Prašom pakartoti* etc.
- `2136_ar_galite_ka_nors` (formerly A2-0964): *Ar galite ką nors parekomenduoti?* (owner 2026-10-19).
- Stress marks are sourced (Wiktionary / kirtis.info / LKŽ), never generated; `a2_build/stress_58_resolved.csv`.

## 8. Study order v3 (`build_study_order_v3.py` → `study_order.csv`, adopted 2026-10-19; v2 2026-10-17 is history)
- Usefulness first, as v2: a hand-ordered `SURVIVAL` list, then score = 0.6·ln(subtitle rank) + 0.4·ln(press rank)
  + tier offset − 0.3 if in the VU A1/A2 lexicon. Lane mixing `LANE_CAP 3 / WINDOW 10` plus **lane pressure**
  (a lane behind its share is pulled forward, `LANE_PULL 0.08`, clipped ±2), so no subdeck ends in a run of one
  kind. Pictures first: A1 `FIRST_CLOZE 100`, `FIRST_PHRASE 20` (greetings from card 20, a phrase every 4+ cards),
  `FIRST_COLOURS 40`; A2 `A2_FIRST_CLOZE 30`; the reading-card cap per 10 follows the subdeck's share (4–8).
- **Dependencies:** a cloze, pair or sentence card waits until every word of its sentence is taught by an
  earlier card (same subdeck or earlier; surface form or simplemma lemma, listed forms, ne- + known verb; names
  ignored); the needed word is pulled to (reading card's score + 1); cycles broken by score. Sentence cards
  are scheduled inside their own subdeck, right after the last of their words.
- **Pairs:** `PIN_AFTER` (batonas after duona, the family pairs …), the Fluent Forever adjective pairs and the
  list's "pair with" `PAIRS` sit adjacent. **Confusables:** same headword `SEPARATION 60`, look-alikes (edit
  distance 1, ≥ 4 letters, paradigms exempt) `LOOKALIKE_SEPARATION 30`. Sequences keep order.
- **Re-tiers** `a2_build/study_order/retier_v3.csv` (49 cards, one reason each; `--apply-retier` writes the
  `level` into `cards_anki.csv`, `master_wordlist.csv` (by its `key` column), `a2_build/a2_wordlist.csv`): 21 A2 → A1
  (words A1 sentences need: manyti, vėluoti, likti …, and dep37 of 2026-10-20: muzika, keltis, tiesa, teisus,
  šviesti; split antonym partners piktas, abi, linksmas, šiemet), 28 A1 → A2 (rare Fluent Forever leftovers:
  plaštaka, lydyti, išlenktas …). The 62-item retag of 2026-10-17 stands.
- **Audit as code:** `--audit FILE` measures any order (coverage, forward dependencies, pairs, confusables,
  pacing, Spearman vs the corpora); `--report` compares the new order with the one it replaces
  (`a2_build/study_order/AUDIT_v3.txt`, `REPORT_order_v3.md`). v2 → v3: forward dependencies 172 → 43 (37 left
  are A1 sentences needing an A2-only word), pairs apart 14 → 0, longest tail run 119 → 11. dep37 (2026-10-20,
  `a2_build/study_order/dep37_plan.md`, `AUDIT_v3_1.txt`): 5 words to A1 and 27 example sentences reworded →
  **0 A1 cards need an A2-only word**, 6 forward dependencies left (4 A1-internal cycle cases, 2 A2).
- **Recording order** `a2_build/study_order/recording_order_v3.csv`: A1 first, then A2, each in study order.
- Deck v3.0 is delete-and-reimport. Keys and GUIDs are **not yet frozen**: they lock once both A1 and A2 are signed off by the owner (owner, 2026-10-19: "day 0 of release"). Until then a key may change when that gives a cleaner deck; record every change in `a2_build/merged_keys.csv`, a key map (§12) or the plan that made it. After the lock, keys and GUIDs never move.
- **Since the rename (2026-10-20) `study_order.csv` is the authority**, not the builder: the key numbers were
  taken from it, and the builder now breaks ties on those numbers, so a regeneration need not reproduce it.
  `build_apkg` writes the position to `due`.

## 9. Packages, versioning, release
- Version scheme: packages `Lietuviu_Flashcards_v<APKG_VERSION>_<level>.apkg` (`APKG_VERSION` default
  `"2.1"`, env; `APKG_LEVELS=A1` or `A2`, one package per level under AnkiWeb's 250 MB cap);
  `versioned_out()` never overwrites — a repeat build gets `-1`, `-2`. Engine/data history uses
  `files X.Y.Z / wordlist N.M` (`CHANGELOG.md`, `VERSIONS.md`). Current packages: `Lietuviu_Flashcards_v2.1_A1.apkg`,
  `_A2.apkg`; v1 and v2.0 are in `_TO_DELETE/`. The A1 release is **v3.0** (major, delete-and-reimport; card keys and GUIDs lock once A1 and A2 are both signed off), built 2026-10-19 as `Lietuviu_Flashcards_v3.0_A1.apkg`; see `docs/VERSIONS.md`.
- **Release plan (owner 2026-10-19):** release **A1 now, audio later**; because the note types changed
  (usage field, backs, frame) this release is **delete-and-reimport** for existing users — deck coherence
  over old study history. A2 follows (`A1_WRAPUP.md` "A2 — the shorter list").
- **Image versioning:** a re-roll moves the old render to `<dir>/_rerolled/<key>.r<n>.png` (the gen.py
  scripts, `edit_inset.py`, `restore_before.py`); a design change moves replaced pictures to
  `<dir>/_superseded/`. Nothing is overwritten or deleted; clean-ups go to `_TO_DELETE/` for the owner.
- Media is distributed via GitHub Releases / AnkiWeb, not committed (`.gitignore`).

## 10. Ways of working
- **Review Desk SOP** (`review_desk/README.md`): one artifact holds everything the owner must decide;
  `items.json` → `build.py` → republish; answers in the page db; **every message to the owner ends with a
  link to the Review Desk** and to any page he must open. Nothing ships without his verdict on a review page.
- **Planner / executor split:** Fable plans and judges (staging, rules, spec, review pages); Opus executes
  (renders, edits, builds) from written plans (`a2_build/PLAN_*.md`, `A1_WRAPUP.md` tags owner/planner/executor).
- Positive prompting (state what to draw; never a condition in a prompt), audit before scale, one canonical
  spec (this file), version-track instead of overwrite.
- **Fix by whole re-roll, not masked edits, unless the owner asks for an edit** (owner 2026-10-19, round 5: "this
  patching of images isn't working"). A faulty picture is re-rolled whole from its staging (changed where needed);
  masked/inpainted edits (`edit_inset.py`) and composites are used only when the owner asks for an edit. Every
  version is kept in `_rerolled/`.

## 11. Versioning of this spec and of the look
- **Spec version** (header line, semantic): **major** = the look or the card format changes; **minor** = a
  rule is added; **patch** = wording. `tools/spec_release.py --bump major|minor|patch --note "..."` bumps the
  header, adds the changelog line below, freezes a copy as `docs/spec_history/DESIGN_SPEC_v<X.Y.Z>.md`,
  commits and tags `spec-v<X.Y.Z>`. Frozen copies are never edited.
- **Style lock** `style/STYLE_LOCK.json` (`tools/style_lock.py`): every look-defining constant (leads,
  suffixes, every `*_RULE`, `FIGURE_DRESS`, hair wording, model/quality/size, QA prompts, frame CSS, band
  colour and widths, fonts, section labels, templates; since 3.0.1 also `go_grammars.py` — `SCENE_TAIL`,
  the category grammars `NOUN_GRAMMARS` / `CAT2CLASS` / `PEOPLE_CLASS` / `NO_INSET_CLASSES` and the output
  of `compose_class` for every class and category) with a hash per item and one **style hash**.
  `check` fails when the code drifts from the lock (pre-commit hook `tools/hooks/pre-commit`; `build_apkg.py`
  refuses to build, `GO_ALLOW_STYLE_DRIFT=1` overrides and is logged in the build manifest). `update`
  refuses unless the spec version was bumped.
- **Golden set** `style/golden/` (24 exemplars + prompts): any new model or engine must reproduce them to
  the owner's satisfaction before adoption (`style/golden/README.md`).
- **Linkage:** each package build records APKG version, spec version, style hash, commit, counts and a
  media hash in `build_reports/builds/<package>.json` and in the deck description; `docs/VERSIONS.md` is the
  register deck ↔ spec ↔ style; every ledger row written since 3.0.0 carries `spec_version` and `style_hash`.
- Procedure for any change to the aesthetic: `docs/HOW_TO_CHANGE_THE_LOOK.md`.

## 12. Keys, plate numbers and tags (2026-10-20; `tools/rename_keys.py`, `a2_build/rename/`)
- **One key namespace.** Every card key is `NNNN_slug`: a four-digit number and the ASCII-folded headword
  (phrases and sentences: their first words, ≤ 4 words / 32 characters; `rename_keys.slug`). The number is
  the card's study-order position when the key was minted (`study_order.csv`, A1 block 0001–1191 then A2 block
  1192–2433 at the rename of 2026-10-20); the slug is a reading aid, not an identifier — two cards may share one,
  and it is never re-derived when a headword is corrected.
- **Keys do not encode the level, the kind, the list or the batch.** Those are tags (below) and the subdeck.
- **Lock.** Keys, and with them GUIDs (`genanki.guid_for(key)`), are frozen once A1 and A2 are both signed
  off. After the lock a key never changes or is reused; a card that changes meaning keeps its key; a card
  that would change note type is a new card. **New cards append:** `tools/rename_keys.py --mint "<headword>"`
  gives max number in use + 1 and the slug; the card is scheduled wherever the order puts it, so after
  additions the number is a stable name, not a position.
- **History of names.** Every earlier name of a card (`001_suo`, `A2-0348`, `S-0001`, media aliases such as
  `265_lupos`) is in `a2_build/rename/key_map_v<N>.csv` (append-only; never edited or deleted). Append-only
  records (ledgers, gen logs, QA sheets, build manifests, reports, round folders, the spec history, the
  proofreading sheet sent before the rename) are never rewritten; they are read through `tools/keymap.py`
  (`canonical`, `canonical_take`, `aliases`, `lookup`). Live data carries the current key only.
- **Media names follow the key**: `<key>.png|webp|jpg`, `<key>.mp3`, `<key>_s.mp3` (example sentence),
  `<key>_sf<v>.jpg` (cropped copy), `_rerolled/<key>.r<n>.png`, `style/golden/<key>.jpg` + `.prompt.txt`.
  Recorder take keys are `<key>` and `<key>_s`; the recorder page carries the key map and re-keys stored
  clips on start (move, never delete); `tools/ingest_takes.py` maps exported file names the same way.
- **Plate number.** `pav. N` in the bottom band is the key's number, for every note type
  (`build_apkg.plate_number`), rendered from the `number`/`Number` field by the frame CSS; no picture carries
  a number. The Fluent Forever row (`master_wordlist.csv` `#`, `cards_anki.csv` `ff_no`) is a data join only
  and is not shown. (Until 3.3.0: A1 1–531 by wordlist row, A2 1001+, sentences 4001+.)
- **Tags.** Hierarchical tags per note: `lt::level::A1|A2`; `lt::kind::picture|phrase|cloze|sentence`;
  `lt::pos::noun|verb|adjective|adverb|pronoun|numeral|preposition|conjunction|question` (words only; phrases
  and sentences have none); `lt::topic::<section slug>` — one of the twenty top-band sections, ASCII-slugged
  (`zmones` … `sakiniai`), from `a2_build/rename/topic_map_v1.csv` (category → topic; an unmapped category
  fails the build). The topic is always the section the card's top band shows: the label is chosen by the
  Category field, overridden to XIX/XX by `lt::kind::phrase` / `lt::kind::sentence` (`card_frame.ROUTE_SECTIONS`),
  so phrase notes are tagged `lt::topic::frazes` and sentence notes `lt::topic::sakiniai` whatever their category.
  The former `route` (IMG/PHRASE/CLOZE/PAIR/SENT) and `phase` (PA … PL) tags are retired.
- **Tooling.** `tools/rename_keys.py` (dry run by default; `--apply`, `--apply-media`, `--verify`, `--mint`)
  is the only way keys are renamed; `--verify` fails on any old key outside history, on unclassified files
  and on media missing under the new name. `tools/verify_apkg.py --against OLD --key-map key_map_v1.csv`
  compares a package with one built before a rename (GUIDs changed exactly as mapped; fields modulo key,
  number, media names and tags) and checks plate = key number and the tags on every note.

## Spec changelog
- **3.4.0 — 2026-10-20.** §12 added: one NNNN_slug key namespace (numbers from the study order at the rename of 2026-10-20, slugs from the headword), plate number = key number for all note types, hierarchical lt:: tags with the 20-section topic map (topic = the section shown), key history in a2_build/rename/key_map_v1.csv read through tools/keymap.py; SECTIONS gains Functions, ROUTE_SECTIONS keyed by lt::kind tags; §7/§8 updated for the rename and dep37 (owner decision 2026-10-19: rename everything so it's consistent)
- **3.3.0 — 2026-10-19.** Key/GUID freeze moved: keys lock once A1 and A2 are both signed off, not at v3.0 (owner, 2026-10-19)
- **3.2.1 — 2026-10-19.** §9: the A1 release is v3.0 (major), not v2.2
- **3.2.0 — 2026-10-19.** Study order v3: dependency ordering (words before the sentences that use them), lane pressure against tail runs, PAIRS adjacency, look-alike separation, sentence cards in their own subdeck, 44 re-tiers (retier_v3.csv); build_study_order_v3.py replaces v2, audit as code
- **3.1.0 — 2026-10-19.** rule added: DIRECTION_RULE (main figures travel left to right; main actors only, not background; DIRECTION_FREE_ROWS, situation_2 and LEFT/RIGHT-named stagings exempt; new renders only; FIT_PROMPT direction WARN); working rule: fix by whole re-roll, not masked edits, unless the owner asks for an edit. Erratum: 3.0.1 added a rule (posters/signs) and should have been a minor release; it is not renumbered.
- **3.0.1 — 2026-10-19.** wording: emblem rule dormant (097 restored, no shipped Vytis); poster/sign rule (real period work, declared card_text, QA read-back, no blank posters); go_grammars.py (SCENE_TAIL, compose_class, category grammars) added to the style lock as six new items
- **3.0.0 — 2026-10-19.** First versioned release: the 2026-10-19 de facto spec (F6.2 house style, v2.1
  standard bands, proposed backs, Brygada 1918, situation grammar, emblem scope, study order v2), with the
  style lock, golden set and build manifest introduced in §11.
