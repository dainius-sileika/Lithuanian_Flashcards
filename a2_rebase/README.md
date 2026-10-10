# A2 re-base — official-list coverage and decision sheets

*Built 2026-10-10. Regenerate with the three scripts below, in order.*

The September audit said the queue was aimed off-target and should be re-based on
the official A1+A2 descriptor list before any more images are spent. This folder
does that and turns it into two sheets you decide line by line.

## The yardstick, and its limit

`sources/A2_2_lygis_VU_A1A2_lexicon.pdf` is the Vilnius University list built by
merging the A1 (*Lūžis*, Stumbrienė 2016) and A2 (*Pusiaukelė*, Ramonienė 2016)
descriptor vocabularies, 1,606 entries as parsed.

**It is not the whole A1+A2 vocabulary.** *laikas, du, trys, prašau, vėl, mūsų,
muziejus* are all absent. Its own introduction pairs it with the 3,000 most frequent
lemmas (`sources/LT_3000_most_frequent_PERLSI.pdf`), so the core seems to be
assumed rather than listed. The audit's "58% of the queue is off-list" therefore
overstates the problem: being off-list alone is not a reason to prune. Both sheets
carry a `freq_rank` column so you can see which off-list words are still frequent.

Coverage (exact match, stress-insensitive): deck + queue hold 43% of the list;
**910 list entries are in neither.**

## Sheet 1 — `official_missing_triage.csv` (910 rows: what to add)

Each missing list entry has a hand-authored gloss, part of speech and route.
Glosses and routes are drafts for your check. A blind second review (Fable,
2026-10-10) flagged 15 rows (~1.6%); all 15 were accepted. Every reviewed
correction, with its source, is in `route_fixes.csv` and tagged in the note column.

| route | n | meaning |
|---|---:|---|
| IMG | 329 | concrete; a picture card through the engine (74 are also top-3,000) |
| CLOZE | 303 | function word, adverb, abstract verb, set phrase: sentence/cloze card |
| PHRASE | 41 | fixed expression, greeting or sign text |
| PAIR | 14 | perfective partner of a deck/queue verb (*rašyti → parašyti*); teach as pairs |
| SWAP | 8 | official word that should replace an off-list queue synonym |
| DUP | 23 | already queued in another form (feminine, plural, punctuation); retarget there |
| SYN | 58 | near-synonym of something in the deck/queue/list; one is enough |
| SKIP | 118 | low A2 value, administrative, dated or sensitive |
| FRAG | 16 | PDF artefact (collocation fragment) |

Notable: the list carries the **perfective** for some verbs: *padaryti*, not
*daryti*. That supports building the cloze layer around aspect pairs.

Fill `owner_decision`: blank = accept the route; otherwise write the route you want
or a correction to the gloss.

## Sheet 2 — `queue_offlist.csv` (478 rows: what to cut)

The live queue rows whose target is not on the list, each with a suggestion:

| suggestion | n | rule |
|---|---:|---|
| KEEP | 315 | phrase/sentence, numeral, pronoun form, or frequency rank ≤ 3,000 |
| DEFER | 139 | neither on the list nor frequent; keep, but generate after list words |
| SWAP | 8 | replaced by the official synonym from sheet 1 |
| DROP | 16 | P-E case/tense-name cards (*naudininkas*); fold into cloze, as the audit advised |

## Files

| file | made by | what |
|---|---|---|
| `coverage.py` | — | parses the list → `sources/vu_a1a2_lexicon.csv`, `official_missing.csv`, `queue_offlist.csv`, `coverage_report.md` |
| `triage_drafts.csv` | hand | the 910 first-draft glosses and routes |
| `route_fixes.csv` | hand | reviewed corrections applied over the drafts (overlap check + Fable review); add new corrections here |
| `overlap.py` | — | checks the triage against deck/queue glosses, singular/plural forms and SYN targets → `official_missing_triage.csv` |
| `frequency.py` | — | adds `freq_rank` to both sheets and the queue suggestions → `sources/lt_3000_frequency.csv` |

```
python3 a2_rebase/coverage.py && python3 a2_rebase/overlap.py && python3 a2_rebase/frequency.py
```
Re-running `coverage.py` rewrites `queue_offlist.csv`, so any `owner_decision`
entries there are lost; fill decisions only once the sheets are final.

## Source URLs

The two PDFs are kept in `sources/` locally but not committed; fetch them from:
- VU A1+A2 list: https://www.lu.lv/fileadmin/user_upload/LU.LV/Apaksvietnes/Projekti/perlsi/A2_2_lygis.pdf
- 3,000 most frequent lemmas: https://www.lu.lv/fileadmin/user_upload/LU.LV/Apaksvietnes/Projekti/perlsi/3000_zodziu.pdf

The descriptors themselves (*Pusiaukelė*, *Lūžis*) are on vlkk.lt, which refuses
scripted downloads; a manual browser download would allow checking whether the
list's omissions (*laikas, prašau*) come from the descriptors or from the merge.
