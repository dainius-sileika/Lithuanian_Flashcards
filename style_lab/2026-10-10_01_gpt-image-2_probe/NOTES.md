# 01 — gpt-image-2 style probe (2026-10-10)

**Why:** `gpt-image-1.5`, which drew all 520 shipped cards, leaves the OpenAI API on 1 Dec 2026.
**What:** 10 shipped cards (suo, mokykla, gydytojas, eiti, pjauti, letas, akis, auksas, tylus, karas)
re-run through `gpt-image-2` with their **exact shipped prompts** from `out_deck/ledger.csv`
(medium quality, 1536x1024). miestas and klubas were added later for experiment 03.
**Script:** `../scripts/probe.py` (at the time `_proto/probe.py`). **Cost:** ~$0.044/image.
**Sheet:** `compare_sheet.jpg` (left 1.5, right gpt-image-2).
**Owner's verdict:** "more serious, consistent, and better" — gpt-image-2 adopted as engine default (`1a574fa`).
Later the same day he judged the newer models *too detailed* and drifting from the 1981 GO look (see 04, 05).
