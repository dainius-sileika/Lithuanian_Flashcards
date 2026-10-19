# Spec reconciliation — 2026-10-19

Every design, spec and plan document in the repo was read against the code and the owner's dated
decisions while writing `docs/DESIGN_SPEC_CURRENT.md`. Rule applied throughout: **the code plus the most
recent owner decision is the truth; the document is corrected, superseded or archived.** Code docstrings
were left as they are (listed below so the next code edit can fix them).

## Documents reviewed and their disposition

| document | state | action |
|---|---|---|
| `GO_STYLE_SPEC.md` (files 1.7.1, 2026-07-28) | obsolete spec | header, moved to `_archive/docs/` |
| `ROADMAP.md` (2026-07-25) | obsolete plan | header, moved to `_archive/docs/` |
| `NEEDS_YOUR_REVIEW.md` (2026-10-11) | replaced by the Review Desk | header, moved to `_archive/docs/` |
| `VERSIONS.md` | production notes 0.1→1.9.2; "current working files" section wrong | header; kept at root as history |
| `CHANGELOG.md` | stops at 2026-10-11 (nothing on v2.1 bands, backs, usage field, situations, labels, study order v2, emblem rule, merges) | pointer line; the v2.2 entry is `A1_WRAPUP.md` §E4 (planner) |
| `README.md` | described the 520-card 1.x deck, `images/` as the build source, `driver.py`, `build_review.py` | rewritten as the folder map |
| `ANKIWEB_DESCRIPTION.md` | "520 core words"; rewrite is `A1_WRAPUP.md` §F1 (owner approves the text) | header; kept |
| `anki/templates.md` | field list without `usage`; v2.0 drawn-frame templates | header |
| `a2_build/README.md` (2026-10-11) | describes the bubble phrase cards (`bubbles.py`) and the first A2 build | header |
| `a2_build/PLAN_A2_completion.md` (2026-10-12) | executor plan, tasks 0–7 done; `out_deck/` protection line | header |
| `a2_build/RESTAGE_PROPOSAL.md`, `PILOT_24.md`, `pilot_round2/RULES.md`, `pilot_round2/DIAGNOSIS.md` | applied to code 2026-10-17 | header |
| `a2_build/BACKS_AUDIT.md` | applied (backs default, plate numbers, adjective forms) | header |
| `a2_build/historical/implementation/RULES_precedent_likeness.md` | applied; §3b emblem allowance narrowed (see below) | header |
| `a2_build/sentences/design.md` | consistent with `card_frame.CLOZE_FRONT` (no English on sentence fronts) | header (design recorded in the spec) |
| `a2_build/A1_WRAPUP.md` | the current plan; C4 and D3 decided | pointer line; items C4/A7 noted below |
| `a2_build/*/README.md`, `out_*/README.md`, `fonts/README.md`, `review_desk/README.md`, `docs/PLAYBOOK_*.md`, `style_lab/**/NOTES.md` | folder status notes, SOP, method, lab records | unchanged |
| `_archive/deprecated/README.md`, `spec_1.6.1/`, `docs_superseded/` | frozen 1.6/1.7 history | archived with `deprecated/` |

## Contradictions found (doc → code), and what was treated as truth

