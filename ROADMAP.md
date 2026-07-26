# Roadmap — from the 520-card base to A2

**Target: CEFR A2 Lithuanian.** This document is the plan of record: what the deck
covers now, what A2 additionally requires, how we get there, and the non-vocabulary
work that has to land alongside it.

Companion files:
- **`wordlist_a2_pending.csv`** — the queue of words, phrases and grammar items,
  one row per proposed card, phased and deduplicated against the existing deck.
- **`accents_todo_kirtis.csv`** — the 195 words whose stress no automated source
  carries; fill `accented_form_FILL_ME` from [kirtis.info](https://kirtis.info)
  and they merge straight back into the queue.

---

## 1. Where we are

520 cards, complete and QA'd through five owner rounds, each with an illustration,
audio and a stress-accented headword.

The base is a *Fluent Forever 625*-style concrete vocabulary: things you can
photograph. Coverage by type:

| type | count |
|------|------:|
| nouns | 362 |
| verbs | 86 |
| adjectives | 74 |
| pronouns | 8 |

**This is roughly an A1 concrete core — and it has a specific, systematic hole.**
An audit of the wordlist found the deck contains **zero** of the following:

- numbers (no *vienas, du, dešimt, šimtas*)
- days, months, seasons, or clock/calendar words (no *diena, savaitė, metai, valanda*)
- question words (no *kas, kur, kada, kaip, kodėl, kiek*)
- prepositions (no *į, iš, su, ant, prie, be, po*)
- conjunctions (no *ir, bet, arba, nes, kad, jei*)
- adverbs (no *labai, dažnai, visada, niekada, jau, dar, tik*)
- possessives (no *mano, tavo, jo, jos, mūsų*)
- core modal verbs (no *būti, turėti, galėti, norėti, reikėti*)
- greetings and everyday formulas (no *labas, ačiū, prašau, atsiprašau*)

Also missing at the concrete level: *vardas, telefonas, parduotuvė, oras,
pusryčiai/pietūs/vakarienė, rytas/vakaras/naktis*.

That absence is not an oversight in the original list — it is a direct consequence
of the method. The picture rule ("no text in the art; infer the word from the image
alone") works beautifully for *šuo* and badly for *nes*.

## 2. What A2 actually requires

A2 is not "more nouns". It is the level at which a learner handles routine
exchanges: describing the past and future, asking and answering, expressing need
and preference, and getting through shops, travel, appointments and small talk.

Published estimates vary widely, but A2 is commonly put at **1,500–2,500 words**
(one survey: "at A2 learners should understand between 1,500 and 2,500 words";
another gives A1 500–1,000 and A2 1,000–2,000). **We target ~2,000.** The deck
supplies ~520 of those — but more importantly, size is not the real problem:
A2 needs **function words, phrases and grammar**, which is exactly the hole above.

**So the honest conclusion: reaching A2 requires a second card type.** The image
card cannot teach *although* or *+genitive*. This is the same conclusion Fluent
Forever reaches — pictures for concrete vocabulary, then **sentence/cloze cards**
for grammar and abstractions.

## 3. Phased plan

`wordlist_a2_pending.csv` holds **984 proposed rows** (845 net new; 139 flagged as
already covered or duplicated within the queue). Projected deck: **~1,365 cards.**

| phase | what | rows | card type | images? |
|-------|------|-----:|-----------|---------|
| **P-A** | A1 completion — time, calendar, numbers, missing everyday nouns | 107 | image | yes (numerals/day names via `card_text`) |
| **P-B** | Function words — question words, prepositions, conjunctions, adverbs, possessives, modals | 101 | sentence | no |
| **P-C** | A2 topical — travel, health, work, shopping, home, feelings, technology, society | 139 | image | yes |
| **P-D** | Phrases — greetings, politeness, getting by | 39 | phrase | no |
| **P-E** | Grammar patterns — the 7 cases, tenses, reflexives, comparatives | 16 | pattern | no |
| **P-F** | Vocabulary expansion — 200 verbs/adjectives, 300+ nouns across every domain | 476 | image | yes |
| **P-G** | Phrases & sentences for **both levels** — A1 survival formulas and core sentence patterns, A2 discourse, transactions and extended patterns | 106 | phrase / sentence | no |

**722 of the 984 rows are marked `image_possible = yes`** and can go straight
through the existing engine. The remaining 262 are the function words, phrases,
sentences and grammar patterns that need the new note types.

**Honest gap:** this queue lands at ~1,365 cards, not 2,000. That is a solid A2
core covering every high-frequency domain; closing the last ~600 to the top of
the cited range wants a **frequency-list pass** (phase P-H) rather than more
hand-authoring, so the additions are driven by real corpus frequency instead of
intuition. Recommended only once P-A…P-G are generated and in use.

### Sequencing

1. **Phase A first.** It is picturable, uses the engine exactly as it stands, and
   removes the most embarrassing gaps (a learner cannot count or say "Monday").
2. **Phase C next**, for the same reason — pure content, no new machinery.
3. **Phase B and D require the new card types.** Build the sentence/phrase note
   type once, then both phases are data entry.
4. **Phase E last** — it is reference material, most useful once the learner has
   enough vocabulary to apply it.

### Per-phase definition of done

- Lithuanian target verified by a native speaker (every row currently says
  `LT proposed — verify`).
- Stress accent sourced (Wiktionary → kirtis.info), validated by the stress-strip
  rule, never invented. **Status: done for the queue** — 634 of 829 single-word
  rows (76%) carry a sourced accent; the remaining **195 are listed in
  `accents_todo_kirtis.csv`** for manual lookup, because neither English nor
  Lithuanian Wiktionary has them.
- Grammar forms filled: genitive for nouns, principal parts for verbs, feminine
  for adjectives.
- Audio generated.
- Images generated and QA'd against the guessability gate (Phases A, C).
- `build_recorder.py` re-run so the recorder stays in step.
- Changelog entry + version bump.


### Accent sources: what was tested (2026-07-25)

Evaluated for automating the remaining stress marks. Recorded here so the
dead ends are not re-litigated.

| resource | verdict |
|----------|---------|
| **English Wiktionary** (wikitext `head=`, rendered headword) | **In use.** Supplied 630 of the queue's accents. |
| **Lithuanian Wiktionary** | **In use, marginal.** Added 7 words over the whole run. |
| **Kaikki.org / wiktextract** | **No value for our gap.** It is a re-extraction of the same Wiktionary. Sampled 25 of the 195 misses: 19 have no Wiktionary page at all, and the 6 that do render *unstressed* headwords even with full template expansion. The data is absent, not merely hard to extract. Would be useful later purely as an offline bulk lookup for a large pass (avoids ~800 rate-limited API calls). |
| **phonology_engine** (rule-based accentuation, VDU/LIEPA lineage) | **Best candidate, currently unrunnable.** Algorithmic, so it covers out-of-vocabulary and inflected forms — exactly our failure mode. But it ships **x86_64 Linux + Windows binaries only**: no aarch64, no macOS, no sdist on PyPI, and the GitHub repo ships the same prebuilt binary (build fails). Needs an amd64 Linux environment (Docker `--platform linux/amd64`). Worth standing up before the P-H frequency pass, not for 195 words. |
| **Hunspell LT** (`.dic`/`.aff`) | **Does not carry stress.** Encodes morphology and inflection only; useful for lemmatisation and generating inflected forms, not accents. |
| **LIEPA engine / neural stress taggers** | **Projects, not tools.** LIEPA has real stressing internals but needs compiling from C/C++; the neural work is research-stage with no downloadable model. |

**Standing rule:** any engine-derived accent is a *candidate for verification*,
never truth. Rule-based accentuation errs on homographs and irregular paradigms,
and a confidently wrong stress mark is worse for a learner than a blank one.

## 4. Engine work required

**New note type: sentence/cloze cards** (Phases B, D). Front = a short Lithuanian
sentence with the target word blanked; back = the full sentence, the word, its
gloss and audio. Needs: a template, a `sentences` column in the data, and a build
path in `build_apkg.py`. This is the single biggest technical item on the roadmap.

**`TEXT_EXCEPTION` for numerals** (Phase A) — the mechanism already exists (used
for `m`, `cm`, `in`, `ABC/123`, `A E I O U`); numbers just need rows added.

**Calendar and season staging** (Phase A) — days and months are near-impossible to
disambiguate visually. Likely approach: a calendar page with the day/month
position marked, using the text exception for the numeral only.

**Pattern cards** (Phase E) — a reference layout: the rule, a worked example, and
a small paradigm table, in the house style.

## 5. Non-vocabulary work

Independent of A2, these are outstanding:

1. **Human audio.** The current audio is Azure neural; its Lithuanian word stress
   is unreliable, and no cloud engine (Azure, Google, ElevenLabs) accepts phoneme
   overrides for `lt-LT` — this was tested and confirmed. `recorder.html` is built
   and current, ready for a native speaker (or the owner) to record one clip per
   card. **This is the highest-value single improvement to the deck.**
2. **Native verification of the rule-derived forms.** Glosses and verb principal
   parts are owner-confirmed; the bulk noun genitives and adjective feminines are
   rule-derived and still want a spot-check.
3. **Pre-1.7.1 image backlog.** ~105 of the earliest cards (#1–231) had their
   insets generated under the old "worker" dress default, before the civilian rule.
   They are serviceable but stylistically inconsistent with the rest.
4. **Weak cards.** #440 dėvėti (wear) still reads closer to "protective gear".
5. **Distribution.** The `.apkg` is ~170 MB, too large to attach automatically to a
   GitHub Release. Options: a phone-sized build (downscaled images, ~40–50 MB), or
   manual upload each release. AnkiWeb listing text lives in
   `ANKIWEB_DESCRIPTION.md`.
6. **Card direction.** Every card is currently recognition-only
   (image → word). Production practice (EN → LT, or typed answer) would need a
   second template — worth deciding before the deck grows to 900.

## 6. Decisions taken

- **Target ~2,000 words** (the queue delivers ~1,365; a frequency pass closes the rest).
- **A1/A2 split: subdecks + tags.** `Lietuvių Flashcards::A1` and `::A2`, plus an
  `A1`/`A2` tag on every note. Studying the parent deck studies everything;
  clicking a subdeck studies one level; tags keep custom filtered decks possible.
  The existing 520 are already tagged (**427 A1 / 93 A2** — the abstract round and
  the measurement/meta-linguistic cards are A2; auto-assigned, worth a review).
- **Text on cards: only where undepictable.** Generalised from a hardcoded table
  into a `card_text` column on the wordlist — any row may now name exactly what
  lettering it may show (a day name on a calendar page, a numeral, a unit mark),
  and everything else stays wordless. This is what makes days, months and numbers
  generable at all.
- **Sentences: generic model sentences**, authored with a grammar note explaining
  the pattern (case government, impersonal constructions, negation-takes-genitive).

## 7. Open decisions

- **Drop or keep the 26 flagged duplicates** in `wordlist_a2_pending.csv`
  (`status = review-duplicate`). Some are genuine collisions; a few are arguably
  distinct senses (*sąskaita* = restaurant bill vs bank account; *kaina* = price
  vs cost).
- **Sentence cards: whose sentences?** Fluent Forever recommends personal,
  memorable sentences over generic ones. Generic can be authored quickly;
  personal ones are better learning but need the owner to write them.
- **Numbers: how far?** The list stops at *milijonas* with ordinals to *penktas*.
  A2 arguably needs ordinals to ~20 for dates.
- **Do phrases need images?** Currently specified as text+audio. A GO-style
  illustration for *"Kiek kainuoja?"* is possible but expensive and may add little.

## 8. Milestones

| milestone | deck size | gate |
|-----------|----------:|------|
| **M1** — Phase A generated and QA'd | ~625 | numbers/calendar legible |
| **M2** — Phase C generated and QA'd | ~765 | guessability gate passes |
| **M3** — sentence note type shipped; Phase B + D loaded | ~905 | cloze cards render with audio on desktop + mobile |
| **M4** — Phase E pattern cards | ~920 | — |
| **M5** — human audio replaces synthesized | ~920 | full re-record, deck rebuild |
| **A2 release** | ~920 | native verification complete; version 2.0 |
