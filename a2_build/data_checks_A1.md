# A1 data checks B1–B3 (2026-10-18)

Executor run of `a2_build/A1_WRAPUP.md` §B1–B3. Scripts in `a2_build/data_checks/`: `check_A1.py` (the three checks,
report `data_checks/results.json`, kirtis cache `kirtis_cache.json`), `phrase_stress.py` (B3 proposals),
`apply_fixes.py` (writes the clear fixes; log `data_checks/fixes_applied.csv`, 106 rows). Source for every fix:
kirtis.info's analyser, `https://kirtis.info/api/krc/<form>` (example: https://kirtis.info/api/krc/vizos), read 2026-10-18.

## B1 — no noun without a gender: **proved, after 15 fixes**
- `cards_anki.csv`: 94 rows have an empty gender: 84 verbs, 8 pronouns, and 354 *taip* / 355 *ne*, which
  `master_wordlist.csv` types as N but are particles (yes/no). **No noun.**
- The A1-tagged rows of `a2_wordlist.csv` had **15 nouns with no gender**, all plural-only or indeclinable. Filled from
  kirtis (`fixes_applied.csv`): meniu M, taksi M (both indeclinable, *vyr.gim.*); laiptai, akiniai, vaisiai, namai, orai,
  šortai, makaronai, žmonės M pl; atostogos, žirklės F pl; salotos, daržovės, šlepetės F pl (kirtis lists *mot.gim. dgsk.*
  beside a singular reading of the same spelling; the cards mean the plural). After the fix no A1 noun lacks a gender.

