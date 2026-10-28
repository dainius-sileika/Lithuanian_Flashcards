# Naturalness round — applied (2026-10-28)

`final_v1.csv` (owner-approved, second-checked; `SECOND_CHECK.md`) is in the live data. No package was built
(the owner still has answers pending on the audio pages and the stress sheets).

| step | script | result |
|---|---|---|
| data | `apply_v1.py` | 67 EDIT, 6 RETARGET, 2 NEW_CARD; 300 field changes before the new rows; a `naturalness 2026-10-28 …` note on every changed row |
| keys | `amend_v3.py` | `data/key_maps/key_map_v3.csv`: 9 re-slugs, numbers kept; 2 keys minted |
| media | `amend_v3.py`, `tools/rename_keys.py --apply-media` | 4 tracked takes `git mv`'d; 6 pictures renamed on the Mac, 2 picture copies in the cloud clone (sha1 logs `media_log_key_map_v3_*.tsv`) |
| re-takes | `supersede_v1.py` | 20 recorded takes (19 cards) set aside to `media/audio/_history/`, a `superseded` row each in `data/audio_source.tsv` (`retakes_v1.tsv`) |
| owner stress | `make_owner_stress_v1.py` | `OWNER_STRESS_v1.csv`: 7 forms |
| audit | `build_study_order_v3.py --audit`, `check_keys_v1.py` | `reports/study_order/AUDIT_v3_4.txt` |
| recorder | `build_recorder.py A2` on the Mac; `recorder_test_v1.py` | 2,336 takes; headless test PASS (`recorder_test_v1.txt`) |

## What changed

- **data/a2_wordlist.csv** — `example_lt` / `example_en` of the cloze cards; phrase cards also `lithuanian_TARGET`,
  `english` and `lt_pron` where final_v1's `field(s)` names them (0214, 0966, 1243, 1482, 1793, 2147; English only:
  0043, 0768, 1706, 2265); the four gloss edits (1006, 1399, 1733, 1852). **data/sentences/sentences.csv** — 0856
  (*vieną eurą*; `words_used` 0609_litas → 0262_euras) and 1410 (*Man skambina draugas*).
- **Retargets** (headword, gloss, pron, pron_src, forms, sentence, the stress source in `check`):
  0239 *orai* → **oras** (óras, gen. óro, gender M pl → M; en.wiktionary), 2422 *puslitris* → **bokalas** (bokãlas,
  gen. bokãlo; en.wiktionary), 1589 *naudotis* → **pasinaudoti**, 1968 *vieta prie tako* → **vieta prie praėjimo**,
  0778 → **Truputį kalbu lietuviškai.**, 1169 → **Sveik!**.
