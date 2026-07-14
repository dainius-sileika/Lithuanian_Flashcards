# Lietuvių Flashcards

A ~429-card Lithuanian vocabulary flashcard deck, illustrated in the deadpan style
of a 1980s Soviet civil-defense training manual ("Grazhdanskaya Oborona"). Each
card pairs a Lithuanian target word with a guessable illustration plus supporting
insets; the vocabulary lives in a companion CSV for the Anki layer (no text is
baked into the art).

**Author:** Dainius Sileika
**License:** [CC BY-NC 4.0](LICENSE) — free for non-commercial use with attribution and a link back.

## What's here
| Path | What |
|------|------|
| `go_generator.py` | The GO image engine (style, palette, prompt assembly). Backend: OpenAI gpt-image-1.5. |
| `go_grammars.py` | Per-category visual grammars (the executable design bible). |
| `deck_builder.py` | Production runner: reads `master_wordlist.csv`, routes every row, stages per-card overrides. |
| `driver.py` | Batch/parallel runner; merges into `out_deck/`. Resumable. |
| `verb_flashcards.py`, `noun_flashcards.py` | Verb staging / noun demo helpers. |
| `master_wordlist.csv` | The wordlist (v2.5) — 429 generable rows. |
| `images/` | The 429 finished cards as compressed **WebP** (1536×1024, ~101 MB). This is the distributed set. |
| `out_deck/ledger.csv`, `out_deck/cards.csv` | Per-card prompts (ledger) and Anki fields (cards). |
| `out_deck/*.png` | Full-resolution PNG masters — kept **local only**, not committed (regenerate from code). |
| `GO_STYLE_SPEC_files_1_7_1.md` | Canonical art spec + full changelog. |
| `files_1_7_DIFF.md`, `files_1_7_1_DIFF.md` | Per-release sign-off diffs. |
| `VERSIONS.md` | Version index (current: files 1.7.2 / wordlist 2.5). |
| `deprecated/` | Frozen older versions for rollback. |

## Regenerating
```bash
pip3 install openai
export OPENAI_API_KEY=sk-...
python3 driver.py <Category> [N] [budget_seconds]     # e.g. python3 driver.py Verbs 5 40
python3 driver.py --reroll key1,key2 [N] [budget]     # re-roll specific cards
```

## Status
Deck complete: 429/429 cards generated and QA'd under files 1.7.2 / wordlist 2.5.

## Attribution
> "Lietuvių Flashcards" by Dainius Sileika, licensed under CC BY-NC 4.0.
> Source: https://github.com/dainius-sileika/Lithuanian_Flashcards
