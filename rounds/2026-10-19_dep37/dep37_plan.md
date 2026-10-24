# dep37 — the 37 A1 reading cards that use an A2-only word (plan, not applied)

*Fable, 2026-10-19. Against `study_order.csv` v3 (commit 707dadf) and `AUDIT_v3.txt` ("37 of them are A1 cards needing a word taught only in A2"). Files: `dep37_plan.csv` (one row per affected card), `check_dep37_plan.py` (applies the plan in memory and re-runs the v3 dependency check). Nothing in the data files is changed by this plan; the executor applies it.*

## Result in one line

**5 words move A2 → A1** (fixing 7 of the 37 uses on 7 cards); **26 cards are reworded** (30 uses). Dry-run of the audit's own dependency logic after the plan: **0 A1 word uses depend on an A2-only card** (was 37). A simulated full rebuild (`build_study_order_v3.py --report` on a scratch copy with the plan applied) gives the same 0, with only the 4 pre-existing within-A1 forward dependencies left (teisingas, numeris, padaryti, manau — the cycle cases the v3 report already lists), no new ones. No key changes are needed (see below).

## 1. Words to move to A1 (5)

Sources: VU A1+A2 list = `sources/vu_a1a2_lexicon.csv`, parsed from `sources/A2_2_lygis_VU_A1A2_lexicon.pdf` (https://www.lu.lv/fileadmin/user_upload/LU.LV/Apaksvietnes/Projekti/perlsi/A2_2_lygis.pdf); subtitle rank = `a2_build/study_order/opensubtitles_lt_lemmas.csv` (OpenSubtitles 2018 lemmatised, the deck's own scoring table); press rank = `sources/lt_3000_frequency.csv` (PERLSI 3,000, https://www.lu.lv/fileadmin/user_upload/LU.LV/Apaksvietnes/Projekti/perlsi/3000_zodziu.pdf). **Caveat:** the VU list merges the A1 (*Lūžis*) and A2 (*Pusiaukelė*) vocabularies without marking which is which, so "on the VU list" means A1-or-A2; *Lūžis* itself (vlkk.lt) is not reachable from this session, so "A1 specifically" is argued from frequency and from what the sentences need, and is marked unverified.

| key | word | why A1 | fixes |
|---|---|---|---|
| `169_muzika` | muzika | Fluent Forever 625 deck card; subtitle rank 1,560, press 461 (top 500); in the deck's CORE "society" T1 list. Not on the VU list (neither is *televizorius*'s partner *televizija*). It got `A2` on 2026-07-25 in the blanket CEFR tagging of the deck (commit 803067e); `a2_build/deck_fixes.csv` row 89 already proposed A2→A1 ("tag only"); `REPORT_order_v3.md` left it to the owner, who has now named it. Picture card: image exists. | 2 — S-0020 "Man {patinka} muzika." (picture + words_used unchanged), A2-1947 kurti "Ji {kuria} muziką." |
| `A2-0291` | keltis | VU list; subtitle 649; daily-routine verb ("I get up at seven" is A1 textbook matter — unverified against *Lūžis*). Picture card, image exists (`_apkg_media/A2-0291.jpg`). | 2 — A2-0192 anksti "Keliuosi {anksti}.", A2-1033 paprastai "{Paprastai} keliuosi septintą." |
| `A2-0848` | tiesa | VU list; subtitle 108, press 413 — the most frequent of the 37. Its own cloze "Tai {tiesa}." is A1-clean. | 1 — A2-1682 pasakyti "{Pasakyk} man tiesą." (alternative without a move: "{Pasakyk} man savo vardą.") |
| `A2-1475` | teisus | VU list; subtitle 308 (press 2,892). Its own cloze "Tu {teisus}." is A1-clean. In the simulated rebuild it lands at ~699, before klientas (~737) — but after kad (171), which is why the kad card is reworded instead (row A2-0159). | 1 — A2-0779 "{Klientas} visada teisus." (keeps the idiom; the alternative "{Klientas} laukia." loses it) |
| `A2-1725` | šviesti | VU list; subtitle 4,361 — the weakest by frequency, but S-0023's cloze word *is* šviečia, so the sentence cannot be reworded: the only choices are moving šviesti up or demoting S-0023 to A2. "Šviečia saulė" is A1 weather talk by any syllabus (unverified against *Lūžis*). | 1 — S-0023 "Saulė {šviečia}." |

