# Naturalness review, packet C (A2 rows 431–751) — Fable, 2026-10-28

Rows: 321 (A2, study positions 1813–2431, including the three A2 sentence cards). None recorded yet.
Verdicts: **keep 307 · change 12 · owner 2**. Full detail in `review_C.csv`.

Method: every row read against the rubric question (would a native say exactly this, here, to this person?).
Supporting words were checked against the deck's taught forms with the lemma logic of `build_study_order_v3.py`
(`intro_forms` / `introducers`); A2 rows have no A1 constraint, so untaught and forward words are listed as
information in `a1_dependency_ok`. Where a claim rested on more than judgement I searched; what I could not read
is marked "unverified". One fetch was refused (VLKK consultation bank) and not retried.

## The changes (12)

| key | current → proposed | why |
|---|---|---|
| 1968_vieta_prie_tako | vieta prie tako → **vieta prie praėjimo** | *takas* is a footpath; airlines say *prie praėjimo* (airBaltic LT: "vietų prie lango … ir prie praėjimo"). Picture of an aisle seat unaffected. |
| 2247_ketvirtadalis | Ketvirtadalis valandos. → **Suvalgiau {ketvirtadalį} pyrago.** | time uses *ketvirtis* (ketvirtis valandos, be ketvirčio penkios), never *ketvirtadalis*. |
| 1824_iskart | Ateik {iškart}. → **{Iškart} supratau.** | *iškart* = "straight away (after something)": *iškart supratau*; the command is *Ateik tuoj pat*. |
| 1834_interneto_svetaine | Žiūrėk mūsų {interneto svetainėje}. → **Daugiau informacijos rasite mūsų {interneto svetainėje}.** | calque of "look on our website"; this is the stock Lithuanian line. |
| 2345_nudegti | {Nudegiau} ranką. → **{Nudegiau} saulėje.** | *nudegti* is first of all sunburn; a burnt hand is *nusideginau ranką*. |
| 2422_puslitris | {Puslitrį} pieno, prašau. → **{Puslitrį} alaus, prašau.** | *puslitris* is the bar / bottle measure; milk is *pusę litro pieno*. |
| 2215_klaidingai | Parašei {klaidingai}. → **Tu mane {klaidingai} supratai.** | *klaidingai* pairs with *suprasti / manyti*; a misspelling is *neteisingai parašei*. |
| 2039_tiksliai | Nežinau {tiksliai}. → **{Tiksliai} nežinau.** | the idiomatic order (like *Tikrai nežinau*). |
| 2200_plansete | Vaikas žaidžia žaidimus {planšetėje}. → **Vaikas žaidžia {planšete}.** | *žaisti planšete / telefonu* (instrumental) is what parents say; the long form is redundant. |
| 1852_dinges | Mano piniginė {dingo}. → **Ieškau {dingusio} šuns.** | retarget: the card teaches the adjective *dingęs*, the cloze shows the verb *dingo*, and *dingti* is already card 1389. Or merge into 1389. |
| 2015_gimnazija | English only → **My son is at gimnazija (upper secondary school).** | "gymnasium" is a sports hall to an English reader. |
| 2265_linksmu_velyku | English only → **Happy Easter!** | *Linksmų Velykų* is Easter only; "happy holidays" is *Linksmų švenčių* (0841). |

Confidence: high for 1968, 2247, 1834, 2015, 2265; medium for the rest (judgement calls a native will settle in a second).

## Owner decisions (2)

**2204_dalintis — `{Dalinamės} kambariu.`** The normative verb is *dalytis* (dalijasi, dalijosi); *dalintis* is the
everyday variant most speakers actually use. Both the headword and the cloze use the variant. Since the deck's
stated aim is "the best and most natural, and correct" Lithuanian, this is a policy call: teach *dalytis /
Dalijamės kambariu* (normative; a learner will still hear *dalinamės* everywhere) or keep *dalintis* (what is
said). I could not read VLKK's consultation on it (fetch refused — `https://www.vlkk.lt/konsultacijos?search=dalintis`);
my recollection that DLKŽ cross-refers *dalintis → dalytis* is unverified. Proposed: *Dalijamės kambariu* if the
headword changes to *dalytis*; otherwise keep.

**2147_gero_poilsio — `Gero poilsio! / Smagiai praleisti laiką!`** The second half is a bare-infinitive wish, an
ellipsis of *Linkiu smagiai praleisti laiką*. On its own, people say the imperative *Smagiai praleiskite laiką!* or
a genitive wish (*Smagaus vakaro! / Smagaus savaitgalio!*). Searching found no usage evidence either way, so this
goes to the native speaker. Proposed: *Gero poilsio! / Smagiai praleiskite laiką!* Phrase card; the picture shows
the situation and is unaffected either way.

## Rows marked "see politeness" (checked against `rounds/2026-10-28_politeness/proposals.csv`)

1819, 1858, 1926, 1976, 2108, 2136, 2171, 2175, 2185, 2234, 2245, 2290. Agree with its keeps (1819, 1976).
Two of its changes create word-for-word duplicates inside this packet:

