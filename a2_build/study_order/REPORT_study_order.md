# Study order: audit and proposal (2026-10-17)

`build_study_order_v2.py` → `study_order_v2.csv`, a proposal; nothing existing was changed. First 100 of each subdeck and the correlations: `AUDIT_tables.txt`.

## Verdict

**A1's 428 pictures are already utility-first** (bread 5, beer 146, pig 310). The rest is not: after the pictures the order runs phase by phase, so *Labas* is card 1007, *kalbėti* 1212, *mėsa* 1536, *tualetas* 1557, *antis* 2241, and the A2 subdeck opens with the Fluent Forever "Society" leftovers (*melstis, pragaras, branduolinis*).

## Why you see pig early

Your collection predates the study order (deck 19 July; order 11 October). Those cards had no position, so Anki shows them in the order they were written: the wordlist, which starts with animals; pig is word six. Anki never moves cards a collection already has (confirmed in its importer source), and the documented fix, sort by Key then Reposition, reproduces the wordlist because Key is the wordlist number.

## Method

Counting alone cannot do it: press ranks *teismas* 76 and *duona* 1992; film subtitles rank *prezidentas* 567 and *duona* 2044. So:

1. **Spoken frequency.** OpenSubtitles 2018 Lithuanian (hermitdave/FrequencyWords, CC-BY-SA), lemmatised with simplemma, 60% weight, blended with PERLSI press (40%). Missing from the press top 3000 is not penalised; that list has almost no food or household words.
2. **Judged utility.** The first ~40 words are a hand-ordered survival list (people, water, bread, eat, drink, coffee, beer, apple, soup, shoes, bus, dog…); greetings likewise. Then four tiers: survival, daily life, general, demoted (court, president, hell, nuclear, *asmuo*).
3. **Mixing as a brake.** Frequency places cards; at most 3 of a kind per 10 keeps verbs, food and adjectives together. v1's quotas forced one animal per unit, useful or not.
4. **Phases dropped, reasons kept.** No cloze card before position 100 in A1; numbers, days, months in natural order; antonym pairs adjacent; colours one run; confusables 60 apart; *batonas* after *duona*; sentences after their words.

Spearman agreement with subtitles rises 0.35 → 0.55; with press 0.15 → 0.36.

## Before / after (position in the whole order)

| word | old | new | | word | old | new |
|---|---|---|---|---|---|---|
| duona | 5 | 5 | | prezidentas | 318 | 724 |
| vanduo | 4 | 4 | | teismas | 372 | 662 |
| alus | 146 | 26 | | asmuo | 389 | 804 |
| kava | 8 | 15 | | branduolinis | 459 | 1773 |
| obuolys | 51 | 27 | | kiaulė | 310 | 837 |
| sriuba | 103 | 28 | | karvė | 226 | 890 |
| batai | 40 | 22 | | višta | 1305 | 886 |
| šuo | 39 | 24 | | antis | 2241 | 1034 |
| vienas | 584 | 29 | | mėsa | 1536 | 690 |
| kalbėti | 1212 | 30 | | tualetas | 1557 | 325 |
| važiuoti | 1476 | 44 | | euras | 1429 | 544 |
| galėti | 650 | 131 | | Labas | 1007 | 1097 |
| šiandien | 555 | 330 | | Ačiū | 1017 | 1098 |
| pirmadienis | 560 | 340 | | Kiek kainuoja? | 1035 | 1133 |

*Labas* and *Ačiū* stay past 1000 because they are tagged A2 and so sit in the A2 subdeck, after the 1,042 A1 cards; they now head it (10th–11th, not 160th).

## Decisions for you

1. **Adopt v2?** Build with `STUDY_ORDER=study_order_v2.csv`. The lists at the top of the script are the judgement; edit freely.
2. **Retag day-one items to A1:** *Labas, Ačiū, Prašau, Laba diena, Viso gero, Iki, Kiek kainuoja?, Nesuprantu, Kur yra…?* and the deck's *aš, tu, jis, ji, mes, jūs, jie, tai, taip, ne, geras, blogas, pinigai, kaina*. I did not edit the data files.
3. **Existing collections.** Recommended: write the zero-padded position into the existing *Number* field and make it the sort field of both note types. Not a schema change, so no one-way sync or prompt; users do Browse → sort by Sort Field → select all → Cards → Reposition. Cost: the bottom-bar number becomes the study position. A new *Order* field is a schema change: the importer skips every existing note as "conflicting" unless "Merge note types" is ticked (Anki 23.10+), then a one-way sync. Delete-and-reimport loses history, but for your own near-fresh collection it is quickest.
4. **Keep the 100-card picture gate and the A1→A2 split?** v2 assumes both.

Sources: github.com/hermitdave/FrequencyWords (content/2018/lt/lt_full.txt); github.com/adbar/simplemma; `sources/lt_3000_frequency.csv` (PERLSI, Dadurkevičius 2020); github.com/ankitects/anki rslib/src/import_export/package/apkg/import/{notes,cards}.rs.
