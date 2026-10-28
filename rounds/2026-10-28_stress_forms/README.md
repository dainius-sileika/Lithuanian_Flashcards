# Stress marks on the forms shown on the backs (2026-10-28)

The owner, recording from the sheet, noticed feminine forms without stress marks. The audit was systematic: every
headword (`pron`) was stressed, but **no genitive (`gen_sg`) and no feminine (`fem`) form anywhere** carried a mark
(1,046 genitives, 214 feminines), nor did the `pres3`/`past3` of 26 verbs of the A2 list, and five multi-word prons
lacked the mark on one word. The backs showed *áukštas ♂ · aukšta ♀* and *šuõ … šuns*.

Spec §7: **stress marks are sourced, never generated.** The one source read here is English Wiktionary's
Lithuanian entries, as the Wiktextract dump `https://kaikki.org/dictionary/Lithuanian/kaikki.org-dictionary-Lithuanian.jsonl`
(83 MB, 30,371 entries, fetched 2026-10-28; not committed — fetch it again to re-run). kirtis.info was not reachable
from any shell at the time; nothing was derived from accent rules or an accentuator.

| file | what |
|---|---|
| `match_kaikki_v1.py`, `proposals_v1.csv` | the lead's first matcher: 896 unique, 23 ambiguous, 377 not found |
| `match_kaikki_v2.py` | the matcher that was applied (docstring = what it reads and how it decides) |
| `proposals_v2.csv` | every unstressed form (1,304 rows): `key, level, field, current, proposed, how, source, read_from, options, reason, file` |
| `OWNER_LIST.csv` | the 355 forms the owner must stress himself, A1 first in study order, with the reason and the source's options |
| `apply_v2.py`, `applied.csv` | what was written into `data/cards_anki.csv` and `data/a2_wordlist.csv` (949 fields, before → after) |

## What v2 reads (same source, more of the page)

1. the headword line's groups: a canonical form with its `stress-pattern-N` and the feminine / plural /
   third-person forms beside it (*raudónas* 1: *raudóna*; *raudónas* 3: *raudonà*);
2. the declension and conjugation tables, split at the dump's table markers; a table's own nominative is the
   headword it belongs to (*ener̃gija* / *enèrgija* have one table each);
3. the form-of entries (*tėvų̃* "genitive plural of tė́vas"), 13,000 of which carry a stressed head;
4. paradigm neighbours: any table in which our lemma word is the nominative row (*batai*, *tėvai*, *sultys*,
   *mobilusis*, *grynieji*) gives the genitive / feminine row of the same number and gender;
5. multi-word lemmas word by word (*kojos pirštas → kojos piršto*), every word sourced, and a one-word form of a
   multi-word lemma through the word it inflects (*važiuoti dviračiu → važiúoja*).

Case-only duplicates (*Žẽmės* / *žẽmės*) collapse to the spelling of our form. Wiktionary's dotted stressed *i*
(*i̇̀*) is written as every pron in the data writes it (*ì*).

## Decisions (`how`)

- **unique** (931): one stressed form in the source, and its headword agrees with the card's pron (or the
  source gives no stressed headword to compare: 3 multi-word rows).
- **chosen-by-headword** (16): the source offers two accentuations; the one whose headword (entry canonical, table
  nominative or stress-pattern group) equals the card's own sourced pron is taken. Selection among sourced forms,
  not a derivation. `0520_suris sūrio → sū́rio` (pron *sū́ris*, not *sū̃ris*), `0318_laikas → laĩko`, `0434_geguze →
  gegužė̃s`, `0336_aukstas → áukšto`, `1312_aiskus aiški → áiški` (the source pairs *áiški* with *áiškus*; the owner may
  want to look at this one).
- **project-pron** (2): the word *kortelė* in two multi-word prons takes *kortẽlė*, the project's own sourced pron of
  the same word (`0771_kortele`, kirtis.info); en.wiktionary has no stress for it.
