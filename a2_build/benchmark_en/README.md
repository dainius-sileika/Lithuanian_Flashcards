# English A1–A2 benchmark for the deck (Fable, 2026-10-17)

Owner's question: instead of reconstructing an A1–A2 inventory from the thin Lithuanian side, compare what we have with a validated English A1–A2 word and phrase list.

This folder holds the comparison, not the lists. Nothing here is generated into cards; it is a checklist for the owner and the executor.

## 1. Candidate lists and what they are

| List | Maker, validation | Contents | Access / licence | Used here |
|---|---|---|---|---|
| **Oxford 3000 by CEFR level** (2019 edition) | OUP; frequency in the Oxford English Corpus (>2 bn words) weighted by frequency in OUP coursebooks; built with James Milton, reviewed by Paul Nation; "every word is aligned to the CEFR" (method not published on the page) | 3,000 headwords with POS and CEFR level A1–B2; by our parse 900 A1, 867 A2, 810 B1, 729 B2 (a headword can appear at two levels with different POS) | Free PDF download (© Oxford University Press; no explicit reuse licence on the PDF). We store only the gap subset (headword + level), not the list. | **Yes — primary word benchmark** |
| **Cambridge A2 Key / Key for Schools Vocabulary List** (Aug 2025) | Cambridge English (UCLES); "drew on vocabulary from the Council of Europe's Waystage (1990) specification and other vocabulary which corpus evidence shows is high frequency"; updated against the Cambridge Learner Corpus (44 m words) and the English Vocabulary Profile | ~1,686 entries (our parse) with POS, example sentences constraining senses, phrasal verbs, Appendix 1 word sets (days, months, numbers), Appendix 2 topic lists; receptive + productive; A1 and A2 together, not separated | Free PDF (© UCLES 2025). Same storage rule: gap subset only. | **Yes — phrase/multiword and A2 benchmark** |
| **English Vocabulary Profile** (Cambridge) | Cambridge University Press + Cambridge English; Cambridge Learner Corpus; CEFR level per *word sense*, phrase, phrasal verb and idiom, A1–C2 | The most fine-grained list in existence (senses and phrases at level) | Online search only after registration; "available to all for a limited time for free after registration" (Wikipedia; the site itself has moved to a JS app and returned 404 for its list pages this session). No bulk download; terms not readable this session → treat as **not redistributable** | No (unreachable as data). Recommended for spot checks of individual senses by the owner. |
| **Council of Europe Waystage 1990 / Threshold 1990** (van Ek & Trim) | The canonical functional-notional specification behind A2/B1; expert-built, not corpus-validated; the Key list and EVP both descend from it | Language functions (6 categories: factual information, attitudes, suasion, socialising, discourse, repair), general and specific notions, with recommended exponents | Books (CUP, © Council of Europe). Waystage not accessible online; Threshold 1990 PDF is hosted by EALTA. We store only our own function checklist, no exponents. | **Yes — function checklist** (Threshold inventory, restricted to A2-relevant functions) |
| **Pearson GSE Vocabulary** | Pearson; GSE scale 10–90 mapped to CEFR; teacher-rated plus corpus | Words and phrases with GSE value | Online Teacher Toolkit; no bulk download seen; terms not checked [unverified] | No |
| **Kelly project** (Kilgarriff et al. 2014) | 9 languages (Arabic, Chinese, English, Greek, Italian, Norwegian, Polish, Russian, Swedish); 9,000 most frequent lemmas per language, CEFR bands by frequency rank, cross-translated | Frequency lists with CEFR bands | CC BY-SA 4.0 (per the UiO Text Laboratory page). No Baltic language; CEFR bands are frequency cut-offs, not learner-validated | No (no Baltic list; frequency-only banding adds nothing over our Lithuanian 3000 list) |
| Profile Deutsch, Référentiel A1/A2 (French) | Goethe-Institut / Didier; expert function–notion inventories for German and French | Functions, notions, grammar, word lists | Paid books/CD-ROM | No; the Threshold functions cover the same ground |

Verdict on the owner's premise: he is right. The English side has three mutually reinforcing, learner-corpus-validated lists (Oxford 3000, Key list, EVP), all descended from the Waystage/Threshold functional inventory. Lithuanian has the VU A1/A2 lexicon (1,606 entries, expert-built from Lūžis and Pusiaukelė) and the PERLSI 3000 frequency list, neither of which carries phrases or functions.

