# Naturalness review — second check after the owner's answers (Fable, 2026-10-28)

**Plan only.** Nothing in `data/`, the recorder or the package was changed. The table ready to apply is
`final_v1.csv` (75 rows: 67 EDIT, 6 RETARGET, 2 NEW_CARD; 22 of them have a recorded take and become re-takes).
Inputs: `merged_v1.json` (the 79 rows the owner saw), `owner_answers/*.json`, `review_A/B/C.md`,
`../2026-10-28_politeness/PROPOSAL.md`. Page defaults applied as the owner was told: "change" group unanswered =
proposal; "call" / "own" groups unanswered = keep; a note overrides the default. Six rows stay as they are (owner
chose keep: 0148, 0171, 1426, 1487, 2204, 2234).

Every final sentence was run through `build_study_order_v3.py`'s own lemma logic (`intro_forms` / `introducers`,
simplemma) against `data/study_order.csv`, and against every other sentence in `data/a2_wordlist.csv` and
`data/sentences/sentences.csv` for identical text. Stress for retargets comes from the English Wiktionary dump
(kaikki, `…/scratchpad/kaikki/lt.jsonl`, fetched 2026-10-28); what the dump does not have is marked UNSOURCED
in `extra_fields` and goes to the owner.

## The owner's notes, resolved

**0340 padaryti** — "Ką daryti? is a classic line … less a question and more of a 'what can you do?'. Consider two
cards." Agreed, and nothing in the deck teaches it (0307 is *Ką darai?*, the verb). Resolution: a **new phrase card
`2434_ka_daryti` "Ką daryti?"** = "What can you do? (resigned shrug; also: what should I do?)", scheduled straight
after 0340 (A1; *ką* @99, *daryti* @307, so A1-clean; pron Ką̃ darýti? from the two words' sourced prons). The
padaryti card itself takes review A's **"Ką tu {padarei}?"** / "What have you done?", the perfective partner of
*Ką darai?*; the old "Ką padaryti?" is not said. Recorded → re-take.

**0759 reklama** — his wording "Per televiziją daug reklamų". The plural genitive is applied: **"Per televizorių
daug {reklamų}."** / "There are a lot of adverts on TV." *Televiziją* is not: *televizija* is card 1779 (A2,
@1779) and 0759 is A1 @746, so his sentence would make an A1 card need an A2 word (the audit's zero-tolerance
rule). *Per televizorių* is said just as much (review A). Not recorded.

**0966 Iki greito!** — applied as written: headword and example **"Iki greito!"**, English "See you soon!",
pron *Ikì greĩto!* (from the present pron). *Iki vėliau!* is dropped. Not recorded.

**1169 Sveik!** — applied as written: **"Sveik!"** / **"Get well! (to someone who is ill)"**. The English carries
the meaning, as asked. Usage check: the imperative of *sveikti* is the base of every variant (*Sveik!*, *Greitai
sveik!*, *Sveik greičiau!* — the last is what lt.speaklanguages.com gives for "Get well soon!",
https://lt.speaklanguages.com/angl%C5%B3/fraz%C4%97s/sveikata; omniglot's phrase page was refused, robots). One
thing for the owner to weigh, not a question: a learner meets **0088 Sveiki** (hello) at @88 and **0232 sveikas**;
"Sveik!" one letter away may be confused with the greeting, which "Greitai sveik!" would avoid. The pron
*Sveĩk!* is UNSOURCED (the dump has no *sveikti*; card 1277 has *sveĩkti* from the kirtis.info engine): owner to
tick. Recorded → re-take. RETARGET (the lemma changes from *pasveikti* to *sveikti*).

**1237 darbo vieta** — he chose "Naujoje {darbo vietoje} man patinka." and asked that *dirbu centre* be taught.
*dirba/dirbu + locative of place* is already taught (0146 *Jis dirba ligoninėje* @146, 0824 *Jo žmona dirba
ligoninėje*, 0769, 1492 *Dirbu didelėje įmonėje*), but the literal *dirbu centre* is nowhere. Rather than split
1237, it goes into the A1 card he had just approved for a smaller change: **0394 mėnuo → "Dirbu centre jau
{mėnesį}."** / "I have been working in the centre for a month already." (*centras* 0216 @216; keeps review A's
*jau mėnesį*, drops the counted *vieną*). 1237 stays as he chose. If the lead would rather keep review A's "Čia
dirbu jau mėnesį.", nothing else depends on this. 0394 is recorded either way → re-take.

**1270 panelė** — applied as written: **"Atsiprašau, {panele}!"** / "Excuse me, miss!". Review B's register note
(the vocative is dated towards younger women) stands on record; the owner, a native, keeps the card. Not recorded.

