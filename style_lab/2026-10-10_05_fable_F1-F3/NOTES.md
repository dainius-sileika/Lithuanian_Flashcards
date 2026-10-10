# 05 — Fable's three prompt candidates (2026-10-10)

A Fable subagent (art-director brief in `fable_brief/`) studied the 1.5 originals, the newer outputs and the
owner's real GO poster references, and diagnosed: the "Western" read lives in the **people** (magazine faces,
slim bodies, tailored/glamorous clothes, dynamic poses, glossy interiors); "too detailed" = full-bleed picture
vs. subject floating on bare paper; paragraph A pulled models toward US mid-century ad art.
Candidates (full text in `fable_brief/fable_style_candidates.json`):
- **F1** minimal edit of CONCEPT_LEAD, keeping the owner's key phrases; ink outline, one shadow tone, bare paper, plain sturdy people.
- **F2** print-production vocabulary (brush-ink line, gouache wash, offset halftone, flat diagram light, manual-page layout).
- **F3** 1981 people described concretely (faces, build, hair, cheap state-made clothes, stiff poses).
**Run:** 15 test cards x 3 candidates x {Sunburst, gpt-image-2} at medium + F1 Sunburst at low = 105 images, $2.79.
Script `../scripts/fable_run.py`. Sheets in `sheets/` (favourites, verbs, people, clothing).
**Read:** gpt-image-2 follows the prompts (floating on paper, plain 1981 people, esp. F3); Sunburst gets
the people better but stays full-bleed and keeps the disco klubas. Owner answers to Fable's questions:
soft shading fine; full-bleed acceptable if people right but float preferred; stiff poses fine.
Next: blind ranked survey (06).
