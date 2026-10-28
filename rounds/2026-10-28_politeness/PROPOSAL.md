# Register of requests: *noriu* / *norėčiau*, *galiu* / *ar galiu*, imperatives (2026-10-28)

**Plan only. Nothing in `data/`, the recorder or the package was changed.** The decisions are in
`proposals.csv` (one row per sentence examined: current, verdict, proposed sentence, evidence, dependency check,
whether a take already exists).

## The owner's question

> "#616, intuitively, I would use 'Norėčiau' vs 'Noriu,' i.e., a future form, like 'J'aimerai' in French, which
> would be more polite. Consider if some of these phrases need to be changed from the present to the future; check
> for idiomatic usage, cross reference from text online to check."

Later the same day: these cards teach more people than the owner, so the standard is **the most natural, correct
Lithuanian**, not the technically correct form; re-recording is accepted.

One terminological note, gently: *norėčiau* is the **conditional** (tariamoji nuosaka), not the future
(*norėsiu*). The French parallel is *j'aimerais* (conditionnel), not *j'aimerai* (futur). The intuition is right;
the label is the only thing to adjust, and the English on the cards says "I would like", which is the conditional.

## Answer on #616

**Change.** `0616_pakeisti` "Noriu {pakeisti} bilietą." → **"Norėčiau {pakeisti} bilietą."** / "I would like to
change the ticket." The target *pakeisti* keeps its braces. A want-statement in the indicative addressed to a clerk
is the *direct* strategy; the ordinary polite form at a counter is the conditional. The same situation in the
50languages Lithuanian course reads "Norėčiau pakeisti užsakymą" (lesson 35, *Oro uoste*). Dependency: *norėčiau*
is taught at `0121_noreciau` (position 121); the card is at 626. Not yet recorded, so no re-take.

The alternative a native would also use at a counter is the impersonal **"Ar galima pakeisti bilietą?"**
(*galima* is taught at `0389` @391). The owner may prefer it; *norėčiau* is proposed because it was his
intuition, and because the deck then teaches one formula for one situation.

## What was examined

Every sentence and phrase in `data/a2_wordlist.csv` (phrase targets; cloze/PAIR `example_lt`),
`data/sentences/sentences.csv` and `data/cards_anki.csv` (no sentences there) that addresses another person or
states a wish: *nori-/norė-*, *gali-/galė-*, *duok/-ite*, *prašau/prašom*, imperatives, *tu/tavo* vs *jūs/jūsų*.
About 230 rows matched the wide grep; 47 are rows where register or naturalness could matter and are listed in
`proposals.csv`; the rest (greetings, *prašau* + noun orders, directions, question-word cards) are sound.

## Verdicts

| verdict | n | keys |
|---|---|---|
| **change** | 5 | 0616_pakeisti, 2175_rezervuoti, 1371_suzinoti, 2234_pasimatuoti, 1589_naudotis |
| **owner's call** | 4 | 1426_paklausti, 1487_pavyzdys, 1955_letai, 0569_be |
| **keep** | 38 | the *noriu* statements of wish or plan, the tu-imperatives between intimates, the jūs-imperatives from authority or in directions, the cards already in *Ar galiu / Ar galite* form |

### Change (5)

| key | now | proposed | why |
|---|---|---|---|
| 0616_pakeisti (A1) | Noriu {pakeisti} bilietą. | **Norėčiau {pakeisti} bilietą.** | customer → clerk; see above |
| 2175_rezervuoti (A2) | Noriu {rezervuoti} kambarį. | **Norėčiau {rezervuoti} kambarį.** | hotel; phrase 2194 already teaches exactly this with *norėčiau*; two registers for one situation would teach the learner that both are equal. Variant if the owner wants variety: *Norėčiau {rezervuoti} staliuką.* |
| 1371_suzinoti (A2) | Noriu {sužinoti} kainą. | **Norėčiau {sužinoti} kainą.** | enquiry to a seller; *Norėčiau sužinoti …* is the stock opener |
| 2234_pasimatuoti (A2) | Galiu {pasimatuoti}? | **Ar galiu {pasimatuoti}?** | shop; matches phrase 2290 and the textbook form |
| 1589_naudotis (A2) | Galiu {pasinaudoti} telefonu? | **Ar galiu {pasinaudoti} telefonu?** | favour asked of a stranger. *Ar galėčiau …* would be the most deferential, but *galėčiau* is taught only at 2245 (after 1589) |