## 2. Method

- Our side: `master_wordlist.csv` `english` (531 rows incl. batonas) + `a2_build/a2_wordlist.csv` `english` (1,709 rows) = 2,240 glosses.
- Normalisation: lower-case; split on `/`, `;`, commas; parentheticals used as extra variants; `to`/`a`/`the` stripped; crude singularisation; British↔American spelling map; accent stripping; a synonym map for cases where we chose a different English headword for the same Lithuanian word (start→begin, photo→photograph, tv→television, quick→fast, nearly→almost, mum/dad→mother/father only for *matching*, see gaps for why mama/tėtis still count).
- A list word counts as covered if any of our glosses matches it after normalisation. This is headword matching, not sense matching: "point", "case", "mind" count as covered if we have any sense. The error runs both ways and is small at A1, larger at A2.
- Scripts live in the scratchpad, not the repo; they are 150 lines of Python and are reproducible from the two PDFs named above.

## 3. Coverage (`coverage.csv`)

| English list | Covered by our 2,240 glosses |
|---|---|
| Oxford 3000 **A1** (900 headwords) | **770 = 85.6%** |
| Oxford 3000 **A2** (867) | **493 = 56.9%** |
| Cambridge **A2 Key** list (1,686, A1+A2 together) | **1,144 = 67.9%** |

Our items by Oxford level: A1 master — 321 A1, 133 A2, 35 B1, 13 B2, 29 not in Oxford 3000. A2 list — 638 A1, 288 A2, 98 B1, 39 B2, 646 not in Oxford 3000 (of which ~195 are phrases/sentences and ~250 are concrete nouns from the VU lexicon: trolleybus, kefir, cepelinai, amber, prescription, embassy, pavement…).

Reading: the A1 side is sound. The A2 side is where we built from the Lithuanian list and it shows: we hold only 57% of Oxford's A2 headwords, and the missing 43% is dominated by abstract and relational vocabulary (ability, decision, opinion, reason, advantage, opportunity, support, depend, expect, suppose, mind, worried, lucky, sure, available), adverbs (actually, certainly, instead, nearly, recently, mostly, normally), reflexives (myself, yourself, themselves) and quantifiers (few, most, another, several, neither).

## 4. Gaps (`gaps_words.csv`, `gaps_phrases.csv`)

`gaps_words.csv`: 711 single-word gaps, ranked. Priority: **P1** = Oxford A1 and in the Key list (60 after removing grammar-only items); **P2** = Oxford A1, or Oxford A2 and in Key (128); **P3** = Oxford A2 only or Key only (439); suffix `-skip` = not a lexical gap in Lithuanian (articles, *of*, verb particles *up/down/out/off*, gerunds, items we hold as compounds); suffix `-defer` = EFL-classroom metalanguage (paragraph, dialogue, chart, blog, spelling, essay…) or Anglophone sport/culture (baseball, golf, penny, mile). The `note` column carries a suggested Lithuanian for most P1/P2 items — **suggestions, unverified, for the owner to confirm**.

P1 highlights (all A1 in Oxford and in the Key list): another (kitas), few (keli), most (dauguma), else (dar), yourself (pats/save), everybody/somebody (visi / kas nors), easy/difficult (lengvas/sunkus), funny, sunny, favourite (mėgstamiausias), thirsty (noriu gerti), tonight (šįvakar), midnight, century (amžius), supermarket (prekybos centras), t-shirt (marškinėliai), picture (paveikslas), pair (pora), front (priekis/priešais), capital (sostinė), event (renginys), group (grupė), activity (veikla), conversation (pokalbis), carrot (morka), guitar, piano, desk, class, girlfriend (draugė/mergina), mama and tėtis (we have motina/tėvas only — the child-register words are the ones actually used), should/could/would as productive patterns (reikėtų, galėčiau, norėčiau — partly present in sentences).

