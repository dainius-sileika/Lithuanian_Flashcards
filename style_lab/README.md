# style_lab — image-style experiments

The project's history of art-direction experiments. Each dated folder is one experiment with a `NOTES.md`
(why, what, how, cost, the owner's verdict). `MANIFEST.csv` lists every image: experiment, card, model,
prompt variant, quality, whether reference images were used, measured cost.

Images are kept here on disk but **not in git** (size); notes, prompts, scripts, logs and the manifest are.
The 1.5 originals they are compared against are the shipped masters in `out_deck/`.

| folder | question |
|---|---|
| `2026-10-10_01_gpt-image-2_probe` | can gpt-image-2 replace gpt-image-1.5 (shut down 1 Dec 2026)? |
| `2026-10-10_02_engine_check` | does the switched engine work end to end? |
| `2026-10-10_03_model_comparison` | gpt-image-2 vs 2.5-flare vs 2.5-sunburst on the owner's favourites, with cost |
| `2026-10-10_04_levers_A_B` | does an explicit style paragraph (A) or reference images (B) stop the drift? |
| `2026-10-10_05_fable_F1-F3` | Fable's diagnosis and three prompt candidates on 15 cards |
| `scripts/` | the probe scripts as they were run (paths then pointed at `_proto/`) |

Total measured spend on 2026-10-10 experiments 01–05: ~$3.90.