English for the first three becomes "I would like to …"; the last two keep theirs.

### Owner's call (4)

- **1426_paklausti** "Galiu {paklausti}?" — a set phrase, neutral for friends and strangers; the bare form is
  arguably the more natural spoken one. Add *Ar* only if every ability question in the deck should carry it.
- **1487_pavyzdys** "Duok man {pavyzdį}." — natural between peers and from teacher to pupil (Lithuanian requests
  are markedly more direct than English ones: Hilbig 2009). Wrong only if said upward. Keep as peer register, or
  "Ar galite duoti {pavyzdį}?"
- **1955_letai** "Kalbėkite {lėtai}." — not politeness but idiom: when asking someone to slow down natives say
  *lėčiau* (the deck's 0203 *Prašom kalbėti lėčiau*). Bare "Kalbėkite lėtai" is a teacher's instruction. Either
  add ", prašau" or restate where *lėtai* is at home: "Jis kalba {lėtai} ir aiškiai."
- **0569_be** "Arbata {be} cukraus, prašau." — case, not politeness: the deck's other orders use the partitive
  genitive or the accusative (*Negazuoto vandens, prašau*; *Vieną kavą, prašau*; *Man sriubos, prašau*); the
  nominative reads as a menu line. "Arbatos {be} cukraus, prašau" or "Arbatą {be} cukraus, prašau". **Already
  recorded** (`0569_be_s`, batch 16-50): a change is one re-take.

### Keep: the principle

- *Noriu* stays where nobody is being asked: 0161 *{Noriu} valgyti*, 0637, 0940, 0124, 1281, 0259 *Noriu eiti, bet
  neturiu laiko*, 0724 *Aš irgi noriu kavos* (peer), 1333 *Noriu pamatyti jūrą*, 2201, 1940. The VU textbook's
  own key has "Aš noriu važiuoti į Klaipėdą pas mamą."
- Tu-imperatives between intimates stay: 0594 *Parodyk man nuotraukas*, 0350, 0936 *Paduok druską* (the textbook:
  "Mindaugai, paduok cukraus!"), 1464, 1598, 1322, 1844, 1503, 1455; and 2352 *Galiu pasiskolinti tavo knygą?*
  (*tavo* fixes the register; the bare question is what friends say).
- Jūs-imperatives from the service side or an authority stay: 0893 *Parodykite pažymėjimą*, 0590, 1945, 2058,
  1775, 1637, 1887, 1898, and all directions (*Eikite tiesiai*, *Pasukite į dešinę* …). Written requests in
  Lithuanian are overwhelmingly direct (*prašom* + infinitive, imperatives: Aleksaitė 2022).
- 0271 / 0151 *Ar tu kalbi lietuviškai / angliškai?* are the tu counterparts of 1189 / 0125; peers, keep.
- 1976 *Čia {galima} rūkyti?* — adding *Ar* would duplicate 1225 word for word; keep as the spoken variant.

## Evidence

Read in full or in the part quoted; everything else is marked.

1. **Hilbig, Inga (2009). "Lietuvių ir anglų prašymų strategijos ir mandagumas", *Lietuvių kalba* 3, VU.**
   https://www.zurnalai.vu.lt/lietuviu-kalba/article/download/22872/22150/42651 — 100 Lithuanian and 100 English
   students, 12 scenarios. Lithuanian requests: **64.0 % conventionally indirect** (*Galite išrašyti man …?*, *Gal
   galėtumėt …?*), **26.9 % direct** (imperatives, *Prašom / prašau / prašyčiau uždaryti langą*, hedged
   performatives *Norėčiau / norėjau paprašyti …*), 6.6 % hints; English 10.9 % direct. The author argues the
   *Gal galėtumėte …?* type is the most ordinary polite request and therefore neutral, not servile. Two things
   follow for the deck: the polite service request is an ability question or a conditional want (supports the five
   changes), and Lithuanians are three times as direct as the English, so peer-level imperatives and *noriu*
   statements are not rude (supports the 38 keeps and the caution on 1487).
2. **Hilbig (2009), doctoral summary, VU** https://epublications.vu.lt/object/elaba:1946587/ — Lithuanian requests
   show "less consideration of the hearer's freedom", "more directness", positive-politeness orientation. The full
   PDF (`…/elaba:1946649/1946649.pdf`) came back as binary and was **not read**.
3. **Klaas, Birutė (2004). "Conditional mood and politeness in Lithuanian in comparison with Estonian", *Linguistica
   Uralica* 40(4).** https://www.lituanistika.lt/content/74645 — abstract only: the conditional of *prašyti*,
   *norėti* as a politeness device in corpus and parliamentary speech; the article body was not read.
4. **Aleksaitė, Agnė (2022). "Kalbinis mandagumas nekilnojamojo turto skelbimuose: prašymai", *Res humanitariae*
   30.** https://www.lituanistika.lt/content/99465 — 1,000 written requests: 83.1 % explicit performatives
   (*prašome* 61.3 %, *prašau* 36.1 %), 14.1 % imperatives, want-statements 0.2 %, no *ar galėtumėte*-type at all.
   Written instructions are direct; relevant to the jūs-imperative keeps (1945, 2058).
5. **50languages / Goethe-Verlag Lithuanian course** (native-translated phrasebook; moderate weight, but it is the
   same encounters as the deck): lesson 35 *Oro uoste* "Norėčiau pakeisti užsakymą", "Norėčiau užsakyti bilietą į
   Atėnus" https://www.goethe-verlag.com/book2/EN/ENLT/ENLT037.HTM ; lesson 27 *Viešbutyje* "(Aš) norėčiau kambario
   su vonia", "Ar galiu pamatyti kambarį?" https://www.goethe-verlag.com/book2/EN/ENLT/ENLT029.HTM ; lesson 54
   *Pirkiniai* "(Aš) norėčiau pirkti dovaną" (for "I want to buy a present"), "Ar galiu šitą pasižiūrėti?"
   https://goethe-verlag.com/book2/EN/ENLT/ENLT056.HTM ; lesson 73 "Ar galiu kai ko paklausti?", "Ar galiu
   paskambinti?", "Ar čia galima rūkyti?", "Ar galima sumokėti kreditine kortele?"
   https://www.goethe-verlag.com/book2/EM/EMLT/EMLT075.HTM ; lesson 72 renders every "I want to …" with
   *norėčiau* https://www.goethe-verlag.com/book2/EN/ENLT/ENLT072.HTM .
6. **Ramonienė & Vilkienė, *Nė dienos be lietuvių kalbos*, answer key (VU leidyba)**
   https://www.vu.lt/leidyba/images/eknygos/Ne_dienos/Ne_dienos_be_lietuviu_kalbos_Uzduociu_atsakymai.pdf —
   "Mindaugai, paduok cukraus!" (tu-imperative at table), "Aš noriu važiuoti į Klaipėdą pas mamą" (*noriu* for a
   plan). No *norėčiau* in the key.
7. **vocal.ovgu.de Lithuanian travel dialogue, bus station**
   https://vocal.ovgu.de/START+HERE/LITHUANIA/Travel/Dialogues/Bus+station.html — the customer opens "Atsiprašau,
   gal galite pasakyti …?", asks "Kur galima įsigyti autobuso bilietą?", "Kokiu autobusu turėčiau važiuoti …?":
   conditional and ability/possibility questions throughout; no *noriu*. The dialogue index page was refused
   (provenance) and not fetched by another route.
8. **sublearn.com "Galiu paklausti?"** https://sublearn.com/learn/lt/phrases/galiu-paklausti — learner site, weak
   source: calls the bare form neutral for friends and strangers; lists *Norėjau paklausti…* as a softer variant.

**Not obtained.** Corpus counts (DLKT / tekstynas.vdu.lt) were not queried. Exact-string web searches for
"norėčiau pakeisti bilietą" / "noriu pakeisti bilietą" and "norėčiau / noriu sužinoti kainą" returned no dialogue
use of either (airline FAQ pages, price listings); the *noriu* form appears only as FAQ-style self-description,
never addressed to a person. The Masaryk University course pages (`is.muni.cz`, *Nė dienos* dialogue 98-4,
*Drabužiai*) returned an anti-bot script, not content: **unverified**. The VLKK consultation bank was not reached.

**Counter-hypothesis tested.** "Lithuanian is direct; *Noriu pakeisti bilietą* is what people actually say at
the window." Hilbig's numbers give the direct strategy a real share (26.9 %), so the sentence is not wrong; but
within that share the hedged forms (*norėčiau*, *norėjau*) are the ones her informants used toward strangers, and
no course or dialogue source read here puts an indicative *noriu* in a customer's mouth. The counter-hypothesis
does change the answer for the peer-level rows: it is why 1487, 2352 and the tu-imperatives are kept.

## Two things seen on the way (one line each, no proposal)

- Spoken polite requests very often open with **Gal** rather than *Ar* (*Gal galite pasakyti …?*, *Gal
  galėtumėte …?*; Hilbig calls this the most ordinary form). The deck teaches only *Ar*; correct, slightly bookish.
- The past tense as a softener (*Norėjau paklausti…*, Hilbig's *norėjau paprašyti*) is a Lithuanian idiom the deck
  does not show; B1 material.

## Dependency check

Run with the functions of `build_study_order_v3.py` (`load_cards`, `build_dependencies`, `sentence_tokens`)
against `data/study_order.csv` positions, substituting each proposed sentence for the card's `example_lt`
(script in the session scratchpad; results copied into `proposals.csv`). Every word of every proposed sentence is
taught earlier: *norėčiau* ← 0121 @121; *ar* ← 0125 @125; *galiu / galite* ← 0137 @137; *prašau* ← 0032 @32;
*bilietą* ← 0097; *kambarį* ← 0310; *kainą* ← 0041; *telefonu* ← 0056; *duoti* ← 0093. The only A1 change
(0616 @626) needs nothing from A2. Two caveats the audit cannot see: it matches by lemma, so it would also pass
*galėčiau* (← *galėti*) although the conditional form is first shown at 2245 — hence not proposed for 1589; and the
token *pasinaudoti* in 1589 is already "taught by no card" (the headword is *naudotis*), unchanged by this round.

## Recording impact

Of the 5 changes none is recorded (recording has reached about position 600 of A1; 0616 @626 is just past the
front). Of the 4 owner's-call rows one is recorded: `0569_be_s` (`media/audio/0569_be_s.mp3`, batch
`lt_A2_takes_2026-10-28-16-50`), one re-take if the owner changes it. Among the 38 keeps, 12 are recorded and
stay as they are. **Re-takes caused by this proposal as it stands: 0; at most 1.**

## Applying it (for whoever does)

Edit `example_lt` / `example_en` of the five rows in `data/a2_wordlist.csv` (braces stay on the same target),
then `python3 build_study_order_v3.py --audit` (0 A1 cards needing an A2-only word), then the recorder regenerates
(`build_recorder.py A2`), which will list `0616_pakeisti_s` etc. with the new words. No key changes.