1. **Image model.** `GO_STYLE_SPEC.md`, `README.md`, `VERSIONS.md`: backend gpt-image-1.5 (and Z-Image-Turbo
   864×1152, 8 steps as the generation settings); `CHANGELOG.md` [Unreleased]: "gpt-image-2 stays the default
   until the spot-check"; `go_generator.py` docstring line 61: `gpt-image-2`. **Truth:** `go_generator.OPENAI_MODEL
   = "gpt-image-2.5-sunburst"`, `OPENAI_QUALITY = "medium"`, 1536×1024 (spot-check 09 decided it, 2026-10-11).
2. **Lettering.** `GO_STYLE_SPEC.md` hard exclusion "no readable text"; `README.md` "no text is baked into the art";
   `CHANGELOG.md` "lettering pilot designed but not yet run"; `anki/templates.md` same. **Truth:** lettering is
   allowed only where `card_text` declares it (`_exact_text_rule`) and QA rule 3 verifies the read-back
   (owner decision 2026-10-11; 22 A1 + 98 A2 rows carry declared text; prices in litai).
3. **Palette and prompt.** `GO_STYLE_SPEC.md` fixes hex colours (#E4DCC8 …), a "master prompt template", "no border",
   "overcast institutional" mood. **Truth:** the F6.2 leads (`CONCEPT_LEAD`, `CONCEPT_LEAD_SCENE`, suffixes),
   red bands (`BARS_RULE`), warm aged-cream paper with a nostalgic register (blind surveys 2026-10-10/11).
4. **Emblems.** `_archive/docs/GO_STYLE_SPEC.md` and 0.9 notes: flag only. `RULES_precedent_likeness.md` §3b and
   `historical/implementation/README.md`: Cross of Vytis / Vytis allowed on the six test cards, "promote to the
   default if T4/T5 pass". The project memory also records "Vytis and Cross of Vytis allowed". **Truth:** owner
   2026-10-19 — Vytis accepted on 097 prezidentas, **flag (not the Cross) on 035 teismas**; code
   `deck_builder.FLAG_OVERRIDE.update({97: "emblem"})`, every other card `FLAG_RULE` (tricolour only).
5. **Dress classes.** Memory/older notes: three classes. **Truth:** four — `formal` added in F6.1
   (`FIGURE_DRESS`, `deck_builder.FORMAL_ROWS`).
6. **Hair.** Spot-check 09 wording made curls a rule for older women. **Truth:** owner 2026-10-11 — curls are one
   option among everyday styles; the lead text says "occasionally curled".
7. **Review loop.** `README.md`, `NEEDS_YOUR_REVIEW.md`: generate → `qa_images.py` → `build_review.py` →
   owner. **Truth:** `build_review.py` is retired (`_archive/code/`); review pages are built per round
   (`a2_build/<round>/build_page.py`, `review_pub` builders) and linked from the Review Desk
   (`review_desk/README.md`).
8. **Generation runner and output.** `README.md`/`VERSIONS.md`: `driver.py` merges into `out_deck/`, the
   "distributed set" is `images/`. **Truth:** per-folder `gen.py` scripts (`out_deck_f62`, `out_deck_a2`,
   `out_deck_sent`, `out_phrases_v3`) import `deck_builder`; the build resolves A1 from
   `out_phrases_v3 → out_deck_f62 → images`. `deck_builder.OUT_DIR` still defaults to `./out_deck`, which
   would recreate that folder if `deck_builder.py` were run directly (it is used with `--dry-run`).
9. **Plate numbering.** `A1_WRAPUP.md` §C4 "decision pending". **Truth:** decided and implemented —
   `build_apkg.plate_number`: A1 1–531, A2 1001+, sentences 4001+ (`card_frame.py` comment, 2026-10-18).
10. **Superseded bubble pictures.** `A1_WRAPUP.md` §A7 "delete once A1 is passed"; `build_apkg.py` comment and
    `a2_build/rollout/README.md`: "moved to `<dir>/_superseded/`". **Now:** moved to
    `_archive/recent_versions/<dir>/_superseded/` (nothing deleted; the owner decides).
11. **Note type fields.** `anki/templates.md`: 13 fields. **Truth:** 14 — `usage` appended 2026-10-18
    (`build_apkg.GO_FIELDS`); schema change ⇒ delete-and-reimport for existing users.
12. **Study order.** `ROADMAP.md`, `PLAN_A2_completion.md`: phase-by-phase order, `build_study_order.py`.
    **Truth:** `build_study_order_v2.py` (usefulness first, 2026-10-17); v1 is in `_archive/deprecated/`.
13. **Card counts.** `README.md` "520 cards"; `A1_WRAPUP.md` "1,164 A1 cards". **Truth today:**
    `study_order.csv` 2433 rows — 1163 A1 subdeck, 1215 A2 subdeck, 55 sentences (one fewer than A1_WRAPUP.md's 1,164; see the
    2026-10-19 merges); the scratch A1 build has 1198 notes.
14. **`.gitignore`** listed `recorder*.html` as ignored while the four sheets were tracked; `_qa/` was untracked
    but not ignored. Now: `_qa/` ignored (cache); the three July sheets are in `_TO_DELETE/`.
15. **Stale docstrings in live code** (not changed here): `go_generator.py` line 61 (gpt-image-2 default),
    `go_generator.py` header "files 1.7.1"; `build_apkg.py` line 2 ("Lietuviu_Flashcards.apkg from
    cards_anki.csv + images/"); `go_grammars.py` line 34.

## Open points for the owner (not decided by this pass)

- `style_lab/` keeps 1.1 GB of experiment renders (F1–F6.2 surveys). The decision record is in the tracked
  NOTES/analysis files, and `go_settings.py` reads `style_lab/research/`; only the image sets could go.
- `out_deck_a2/` holds 14 pictures no card resolves to (merged/deferred keys or keys now served from
  `out_phrases_v3`), `out_deck_sent/` 5, `out_phrases_v3/` 17 (shadowed by `round2/`). Left in place as
  recent history.
- `_apkg_media/` (435 MB) is the transcode cache; stale entries from the v2.0 drawn-frame builds could be
  cleared by deleting the folder (it rebuilds).
- Project memory `decisions.md` should record the 2026-10-19 emblem ruling (Vytis on 097 only, flag on 035)
  and the four dress classes.
