# Lithuanian section labels for the top band

Owner, 2026-10-17: "have the top categories in Lithuanian — a bit more passive Lithuanian to learn." Plan only.

`section_labels_lt.csv`: the 20 sections of `card_frame.SECTIONS`, the current English label, the proposed Lithuanian label in the owner's form (`VI skyrius · maistas`), the source each word was checked against (lt.wiktionary / en.wiktionary pages fetched 2026-10-17; `frazė` on vle.lt because neither wiktionary has it), and notes where a choice was made (XV, XVI, XVIII, XIX).

## What the executor changes in `card_frame.py`

1. The label strings in `SECTIONS` become the Lithuanian ones (second column of each tuple), lowercase as now — the band prints them in small caps.
2. In `section_css()` the `::before` content changes from `f"Section {n} ·"` to `f"{n} skyrius ·"` (both places: the per-category loop and the `ROUTE_SECTIONS` loop). "skyrius" after a Roman numeral is the normal Lithuanian form (II skyrius), lowercase.
3. `section_of()` returns the Lithuanian label; `build_apkg.py` only prints it in warnings, nothing parses it.
4. Fonts: Brygada 1918 (commit 0afc17a) covers ą č ę ė į š ų ū ž; the only new glyphs in the labels are ū (kūnas), ė (sąvokos has ą, savybės ė) — check the small-caps rendering of `ė` and `ų` once in the frame preview.

Note type FIELDS are untouched (the label is CSS from the Category field), so this rides on an ordinary re-export; no re-import schema change.

## Owner decisions

- XVIII "small words": `pagalbiniai žodžiai` proposed over the grammar term `tarnybiniai žodžiai`, which would be false for the pronouns and adverbs in that section.
- XVI: `daiktai ir sąvokos` (things and concepts) or the literal `daiktai ir idėjos`.
