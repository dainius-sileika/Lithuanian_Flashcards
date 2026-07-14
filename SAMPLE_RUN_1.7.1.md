# 1.7.1 validation sample — run locally

A 10-card spread to confirm the 1.7.1 dress + inset changes look right **before**
committing to the big run. Generates into a **separate** `out_sample_1.7.1/`
folder — it does NOT touch your existing `out_deck/` cards, so you can compare
old vs new side by side.

## Run it
```bash
cd ~/Documents/lithuanian_deck_production
pip3 install openai            # only if not already installed
export OPENAI_API_KEY=sk-...   # your key — used from the env, never written to disk by the script

python3 deck_builder.py \
  --only 001_suo,057_kepure,172_kava,182_duona,019_padanga,195_tepalas,232_lubos,236_telefonas,245_irankis,363_dirbti \
  --out out_sample_1.7.1
```
~10 images (a few minutes). Output: `out_sample_1.7.1/*.png` + its own `ledger.csv` / `cards.csv`.

## What each card is testing
| card | test | expect |
|------|------|--------|
| 001 suo (dog) | animal inset dress | person handling it is a **civilian** (was worker) |
| 057 kepurė (hat) | garment | **civilian** wearing it |
| 172 kava (coffee) | beverage | **civilian** drinking it |
| 182 duona (bread) | food | **civilians** with the food |
| 019 padanga (tire) | vehicle | **ordinary people**, not coverall workers |
| 195 tepalas (machine oil) | tool/industry pin | still a **worker/mechanic** ✓ |
| 232 lubos (ceiling) | new Home object | **civilian** if any person |
| 236 telefonas (telephone) | new Home object | **civilian** |
| 245 įrankis (tool) | tool worker override | **worker** ✓ |
| 363 dirbti (to work) | verb path | **worker**; inset-meaning rule applied |

## Compare old vs new (macOS)
```bash
open out_sample_1.7.1/001_suo.png out_deck/001_suo.png     # new vs current
```

## The two things to judge
1. **Dress:** civilians where they should be now; workers only on tepalas / tool / verb.
2. **Insets support the word:** each inset should make the target easier to guess and
   never depict something mistakable for a neighbouring card (the 1.7.1 gate).

## If it looks good → the real run (later)
- Re-roll the 105 dress-flip cards straight into the deck:
  `python3 driver.py --reroll 001_suo,057_kepure,... 6 120`  (batches of 6, 120s budget)
- Push forward by category:
  `python3 driver.py Home 10 150` → then Electronics, Body, Nature, Materials, then Verbs, Adjectives.
- `driver.py` is resumable (skips cards whose PNG already exists) and merges images +
  ledger + cards into `out_deck/` automatically.
