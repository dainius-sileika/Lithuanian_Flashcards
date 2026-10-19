# Golden reference set — what the GO look *is*

Twenty-eight canonical pictures (24 present here, 4 to be copied from the local renders, see below)
that define the house style **F6.2** as the owner accepted it, with the exact prompt that drew each one.
They are the yardstick for any change to the engine: **a new image model, a new quality or size, a changed
lead or rule, or a different QA model must reproduce these — same key, same prompt, same settings — to the
owner's satisfaction on a Review Desk page before it is adopted.** Judge the set as a whole: paper tone,
line weight, matte fills, the 1981 people and their hair and dress, gaze, inset frames, red bands, the
flat diagram light, and whether the main picture alone carries the word.

Spec: `docs/DESIGN_SPEC_CURRENT.md` (§1, §4, §6, §11). Lock: `style/STYLE_LOCK.json`. Procedure:
`docs/HOW_TO_CHANGE_THE_LOOK.md`.

## Files
- `manifest.csv` — the list of record: key, group, what the picture exemplifies, English.
- `<key>.jpg` — an 800 px, q85 copy of the current render (never the master; masters live in the image
  folders and GitHub Releases).
- `<key>.prompt.txt` — the ledger row that drew it: backend/model, size, subject, the full prompt, and the
  spec version and style hash where the ledger has them (renders before spec 3.0.0 have none; spec 3.0.0
  describes them).
- `tools/golden_set.py` builds or refreshes the set from the manifest (`--status` to list, `--refresh` to
  rewrite). It takes a picture only from the folder whose ledger holds the key's current row, or from that
  folder's 1024 px cloud mirror when the key was never re-rolled.

## The groups
| group | keys | why |
|---|---|---|
| vignette · animals and objects | 001_suo, 005_karve, 224_raktas, 180_kiausinis, 057_kepure, 209_stalas | `CONCEPT_LEAD`: subject on bare light paper, surroundings fading out, 2–3 ruled insets |
| vignette · people | 082_motina, 092_senele, 110_mokytojas, 118_policininkas, 137_vestuves, 021_variklis, 098_kaimynas | the four dress classes, the hair wording (092), professional text exception (110), gaze, Setting lines |
| full scene · places | 027_gatve, 036_mokykla, 034_ukis, 024_miestas | `CONCEPT_LEAD_SCENE`: the scene fills the panel edge to edge with its own sky and ground |
| verbs and qualities | 366_eiti, 448_aukstas, 069_raudonas, 227_raide, A2-0044 | motion strip, contrast adjective, no-inset colour card, the glyph exception, a number text exception |
| A2 vignettes | A2-0220, A2-0729 | the same look on the A2 list (Sunburst, 2026-10-11/12) |
| situations (bubble-free) | A2-0262 *, 374_galvoti *, A2-0906 * | conversation gaze with insets, house gaze on a non-speaking situation, a two-panel `situation_2` under `PANEL_CONTINUITY_RULE` |
| sentence cards | S-0006 * | a sentence picture for a cloze card |

\* **Pending pictures (4).** The cloud clone holds only the 2026-10-11 renders; the bubble-free situation
cards (`out_phrases_v3/`, 2026-10-18) and the sentence pictures (`out_deck_sent/`) exist on the owner's
machine. Their prompts are already here. To complete the set, on the machine with the renders:
`python3 tools/golden_set.py` then commit the four JPEGs.

All 24 present pictures are single-row ledger keys (drawn once, never re-rolled or edited), so each JPEG is
the picture the deck ships. Every one was drawn by `gpt-image-2.5-sunburst`, quality medium, 1536×1024.

## How to use it for an engine comparison
1. Render all 28 keys with the candidate (same prompts from the `.prompt.txt` files; `tools/golden_set.py`
   shows the ledger each came from) into a scratch folder, never over the originals.
2. Build a Review Desk page with the golden JPEG beside the candidate, one row per key, OK/Reject + note.
3. The owner decides. A candidate that fails even one group is not adopted; a partial win is a proposal
   for the spec, not a switch.
4. On adoption: spec release (major if the look moved), style lock update, and this set is refreshed with
   the new renders under the new spec version — the old set stays in git history under the old tag.