- **owner** (355 → `OWNER_LIST.csv`): 330 not in the source (lemma absent, no table, or the table unstressed — e.g.
  *teatras*, *batai*, *mėlynas*; 35 of the 52 verb forms, whose tables Wiktionary leaves unstressed), 7 ambiguous with an identical headword (*raudonas* 1/3: *raudóna* /
  *raudonà*; *geltonas*, *tobulas*, *asmuo*, *dujos*, *saga*, *bala*), 11 **conflicts** where the source's headword
  contradicts our pron (below), 6 multi-word forms with one word unsourced, and the pron of `0736_ne_vienas` (*nė* is
  not in the source).

## Conflicts: the source's headword is not our pron (not applied; the headword may be wrong)

| key | our pron | source headword | source form | note |
|---|---|---|---|---|
| 0084_pirmadienis | pirmãdienis | pirmadiẽnis (1) | pirmadiẽnio | our pron_src: "kirtis.info; pattern of the other six weekdays" |
| 0646_treciadienis | trečiãdienis | trečiãdiẽnis | trečiãdiẽnio | the source form carries two marks — a Wiktionary error |
| 0923_cekis | čẽkis | čèkis (2) | čèkio | pron_src says en.wiktionary, which now reads čèkis |
| 1558_priezastis | príežastis | priežastìs (3a) | priežastiẽs | both accentuations exist in dictionaries |
| 1213_alkanas | alkãnas | álkanas | alkanà | |
| 1934_akademija | akadèmija | akàdemija | akàdemijos | |
| 1631_kaltas | káltas | kal̃tas (4) "guilty" | kaltà | our pron is the noun *káltas* "chisel"; the `check` column already says DISAGREE |
| 1013_sostine | sóstinė | sõstinė | sõstinės | |
| 1138_antis | ántis (M, gen *ančio*) | ántis f "duck" / añtis m "bosom" | añčio | the duck is feminine, gen *ánties*; our gender and gen_sg follow *añtis* "bosom" |
| 1921_neiprastas | neįprãstas | neį̃prastas (3) | neįprastà | |
| 2277_valgomasis | válgomasis | valgomàsis | válgomojo | |

Also seen, not applied: the source's *rugsė́jio* (our *rugsėjo*), *pẽčio* for *petys* (our *peties*), *slė̃pia* for
*slėpti* (our *slepia*) — Wiktionary table artefacts; our forms stand, unmarked, on the owner's list.

## What changed in the data and the build

- `data/cards_anki.csv`: 368 rows, 368 fields; `data/a2_wordlist.csv`: 573 rows, 581 fields (`applied.csv`). Only
  `gen_sg` / `fem` / `pres3` / `past3` (and the five prons) changed; the row's `notes` / `check` column says how
  (`gen_sg stress: en.wiktionary 2026-10-28`, `… chosen by headword …`). CSV quoting and CRLF kept.
- The build passes the fields through untouched (`build_apkg.adjective_forms`, `a2_forms`; the back templates in
  `code/card_frame.py`); only the masculine of an adjective is compared stress-blind to pick the pron.
- The recorder: `build_recorder.py A2` to scratch before and after — 1,991 takes, same take ids, dests and order,
  same statuses; 239 `say` lines gained marks; `said_key` equal for every one (the stale-take check is stress-blind,
  commit 363b5fd). The live `recorder_A2.html` is regenerated on the Mac, not here.
- Spec 3.5.0 (§7): every form on a back carries a sourced stress mark; an unsourced form is shown unmarked and
  listed in `OWNER_LIST.csv` until the owner supplies it.

## Lead, 2026-10-28 (after v2)

- Two conflicts were wrong data, confirmed in the dump and fixed in `data/a2_wordlist.csv`:
  **1138_antis** (A1 picture card "duck") had gender M and gen *ančio*, which belong to *añtis* m "bosom":
  now F, gen *ánties* (en.wiktionary antis, ántis f (1)). **1631_kaltas** had the pron of the noun *káltas*
  "chisel": now *kal̃tas*, fem *kaltà* (adjective, pattern 4; agrees with kirtis.info).
- `OWNER_SHEET_v1.csv` is the owner's round-trip sheet: the 353 remaining forms (90 A1, 263 A2), A1 first in
  study order, with an empty "YOUR stressed form" column. `OWNER_LIST.csv` stays as written by v2.