**1399 tvarka** — he chose "Kambaryje {tvarka}." but hears "Kambarys tvarkingas". That instinct says the elliptical
noun sentence is not what he would say of a tidy room; *tvarkingas* is its own card (2025, 626 positions later),
so it cannot carry 1399. Keeping the noun, the everyday sentence is **"Mėgstu {tvarką}."** / "I like order
(tidiness)." — short, unmarked, and it shows the accusative. "Viskas tvarkoje" stays out (review B: the
non-standard adverbialised locative, https://mokslai.lietuviuzodynas.lt/lietuviu-kalba/linksniu-vartojimo-klaidos
§4.6); "Pas mus tvarka" was considered and is no better than the room sentence. The gloss "order (sequence)" fitted
neither the old nor the new sentence → **"order; tidiness"** (gloss edit, same headword). This overturns the
sentence he ticked; his note asked for it. Not recorded.

**1414 priklausyti** — applied as written: **"Viskas {priklauso} nuo tavęs."** / "Everything depends on you."
This ends the word-for-word duplicate with 1354 *Tai priklauso nuo oro.*; 1592 *Ar eisi? – Priklauso nuo oro.* is a
different sentence (phrase card for the one-word answer). Two cards still carry the headword *priklausyti* (1354,
1414) — he chose the sentence route over a merge, so that is recorded, not reopened. Not recorded.

