# Sentence proofreading round-trip (owner request 2026-10-19)

Every Lithuanian sentence and phrase in the deck (A1 + A2), 1,255 lines, in study order, A1 first:
cloze sentences (981), phrase cards (219) and sentence cards (55). The 27 rewordings planned on 2026-10-19
(`a2_build/study_order/dep37_plan.csv`, plus A2-1725 → *Mėnulis {šviečia}.*) are already in, marked in `status`.

| file | for |
|---|---|
| `sentences_for_proofreading_v1.csv` | the working sheet: `lt_with_blank` (the blank is in braces), `lt_plain`, `target`, `en`, and empty `lt_corrected`, `en_corrected`, `note` columns to fill. UTF-8 with BOM, so Excel/Numbers read the diacritics. |
| `sentences_lt_only_v1.txt` | key ⇥ Lithuanian, one per line, to paste into a proofreading engine |
| `sentences_lt_en_v1.txt` | key ⇥ Lithuanian ⇥ English, for translation checkers |

Return: fill `lt_corrected` / `en_corrected` only where something should change (leave the rest empty), and save it as
`sentences_for_proofreading_v1_returned.csv` in this folder. Keep the `key` column untouched: keys are being renamed to
one scheme, and the rename keeps an old→new map, so the returned sheet still applies after the rename.
A correction that changes the blank word itself (`target`) is flagged for a decision, not applied silently.

## v2 (2026-10-20)

The owner's returned sheet (`sentences_for_proofreading_v1_returned_spelling_structure_pass.csv`, 25 corrections)
was planned in `returned_plan_v1.{csv,md}` and applied with `apply_returned_plan_v1.py`; five keys whose slug no
longer matched were re-slugged (`a2_build/rename/key_map_v2.csv`). `export_v2.py` writes the same three files with
the current keys and the corrections in: `sentences_for_proofreading_v2.csv`, `sentences_lt_only_v2.txt`,
`sentences_lt_en_v2.txt` (1,255 lines; `status` marks the 26 corrected rows and carries v1's rewording marks).
The v1 files are unchanged.
