# Proofreading return, plan v1 (owner's spelling-and-structure pass, 2026-10-19)

Input: `sentences_for_proofreading_v1_returned_spelling_structure_pass.csv` against `sentences_for_proofreading_v1.csv` — 25 rows changed (24 with `lt_corrected` + a note; A2-1193 edited in `lt_with_blank`). Owner's instruction: incorporate. Default here is adopt; where a correction drops or replaces the cloze target, the decision rules of 2026-10-20 (lead) apply. One extra row (A2-1111 → 2021_kelinta) is a consequence of rule 5.

Plan: `returned_plan_v1.csv` (26 rows; `new_key` filled from `a2_build/rename/key_map_v1.csv` via `tools/keymap.py`). Counts: EDIT 11, KEEP_TARGET_NEW_SENTENCE 13, RETARGET 2, MERGE 0, REJECT 0.

## Summary

| old | new key | lvl | action | final example_lt | owner's correction |
|---|---|---|---|---|---|
| A2-1193 | 0331_kuri_valanda | A1 | EDIT | Kelinta valanda? | Kelinta valanda? |
| A2-1111 | 2021_kelinta | A2 | KEEP_TARGET_NEW_SENTENCE | {Kelinta} šiandien? | — |
| A2-0080 | 0514_amzius | A1 | KEEP_TARGET_NEW_SENTENCE | {Amžius} – tik skaičius. | Kiek jums metų? |
| A2-1972 | 0996_reiksme | A1 | KEEP_TARGET_NEW_SENTENCE | Šis žodis turi dvi {reikšmes}. | Ką reiškia šis žodis? |
| A2-1902 | 1006_veikla | A1 | RETARGET | Mėgstu {užsiėmimus} lauke. | Mėgstu užsiėmimus lauke. |
| A2-1701 | 1141_pusryciauti | A1 | EDIT | {Pusryčiauju} septintą valandą. | Pusryčiauju septintą valandą. |
| A2-1700 | 1422_pristatyti | A2 | EDIT | Leiskite {pristatyti}: tai mano žmona. | Leiskite pristatyti: tai mano žmona. |
| A2-0731 | 1514_eismas | A2 | EDIT | Centre intensyvus {eismas}. | Centre intensyvus eismas. |
| A2-0519 | 1521_reikalingas | A2 | KEEP_TARGET_NEW_SENTENCE | Ar tai {reikalinga}? | Man reikia žodyno. |
| S-0049 | 1543_ryte_as_geriu_kava | A2 | EDIT | Rytais {geriu} kavą. | Rytais geriu kavą. |
| A2-1017 | 1646_lengvai | A2 | KEEP_TARGET_NEW_SENTENCE | Ji {lengvai} išmoko plaukti. | Jis greitai išmoko. |
| A2-1484 | 1798_rusu_kalba | A2 | KEEP_TARGET_NEW_SENTENCE | Senelis skaito laikraščius {rusų kalba}. | Senelis kalba rusiškai. |
| A2-1756 | 1846_nuotaika | A2 | EDIT | Šiandien esu geros {nuotaikos}. | Šiandien esu geros nuotaikos. |
| A2-1968 | 1912_gebejimas | A2 | EDIT | Svarbus {gebėjimas} – klausytis. | Svarbus gebėjimas – klausytis. |
| A2-1190 | 1968_vieta_prie_tako | A2 | EDIT | {Vietą prie tako}, prašau. | Vietą prie tako, prašau. |
| A2-0330 | 1975_prognoze | A2 | KEEP_TARGET_NEW_SENTENCE | Kokia orų {prognozė} rytoj? | Rytoj prognozuojamas lietus. |
| A2-0996 | 2051_dukart | A2 | KEEP_TARGET_NEW_SENTENCE | Skambinau tau {dukart}. | Valgau du kartus per dieną. |
| A2-1481 | 2086_ispanu_kalba | A2 | KEEP_TARGET_NEW_SENTENCE | Ji gerai moka {ispanų kalbą}. | Ji kalba ispaniškai. |
| A2-0232 | 2100_persalimas | A2 | KEEP_TARGET_NEW_SENTENCE | Tai tik {peršalimas}. | Peršalau. |
| A2-0468 | 2201_gerinti | A2 | EDIT | Noriu {pagerinti} savo lietuvių kalbos žinias. | Noriu pagerinti savo lietuvių kalbos žinias. |
| A2-1577 | 2200_plansete | A2 | EDIT | Vaikas žaidžia žaidimus {planšetėje}. | Vaikas žaidžia žaidimus planšetėje. |
| A2-1008 | 2251_kazkiek | A2 | KEEP_TARGET_NEW_SENTENCE | Dar turiu {kažkiek} pinigų. | Turiu šiek tiek pinigų. |
| A2-0233 | 2309_karsciavimas | A2 | KEEP_TARGET_NEW_SENTENCE | Reikia vaistų nuo {karščiavimo}. | Vaikui pakilo temperatūra. |
| A2-1632 | 2360_draustis | A2 | RETARGET | Prieš kelionę reikia {apsidrausti}. | Prieš kelionę reikia apsidrausti. |
| A2-1702 | 2392_rakinti | A2 | KEEP_TARGET_NEW_SENTENCE | Kai {rakino} duris, atėjo kaimynas. | Vakare užrakinu duris. |
| A2-0975 | 2410_metus_mokausi_lietuviu_kalbos | A2 | EDIT | Jau {metus} mokausi lietuvių kalbos. | Jau metus mokausi lietuvių kalbos. |