**1514 eismas** — his note "spūstys" says that for heavy traffic in the centre he thinks of traffic jams, not
*eismas* at all; the reviewer's *didelis eismas* did not appear in any traffic page read. *Eismas* is the word of
signs and news: LRT, 2026 — "eismas centre apribotas", "Eismas minėtoje gatvėje laikinai uždarytas", "dėl eismo
įvykio … laikinai uždarytas eismas abiem kryptimis"
(https://www.lrt.lt/naujienos/eismas/7/3007208/vilniuje-automobilis-rezesi-i-stotele-ir-suzalojo-dvi-moteris-eismas-centre-apribotas);
JUDU/Reidas: "eismo intensyvumas", "nestrigti spūstyse"
(https://reidasofficial.lt/eismas/eismas-pries-kaledas-sostineje-kaip-mieste-judeti-saugiau-ir-nestrigti-spustyse/).
So 1514 gets its own register: **"Dėl avarijos {eismas} uždarytas."** / "Because of an accident the road is closed
to traffic." (*dėl* 0315, *avarija* 1231, *uždarytas* 0555 — all earlier). *Spūstis* is not a card and should be
one: **new `2435_spustis` "Centre {spūstys}."** / "There are traffic jams in the centre.", gloss "traffic jam", F,
after 1514. Its stress is UNSOURCED (not in the dump): headword, genitive and the plural go to the owner.

**1533 skonis** — "check elsewhere, not 100 % sure." Found: zodynas.lt, entry *skonis*, aesthetic sense, example
"Jis turi gerą skonį drabužiams rinktis" (https://www.zodynas.lt/terminu-zodynas/S/skonis). The collocation holds;
**"Ji turi gerą {skonį}."** / "She has good taste." is applied. (ekalba.lt's BŽ entry was refused — not read; web
searches for the exact string returned only noise.)

**1955 lėtai** — condition "if *prašom kalbėti lėčiau* is elsewhere": it is, phrase **0203 "Prašom kalbėti lėčiau"**
(A1 @203). So the politeness proposal is applied: **"Kalbėkite {lėtai}, prašau."** / "Speak slowly, please."

**2175 rezervuoti** — his alternate applied: **"Norėčiau {rezervuoti} staliuką."** / "I would like to book a
table." *Staliukas* is taught at 1482 (@1482, before 2175) and survives 1482's own change to *laisvų staliukų*
(simplemma: staliukų → staliukas). No duplicate with phrase 2194 any more.

**2422 puslitris** — "I've never heard this; *bokalas* is the term I most often hear at the bar." His experience
decides: **RETARGET to `bokalas`** — "{Bokalą} alaus, prašau." / "A mug of beer, please.", gloss "beer mug; a
(mug of) beer", pron **bokãlas** (stress pattern 2), gen. **bokãlo** — both from the Wiktionary dump ("mug, jug
(chiefly for drinking beer)"). A second reason not to teach *puslitris* as "half a litre": colloquially it is the
half-litre bottle of spirits. "Half a litre" itself is not lost to the deck's needs (*pusė* 1195, *pusė
kilogramo* 2035 model the measure). *Alus* 0026 @26. Key and slug `2422_puslitris` stay (slugs are never
re-derived).

**0043 atsiprašau and 0535 tačiau** — "I don't see the options being compared" / "Comparison and alternate are
the same?" Right: these two change only the English line, which the page did not show. In one sentence each:
- 0043: English **"Excuse me, please…" → "Excuse me…"** ('please' is not in the Lithuanian). Lithuanian unchanged, no re-take.
- 0535: English **"It was cold, however sunny." → "It was cold, but sunny."** Lithuanian unchanged, no re-take.
Both applied, as he chose the proposal. (Four more rows are English-only in the same way and were ticked without
comment: 0768 "Have a good trip!", 1706 "…to the centre?", 2015 "gimnazija (upper secondary school)", 2265 "Happy
Easter!".)

## Second check of everything else

**Naturalness.** All 73 final sentences re-read as "what a native says here, to this person". Nothing else is
overturned. Two I weighed and left: 1745 "Pigu, bet, {kita vertus}, toli." (*bet, kita vertus* is a frequent
spoken string; the two-sentence "Pigu. Kita vertus, toli." is no better) and 1501 "Veikiantis liftas – kairėje."
(sign register, which is where the participle lives; the owner chose it over a merge into 1324).

**Dependencies.** Every A1 row uses only words taught by an earlier A1 card or its own target: 0 forward, 0
A2-only (the *televiziją* case above was caught here). A2 rows: every supporting word is taught earlier. Words the
checker cannot assign are all the card's own cloze form or a phrase-internal word the builder never resolved before
either (`nenaudoju`, `jaučiu`, `nudegiau`, `bokalą`, `spūstys` = the target; `praleiskite` in 2147, `praėjimo` in
1968, `sveik` in 1169 = inside a phrase card, which the builder does not audit; `suvalgiau` in 2247 = prefixed
*valgyti*, same as before the round). No new word enters a reading card unannounced.

**Duplicates.** None of the 75 final sentences (nor the two new cards) matches any other card's sentence. The
round removes three identical pairs (0406/0469 *po*, 0192/0327 *per*, 1354/1414 *priklausyti*). **34 identical
pairs remain deck-wide, all pre-existing**, for the lead: 2128/2188 *Jis neišlaikė egzamino* (known); 0043/0103
*Atsiprašau* (two phrase cards, "Excuse me…" / "I'm sorry"); and 32 pairs where a phrase, cloze or sentence card was built on purpose on
another card's line (0318 *Neturiu laiko* / 0253; 0137 *Ar galite man padėti* / 0191; 0161 *Noriu valgyti* /
0637; 0248 *Man reikia pagalbos* / 0247 / 0558; 0240 / 0275; 1239 / 1727; 0922 / 1252; 0459 / 0264; 1247 / 0187;
1908 / 1973; 0360 / 0104; 0132 / 1398; 0058 / 1278; 0143 / 1235; 0755 / 0869; 0521 / 1653; 0408 / 0601; 1012 /
0208; 0707 / 0157; 0595 / 0251; 0887 / 0260; 1193 / 0602; 0902 / 1819; 2297 / 1895; 1029 / 1112; 0630 / 1894; 0728 /
1659; 0229 / 1776; 0204 / 0284; 0347 / 0855; 0194 / 0303; 0106 / 0127). The lesson's rule ("no two cards share a
sentence") needs a decision on whether a phrase card and the cloze on the same sentence are exempt; the build check
it asks for would flag all 34. Not acted on here.

**English.** Checked line by line; one adjusted beyond the reviews: 1482 "Ar yra laisvų staliukų?" → "Are there
any free tables?" (plural, as the Lithuanian now is).

**Retargets (6)**, each with headword, gloss, stress and forms in `extra_fields`:
- 0239 *orai* → **oras** "weather (also: air)", óras (3), gen. óro — Wiktionary dump. The owner chose "Koks
  šiandien {oras}?", so the headword follows the cloze lemma; 1200 *oras* "air" keeps its card (961 positions
  apart; the deck already has *per*, *po*, *prieš*, *iki* twice each).
- 2422 *puslitris* → **bokalas** (above).
- 1589 *naudotis* → **pasinaudoti** "to use, make use of (perf. of naudotis; +instr.)". He chose the politeness
  sentence "Ar galiu {pasinaudoti} telefonu?"; review B had flagged that its cloze lemma is not the headword, so the
  headword follows and *naudotis* stays visible in the gloss. Stress UNSOURCED (not in the dump) → owner. If he
  would rather keep *naudotis*, review B's "Nemoku {naudotis} šiuo telefonu." is the sentence.
- 1968 *vieta prie tako* → **vieta prie praėjimo** (aisle seat; picture unaffected). Pron UNSOURCED → owner.
- 0778 *Galiu truputį kalbėti* → **Truputį kalbu lietuviškai.** Pron: trupùtį and lietùviškai sourced, *kalbù*
  UNSOURCED → owner.
- 1169 *Greitai pasveik!* → **Sveik!** (above).

Gloss edits on the same headword (EDIT rows, see `extra_fields`): 1006 "class, session (also: activity,
pastime)", 1733 "unhealthy", 1852 "missing; lost", 1399 "order; tidiness". Phrase headword edits: 0214, 0966,
1243 "Minutėlę!", 1482, 1793, 2147.

## Still for the owner (stress marks only; no decisions pending)

Five forms the Wiktionary dump does not have, to tick or correct on the stress sheet when the round is applied:
*Sveĩk!* (1169), *kalbù* in 0778, *pasinaudoti* (1589 headword), *praėjimas* in 1968, and the new *spūstis*
(headword, genitive, plural). Everything else in this round is decided.

## Not done, by rule

Refused fetches, not retried: ekalba.lt BŽ *skonis* (provenance); omniglot get-well page (robots). The LESSONS
file changed on disk while this check ran (another agent); it was not touched here.
