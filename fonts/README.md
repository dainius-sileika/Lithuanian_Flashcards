# Fonts embedded in the deck

Shipped as Anki media (the leading underscore keeps Anki's "Check Media" from deleting
files that only the note-type CSS references) and loaded by `@font-face` in
`anki/frame_standard.css`.

| media file | source (github.com/google/fonts, branch main) | licence |
|---|---|---|
| `_PTSerif-Regular.ttf` | `ofl/ptserif/PT_Serif-Web-Regular.ttf` | `OFL_PTSerif.txt` |
| `_PTSerif-Italic.ttf` | `ofl/ptserif/PT_Serif-Web-Italic.ttf` | `OFL_PTSerif.txt` |
| `_PTSerif-Bold.ttf` | `ofl/ptserif/PT_Serif-Web-Bold.ttf` | `OFL_PTSerif.txt` |
| `_OldStandardTT-Regular.ttf` | `ofl/oldstandardtt/OldStandard-Regular.ttf` | `OFL_OldStandardTT.txt` |

Both families are under the SIL Open Font License 1.1 (full text in the OFL files);
the files are unmodified, only renamed.

Glyph check (2026-10-17, fontTools cmap): all four cover ą č ę ė į š ų ū ž in both
cases and the combining acute U+0301. **PT Serif lacks the combining grave U+0300,
the combining tilde U+0303 and the combining dot U+0307, the precomposed ĩ ũ ẽ ỹ,
and has no GPOS mark positioning.** Old Standard TT covers all of them, with mark
positioning, so the CSS lists it right after PT Serif: a browser renders a stressed
cluster the primary font cannot (ẽ, ė̃, ĩ, l̃ ...) in the fallback font as a whole.
