# Study order: audit and proposal (2026-10-17)

> Superseded by v3 on 2026-10-19: `REPORT_order_v3.md`, `AUDIT_v3.txt`, `build_study_order_v3.py`. Kept as history.

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

## Adopted 2026-10-17

Owner: "adopt the order, yes; don't worry about old studying, it is what it is, deck coherence is more important than whatever studying someone has done with it; retagging words to A1, yes."

Done, in three commits:

- **Retag, 62 items A2 → A1** (`retag_A1.csv`, one reason per row; only the `level` field changed in `cards_anki.csv`, `master_wordlist.csv` and `a2_build/a2_wordlist.csv`, keys and GUIDs untouched): basics / introductions 13 (*Kaip sekasi?, Mano vardas…, Nesuprantu, Ar kalbate angliškai?* …), survival 12 (*Kur yra…?, Norėčiau…, Padėkite!, Gelbėkit!, Aš pasiklydau, vaistinė, vaistai, Kaip nuvykti į…?* …), greetings 9, pronouns 8 (the deck's *aš … jie, tai*), money and price 7 (*pinigai, kaina, kainuoti, sąskaita, Kiek kainuoja?, Sąskaitą prašau, Ar galiu mokėti kortele?*), politeness 6, core verbs 3 (*galvoti, mokytis, mylėti*), yes/no 2, *geras/blogas*. Left at A2 on purpose: *muzika, sportas, daina* (hobby nouns, not in the brief), *mokyti, laimėti*, the P-L "Functions" phrases, *alio, šiaip sau, Sudie*, the time-telling phrases. Numbers 1–10, the question words, the modal verbs and *euras/centas* were already A1 in the list.
- **The order rebuilt and adopted.** `build_study_order_v2.py` now writes `study_order.csv` (the file `build_apkg.py` reads); `study_order_v2.csv` is gone and `build_study_order.py` is `deprecated/build_study_order_v1.py`, marked superseded. 2,437 rows: 1,164 A1 subdeck, 1,218 A2 subdeck, 55 sentences. Includes the 182 P-L benchmark additions (A2-1863…2045); the 31 `deferred_B1.csv` rows have no position and are not built. Checked against what `build_apkg.py` loads: all 1,555 keys it currently emits have a position, positions are unique, 1…2,437 without gaps. Spearman with subtitles 0.35 → 0.60, with press 0.14 → 0.40. Audit tables: `AUDIT_tables.txt`.
- **Existing collections:** the `build_apkg.py` identity notes and `anki/templates.md` now say delete and reimport; the order is not retrofitted onto old collections and no field is added to carry it.

### First 60 of the A1 subdeck

žmogus, vyras, moteris, vanduo, duona, batonas, valgyti, gerti, eiti, didelis, mažas, vaikas, namas, draugas, kava, arbata, pienas, šeima, parduotuvė, dirbti, miestas, batai, autobusas, šuo, katė, alus, obuolys, sriuba, taip, ne, aš, tu, jis, geras, blogas, pinigai, kaina, vienas, kalbėti, du, Labas, ji, mes, jūs, Ačiū, padėti, duoti, trys, darbas, sakyti, naujas, senas, jie, tai, Prašau, Laba diena, važiuoti, matyti, pirmas, keturi

### Telling positions (whole order; old = v1 at commit 2ea6462)

| word | old | new | | word | old | new |
|---|---|---|---|---|---|---|
| duona | 5 | 5 | | kiaulė | 310 | 975 |
| alus | 146 | 26 | | karvė | 226 | 1015 |
| Labas | 1007 | 41 | | prezidentas | 318 | 853 |
| Ačiū | 1017 | 45 | | teismas | 372 | 791 |
| Prašau | 1016 | 55 | | asmuo | 389 | 938 |
| aš | 470 | 31 | | branduolinis | 459 | 1875 (A2) |
| taip | 472 | 29 | | pragaras | 518 | 1743 (A2) |
| Kiek kainuoja? | 1035 | 88 | | mėsa | 1536 | 819 |
| Kur yra tualetas? | 1063 | 127 | | tualetas | 1557 | 399 |
| vaistinė | 978 | 369 | | euras | 1429 | 556 |
| kalbėti | 1212 | 39 | | antis | 2241 | 1155 |

### For the owner

- The A2 subdeck now opens with reading cards (*kuo, manyti, kai kuri, tokia*, then *Ir jums!, Ar galėtumėte man padėti?, pasaulis, pusė*) because its picture-card heads moved to A1 and the A2 schedule has no picture-first gate. Harmless for someone who has done 1,164 A1 cards; if you want the A2 subdeck to open on pictures too, set `FIRST_CLOZE` for the A2 block (one line in `schedule()`).
- *batonas* is in the order (6, after *duona*) but has no picture in this clone, so the builder skips it here; it builds wherever the image exists.
