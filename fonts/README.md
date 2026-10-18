# Fonts embedded in the deck

Shipped as Anki media (the leading underscore keeps Anki's "Check Media" from deleting
files that only the note-type CSS references) and loaded by `@font-face` in
`anki/frame_standard.css`.

**Brygada 1918, used throughout** (owner decision 2026-10-18, Backs and Type review).

| media file | source | licence |
|---|---|---|
| `_Brygada1918-Regular.ttf` | `ofl/brygada1918/Brygada1918[wght].ttf`, static instance wght 400 | `OFL_Brygada1918.txt` |
| `_Brygada1918-Bold.ttf` | `ofl/brygada1918/Brygada1918[wght].ttf`, static instance wght 700 | `OFL_Brygada1918.txt` |
| `_Brygada1918-Italic.ttf` | `ofl/brygada1918/Brygada1918-Italic[wght].ttf`, static instance wght 400 | `OFL_Brygada1918.txt` |

Source: github.com/google/fonts at commit 47d54ca1ebb14fd864695f1d39dc734f39017c33 (the revision the
Backs and Type review used, `frame_preview.REVIEW_FONT_REV`). The variable fonts were instanced with
fontTools `varLib.instancer` (static files load in every Anki client); outlines are otherwise
unmodified. SIL Open Font License 1.1, full text in `OFL_Brygada1918.txt`.

Glyph check (2026-10-18, fontTools cmap + GPOS, all three files): ą č ę ė į š ų ū ž in both cases,
the precomposed à á ã è é ẽ ì í ĩ ò ó õ ù ú ũ ý ỹ, and the combining grave U+0300, acute U+0301,
tilde U+0303 and dot above U+0307 are all present; GPOS has `mark` and `mkmk`, so stacked clusters
such as ė̃ and ū̃ are positioned by the font itself. No fallback face is needed; the CSS stack is
`"Brygada 1918", Georgia, serif`.

The previous pair (PT Serif + Old Standard TT, with their OFL files) is kept in `_superseded/` and is
no longer shipped. `review/` (git-ignored) holds the review faces `frame_preview.py --fetch-fonts` fetches.