- **2175** *Noriu {rezervuoti} kambarį* → *Norėčiau {rezervuoti} kambarį*: right register, but phrase 2194 is
  already *Norėčiau rezervuoti kambarį*. If accepted, re-sentence one (e.g. *Norėčiau {rezervuoti} staliuką dviem*).
- **2234** *Galiu {pasimatuoti}?* → *Ar galiu {pasimatuoti}?* — **disagree**: phrase 2290 is already *Ar galiu
  pasimatuoti?*. *Galiu pasimatuoti?* is natural shop speech (politeness itself cites Hilbig dropping *Ar*), and
  politeness kept 1976 as the spoken variant beside 1225 for exactly this reason. Keep 2234 as it is.

2108 *Ar galite mus nufotografuoti?* is fine to a stranger as it stands; *Ar galėtumėte* is softer, not required.

## Sentence cards (3)

1995 *Traukinys {išvažiuoja} devintą valandą.*, 2037 *Naktį {šviečia} mėnulis.*, 2230 *Mes {mokomės} lietuvių
kalbos.* — all keep; nothing in them conflicts with the pictures described in `sentences.csv`. (Station
announcements say *išvyksta*; *išvažiuoja* is what people say, and it is the taught verb.)

## Counter-hypotheses tested

- 2206 *Rudenį {deginame} lapus.* — I suspected the sentence teaches an illegal act. Checked: burning raked
  leaves is permitted under conditions (alkas.lt 2023-09-16: "leidžiama deginti tik surinktas (sugrėbtas) į
  krūvas"). Keep.
- 1968 — checked that *prie praėjimo* is the airline term rather than my own preference (airBaltic LT page read).
- 2247 — checked that *ketvirtis* is the time word (linguapedia telling-time page read: *ketvirtis po dešimtos*,
  *be ketvirčio penkios*).

## Systematic observations

1. **Identical sentences on two cards.** 2128/2188 *Jis neišlaikė egzamino* (only the brace span differs — a true
   duplicate, flagged in both rows); 1908/1973 *Rytoj laikau egzaminą*; 1895/2297 *Domiuosi istorija*;
   2234/2290 *(Ar) galiu pasimatuoti?*; 2175/2194 *Noriu / Norėčiau rezervuoti kambarį*; 1888/2018/1915 three
   appointment-with-the-doctor cards; 2331/2334 *Reikia rezervuoti / registruotis iš anksto*. Where the second
   card is a "pattern" card this may be deliberate; 2128/2188 is not, and should be merged or re-sentenced.
2. **Headword ≠ cloze lemma.** 1852 *dingęs* → *dingo*; 2395 *taisyklinga* (adj.) → *taisyklingai* (adv.);
   1854 *jungti* → *įjunk*; 1864 *skirtis* → *išsiskyrė*; 2201 *gerinti* → *pagerinti*; 2352 *skolintis* →
   *pasiskolinti*; 2382 *skolinti* → *paskolink*; 2216 *kopijuoti* → *nukopijuokite*; 2363 *šlapti* → *sušlapsi*.
   The prefixed perfectives are the natural forms (keep them), but the dependency lemmatiser does not resolve
   them, so these appear as "untaught" in audits. Only 1852 changes the part of speech.
3. **Comparative vs plain adverb in requests.** 1887 *aiškiai*, 1898 *tyliai*, 1955 *lėtai*: in each situation a
   native would more often use the comparative (*tyliau, lėčiau, aiškiau*). The plain forms are the taught words
   and the sentences pass, but the owner may want a back-note on 1898/1955 pointing to the comparative.
4. **Untaught supporting words (information only, A2):** *užmigti* (1984), *atgal* (2177), *įrašyti, failas*
   (2335), *vaikystė* (2405), *branda* in *brandos atestatas* (2355), *mašina* as "car" (1873; *automobilis* is
   taught). Prefixed forms of taught verbs: *nusiplauti, atsiųsti, pakabinti, pažiūrėti, sudėti, sugesti*.
   Forward dependencies: 2092 *pakabink* (kabinti @2219), 2415 *šaldiklyje* (šaldiklis @2428), 2128 ↔ 2188.
5. **Typography.** 2071 uses an em dash (—); every other row uses the en dash (–).
6. **English register is good throughout**; only 2015 and 2265 needed a fix. 2297's "(instrumental)" and 2359's
   "(object first)" are grammar notes inside the English line — fine if that is the convention for pattern cards.

## Evidence URLs read

- https://www.airbaltic.com/lt/vieto-uzsakymas (seat names)
- https://linguapedia.info/en/lithuanian/phrases/telling-time (*ketvirtis*)
- https://www.tv3.lt/zodynas/terminu-zodynas/I/iskart (*iškart* entry)
- https://alkas.lt/2023/09/16/kaip-teisingai-tvarkyti-zaliasias-atliekas (leaf burning)

Refused / not read: https://www.vlkk.lt/konsultacijos?search=dalintis (provenance refusal; final);
europa.eu and continental-tires.com/lt search hits for *Daugiau informacijos rasite mūsų interneto svetainėje*
(not read; the line is marked native-speaker judgement).