## Non-EDIT rows, one paragraph each

**2021_kelinta** (A2-1111, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *{Kelinta} šiandien?* / What is the date today?. Rule 5 consequence: its example 'Kelinta valanda?' is now the phrase card 0331. 'Kelinta šiandien?' is the standard date question; distinct from 0538 'Kokia šiandien diena?' (day of the week). Not in the owner's sheet (no correction of its own).

**0514_amzius** (A2-0080, A1 cloze) — KEEP_TARGET_NEW_SENTENCE: *{Amžius} – tik skaičius.* / Age is just a number.. Rule 3: amžius is source=queue (not official) but the owner's 'Kiek jums metų?' is already an A1 phrase card (0308_kiek_jums_metu), so a retarget would be a merge; a natural sentence is easy, so coverage is kept. The saying uses amžius as a plain subject, not as a questionnaire field. skaičius (0748_skaicius, A1) sits after amžius @514: A1-LATER, the rebuild pulls it forward.

**0996_reiksme** (A2-1972, A1 cloze) — KEEP_TARGET_NEW_SENTENCE: *Šis žodis turi dvi {reikšmes}.* / This word has two meanings.. Rule 3: reikšmė is benchmark_en (not official); the owner's 'Ką reiškia šis žodis?' is, word for word, the example sentence of 0470_zodis, and reikšti is a card (A2-0462 'Ką tai reiškia?'). Retargeting would duplicate; a natural sentence with reikšmė is easy (a dictionary remark). All words A1 and earlier.

**1006_veikla** (A2-1902, A1 cloze) — RETARGET: *Mėgstu {užsiėmimus} lauke.* / I like outdoor activities.. New headword **užsiėmimas** — activity; pastime (also: class, session); stress užsiėmìmas; gen_sg užsiėmìmo; M (source: https://kirtis.info/api/krc/užsiėmimas ; https://kirtis.info/api/krc/užsiėmimo). Rule 3 + rule 4: the engine's condition ('if the intended meaning is outdoor activities') holds; veikla is benchmark_en, not official, and užsiėmimas is not a card, so the card is retargeted to the owner's word. Slug 1006_veikla is now stale — executor to decide whether the key is re-slugged. Level stays A1 (Oxford A1 'activity').

**1521_reikalingas** (A2-0519, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Ar tai {reikalinga}?* / Is that necessary?. Rule 3: reikalingas is source=queue, but reikia is a card several times over (0248_reiketi, 0723 reikia/turiu, 0247 Man reikia pagalbos), so the alternative is a merge; the predicate use 'Ar tai reikalinga?' is natural everyday Lithuanian and keeps the adjective. Cloze form reikalinga is on the card (fem column).

**1646_lengvai** (A2-1017, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Ji {lengvai} išmoko plaukti.* / She learned to swim easily.. Rule 4: the engine's note is conditional on the meaning 'quickly'; the card means 'easily', so greitai is rejected (greitai is a card anyway, 0650). The bare 'Jis lengvai išmoko' is given an object: plaukti (0519, A1), išmokti (1633, A2 < 1646).

**1798_rusu_kalba** (A2-1484, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Senelis skaito laikraščius {rusų kalba}.* / Grandfather reads newspapers in Russian.. Rule 3: official-list word kept; 'kalba rusiškai' is the engine's register for speaking, so the sentence moves to the register where 'rusų kalba' is the natural form (knyga/laikraštis + instrumental 'rusų kalba' = in Russian). laikraštis is a card (1218, A2 @1218 < 1798).

**1975_prognoze** (A2-0330, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Kokia orų {prognozė} rytoj?* / What is the weather forecast for tomorrow?. Rule 3 (deviation, flagged): prognozė is source=queue, and 'prognozuojamas' is not a card, so the rule would retarget — but the owner's note objects to the telegraphic sentence, not to the noun, and 'orų prognozė' is the everyday collocation; a passive participle of an untaught verb is a poor A2 headword. Kept with a natural question. 'orų' is not recognised by the tokeniser (simplemma lemma 'orus'; 0312_oras is 'air') — a pre-existing gap, same as the current sentence.

**2051_dukart** (A2-0996, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Skambinau tau {dukart}.* / I called you twice.. Rule 3: official-list word kept; 'du kartus' is already taught by the phrase card 1637 'Gerkite du kartus per dieną.' The adverb is natural in speech about counted events.

**2086_ispanu_kalba** (A2-1481, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Ji gerai moka {ispanų kalbą}.* / She knows Spanish well.. Rule 3: official-list word kept; 'mokėti kalbą' is the standard collocation (sister card 1933 prancūzų kalba uses it); accusative on the card's pattern.

**2100_persalimas** (A2-0232, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Tai tik {peršalimas}.* / It's just a cold.. Rule 3: peršalimas is source=queue; 'Peršalau' is already the phrase card 2062 'Karščiuoju. / Peršalau.', so the alternative is a merge. 'Tai tik peršalimas' (what a doctor says) is natural and keeps the noun.

**2251_kazkiek** (A2-1008, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Dar turiu {kažkiek} pinigų.* / I still have some money.. Rule 3: official-list word kept; šiek tiek is already a card (1266_siek_tiek). With 'dar' the unknown-amount adverb reads naturally.

**2309_karsciavimas** (A2-0233, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Reikia vaistų nuo {karščiavimo}.* / We need medicine for the fever.. Rule 3: karščiavimas is source=queue; 'temperatūra' (0343, A2) and 'Karščiuoju' (2062) are cards, so the alternative is a merge. The pharmacy phrase 'vaistai nuo karščiavimo' is natural (parallel to phrase card 1665 'vaistai nuo skausmo') and keeps the noun. The card's old DEFER note (off-list) stands if the owner prefers to drop it.

**2360_draustis** (A2-1632, A2 cloze) — RETARGET: *Prieš kelionę reikia {apsidrausti}.* / One should take out insurance before a trip.. New headword **apsidrausti** — to take out insurance; to get insured (perf.); stress apsidraũsti; pres3 apsidraũdžia; past3 apsìdraudė (source: https://kirtis.info/api/krc/apsidrausti ; https://kirtis.info/api/krc/apsidraudžia ; https://kirtis.info/api/krc/apsidraudė). Rule 2: apsidrausti is not a card (2360_draustis is the only draustis; 2360/A2-0496 drausti = to forbid). Retarget to the owner's verb. Slug 2360_draustis is now stale — executor to decide whether the key is re-slugged.

**2392_rakinti** (A2-1702, A2 cloze) — KEEP_TARGET_NEW_SENTENCE: *Kai {rakino} duris, atėjo kaimynas.* / While he was locking the door, the neighbour came.. Rule 2: užrakinti is already a card (1040_uzrakinti, A1 picture), so rakinti keeps its card. The imperfective is natural where the action is a process in progress, not a completed habit ('Vakare rakinu/užrakinu duris' is where the engine prefers the perfective); a 'kai … , atėjo' frame is the textbook imperfective/perfective contrast. pres3/past3 for 2392_rakinti are empty: fill rakìna / rakìno (https://kirtis.info/api/krc/rakina , https://kirtis.info/api/krc/rakino) so the form check recognises 'rakino' (simplemma does not lemmatise rakin- forms).

## EDIT rows that carry a data change beyond the sentence

- **0331_kuri_valanda**: `lithuanian_TARGET` and `example_lt` → *Kelinta valanda?*; `lt_pron` → *Kelintà valandà?* (kelintà: https://kirtis.info/api/krc/kelinta, nominative feminine, same as card 2021_kelinta; valandà as before). English unchanged. The slug `kuri_valanda` is now stale (executor's call).
- **2410_metus_mokausi_lietuviu_kalbos**: the headword is the sentence; `lithuanian_TARGET` → *Jau metus mokausi lietuvių kalbos*. Slug stale, same remark.
- **1968_vieta_prie_tako**: headword stays *vieta prie tako*; only `example_lt` changes (braces on *Vietą prie tako*).
- **1543_ryte_as_geriu_kava** (sentence card): `lt` → *Rytais {geriu} kavą.*, `en` → *In the mornings I drink coffee.*; `words_used` unchanged. Slug stale.
- **1514_eismas**: *intensyvus* is a new word no card teaches (see check). Adopted anyway: it is the owner's collocation and an international word; if the executor prefers a taught word, *Centre didelis eismas* was the original and the engine called it less idiomatic, not wrong.

## RETARGET data (for the executor)

- **1006_veikla → užsiėmimas**: `lithuanian_TARGET` užsiėmimas; `english` activity; pastime (also: class, session); `lt_pron` užsiėmìmas; `pron_src` kirtis.info; `gen_sg` užsiėmimo; `gender` M; `example_lt` *Mėgstu {užsiėmimus} lauke.*; `example_en` *I like outdoor activities.* Level stays A1. Sources: https://kirtis.info/api/krc/užsiėmimas (Užsiėmìmas, dktv., vyr.gim., vnsk., V.), https://kirtis.info/api/krc/užsiėmimo (Užsiėmìmo, K.), https://kirtis.info/api/krc/užsiėmimus (Užsiėmimùs, dgsk., G.). en.wiktionary has no entry for užsiėmimas (404 on 2026-10-20).
- **2360_draustis → apsidrausti**: `lithuanian_TARGET` apsidrausti; `english` to take out insurance; to get insured (perf.); `lt_pron` apsidraũsti; `pron_src` kirtis.info; `pres3` apsidraũdžia; `past3` apsìdraudė; `example_lt` *Prieš kelionę reikia {apsidrausti}.*; `example_en` *One should take out insurance before a trip.* Sources: https://kirtis.info/api/krc/apsidrausti (Apsidraũsti, vksm., sngr.), https://kirtis.info/api/krc/apsidraudžia (Apsidraũdžia, esam.l. III asm.), https://kirtis.info/api/krc/apsidraudė (Apsìdraudė, būt.kart.l. III asm.). en.wiktionary has no entry (404).
- **2392_rakinti** (not a retarget, but a data fill): `pres3` rakìna, `past3` rakìno — https://kirtis.info/api/krc/rakina (Rakìna, esam.l. III asm.), https://kirtis.info/api/krc/rakino (Rakìno, būt.kart.l. III asm.). Without them the form check cannot tie *rakino* (or the current *rakinu*) to the headword, because simplemma does not lemmatise rakin- forms.

## Dependency check

Same tokeniser, simplemma lemma and ne- rule as `build_study_order_v3` / `check_dep37_plan.py`, run on the pulled tree (new keys, `study_order.csv` of 02276fe) with the plan applied in memory (new sentences; retargeted headwords and forms; rakinti pres3/past3 filled). Phrase cards are not reading cards and are not checked.

**A1 cards (0331, 0514, 0996, 1006, 1141): clean.** Every word is taught by an earlier A1 card or is the target, except *skaičius* in 0514_amzius: taught by 0748_skaicius (A1) which sits after 0514 — A1-LATER, the rebuild pulls it forward (the same class of result the dep37 plan accepted).

**A2 cards — words no card teaches (OUTSIDE):**
- 1514_eismas: *intensyvus* — new (owner's word; see above).
- 1975_prognoze: *orų* — pre-existing (the current sentence has it too): simplemma lemmatises *orų* to *orus*, and 0312_oras is glossed 'air'. Not introduced by this plan.
- 2201_gerinti: *pagerinti* — pre-existing: the cloze form was already *pagerinti* on the headword *gerinti*; the dep37-style form check passes only through the old-target equality. Unchanged by this plan.
- 2392_rakinti: *rakino* — resolved by filling pres3/past3 (above); listed here because it fails on the tree as it stands.

```
0331_kuri_valanda                  @ 331 A1 phrase card — no dependency check (phrases are learnt whole)
2021_kelinta                       @2021 A2 {Kelinta} šiandien?
    kelinta          target
    šiandien         ok                                       0206_siandien@206 šiandien [A1], 0887_siandien_salta@887 Šiandien šalta [A1]
0514_amzius                        @ 514 A1 {Amžius} – tik skaičius.
    amžius           target
    tik              ok                                       0263_tik@263 tik [A1]
    skaičius         A1-LATER (rebuild pulls it forward)      0748_skaicius@748 skaičius [A1]
0996_reiksme                       @ 996 A1 Šis žodis turi dvi {reikšmes}.
    šis              ok                                       0193_sis@193 šis [A1], 0275_man_patinka_sis_miestas@275 Man patinka šis miestas [A1], 0361_sie@361 šie [A1]
    žodis            ok                                       0470_zodis@470 žodis [A1]
    turi             ok                                       0128_tureti@128 turėti [A1], 0225_ar_turite@225 Ar turite…? [A1], 0707_as_turiu_broli@707 Aš turiu brolį [A1]
    dvi              ok                                       0055_du@55 du [A1]
    reikšmes         target
1006_veikla                        @1006 A1 Mėgstu {užsiėmimus} lauke.
    mėgstu           ok                                       0273_megti@273 mėgti [A1]
    užsiėmimus       target
    lauke            ok                                       1005_lauke@1005 lauke [A1]
1141_pusryciauti                   @1141 A1 {Pusryčiauju} septintą valandą.
    pusryčiauju      target
    septintą         ok                                       0414_septintas@414 septintas [A1]
    valandą          ok                                       0261_valanda@261 valanda [A1], 0331_kuri_valanda@331 Kelinta valanda? [A1], 0366_kiek_valandu@366 Kiek valandų? [A1]
1422_pristatyti                    @1422 A2 Leiskite {pristatyti}: tai mano žmona.
    leiskite         ok                                       1267_leisti@1267 leisti [A2], 2030_leiskite_prisistatyti@2030 Leiskite prisistatyti. [A2]
    pristatyti       target
    tai              ok                                       0057_tai@57 tai [A1], 0231_kas_tai@231 Kas tai? [A1], 0408_ka_tai_reiskia@408 Ką tai reiškia? [A1]
    mano             ok                                       0031_as@31 aš [A1], 0113_mano@113 mano [A1], 0136_man_gerai@136 Man gerai [A1]
    žmona            ok                                       0823_zmona@823 žmona [A1]
1514_eismas                        @1514 A2 Centre intensyvus {eismas}.
    centre           ok                                       0216_centras@216 centras [A1]
    intensyvus       OUTSIDE (no card teaches it)             
    eismas           target
1521_reikalingas                   @1521 A2 Ar tai {reikalinga}?
    ar               ok                                       0125_ar_kalbate_angliskai@125 Ar kalbate angliškai? [A1], 0151_ar@151 ar [A1], 0191_ar_galite_man_padeti@191 Ar galite man padėti? [A1]
    tai              ok                                       0057_tai@57 tai [A1], 0231_kas_tai@231 Kas tai? [A1], 0408_ka_tai_reiskia@408 Ką tai reiškia? [A1]
    reikalinga       target
1543_ryte_as_geriu_kava            @1543 A2 Rytais {geriu} kavą.
    rytais           ok                                       0077_labas_rytas@77 Labas rytas [A1], 0163_rytas@163 rytas [A1], 0295_rytoj@295 rytoj [A1]
    geriu            target (sentence card)
    kavą             ok                                       0014_kava@14 kava [A1], 0871_noreciau_kavos@871 Norėčiau kavos [A1], 1081_viena_kava_prasau@1081 Vieną kavą, prašau. [A1]
1646_lengvai                       @1646 A2 Ji {lengvai} išmoko plaukti.
    ji               ok                                       0042_ji@42 ji [A1], 0372_ja@372 ją [A1]
    lengvai          target
    išmoko           ok                                       1633_ismokti@1633 išmokti [A2]
    plaukti          ok                                       0519_plaukti@519 plaũkti [A1]
1798_rusu_kalba                    @1798 A2 Senelis skaito laikraščius {rusų kalba}.
    senelis          ok                                       0522_senelis@522 senelis [A1]
    skaito           ok                                       0188_skaityti@188 skaityti [A1]
    laikraščius      ok                                       1218_laikrastis@1218 laikraštis [A2]
    rusų             target
    kalba            target
1846_nuotaika                      @1846 A2 Šiandien esu geros {nuotaikos}.
    šiandien         ok                                       0206_siandien@206 šiandien [A1], 0887_siandien_salta@887 Šiandien šalta [A1]
    esu              ok                                       0069_kur_yra@69 Kur yra…? [A1], 0099_nera_uz_ka@99 Nėra už ką [A1], 0106_buti@106 būti [A1]
    geros            ok                                       0038_geras@38 geras [A1], 0047_viso_gero@47 Viso gero [A1], 0444_geros_dienos@444 Geros dienos [A1]
    nuotaikos        target
1912_gebejimas                     @1912 A2 Svarbus {gebėjimas} – klausytis.
    svarbus          ok                                       0338_svarbus@338 svarbus [A1]
    gebėjimas        target
    klausytis        ok                                       0989_klausytis@989 klausýtis [A1]
1968_vieta_prie_tako               @1968 A2 phrase card — no dependency check (phrases are learnt whole)
1975_prognoze                      @1975 A2 Kokia orų {prognozė} rytoj?
    kokia            ok                                       0236_koks_tavo@236 Koks tavo / jūsų telefono numeris? [A1], 0238_koks@238 koks [A1], 0302_koks_jusu_vardas@302 Koks jūsų vardas? [A1]
    orų              OUTSIDE (no card teaches it)             
    prognozė         target
    rytoj            ok                                       0077_labas_rytas@77 Labas rytas [A1], 0163_rytas@163 rytas [A1], 0295_rytoj@295 rytoj [A1]
2051_dukart                        @2051 A2 Skambinau tau {dukart}.
    skambinau        ok                                       0059_skambinti@59 skam̃binti [A1]
    tau              ok                                       0035_tu@35 tu [A1], 0048_jus@48 jūs [A1], 0226_tave@226 tave [A1]
    dukart           target
2086_ispanu_kalba                  @2086 A2 Ji gerai moka {ispanų kalbą}.
    ji               ok                                       0042_ji@42 ji [A1], 0372_ja@372 ją [A1]
    gerai            ok                                       0136_man_gerai@136 Man gerai [A1], 0264_viskas_gerai@264 Viskas gerai [A1], 0270_gerai@270 gerai [A1]
    moka             ok                                       0235_moketi@235 mokė́ti [A1], 0612_moketi@612 mokėti (plaukti) [A1]
    ispanų           target
    kalbą            target
2100_persalimas                    @2100 A2 Tai tik {peršalimas}.
    tai              ok                                       0057_tai@57 tai [A1], 0231_kas_tai@231 Kas tai? [A1], 0408_ka_tai_reiskia@408 Ką tai reiškia? [A1]
    tik              ok                                       0263_tik@263 tik [A1]
    peršalimas       target
2201_gerinti                       @2201 A2 Noriu {pagerinti} savo lietuvių kalbos žinias.
    noriu            ok                                       0121_noreciau@121 Norėčiau… [A1], 0161_noreti@161 norėti [A1], 0637_noriu_valgyti@637 Noriu valgyti [A1]
    pagerinti        OUTSIDE (no card teaches it)             
    savo             ok                                       0304_savo@304 savo [A1], 0472_saves@472 savęs [A1]
    lietuvių         ok                                       0184_lietuviu_kalba@184 lietuvių kalba [A1]
    kalbos           ok                                       0184_lietuviu_kalba@184 lietuvių kalba [A1], 0458_kalba@458 kalba [A1]
    žinias           ok                                       1381_zinios@1381 žinios [A2]
    !! cloze word 'pagerinti' not recognised as a form of headword 'gerinti' (forms ['', '', '', ''])
2200_plansete                      @2200 A2 Vaikas žaidžia žaidimus {planšetėje}.
    vaikas           ok                                       0012_vaikas@12 vaikas [A1]
    žaidžia          ok                                       0256_zaisti@256 žaĩsti [A1]
    žaidimus         ok                                       1318_zaidimas@1318 žaidimas [A2], 1341_zaidimu_aikstele@1341 žaidimų aikštelė [A2], 1980_kompiuterinis_zaidimas@1980 kompiuterinis žaidimas [A2]
    planšetėje       target
2251_kazkiek                       @2251 A2 Dar turiu {kažkiek} pinigų.
    dar              ok                                       0185_dar@185 dar [A1], 0250_dar@250 dar [A1], 0537_vis_dar@537 vis dar [A1]
    turiu            ok                                       0128_tureti@128 turėti [A1], 0225_ar_turite@225 Ar turite…? [A1], 0707_as_turiu_broli@707 Aš turiu brolį [A1]
    kažkiek          target
    pinigų           ok                                       0040_pinigai@40 pinigai [A1]
2309_karsciavimas                  @2309 A2 Reikia vaistų nuo {karščiavimo}.
    reikia           ok                                       0247_man_reikia_pagalbos@247 Man reikia pagalbos [A1], 0248_reiketi@248 reikėti [A1], 0595_man_reikia_vandens@595 Man reikia vandens [A1]
    vaistų           ok                                       0510_vaistai@510 vaistai [A1]
    nuo              ok                                       0424_nuo@424 nuo [A1]
    karščiavimo      target
2360_draustis                      @2360 A2 Prieš kelionę reikia {apsidrausti}.
    prieš            ok                                       0524_pries@524 prieš [A1], 0591_pries@591 prieš (+acc) [A1]
    kelionę          ok                                       0768_geros_keliones@768 Geros kelionės [A1]
    reikia           ok                                       0247_man_reikia_pagalbos@247 Man reikia pagalbos [A1], 0248_reiketi@248 reikėti [A1], 0595_man_reikia_vandens@595 Man reikia vandens [A1]
    apsidrausti      target
2392_rakinti                       @2392 A2 Kai {rakino} duris, atėjo kaimynas.
    kai              ok                                       0326_kai@326 kai [A1], 0329_kai_kas@329 kai kas [A1], 0337_kai_kuris@337 kai kuris [A1]
    rakino           target
    duris            ok                                       0210_durys@210 durys [A1]
    atėjo            ok                                       0305_ateiti@305 ateiti [A1]
    kaimynas         ok                                       0060_kaimynas@60 kaimynas [A1]
2410_metus_mokausi_lietuviu_kalbos @2410 A2 Jau {metus} mokausi lietuvių kalbos.
    jau              ok                                       0159_jau@159 jau [A1]
    metus            target
    mokausi          target
    lietuvių         target
    kalbos           target
```

## For the owner to glance at (minimal)

1. **1975_prognoze** — I kept *prognozė* (*Kokia orų prognozė rytoj?*) instead of your *Rytoj prognozuojamas lietus*, reading your note as a complaint about the telegraphic sentence rather than the noun. Say if you want the noun dropped.
2. **2392_rakinti** — *Kai rakino duris, atėjo kaimynas.* keeps the imperfective because *užrakinti* already has a picture card (1040). Is the past-progressive frame natural to you?
3. **0514_amzius** — *Amžius – tik skaičius.* (your *Kiek jums metų?* is already card 0308). Fine as the one sentence for *amžius*?
4. **2309_karsciavimas** — kept with *Reikia vaistų nuo karščiavimo.*; the card was once marked DEFER (off-list). Drop it instead if you prefer.
5. Five slugs are now stale after text/headword changes (0331_kuri_valanda, 1006_veikla, 2360_draustis, 2410_metus_…, 1543_ryte_…): a naming question for the executor, not a content one.
