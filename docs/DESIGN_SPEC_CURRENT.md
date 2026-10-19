# Lietuvių Flashcards — current design spec (de facto)

**Spec version 3.0.1** · dated 2026-10-19 · style lock `style/STYLE_LOCK.json` · history `docs/spec_history/`

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
  Rule in force: generate → QA → review page → owner confirms → commit/push.

## 6. Card front and back (v2.1 "standard bands", `card_frame.py`, `anki/frame_standard.css`)
- The drawn frame is cropped off a copy of each picture (`frame_crop.py`, `FRAME_CROP_VERSION = "2"`;
  sources never written; failures → `build_reports/frame_flags.csv`) and redrawn in CSS at one width.
- **Top band:** Lithuanian section label `"N skyrius · <label>"` from `card_frame.SECTIONS` (I žmonės … XX
  sakiniai; XVI *daiktai ir sąvokos*, XVIII *pagalbiniai žodžiai* — owner 2026-10-19), chosen by the
  note's Category field and `ROUTE_SECTIONS` tags (PHRASE → XIX frazės, SENT → XX sakiniai).
- **Bottom band:** `pav. N` · leader · **English caption** (the `english` / `Gloss` field). Plate numbers
  are one sequence (`build_apkg.plate_number`): A1 1–531, A2 1001+ (A2-0001 → 1001), sentences 4001+.
- **Cloze fronts hide the English caption** (`.sf-cloze-front .sf-en { visibility: hidden }`); the
  cloze sentence sits on a paper panel inside the frame (or under the picture on sentence cards).
- **Back (default since 2026-10-18):** `card_frame.proposed_backs("thumb")` + `anki/back_proposed.css`
  — thumbnail picture, word, stressed `pron`, audio, gender, forms, gloss, then the **usage line**
  (field `usage`/`Usage`, from `a2_build/context_notes.csv`, confidence high/medium/owner-approved,
  `build_apkg.USAGE_CONFIDENCE`). **Adjectives** show both forms as `didelis ♂ · didelė ♀`
  (`build_apkg.adjective_forms`). `--back current` and `--frame drawn` keep the older looks reachable.
- **Typography:** Brygada 1918 regular/italic/bold throughout, shipped as media `fonts/_Brygada1918-*.ttf`
  (`card_frame.FONT_FILES`); PT Serif / Old Standard TT retired to `fonts/_superseded/`.
- **Note types:** "Lietuvių GO" (`GO_FIELDS`, 14 fields incl. `usage`) and "Lietuvių GO Cloze"; model ids,
  deck ids and GUIDs (`genanki.guid_for(key)`) never change. Decks: `Lietuvių Flashcards::A1` / `::A2`.

## 7. Content and data
- A1 base: `cards_anki.csv` (520 cards, built from `master_wordlist.csv` + `card_notes.json` staging).
  A2 list: `a2_build/a2_wordlist.csv` (built by `a2_build/src/build_a2.py` from `wordlist_a2_pending.csv`,
  `a2_rebase/*`, `sources/*`; ids reserved in `a2_build/id_map.csv`). Sentences: `a2_build/sentences/sentences.csv`.
- **Image resolution order** (`build_apkg.A1_IMAGE_DIRS` / `A2_IMAGE_DIRS` / `SENT_IMAGE_DIRS`, first hit wins):
  A1 `out_phrases_v3, out_deck_f62, images`; A2 `out_phrases_v3/round2, out_phrases_v3, out_deck_a2,
  out_phrases_a2, images_a2, out_phrases`; sentences `out_phrases_v3, out_deck_sent, images_sent`.
  `images/` holds the 1.x WebP masters as the A1 fallback; the pre-F6.2 PNGs are in `_TO_DELETE/out_deck/`.
- **Merges** (owner 2026-10-19, `a2_build/merged_keys.csv`): A2-1187 Sudie → A2-0354 Viso gero (back note),
  A2-1149 atsargiai → A2-0385 Atsargiai!, A2-1944 → A2-1995, A2-1958 → A2-1991. The surviving key keeps its
  GUID; the absorbed id stays reserved (`id_map.csv` `merged_into`). **B1 deferrals:** 31 rows in
  `a2_build/deferred_B1.csv`, out of the A2 build.
- **Prašom + infinitive** (owner 2026-10-18, `a2_build/PRASOM_SWITCH_2026-10-18.md`): the four postposed
  *prašau* phrases (A2-0902/0903/0375/1166) and two cloze examples now read *Prašom pakartoti* etc.
- A2-0964: *Ar galite ką nors parekomenduoti?* (owner 2026-10-19).
- Stress marks are sourced (Wiktionary / kirtis.info / LKŽ), never generated; `a2_build/stress_58_resolved.csv`.

## 8. Study order v2 (`build_study_order_v2.py` → `study_order.csv`, adopted 2026-10-17)
- Usefulness first: a hand-ordered `SURVIVAL` list, then score = 0.6·ln(subtitle rank) + 0.4·ln(press rank)
  + tier offset − 0.3 if in the VU A1/A2 lexicon. Lane mixing `LANE_CAP 3 / WINDOW 10`; pictures first
  (`FIRST_CLOZE 100`, `FIRST_PHRASE 40`, `FIRST_COLOURS 40`); the **A2 block also opens with pictures**
  (`A2_FIRST_CLOZE 30`); confusables `SEPARATION 60`; sequences keep order; antonym pairs adjacent.
- **62 survival items retagged A1** (`a2_build/study_order/retag_A1.csv`). **Family pins** and other
  neighbours in `PIN_AFTER` (batonas after duona, mama after motina, tėtis after tėvas, dukra after sūnus,
  sesuo after brolis, senelė after senelis, žmona after vyras, …). `build_apkg` writes the position to `due`.

## 9. Packages, versioning, release
- Version scheme: packages `Lietuviu_Flashcards_v<APKG_VERSION>_<level>.apkg` (`APKG_VERSION` default
  `"2.1"`, env; `APKG_LEVELS=A1` or `A2`, one package per level under AnkiWeb's 250 MB cap);
  `versioned_out()` never overwrites — a repeat build gets `-1`, `-2`. Engine/data history uses
  `files X.Y.Z / wordlist N.M` (`CHANGELOG.md`, `VERSIONS.md`). Current packages: `Lietuviu_Flashcards_v2.1_A1.apkg`,
  `_A2.apkg`; v1 and v2.0 are in `_TO_DELETE/`. The next A1 release is **v2.2** (`a2_build/A1_WRAPUP.md` §E).
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

## Spec changelog
- **3.0.1 — 2026-10-19.** wording: emblem rule dormant (097 restored, no shipped Vytis); poster/sign rule (real period work, declared card_text, QA read-back, no blank posters); go_grammars.py (SCENE_TAIL, compose_class, category grammars) added to the style lock as six new items
- **3.0.0 — 2026-10-19.** First versioned release: the 2026-10-19 de facto spec (F6.2 house style, v2.1
  standard bands, proposed backs, Brygada 1918, situation grammar, emblem scope, study order v2), with the
  style lock, golden set and build manifest introduced in §11.
