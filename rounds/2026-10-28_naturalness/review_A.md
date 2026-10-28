# Naturalness review, packet A (A1, 504 rows) — Fable, 2026-10-28

Rubric: `RUBRIC.md`. Data: `review_A.csv` (one row per packet row, same order). No data file was changed.

## Counts

| verdict | rows | of which recorded |
|---|---|---|
| keep | 473 | — |
| change | 25 | 21 (3 of them change the English only, so **18 re-takes**) |
| owner | 6 | 3 |

Every proposed sentence was checked against `data/study_order.csv` with the lemma logic of `build_study_order_v3.py`
(a scratch copy of its `build_dependencies` / `sentence_tokens`): each word is taught by an earlier A1 card or is the
target. The existing packet was scanned the same way; the dependency problems it has are listed at the end.

## The changes, in order of importance

1. **0327 `per` "too"** — `Einame {per} tiltą.` → `Kava {per} karšta.` The card teaches the adverb *per* ("too") but
   reuses 0192's sentence, which shows the preposition ("across"). The learner never sees the sense. Recorded.
2. **0469 `po` "after"** — `Katė miega {po} stalu.` → `{Po} darbo einu namo.` Same defect: the card teaches *po* +
   genitive ("after") but reuses 0406's "under" sentence. Recorded.