## B2 — rule-derived gen_sg / fem of the A1-tagged A2-list rows: **177 of 178 confirmed, 0 wrong**
- 178 forms still marked "rule-derived" (gen_sg) or "fem: rule": kirtis returns the expected analysis
  (*dktv. … vnsk./dgsk. K.* with the row's gender; *mot.gim. vnsk. V.* for feminines) for **177**; the `check` column now
  says "kirtis.info … confirmed 2026-10-18". No form was contradicted, so no data changed.
- **Unverified (1):** A2-0674 *koldūnas* → gen. *koldūno*: kirtis has no entry for the word. The genitive follows the
  regular -as → -o pattern; Wiktionary has the headword (koldū̃nas). Left as is.

## B3 — every A1 row has a stressed pron
- `cards_anki.csv` (521 rows): every pron carries a mark. `accents_todo_kirtis.csv` has no `FILL_ME` left.
- A1-tagged rows of `a2_wordlist.csv`: **149 had no stressed pron** (132 PHRASE, 16 CLOZE, 1 IMG), mostly the survival
  phrases retagged on 2026-10-17. **91 filled** word by word from kirtis, only where every kirtis analysis of each word gives
  the same stress (check note: "kirtis.info per word — verify phrase stress", as for the earlier assembled phrases).
- **58 left open (uncertain)** — a word with two stress patterns (*yra: yrà / ỹra*, *gerai: geraĩ / gẽrai*, the
  infinitive -ti / -tì), or a word kirtis does not have (*ačiū, iki, čia, šiandien, labanakt, dėkui, gaila*). Which reading
  applies depends on the phrase, so these need a reader, not a script.
  Nothing was guessed into the data.

| id | phrase | kirtis partial | open words (kirtis candidates) |
|---|---|---|---|
| A2-0136 | į | į | no stressed word |
| A2-1058 | vis dar | vis dar | no stressed word |
| A2-0348 | Labas | Labas | Labas: labàs / lãbas |
| A2-0350 | Labas rytas | Labas rýtas | Labas: labàs / lãbas |
| A2-0351 | Laba diena | Laba diena | Laba: labà / lãba; diena: dienà / diẽna |
| A2-0352 | Labas vakaras | Labas vãkaras | Labas: labàs / lãbas |
| A2-0353 | Labanakt | Labanakt | Labanakt: no analysis |
| A2-0355 | Iki pasimatymo | Iki pasimãtymo | Iki: no analysis |
| A2-0356 | Iki | Iki | Iki: no analysis |
| A2-0358 | Ačiū | Ačiū | Ačiū: no analysis |
| A2-0359 | Labai ačiū | Lãbai ačiū | ačiū: no analysis |
| A2-0363 | Malonu susipažinti | Malonù susipažinti | susipažinti: susipažintì / susipažìnti |
| A2-0365 | Man gerai | Mán gerai | gerai: geraĩ / gẽrai |
| A2-0378 | Kur yra…? | Kur yra…? | yra: yrà / ỹra |
| A2-0382 | Ar yra…? | Ar yra…? | yra: yrà / ỹra |
| A2-0383 | Ar galite man padėti? | Ar gãlite mán padėti? | padėti: padėtì / padė́ti |
| A2-0887 | Sėkmės! | Sėkmės! | Sėkmės: sėkmė̃s / sė̃kmės |
| A2-0893 | Iki rytojaus | Iki rytójaus | Iki: no analysis |
| A2-0894 | Geros dienos | Geros dienos | Geros: gerõs / gẽros; dienos: dienõs / diẽnos |
| A2-0895 | Geros kelionės | Geros keliõnės | Geros: gerõs / gẽros |
| A2-0896 | Kas tai? | Kàs tai? | tai: taĩ / tái |
| A2-0898 | Kur yra tualetas? | Kur yra tualètas? | yra: yrà / ỹra |
| A2-0899 | Kiek tai kainuoja? | Kiek tai kainúoja? | tai: taĩ / tái |
| A2-0900 | Nekalbu lietuviškai | Nekalbu lietùviškai | Nekalbu: nekalbù / nèkalbu |
| A2-0904 | Ką tai reiškia? | Ką̃ tai réiškia? | tai: taĩ / tái |
| A2-0909 | Kur galiu rasti…? | Kur galiù rasti…? | rasti: rastì / ràsti |
| A2-0910 | Mano vardas Dainius | Mãno var̃das Dainius | Dainius: dainiùs / daĩnius |
| A2-0913 | Man dvidešimt metų | Mán dvìdešimt metų | metų: mètų / mẽtų |
| A2-0917 | Norėčiau kavos | Norė́čiau kavos | kavos: kavõs / kãvos |
| A2-0921 | Tai mano namas | Tai mãno nãmas | Tai: taĩ / tái |
| A2-0922 | Čia yra parduotuvė | Čia yra parduotùvė | Čia: no analysis; yra: yrà / ỹra |
| A2-0923 | Šiandien šalta | Šiandien šalta | Šiandien: no analysis; šalta: šaltà / šálta |
| A2-0925 | Trečia valanda | Trečia valanda | Trečia: trečià / trẽčia; valanda: valandà / vãlanda |
| A2-0926 | Kur tu eini? | Kur tù eini? | eini: einì / eĩni / éini |
| A2-0954 | Ar galiu mokėti kortele? | Ar galiù mokė́ti kortele? | kortele: kortelè / kortẽle |
| A2-0957 | Kaip nuvykti į…? | Kaip nuvykti į…? | nuvykti: nuvyktì / nuvỹkti |
| A2-1150 | gaila | gaila | gaila: no analysis |
| A2-1157 | Kiek jums metų? | Kiek jùms metų? | metų: mètų / mẽtų |
| A2-1160 | Ką veiki? | Ką̃ veiki? | veiki: veikì / véiki |
| A2-1161 | Viskas gerai | Vìskas gerai | gerai: geraĩ / gẽrai |
| A2-1163 | Laimingų Naujųjų metų! | Laimìngų Naujų̃jų metų! | metų: mètų / mẽtų |
| A2-1178 | dėkui | dėkui | dėkui: no analysis |
| A2-1182 | labai gerai | lãbai gerai | gerai: geraĩ / gẽrai |
| A2-1193 | Kuri valanda? | Kurì valanda? | valanda: valandà / vãlanda |
| A2-1620 | na | na | no stressed word |
| A2-1897 | noriu gerti | nóriu gerti | gerti: gertì / gérti |
| A2-1959 | važiuoti dviračiu | važiúoti dviračiu | dviračiu: dviračiù / dvìračiu |
| A2-1983 | Čia (yra) mano draugas. / Susipažinkite — tai… | Čia (yra) mãno draũgas. / Susipažìnkite — tai… | Čia: no analysis; yra: yrà / ỹra; tai: taĩ / tái |
| A2-1987 | Ačiū, ne. | Ačiū, ne. | Ačiū: no analysis |
| A2-1989 | Ar nori arbatos? / Ar norite arbatos? | Ar nori arbãtos? / Ar nórite arbãtos? | nori: norì / nóri |
| A2-1993 | Ar galima? | Ar galima? | galima: galimà / gãlima |
| A2-1994 | Galima. / Prašom. | Galima. / Prãšom. | Galima: galimà / gãlima |
| A2-2003 | Man šalta. / Man karšta. | Mán šalta. / Mán karšta. | šalta: šaltà / šálta; karšta: karštà / kar̃šta / káršta |
| A2-2006 | Ar toli? / Netoli. | Ar tõli? / Netoli. | Netoli: no analysis |
| A2-2009 | Viskas, ačiū. | Vìskas, ačiū. | ačiū: no analysis |
| A2-2019 | Iki greito! / Iki vėliau! | Iki greĩto! / Iki vė́liau! | Iki: no analysis; Iki: no analysis |
| A2-2023 | Atsiprašau, ar čia laisva? | Atsiprašaũ, ar čia laisva? | čia: no analysis; laisva: laisvà / laĩsva |
| A2-2026 | Vieną bilietą į Kauną, prašau. | Víeną bìlietą į Kauną, prašaũ. | Kauną: kaũną / káuną |

Only three rows are open because they are genuinely unstressed or one-word particles: A2-0136 *į*, A2-1058 *vis dar*,
A2-1620 *na* (a mark is optional on these; the owner may accept them as they are).
