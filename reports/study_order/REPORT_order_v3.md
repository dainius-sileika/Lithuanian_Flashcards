# Study order v3 (deck v3.0, 2026-10-19)

`build_study_order_v3.py` → `study_order.csv`. v2 stays as history (git 5b1f43f). Keys and GUIDs untouched, frozen from v3.0 on. Tables: `AUDIT_v3.txt`; `--audit FILE` re-runs the checks.

## What changed and why

1. **Words before the sentences that use them.** A cloze, pair or sentence card now waits until every word of its sentence has been taught. v2: 172 of 1,979 word uses pointed forward — *kad* at 144 read "Manau, kad tu teisus", *manyti* was card 1254. Now 43, of which 37 are A1 sentences using a word that exists only at A2 (listed in `AUDIT_v3.txt`; fixable only by rewording or moving the card — your call). A needed word is pulled a little ahead of its sentence: Monday now precedes "Šiandien pirmadienis".
2. **Greetings on day two.** *Labas* 41 → 21, *Ačiū* 25, *Prašau* 32, *Atsiprašau* 43; a phrase every four cards or more.
3. **No tail runs.** v2 ended A1 with 21 phrases in a row, A2 with 31 nouns and 119 reading cards; lanes are now paced against their share (longest run 11, the colours).
4. **Pairs together, confusables apart.** Every pin, antonym and list-noted pair is adjacent (v2: 14 apart); same headword ≥ 60 apart, look-alikes ≥ 30 (v2: kitas/kinas 5 apart).
5. **Sentence cards inside their own subdeck** (v2 put 20 A2 sentences in the A1 block).
6. **Agreement with spoken frequency** (Spearman, OpenSubtitles) 0.49 → 0.66.

## Re-tiers: 44 cards (`retier_v3.csv`, one reason each; levels written into the data files)

- **16 A2 → A1.** Words A1 sentences need, themselves A1 by frequency and the VU lexicon: *manyti* (subtitle rank 2), *vėluoti, likti, atvažiuoti, paskambinti, sirgti, jaustis, pavargęs, reikšti, lauke, lietuvių kalba, Palaukite minutėlę*; and antonym partners split across subdecks: *piktas, abi, linksmas, šiemet*.
- **28 A1 → A2.** Fluent Forever leftovers at the A1 tail, already demoted, outside the VU lexicon, subtitle rank 1,800–30,000 (*plaštaka, lydyti, išlenktas, kurčias, kosmosas* …); pairs moved together.
- Left alone: *muzika* (your decision), *seklus* (paired with *gilus*), the A1 conjunctions.

Subdecks: A1 1,186, A2 1,247. All 2,433 keys `build_apkg.py` emits have one position, 1…2433.

## Telling positions (v2 → v3)

Labas 41 → 21 · Ačiū 45 → 25 · euras 464 → 260 · pirmadienis 374 → 84 · manyti 1254 → 194 · vėluoti 1296 → 94 · prezidentas 714 → 960 · asmuo 794 → 1000 · plaštaka 1175 → 2420. Bread, beer, water, dog: within three places of before.

## First 60 of A1

žmogus, vyras, vanduo, moteris, valgyti, duona, batonas, gerti, didelis, mažas, eiti, vaikas, namas, kava, parduotuvė, draugas, arbata, pienas, dirbti, šeima, Labas, miestas, batai, autobusas, Ačiū, alus, šuo, obuolys, taip, katė, aš, Prašau, sriuba, ne, tu, Laba diena, jis, geras, blogas, pinigai, kaina, ji, Atsiprašau, pirkti, mokytojas, mes, Viso gero, jūs, ligoninė, brolis, sesuo, vienas, jie, Iki, du, telefonas, tai, Nesuprantu, kaimynas, skambinti

First reading cards, 101–104: *Moteris valgo duoną · Vyras geria kavą.*

## For the recorder

`recording_order_v3.csv`: every card in study order, A1 first, with the sentence for cloze cards. The re-tiers change which recordings count as A1; `recording_list.csv` and the recorder sheets were not touched.

## Hand edit, 2026-10-20 (rc3): 0331 back beside 0366

The 2026-10-20 regeneration (after the proofreading return) put **0331_kelinta_valanda** (*Kelinta valanda?*) at
1,069, because a phrase ranks as its rarest word and *kelinta* is rare. It is the alternative to
**0366_kiek_valandu** (*Kiek valandų?*), so by the pair-adjacent rule it now sits straight after it:
**0366 @ 365, 0331 @ 366**. The cards that were at 366–1,068 each move down one place (704 rows renumbered in
`study_order.csv` and `recording_order_v3.csv`); nothing else changed and no key number changed.

Done by hand because a regeneration is not a no-op: a full run with the pin moves 455 positions (the greedy
scheduler's lane caps cascade). The pair is also in the builder as `PIN_AFTER["0331_kelinta_valanda"] =
"0366_kiek_valandu"`, so any later regeneration keeps it. `old_order` was left as the previous builder run wrote it.
Audit: `AUDIT_v3_3.txt` (before/after, `--audit`): 0 A1 cards needing an A2-only word, the same 6 forward
dependencies (none involves 0331), 0 pins/pairs not adjacent.