`gaps_phrases.csv` has two kinds of rows:
- **function** rows: 37 Waystage/Threshold functions relevant at A2, each marked have / partial / missing with our Lithuanian. Missing or partial: introducing someone else (Čia yra… / Susipažinkite), offering help (Kuo galiu padėti?), suggesting (Gal eikime…? / Susitikime…), declining an offer politely (Ačiū, ne / Deja, negaliu), dislike and preference (Man nepatinka; Man labiau patinka), generic permission (Ar galima? / Galima), asking someone to spell (Kaip rašoma?), asking whether understood (Ar suprantate?), telephone routine (Ar galėčiau kalbėti su…? / Palaukite minutėlę), personal details (telephone number, address), physical states (thirsty, tired, I'm cold/hot). Everything else in the inventory — greetings, leave-taking, thanks, apologies, wishes, requests, assistance, directions, time, shopping, travel, health, emergencies, opinion, repair — we have.
- **multiword** rows: 89 Key-list multiword items we lack (a few, all right, as well, at all, each other, no one, in front of, close to, come back, get up/grow up/pick up/turn on/turn off/wash up, get married, good afternoon, pardon, first name, credit card, swimming pool, city centre, dining room, alarm clock, stomach ache…). Several are English-specific (phrasal verbs that are single Lithuanian verbs: turn on = įjungti, which we have); the executor should check each against the Lithuanian before adding.

## 5. What we have that the English lists put above A2 or omit (`defer_candidates.csv`)

592 rows: our items at Oxford B1/B2 (A1 master 48; A2 list 137) or absent from Oxford 3000 and the Key list (A1 master 29; A2 list 378). Do **not** read this as a cut list. Three groups:

1. Fluent Forever 625 words that English lists rate B1/B2: wing, court, priest, religion, heaven/hell, marriage, murder, election, poison, contract, seed, ceiling, needle, tongue, toe, soil, root, leaf, sand, clay, copper, wound, pray, dig, melt, explode, deaf, blind, shallow, nuclear. These are concrete, picturable and cheap; they sit at B1 in English because of *frequency*, not difficulty. Keep the picturable ones; the deck is a picture deck. Defer the abstract/rare ones (contract, election, nuclear, race ethnicity, sex act) to a later pack.
2. Lithuanian daily-life nouns from the VU A1/A2 lexicon that English lists never needed: trolleybus, kefir, sour cream, cepelinai, stuffed cabbage rolls, amber, embassy, prescription, polyclinic-type items, ticket inspector, pavement, cloakroom, dormitory. These are right for Lithuania and wrong for an English list. Keep.
3. Genuinely B1+ items in the A2 list that came from the frequency list: receipt, discount, therefore, whether, rarely, intend, apparently, occasionally, customs, tax, politics, economy, insurance, loan, debt, truth, safety, profession, exhibition, pregnant, operation, judge, explosion. Candidates to move to a B1 pack (~60–80 items). The owner decides; `keep_reason` column is empty for him.

## 6. Where the English concept does not map one-to-one onto Lithuanian

- **Articles, *of*, particles**: a/an/the have no Lithuanian; *of* is the genitive; *up/down/out/off/away/over* are verb prefixes (iš-, nu-, už-, pa-, per-). We teach these as cloze on endings and prefixed verbs, not as words. Marked `-skip`.
- **Aspect and prefix pairs**: one English verb (to write, to read, to eat) is two or more Lithuanian lemmas (rašyti/parašyti, valgyti/suvalgyti); English lists count one headword, we rightly hold several. Coverage of English verbs therefore understates our verb inventory.
- **Motion verbs**: *go, come, ride, drive, fly, walk* map onto eiti/važiuoti/skristi/vaikščioti and their prefixed forms; the English "ride" gap is really "važiuoti dviračiu / joti".
- **Formal/informal you and imperatives**: *you* is tu/jūs; every request phrase exists twice (Ar gali / Ar galite). English lists have one row; we need the pair, and the Key list's "please" politeness is carried in Lithuanian by the -kite imperative and prašau.
- **Case-governed prepositions**: *in, to, at, from, with* each split by case and by motion vs location (į + acc / -e locative). English prepositions count as covered when we hold any sense; the real learning object is the pattern sentence.
- **Adjective gender and agreement**: one English adjective = two Lithuanian forms; we hold both in one card. Fine.
- **Kinship/child register**: mama/tėtis vs motina/tėvas — English lists have mum/dad at A1 for a reason; add them.
- **Time**: "o'clock", "half past", "quarter to" are different arithmetic in Lithuanian (pusė trijų = 2:30); we have the right phrases, the English headwords look uncovered.
- **Modal verbs**: should/could/would/might/shall/must are morphology (conditional -čiau, reikėtų, galėčiau, turėčiau, privalau) — pattern-sentence material, present in the sentence cards and worth 6–8 more.

## 7. How to combine the three sources

Use the English lists for **communicative need** (what an A2 speaker must be able to do and name), the VU A1/A2 lexicon for **Lithuanian-specific inventory** (what Lithuanian learners are actually examined on), and the PERLSI 3000 frequency list as the **tie-breaker and the B1 fence**:

1. A word enters the A2 deck if it is (Oxford A1/A2 or Key list) **and** (VU lexicon or PERLSI top 3000); phrases enter by function (the 37-row checklist), not by headword.
2. A word that is English A1/A2 but absent from both Lithuanian lists is added only if it names something a resident needs (supermarket, t-shirt, sunny) — a short owner call per item, the P1/P2 notes make the suggestions.
3. A word in the VU lexicon but B1+/absent in English stays if picturable and concrete (group 2 above); otherwise B1 pack.
4. Nothing enters from the English side without a Lithuanian check by the owner: the English headword is a prompt for a Lithuanian decision (which lemma, which aspect, tu/jūs), never a translation request.

Rough size of the resulting additions: ~60 P1 words, ~100 of the P2 words, ~25 function phrases (each tu/jūs where relevant), ~30 multiword items that are single Lithuanian lemmas we lack — about 200–250 new notes, and 60–80 moved to a B1 pack. Net deck size stays near 2,300.

## 8. Files

- `coverage.csv` — the numbers above.
- `gaps_words.csv` — 711 ranked single-word gaps with POS, Oxford level, Key membership, tag, note (suggested Lithuanian, unverified).
- `gaps_phrases.csv` — 37 function rows (have/partial/missing with our Lithuanian) + 89 multiword gaps.
- `defer_candidates.csv` — 592 of our items that English lists rate B1/B2 or omit, with an empty `keep_reason` for the owner.

Licence note: the Oxford and Cambridge PDFs are © OUP / UCLES and carry no redistribution licence; this folder stores only the headwords we *lack* (a derived comparison), not the lists, and the full lists are not committed. EVP data was not accessed. The function checklist is our own wording of the Threshold category headings.

## Sources (read unless marked)

- Oxford 3000 by CEFR level (PDF, OUP): https://www.oxfordlearnersdictionaries.com/external/pdf/wordlists/oxford-3000-5000/The_Oxford_3000_by_CEFR_level.pdf — method page: https://www.oxfordlearnersdictionaries.com/about/wordlists/oxford3000-5000
- Cambridge A2 Key and Key for Schools Vocabulary List, August 2025 (PDF, UCLES): https://www.cambridgeenglish.org/Images/506886-a2-key-2020-vocabulary-list.pdf
- English Profile / English Vocabulary Profile — background via Wikipedia (site pages returned 404 this session): https://en.wikipedia.org/wiki/English_Profile ; https://www.englishprofile.org/ [unverified terms]
- Threshold 1990 (van Ek & Trim, CUP/Council of Europe), PDF hosted by EALTA — language-functions chapter: https://ealta.eu/documents/resources/Threshold-Level_CUP.pdf ; Waystage 1990 on Cambridge Core (not accessible): https://www.cambridge.org/core/books/waystage-1990/language-functions/79EC791F1719FBAD7160F0A9D2FC8E6C [unverified contents]
- Kelly project lists, licence and languages (UiO Text Laboratory): https://hf.uio.no/iln/english/about/organization/text-laboratory/services/kelly.html ; Kilgarriff et al. 2014 paper record: https://repozytorium.amu.edu.pl/handle/10593/10369 [not read]
- Pearson GSE Teacher Toolkit — not accessed this session [unverified]
- VU A1/A2 lexicon (local): `sources/A2_2_lygis_VU_A1A2_lexicon.pdf` (Ramonienė 2016 Pusiaukelė + Stumbrienė 2016 Lūžis); PERLSI 3000: `sources/LT_3000_most_frequent_PERLSI.pdf`
