# Naturalness review, packet B (A2 rows 1–430) — Fable, 2026-10-28

Rows: 430 (study positions 1192–1812; none recorded yet). Verdicts: **keep 403 · change 25 · owner 2**.
Full table: `review_B.csv` (one row per packet row; `reason` is empty-"keep" where nothing was worth saying).

## What was checked
Every row against the rubric's seven questions. Evidence was sought only where a source can settle a point;
the rest is marked "native-speaker judgement". Two web checks landed:

- *tvarkoje* ("Viskas tvarkoje") is on the standard list of non-standard adverbialised locatives, replacement
  "Viskas gerai / Tvarka" — https://mokslai.lietuviuzodynas.lt/lietuviu-kalba/linksniu-vartojimo-klaidos (§4.6).
- *ryte* beside *rytą* for time is accepted — https://kaisiadorys.lt/valstybine-kalba/konsultacijos/gramatika-ir-zodynas/1932
  (entry 2026-09-02 "Vietininkas ir laikas"), so 1288 "rytoj ryte" stays.
- Three searches for restaurant-phrase frequency ("Ar yra laisvų staliukų" vs "laisvas staliukas") returned nothing
  usable; that row is a judgement call (medium) and overlaps the politeness review.

Dependencies: all 430 sentences were run through `build_study_order_v3.py`'s own `build_dependencies()` (simplemma
lemmas, headwords + listed forms, ne- transparency). Words no card teaches are in `a1_dependency_ok` as
"info:" — 18 rows, listed below. Every proposed sentence uses only words taught before its position.

## The changes that matter most (current → proposed)
1. **1399 tvarka** — "Viskas tvarkoje." → "Kambaryje {tvarka}." The one sentence with a documented norm problem
   (Russian locative calque). Ubiquitous in speech, but not what the deck should model.
2. **1467 galvos skausmas** — "Turiu galvos skausmą." → "Ar turite vaistų nuo {galvos skausmo}?" English calque;
   the native sentence is already card 1357 "Man skauda galvą".
3. **1589 naudotis** — "Galiu {pasinaudoti} telefonu?" → "Nemoku {naudotis} šiuo telefonu." The cloze shows a
   different lemma from the headword; the request form, if wanted, is its own card.
4. **1255 galimas** — "Ar tai {galima}?" → "Rytoj {galimas} lietus." Current sentence means "is it allowed?" and
   repeats card 1225 verbatim.
5. **1243 minutėlė** — "minutėlė" → "Minutėlę!" The phrase people say is the accusative.
6. **1501 veikiantis** — "Liftas veikiantis." → "Veikiantis liftas – kairėje." Nobody uses the participle as a
   predicate (that is 1324 "Liftas neveikia"); or retarget/merge into 1324.
7. **1733 nesveikas** — "Jis nesveikas." → "Tai {nesveikas} maistas." Of a person it is heard as "he's not right
   in the head"; gloss to "unhealthy".
8. **1466 Sutinku** — "– Eime į kiną? – Sutinku." → "– Per brangu. – {Sutinku}." Nobody accepts a cinema invitation
   with "Sutinku".
9. **1786 sunkiai** — "Jis sunkiai dirba." → "Senelis {sunkiai} vaikšto." The gloss is "with difficulty"; "sunkiai
   dirba" means heavy work, and English "works hard" is "daug dirba".
10. **1793 Eime į kavinę!** — "Gal eikime į kavinę?" → "Gal einam į kavinę?" The spoken suggestion form.

The remaining 15 changes are collocation/register nudges (medium confidence): 1237 darbo vieta, 1367 greitis order,
1378 pasiekti register, 1410 word order, 1482 partitive genitive, 1498 dalyvauti collocation, 1503 prie jūros,
1514 eismas register, 1533 skonis, 1581 viešas collocation, 1687 mada idiom, 1706 English only, 1709 jausti,
1745 kita vertus (low), 1812 pašalinti collocation.

## "owner" rows
- **1270 panelė** — "Panele, atsiprašau!" Addressing a stranger as *panele* is heard, but increasingly dated and can
  land as patronising with younger women; many would say just "Atsiprašau!". Also the natural order is
  "Atsiprašau, panele!". Native call: keep the vocative use, reorder, or teach *panelė* as a plain noun.
- **1414 priklausyti (nuo)** — identical sentence and gloss to card **1354 priklausyti** ("Tai {priklauso} nuo oro.").
  Not a language question: merge, or give one of them a different sentence ("Viskas {priklauso} nuo tavęs.").

## Systematic observations
- **Fragments as sentences** ("Didelė suma.", "Sunki padėtis.", "Gera kokybė.", "Geras skonis!"): fine when they
  are what people say as a chunk; 1533 was the one that is not.
- **Predicate participles.** Two rows use a participle where Lithuanian uses the verb (1501 *veikiantis*; 1453
  *atidarytas* and 1696 *padarytas* are fine, those are genuine states).
- **English order creeping in**: 1367 "Koks greitis leidžiamas?", 1410 "Draugas skambina man", 1687 "Tai dabar
  mada". Small but worth a sweep in packet C too.
- **Calques of English "have"**: 1467 "turiu galvos skausmą" (1735 "turi garantiją" is shop-speak but genuinely
  current — kept).
- **Near-duplicate sentences across cards** (not errors, but the lead should know): 1239 = 1727 (same sentence),
  1354 = 1414 (same sentence and target), 1357/1515 (skauda galvą), 1248/1468 (Paimk/Pasiimk skėtį — a good
  contrast), 1555/1637 (du kartus per parą/dieną), 1644/1797 (vidury/viduryje kambario — also a good contrast),
  1351/1756 (draudžiama).
- **Gloss mismatches** flagged in `reason` without changing the sentence: 1630 sustabdyti ("to prevent" is wrong),
  1575 registracija (gloss says appointment, sentence shows event registration), 1733 (handled above).
- **Untaught words in current sentences** (information, 18 rows): nesimatėme (1291), sėsk (1323; *sėstis* is
  taught), švietimo (1332), griežtas (1344), sesė (1377; *sesuo* is taught), vidurdienį (1378), menkos (1381),
  kabo (1391), mokytoja (1458, 1787; feminine of taught *mokytojas*), ligonius/ligonį (1510, 1702; *pacientas*
  is taught at A1), intensyvus (1514), tekstą (1534), pasinaudoti (1589), kartą (1598), įvyko (1697, 1719),
  drebėjo (1713), nebėra (1768; transparent). Taught later: sustabdė in 1314 (card 1630). Proposed sentences
  remove four of these (vidurdienį, intensyvus, pasinaudoti, and the 1414 duplicate).
- **Typography**: 1508 uses an em dash "—"; everything else uses "–".
- The lemmatiser's own false alarms (nepyk, nespėju, sutvarkyk, jaučiu, vizitą — forms of the row's target) were
  removed from the information column by hand; `build_dependencies()` already skips them in the real audit because
  the target is in the card's intro forms.
