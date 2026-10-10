# 04 — two levers against the drift (2026-10-10)

**Diagnosis that prompted it:** the live prompt never described the GO drawing style; since files 0.6 it
named the style and asked for "clean technical textbook illustration (between a botanical plate and an
engineering manual), realistic proportions". 1.5 rendered that as poster-flat; newer models literally.
- **Lever A** (`*_A/`): "paragraph A" (see `../2026-10-10_05_fable_F1-F3/fable_brief/paragraph_A.txt`)
  replaces CONCEPT_LEAD: flat gouache, even black outlines, halftone, generic types, 1981 dress list.
- **Lever B** (`*_B/`): shipped prompt + a note, with the three favourite 1.5 masters (`style_refs/`)
  sent as style references via `images.edit`. Adds ~2,100 image-input tokens (~$0.02/img).
**Cards:** turgus, gydytojas, pjauti (+ favourites for Sunburst A). **Script:** `../scripts/style_probe.py`.
**Sheets:** `style_levers_A_B.jpg`, `sunburst_old_vs_A.jpg`.
**Owner:** Sunburst old prompt (disco klubas) "looks Western"; Sunburst + A "also looks Western".
1.5 still best.
