# Proposed additions from the English A1–A2 benchmark (Fable, 2026-10-17 — proposal, nothing implemented)

Files in this folder:
- `proposed_additions.csv` — **183 proposed new notes** (69 PHRASE, 63 CLOZE, 43 IMG, 8 SENT pattern cards).
- `proposed_deferrals.csv` — **82 items** of ours that English lists rate B1/B2 or omit, one-line reason each; about half are "owner call" (picturable, daily), the rest go to a B1 pack.
- `gloss_alignments.csv` — **67 English headwords we already hold under another gloss** (e.g. Oxford *supermarket* = our *prekybos centras*, *another* = *kitas*, *decision* = *sprendimas*). No new card; add the English as an alternative gloss so coverage counts and search works. This alone lifts measured coverage of Oxford A2 from 57% to roughly 64%.

## Entry rule applied
A word enters if it is on an English A1/A2 list (Oxford 3000 A1/A2 or Cambridge Key) **and** its Lithuanian lemma is in the VU A1/A2 lexicon or the PERLSI top 3000. Phrases enter by communicative function (Waystage/Threshold checklist in `gaps_phrases.csv`), not by headword.

Result by rule: 55 meet the rule (`entry_rule = meets rule`), 61 are function phrases, **67 are English-only** (daily-life words absent from both Lithuanian lists: tėtis, mama, marškinėliai, žadintuvas, morka, gitara…) and need an owner yes/no each. Confidence: 56 high, 60 medium, 67 low. Everything is marked; `source` gives the VU/PERLSI evidence or "unverified".

## What the owner must verify
- Every `lithuanian_TARGET` (my lemma choice), the gender/gen_sg and pres3/past3 fields (from memory, **unverified** — no Wiktionary/DLKŽ lookups were run this round; the executor should run the existing wikt/kirtis pipeline on the accepted rows).
- `tu_jus`: phrases with a slash carry both forms; the owner decides which form is the card and which goes on the back.
- Aspect partners given where obvious (spėti/atspėti, jungtis/prisijungti); many left blank.
- 10 rows flagged `merge` or `skip-if-present` in notes were removed or kept only where the sense is new (e.g. *priklausyti nuo* = depend, beside *priklausyti* = belong; *dar* = else beside *dar* = still).

## Expected cost
- Images: 43 IMG + 69 PHRASE = **112 renders ≈ $1.51** at $0.0135, plus ~40% re-rolls ≈ **$2.1**, plus QA vision pass (~$0.01/image) ≈ $1.5. Total under **$4**.
- CLOZE and SENT rows need no image (71 rows); SENT rows reuse a picture if one fits.
- Audio: 183 new notes ≈ 183 word takes + ~130 example/phrase takes ≈ **~310 takes ≈ 40–50 minutes** of the owner's recording time at the current pace, plus the 67 gloss alignments need no audio.
- Executor time: lemma verification pipeline ~1 hour; staging lines exist in `subject_phrase_EN`; builder run as for the rest of A2.

## Order
1. Owner ticks/crosses the 67 English-only rows and the 82 deferrals (one pass, ~30 minutes).
2. Executor applies `gloss_alignments.csv` (text only, no images) and runs stress/gender verification on accepted additions.
3. Additions are generated **after** the bubble re-staging (see `../RESTAGE_PROPOSAL.md`), under the new no-bubble grammar, so no phrase is drawn twice.