3. **0525 `arba`** — `Arbatos {arba} kavos?` → `Ateik šiandien {arba} rytoj.` In an alternative question Lithuanian uses
   *ar* (the deck's own 0140 has it right: *Ko norite, arbatos ar kavos?*); *arba* in a question reads as translated.
   *Arba* belongs in a statement or an imperative. Recorded.
4. **0856** — `Duona kainuoja vieną litą.` → `… vieną eurą.` The litas ended on 1 January 2015
   (https://www.ecb.europa.eu/euro/changeover/lithuania/html/index.en.html). Not recorded.
5. **0340 `padaryti`** — `Ką {padaryti}?` → `Ką tu {padarei}?` Nobody says *Ką padaryti?*; the idiom is *Ką daryti?*
   (imperfective). *Ką padarei?* is natural and shows the aspect contrast against 0307 *Ką darai?*. Recorded.
6. **0778 phrase** — `Galiu truputį kalbėti` → `Truputį kalbu lietuviškai.` A calque of "I can speak a little", and
   incomplete; the stock beginner line is *Truputį / šiek tiek kalbu lietuviškai*. Phrase card: headword changes with
   it. Recorded.
7. **1006 `užsiėmimas`** — `Mėgstu {užsiėmimus} lauke.` → `Šiandien turiu du {užsiėmimus}.` "Outdoor activities" is an
   English pattern; in speech *užsiėmimas* is a class or session. The gloss order on the card should follow (retarget
   note). Not recorded.
8. **0285 `atsakymas`** — `Teisingas {atsakymas}!` → `Nežinau {atsakymo}.` *teisingas* is taught 511 cards later (the
   audit's biggest forward dependency in A1). The replacement is natural and models the genitive of negation. Recorded.
9. **0162 `jai`** — `Padovanojau {jai} gėlių.` → `Aš {jai} padedu.` Natural as it stands, but *padovanoti* is taught by
   no card; *padėti* is card 78. Recorded.
10. **0237 `jūsų`** — `Koks {jūsų} telefono numeris?` → `Ar tai {jūsų} knyga?` *numeris* is taught 291 cards later, and
    the phone-number question is already carried by phrase 0236 and card 0526. Recorded.

The remaining changes: dependency fixes with equally natural sentences (0392 *Jis vėl vėluoja*, 0524 *Prieš darbą
geriu kavą*, 0981 *Jos vyras – vokietis*, 1186 *Mano pomėgis – muzika*, 0294 *Tai supranta bet kas*, 0171 *Gerai,
kad esi namie*); small stiffness fixes (0261 and 0394 drop the counted-out *vieną* in favour of *jau valandą / jau
mėnesį*; 0581 *Ar toli stotis?*; 0583 *Kur galiu gauti informacijos?*; 0569 accusative *Arbatą be cukraus, prašau*
when ordering; 0214 the introduction phrase without its bracketed *(yra)* and dangling *tai…*); and three English-only
fixes (0535 "however sunny" → "but sunny"; 0768 "Good luck on the trip" → "Have a good trip!"; 0043 drop "please").

Confidence is marked per row. The medium-confidence changes (0171, 0237, 0294, 0261, 0394, 0581, 0583, 0569, 0214,
1006, 0981, 1186) are improvements, not corrections: the lead may keep any of them if a re-take is not worth it.

## Rows for the owner (6)

- **0148** `Mano vardas {yra} Jonas.` — textbook and understood, but in speech the copula is dropped (*Mano vardas
  Jonas*, already 0384 and 1149) or one says *Aš (esu) Jonas*. The card's point is *yra*. Keep for the copula, or
  change to `Aš {esu} Jonas.`? Recorded.
- **0239** `Kokie šiandien {orai}?` — said, but the everyday question is *Koks šiandien oras?*; plural *orai* leans
  towards forecasts. A change is a retarget of the headword (*oras* is already modelled by 0358 and 0559). Recorded.
- **0759** `Per televizorių daug {reklamos}.` — both *per televiziją / per televizorių* and *daug reklamos / reklamų*
  are heard. Fine as is; the owner picks the register. Not recorded.
- **0795** `{Naudoju} žodyną.` — with a dictionary the idiomatic verb is reflexive *naudotis* + instrumental
  (*naudojuosi žodynu*); transitive *naudoju žodyną* is correct but less idiomatic. Keeping the target *naudoti* means
  an object that takes it naturally, e.g. `Cukraus {nenaudoju}.` Not recorded.
- **0966** `Iki greito! / Iki vėliau!` — both common in speech; *Iki vėliau* is sometimes called a calque of "see you
  later". I could not read a VLKK ruling (unverified). Teach both, or *Iki greito pasimatymo!* only? Not recorded.
- **1169** `Greitai pasveik!` — used, but the more frequent well-wish is *Sveik! / Greitai sveik!* (omniglot's phrase
  list refused the fetch; unverified). Recorded.

## Systematic observations

- **Two cards reuse another card's sentence and so never show their own sense** (0327 *per* "too", 0469 *po* "after").
  Worth a build check: a cloze card whose sentence is byte-identical to another card's sentence while the glosses
  differ. The 2026-10-20 "parse artefact" lesson is the same family (displayed fields not scanned before a build).
- **Counted-out durations**: *jau vieną valandą*, *vieną mėnesį* — the natural frame is *jau valandą / jau mėnesį*
  (or *visą valandą*). Only two A1 rows; worth a glance in B/C.
- **Explicit subject pronouns everywhere** (*Ar tu kalbi…*, *Aš tave myliu*, *Aš jį matau*). Natives drop them unless
  contrasting; at A1 this is a deliberate teaching choice and I did not touch it, but the deck should not drift into
  modelling them as obligatory in A2.
- **Alternative questions take *ar*, statements take *arba***. 0140 has it right, 0525 had it wrong; check B/C for
  *arba* in questions.
- **Dependency gaps hide behind prefixes and derivations**: the lemmatiser does not see *pavėlavo* ← *vėluoti*,
  *pažiūrėk* ← *žiūrėti*, *neinu* ← *eiti*, *mažesnis* ← *mažas*, *žinomas* ← *žinoti*, *žinau* ← *žinoti*. Real gaps
  in A1 (no card teaches the word): *padovanoti* (0162, fixed above), *kartas* (0348 *Iki kito karto!*), *nusiplauti*
  and *valgis* (0524, fixed), *linkėti* (0631 *Linkiu sėkmės!*), *pirkinys* (0782), *vyresnis* (0916), *ištekėti*
  (0981, fixed), *žvejyba* (1186, fixed). The four I left are fixed phrases or the best collocation; strict alternatives
  are in the CSV's reason column.
- **Duplicates for the lead** (not naturalness): 0869 `{Sėkmės}!` duplicates phrase 0755 `Sėkmės!`; sėkmė is a card
  three times (0631 success, 0869 luck, 0755 phrase). 0106/0127, 0104/0360, 0204/0284, 0194/0303, 0247/0248/0558,
  0251/0595 are cloze cards and sentence cards sharing one sentence — by design, noted only.
- **Typography**: 1083 uses an em dash "—" where the deck uses "–"; several phrase headwords are lower-case
  (*dėkui, atrodo, aišku, gaila, nemokamai, noriu gerti, atidaryta, labai gerai*).
- **Politeness overlap**: the service-encounter rows (0137, 0191, 0198, 0203, 0521, 0565, 0602, 0616, 0902, 0949,
  0449, 0569) are natural as they stand; I agree with *norėčiau* for 0616 and either case for 0569 if the politeness
  review proposes them, and see no reason to move the cards whose point is the plain present form.

## Evidence notes

Most verdicts are native-speaker judgement (the rubric expects this; the owner is the final native check). Read and
cited: ECB changeover page (euro, 0856); lituanistika.lt abstract on *ar* vs *arba* (0525); kaikki.org entry for *ar*.
Refused or unreachable, so marked unverified: omniglot "get well soon" list (robots), ekalba.lt and kaikki.org entries
I had no provenance for (*ar*, *užsiėmimas*), en.wiktionary *naudoti* (not found). No refused fetch was retried.