- **New cards** (minted with `rename_keys.mint`, the function behind `--mint`, in SECOND_CHECK's order):
  **2434_ka_daryti** "Ką daryti?" (A1 phrase, pron Ką̃ darýti?, both words sourced) at @341 straight after
  0340_padaryti; **2435_spustis** "spūstis" / "Centre {spūstys}." (A2 cloze, F) at @1516 straight after 1514_eismas.
  Later positions moved +1 / +2 in `data/study_order.csv` (`old_order` = the position before this round); id_map rows added.
- **id_map.csv** — headword / gloss of the 20 cards whose headword or gloss changed. **context_notes.csv** — 1169's
  note (about *Greitai pasveik!* / *pasveikite*) withdrawn from the back, text kept (as 0331 on 2026-10-20).
- **Re-slugs** (`key_map_v3.csv`; the slug follows the headword while keys are unlocked, the same rule as key_map_v2):
  the six retargets — 0239_orai → 0239_oras, 0778_galiu_truputi_kalbeti → 0778_truputi_kalbu_lietuviskai,
  1169_greitai_pasveik → 1169_sveik, 1589_naudotis → 1589_pasinaudoti, 1968_vieta_prie_tako →
  1968_vieta_prie_praejimo, 2422_puslitris → 2422_bokalas — and three EDITs whose headword or sentence changed so
  that the old slug would mislead: 1482_ar_yra_laisvas_staliukas → 1482_ar_yra_laisvu_staliuku,
  0856_duona_kainuoja_viena_lita → 0856_duona_kainuoja_viena_eura, 1410_draugas_skambina_man →
  1410_man_skambina_draugas. EDITs whose slug does not change (0214, 0966, 1243, 1793, 2147) keep their keys.

## Where this apply departs from final_v1, and why

1. **1501_veikiantis**: final_v1's sentence "Veikiantis liftas – kairėje." has no cloze gap; the build would have
   dropped the card (`skipped_no_sentence`). Applied as **"{Veikiantis} liftas – kairėje."**
2. **kalbù (0778) is sourced.** final_v1 called it unsourced; the en.wiktionary dump has the form-of entry *kalbu*
   (head **kalbù**, "first-person singular present of kalbėti"). The pron is *Trupùtį kalbù lietùviškai.*, fully
   marked, and kalbù is not on the owner sheet.
3. **Unsourced prons are left unmarked** (the brief; spec §7): 1169 *Sveik!*, 1243 *Minutėlę!* (final_v1 proposed
   *Minutė̃lę!* from the stem's rule-engine mark), 1589 *pasinaudoti*, 1968 *vieta prie praėjimo*, 2435 *spūstis* /
   *spūsties* — `lt_pron` empty, as for every other unsourced headword, and all listed in `OWNER_STRESS_v1.csv`.

## Audit (`reports/study_order/AUDIT_v3_4.txt`)

- **0 A1 cards need an A2-only word** (before: 0). Forward dependencies 6 → 3 (0237 *numeris*, 0285 *teisingas*, 0294
  *padaryti* are gone; left: 1314 *sustabdė*, 2128 *neišlaikė*, 0171 *manau*, all earlier). Words no card teaches
  92 → 85; in this round's sentences only the cloze forms *nenaudoju*, *suvalgiau*, *jaučiu*, *nudegiau* (as in
  SECOND_CHECK). Pairs, pins and confusables: 0 problems. Positions 1..2,435, no gaps; A1 block 1,192, A2 1,243.
- **Key numbers**: all 2,433 earlier keys keep their number (9 re-slugged); 2 new keys, 2434 and 2435.

## Re-takes (20 takes, 19 cards)

0162_jai_s, 0214_cia_mano_draugas, 0237_jusu_s, 0239_oras, 0239_oras_s, 0261_valanda_s, 0285_atsakymas_s,
0294_bet_kas_s, 0327_per_s, 0340_padaryti_s, 0392_vel_s, 0394_menuo_s, 0469_po_s, 0525_arba_s, 0524_pries_s,
0569_be_s, 0581_toli_s, 0583_informacija_s, 0778_truputi_kalbu_lietuviskai, 1169_sveik.
Each old mp3 is in `media/audio/_history/<take>.1793223807235.mp3` with its `superseded` row (old words in `said`).
The other 3 recorded cards changed only their English (0043, 0535, 0768): no re-take.

## Recorder

Regenerated on the Mac (`python3 build_recorder.py A2`, after the pictures were renamed there): **2,336 takes**
(was 2,314): A1 473 (new 440, re-take 33 = the 13 earlier + these 20), A2 1,863 (new 1,790, replace-tts 73). The +22
are the 20 re-takes and 2435_spustis / 2435_spustis_s. IndexedDB `lt_recorder_A2_afb2ebe2`, `migrateKeys` and the
KEY_MAP (now with the v3 renames) are in the page; 0263_tik and 0369_si (the two failed takes) are still on it.
`recorder_test_v1.py` (headless Chromium, fake microphone): clips stored under the old keys move to the new ones;
clips with the old words come out under `superseded/`, never lost; the page lists 2,336 takes; no console errors.

## Pictures

Checked by eye against the new words: 1169 (sick man in bed), 0778 (a little), 1968 (aisle seat), 1482 (restaurant,
free tables), 0966, 2147, 1410 still fit. **0856 does not**: the price tag reads "1 Lt" and the sentence is now
*vieną eurą* → re-roll (its `card_text` staging in sentences.csv still says "1 Lt"; change it with the re-roll).
0239, 1589 and 2422 are cloze cards and have no picture (2422 never had a milk picture; only its old sentence had
milk). **2434_ka_daryti** is a phrase card without a picture: until one is rendered the build and the recorder skip
it (no take yet).

## Not done here

- No package built (owner answers pending). No picture generated.
- `data/recording_order_v3.csv` is a generated file written only by a full study-order regeneration; it was already
  stale before this round and is left as it is (`rename_keys --verify` WARN, as before).