Ready to append to `a2_build/study_order/retier_v3.csv` (same columns; then `python3 build_study_order_v3.py --apply-retier`):

```
169_muzika,muzika,music,A2,A1,"dep37: S-0020 and the A1 cloze for kurti use it; FF 625 deck card, subtitle 1560, press 461; A2 since the 2026-07-25 blanket tagging"
A2-0291,keltis,to wake up,A2,A1,"dep37: the A1 cloze for anksti and paprastai use keliuosi; VU list, subtitle 649"
A2-0848,tiesa,truth,A2,A1,"dep37: the A1 pair card pasakyti uses tiesą; VU list, subtitle 108, press 413"
A2-1475,teisus,right (correct),A2,A1,"dep37: the A1 cloze for klientas uses it (Klientas visada teisus); VU list, subtitle 308"
A2-1725,šviesti,to shine,A2,A1,"dep37: S-0023 'Saulė šviečia' is an A1 sentence card whose cloze word is šviečia; VU list"
```

### Considered and not moved

- **pamoka** (A2-0250; VU list, subtitle 1,038) — would fix 2 (prasidėti, devintas) and was the first draft. Simulated rebuild: by its own score it lands at ~758 in A1, after prasidėti (~420), and devintas was dragged to 759 behind it, breaking the ordinals run. The scheduler does not pull it forward because its cycle-breaker (`break_cycles`) waives dependencies between cards of one big strongly-connected component — nearly every cloze card whose sentence contains a pronoun is in it. Rewording both cards is cleaner (filmas / autobusas). Same reason the kad card is reworded rather than relying on the teisus move.
- **virš** (A2-1089; VU list, subtitle 826) — would fix S-0035 and keep its "virš + genitive" grammar point, but its own cloze "Lempa kabo {virš} stalo" uses *kabėti*, which no card teaches (the audit's "outside" class); moving it would put an untaught verb into A1. S-0035 is reworded instead (locative).
- **televizija** (A2-1804; subtitle 1,785, press 481) — the A1 deck already has *televizorius* (256, @601), which the reklama sentence can use.
- **vykti, reikalas, pažinti, nuomonė, pakviesti, papasakoti** — all frequent (subtitle 187–537) and plausible A1, but each fixes one card and a one-line reword does the same without growing A1. If the owner wants any of them in A1 anyway, the rewords still stand.
- **Demoting S-0023 / S-0020 / S-0035 to A2** — not chosen; the three are A1 picture sentences and two of them are fixed by moves that keep them in A1.

### KEY_CHANGE (allowed since keys are not frozen yet)

None proposed: in every one of the 33 cards the headword is the right word and only the surrounding sentence or the level of a teaching card changes, so nothing is gained by a new key. One candidate was weighed — **A2-1725 šviesti and S-0023 teach the identical sentence "Saulė {šviečia}."**, and after the move both sit in A1 (šviesti ~1076, S-0023 ~1135). A merge would lose either the picture card or the headword card, so instead: optional, not in the CSV — change A2-1725's own example to "Mėnulis {šviečia}." / "The moon is shining." (mėnulis 297, A1 @ nature core) so the two cards stop duplicating each other. Owner's call.

## 2. Rewords (26 cards, 30 uses) — `dep37_plan.csv`

Columns: `key, level, position_v3, headword, action, retier_key, retier_word, retier_pos_v3, current_example_lt, current_example_en, new_example_lt, new_example_en, new_words_used, words_taught_by, lithuanian_confidence, note`. `words_taught_by` lists every word of the final sentence with the A1 card that teaches it and that card's v3 position (`target` = the cloze word). Cloze braces follow the current format (`{…}` around the target form). Rules kept: natural, short, A1-plain; same cloze word and form; correct government (laukti + gen, norėti + gen, nekęsti + gen, pagal + acc); no stress marks; every non-target word taught by an A1 card positioned **before** the card (no "A1-later" cases).

| key | @ | current | new |
|---|---|---|---|
| A2-0174 jau | 157 | Vakarienė {jau} paruošta. | Vaikas {jau} miega. |
| A2-1103 jį | 167 | Aš {jį} pažįstu. | Aš {jį} matau. |
| A2-0159 kad | 171 | Manau, {kad} jis teisus. | Manau, {kad} jis namie. |
| A2-1106 kai kuris | 334 | {Kai kurie} žmonės nemėgsta žiemos. | {Kai kurie} žmonės mėgsta žiemą. |
| A2-0160 jei | 373 | {Jei} bus šilta, eisime maudytis. | {Jei} bus šilta, eisime į mišką. |
| A2-0002 valanda | 377 | Kelionė trunka vieną {valandą}. | Laukiu autobuso jau vieną {valandą}. |
| A2-1013 kur nors | 404 | Eime {kur nors} pavalgyti. | Eikime {kur nors} valgyti. |
| A2-1696 prasidėti | 422 | Pamoka {prasideda} aštuntą. | Filmas {prasideda} aštuntą. |
| A2-1792 devintas | 427 | Pamoka {devintą} valandą. | Autobusas {devintą} valandą. |
| A2-0201 bandyti | 449 | {Bandau} išmokti lietuviškai. | {Bandau} kalbėti lietuviškai. |
| A2-0200 ketinti | 494 | {Ketinu} aplankyti močiutę. | Vasarą {ketinu} važiuoti į Kauną. |
| A2-0808 istorija | 506 | Papasakok man {istoriją}. | Skaitau įdomią {istoriją}. |
| A2-1120 mus | 515 | Pakviesk {mus}. | Ar matai {mus}? |
| A2-1526 kairė | 576 | Pasukite į {kairę}. | Eikite į {kairę}. |
| A2-1082 pagal | 628 | Gaminu {pagal} receptą. | Viskas {pagal} planą. |
| A2-1506 dešinė | 642 | Pasukite į {dešinę}. | Eikite į {dešinę}. |
| A2-1941 nekęsti | 686 | Aš {nekenčiu} šalčio. | Aš {nekenčiu} žiemos. |
| A2-1977 norėčiau | 687 | {Norėčiau} užsisakyti staliuką. | {Norėčiau} eiti namo. |
| A2-1592 reklama | 743 | Per televiziją daug {reklamos}. | Per televizorių daug {reklamos}. |
| S-0035 | 778 | Paukštis {skrenda} virš miško. | Paukštis {skrenda} danguje. |
| A2-1973 faktas | 783 | Tai {faktas}, ne nuomonė. | Tai įdomus {faktas}. |
| A2-1593 salė | 835 | Koncertas vyks didžiojoje {salėje}. | Koncertas bus didelėje {salėje}. |
| A2-0500 lankyti | 873 | {Lankau} lietuvių kalbos kursus. | {Lankau} draugą ligoninėje. |
| A2-1887 asmeninis | 880 | Tai mano {asmeninis} reikalas. | Tai {asmeninis} klausimas. |
| A2-1694 pietauti | 1067 | {Pietaujame} dvyliktą. | {Pietaujame} pirmą valandą. |
| A2-1881 mėgstamiausias | 1078 | Mano {mėgstamiausias} valgis — cepelinai. | Mano {mėgstamiausias} gėrimas — kava. |

Two audit quirks the rewords work around (documented in the CSV notes, not fixed in the script):
- `nemėgsta` is matched to the A2 card *nemėgti* (A2-1662) before the ne- rule can fall back to *mėgti*, so A2-1106 uses the positive form.
- `didžiojoje` is lemmatised onto the A2 phrase "Šis didesnis nei tas", not onto *didelis*; `didelėje` is.
- Sentence cards (S-####) teach nothing in the audit's model, so their cloze word counts as a dependency too (S-0023); the plan respects that rather than special-casing it.

**For the owner's glance (Lithuanian I am least sure of, `lithuanian_confidence = check`):**
- A2-0002 "Laukiu autobuso jau vieną {valandą}." — word order; "Autobuso laukiu jau valandą" is the more spoken variant.
- A2-1013 "Eikime {kur nors} valgyti." — *pavalgyti* is the idiomatic verb here but no card teaches it (the audit counted it as an untaught word even now); *valgyti* is acceptable speech.
- A2-1592 "Per televizorių daug {reklamos}." — everyday but colloquial; "Per televizorių rodo daug reklamos" (rodyti A1 @666 < 743) if preferred.
- Minor: A2-1792 "Autobusas {devintą} valandą." keeps the elliptical shape of the current "Pamoka devintą valandą".

## 3. Knock-on effects

1. **Recorder.** Every reworded card's sentence take `<key>_s.mp3` (and S-0035.mp3) is `status = new` in `a2_build/recording_list.csv` — none has a human take yet; the word takes are untouched (A2-0002's word take already exists as `audio_a2/A2-0002.mp3`, unaffected). Re-running `python3 build_recorder.py A2` after the edits regenerates the sheet with the new scripts; the 5 moved cards' takes change level A2→A1 (169_muzika is `replace-tts`; A2-1475, A2-0848, A2-1725 have word + sentence takes; A2-0291 word only). The browser store (`DECK_SHEET_ID` fixed) is unaffected.
2. **Pictures.** The 25 reworded list cards are plain cloze rows (`image_possible = no`): no picture to mismatch. S-0020 and S-0023 keep their sentences, so their pictures stand. **S-0035** is reworded: its picture (`out_deck_sent/ledger.csv`: "a stork with wings spread high above a pine forest, the treetops below") still depicts a bird flying in the sky; no re-render needed, but `grammar_point` in `sentences.csv` must change from "virš + genitive" to "present 3sg; locative" and `words_used` to `004_paukstis 369_skristi 301_dangus` (in the CSV).
3. **Levels on disk.** `--apply-retier` writes the 5 levels into `cards_anki.csv` (1), `a2_build/a2_wordlist.csv` (4) and `master_wordlist.csv` (1) — verified in the simulation. Subdecks become A1 1,191 / A2 1,242 (from 1,186 / 1,247). The deck description's counts (filled from the built package) will change accordingly.
4. **Duplicate sentence in A1.** After the šviesti move, A2-1725 "Saulė {šviečia}." (cloze, English hint on the front) and S-0023 "Saulė {šviečia}." (picture cloze) are both in A1 (~1076 and ~1135). Optional fix above (A2-1725 → "Mėnulis {šviečia}."). S-0023 moves from 640 to ~1135 because šviesti's frequency score is low; still inside A1.
5. **Order moves in the rebuild** (simulated): S-0020 296 → ~593 (it now waits for muzika at ~299 and the reading-card cap); pasakyti 279 → ~350 (waits for tiesa ~349); valanda 377 → ~261 (its new sentence has only early words); everything else within a few places. `recording_order_v3.csv` is regenerated by the build.
6. **Scheduler note for a later version, not for this fix:** `break_cycles` treats the whole reading-card dependency graph as one component because pronoun cloze cards (*mano, man, mane, jį …*) occur in most sentences and are themselves cloze cards; it then waives any dependency on a worse-scored member. That is why a moved word with a late score (pamoka, teisus) is not pulled before the sentence that needs it, and why "Aš {jau} namie" let jau drift behind jų in a first simulation (the final "Vaikas {jau} miega." uses picture-card words only). A tighter cycle-breaker (waive only the edges that actually close a cycle) would make the order robust to this; worth a line in QUEUE.md.

## 4. Executor steps

1. Append the 5 rows above to `a2_build/study_order/retier_v3.csv`; `python3 build_study_order_v3.py --apply-retier`.
2. In `a2_build/a2_wordlist.csv` set `example_lt` / `example_en` for the 25 list cards from `dep37_plan.csv` (`new_example_lt`, `new_example_en`). In `a2_build/sentences/sentences.csv` set S-0035 `lt`, `en`, `words_used`, `grammar_point`. Keys, GUIDs, headwords, forms untouched.
3. `python3 a2_build/study_order/check_dep37_plan.py` must still print `RESULT: OK` (it now sees the applied state: 0 before, 0 after).
4. `OLD_ORDER=study_order.csv python3 build_study_order_v3.py --report > a2_build/study_order/AUDIT_v3_1.txt` (new file, do not overwrite `AUDIT_v3.txt`); expect "0 of them are A1 cards needing a word taught only in A2" and 6 forward dependencies in all (4 A1-internal, 2 A2-internal, as today).
5. `python3 build_recorder.py A2`; then the A1 v3.0 package build.

## 5. Checker output (`python3 a2_build/study_order/check_dep37_plan.py`, 2026-10-19)

```
before the plan: 37 A1 word uses depend on an A2-only card (33 cards)
moved to A1: 169_muzika muzika, A2-0291 keltis, A2-0848 tiesa, A2-1475 teisus, A2-1725 šviesti

== words of the new sentences ==
A2-0174  @ 157 Vaikas {jau} miega.
    vaikas           ok                                           101_vaikas@12 vaikas
    jau              target
    miega            ok                                           409_miegoti@144 miegóti
A2-1103  @ 167 Aš {jį} matau.
    aš               ok                                           510_as@31 aš, A2-0118@113 mano, A2-0365@136 Man gerai
    jį               target
    matau            ok                                           394_matyti@122 matýti
A2-0159  @ 171 Manau, {kad} jis namie.
    manau            A1-LATER (rebuild pulls it forward)          A2-1656@194 manyti
    kad              target
    jis              ok                                           512_jis@37 jis, 517_jie@53 jie, A2-0121@149 jos
    namie            ok                                           025_namas@13 namas, A2-1557@383 namai, A2-0921@430 Tai mano namas
A2-1106  @ 334 {Kai kurie} žmonės mėgsta žiemą.
    kai              target
    kurie            target
    žmonės           ok                                           103_zmogus@1 žmogus, A2-0897@244 Kas tas žmogus?, A2-1800@285 žmonės
    mėgsta           ok                                           A2-0206@323 mėgti
    žiemą            ok                                           A2-0040@100 žiema
A2-0160  @ 373 {Jei} bus šilta, eisime į mišką.
    jei              target
    bus              ok                                           A2-0378@69 Kur yra…?, A2-0360@99 Nėra už ką, A2-0194@106 būti
    šilta            ok                                           458_siltas@119 šiltas
    eisime           ok                                           366_eiti@11 eĩti, 371_eiti@297 eĩti, A2-0926@442 Kur tu eini?
    mišką            ok                                           300_miskas@291 miškas
A2-0002  @ 377 Laukiu autobuso jau vieną {valandą}.
    laukiu           ok                                           A2-0413@82 laukti
    autobuso         ok                                           016_autobusas@24 autobusas
    jau              ok                                           A2-0174@157 jau
    vieną            ok                                           A2-0042@52 vienas, A2-2026@513 Vieną bilietą į Kauną, prašau., A2-1122@732 nė vienas
    valandą          target
A2-1013  @ 404 Eikime {kur nors} valgyti.
    eikime           ok                                           366_eiti@11 eĩti, 371_eiti@297 eĩti, A2-0926@442 Kur tu eini?
    kur              target
    nors             target
    valgyti          ok                                           376_valgyti@5 válgyti, A2-0916@638 Noriu valgyti
A2-1696  @ 422 Filmas {prasideda} aštuntą.
    filmas           ok                                           170_filmas@141 filmas
    prasideda        target
    aštuntą          ok                                           A2-1791@417 aštuntas
A2-1792  @ 427 Autobusas {devintą} valandą.
    autobusas        ok                                           016_autobusas@24 autobusas
    devintą          target
    valandą          ok                                           A2-1193@286 Kuri valanda?, A2-0379@363 Kiek valandų?, A2-0002@377 valanda
A2-0201  @ 449 {Bandau} kalbėti lietuviškai.
    bandau           target
    kalbėti          ok                                           A2-0426@71 kalbėti, A2-0370@125 Ar kalbate angliškai?, A2-0375@202 Prašom kalbėti lėčiau
    lietuviškai      ok                                           A2-0900@271 Nekalbu lietuviškai, A2-0905@1055 Kaip lietuviškai …?, A2-1018@1184 lietuviškai
A2-0200  @ 494 Vasarą {ketinu} važiuoti į Kauną.
    vasarą           ok                                           A2-0038@91 vasara
    ketinu           target
    važiuoti         ok                                           A2-1445@61 važiuoti, A2-1959@1080 važiuoti dviračiu
A2-0808  @ 506 Skaitau įdomią {istoriją}.
    skaitau          ok                                           A2-1438@247 skaityti
    įdomią           ok                                           A2-0524@290 įdomus
    istoriją         target
A2-1120  @ 515 Ar matai {mus}?
    ar               ok                                           A2-0370@125 Ar kalbate angliškai?, A2-0165@156 ar, A2-0383@191 Ar galite man padėti?
    matai            ok                                           394_matyti@122 matýti
    mus              target
A2-1526  @ 576 Eikite į {kairę}.
    eikite           ok                                           366_eiti@11 eĩti, 371_eiti@297 eĩti, A2-0926@442 Kur tu eini?
    kairę            target
A2-1082  @ 628 Viskas {pagal} planą.
    viskas           ok                                           A2-1161@266 Viskas gerai, A2-1131@459 viskas, A2-2009@633 Viskas, ačiū.
    pagal            target
    planą            ok                                           A2-0833@411 planas
A2-1506  @ 642 Eikite į {dešinę}.
    eikite           ok                                           366_eiti@11 eĩti, 371_eiti@297 eĩti, A2-0926@442 Kur tu eini?
    dešinę           target
A2-1941  @ 686 Aš {nekenčiu} žiemos.
    aš               ok                                           510_as@31 aš, A2-0118@113 mano, A2-0365@136 Man gerai
    nekenčiu         target
    žiemos           ok                                           A2-0040@100 žiema
A2-1977  @ 687 {Norėčiau} eiti namo.
    norėčiau         target
    eiti             ok                                           366_eiti@11 eĩti, 371_eiti@297 eĩti, A2-0926@442 Kur tu eini?
    namo             ok                                           025_namas@13 namas, A2-1557@383 namai, A2-0921@430 Tai mano namas
A2-1592  @ 743 Per televizorių daug {reklamos}.
    per              ok                                           A2-0144@189 per, A2-0188@328 per
    televizorių      ok                                           256_televizorius@601 televizorius
    daug             ok                                           A2-0186@201 daug
    reklamos         target
S-0035   @ 778 Paukštis {skrenda} danguje.
    paukštis         ok                                           004_paukstis@541 paukštis
    skrenda          target (sentence card: the audit still counts it as a dependency)
    skrenda          ok                                           369_skristi@478 skrìsti
    danguje          ok                                           301_dangus@375 dangus
A2-1973  @ 783 Tai įdomus {faktas}.
    tai              ok                                           514_tai@57 tai, A2-0896@233 Kas tai?, A2-0904@412 Ką tai reiškia?
    įdomus           ok                                           A2-0524@290 įdomus
    faktas           target
A2-1593  @ 835 Koncertas bus didelėje {salėje}.
    koncertas        ok                                           A2-0812@834 koncertas
    bus              ok                                           A2-0378@69 Kur yra…?, A2-0360@99 Nėra už ką, A2-0194@106 būti
    didelėje         ok                                           452_didelis@9 didelis
    salėje           target
A2-0500  @ 873 {Lankau} draugą ligoninėje.
    lankau           target
    draugą           ok                                           104_draugas@16 draugas
    ligoninėje       ok                                           048_ligonine@49 ligoninė
A2-1887  @ 880 Tai {asmeninis} klausimas.
    tai              ok                                           514_tai@57 tai, A2-0896@233 Kas tai?, A2-0904@412 Ką tai reiškia?
    asmeninis        target
    klausimas        ok                                           A2-0803@320 klausimas
A2-1694  @1067 {Pietaujame} pirmą valandą.
    pietaujame       target
    pirmą            ok                                           A2-0072@118 pirmas
    valandą          ok                                           A2-1193@286 Kuri valanda?, A2-0379@363 Kiek valandų?, A2-0002@377 valanda
A2-1881  @1078 Mano {mėgstamiausias} gėrimas — kava.
    mano             ok                                           510_as@31 aš, A2-0118@113 mano, A2-0365@136 Man gerai
    mėgstamiausias   target
    gėrimas          ok                                           179_gerimas@357 gėrimas
    kava             ok                                           172_kava@14 kava, A2-0917@867 Norėčiau kavos, A2-2007@1077 Vieną kavą, prašau.

after the plan: 0 A1 word uses depend on an A2-only card (0 cards)

RESULT: OK — residual A1→A2 dependencies 0
```

Simulated rebuild (scratch copy, plan applied, `--report`):

```
==== new study_order_sim.csv: 2433 positioned cards (1191 A1, 1242 A2; 55 sentences) ====
blocks: 0 A1 cards positioned after the first A2 card
dependencies: 1979 word uses in reading cards point at a deck card; 6 point FORWARD (> 20 later: 6, > 50 later: 4); 0 of them are A1 cards needing a word taught only in A2; 92 uses of words no card teaches (86 distinct)
  forward dependencies (card @pos: word <- teaching card @pos):
    A2-0804  @  285 A1 atsakymas    teisingas  <- A2-0539  teisingas    A1 @796
    A2-1532  @ 1314 A2 kelių policija  sustabdė  <- A2-1964  sustabdyti   A2 @1630
    A2-0123  @  237 A1 jūsų         numeris    <- A2-1561  numeris      A1 @526
    A2-1661  @ 2128 A2 neišlaikyti egzamino  neišlaikė <- A2-1949  neišlaikyti (egzamino) A2 @2188
    A2-1093  @  294 A1 bet kas      padaryti   <- A2-1672  padaryti     A1 @340
    A2-0159  @  171 A1 kad          manau      <- A2-1656  manyti       A1 @196
pairs: 0 PIN_AFTER not adjacent []; 0 FF adjective pairs not adjacent []; 0 noted pairs not adjacent []; 0 pairs split across subdecks []
```
