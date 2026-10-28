#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_owner_stress_v1.py — writes OWNER_STRESS_v1.csv: the forms the naturalness round put on cards that no
source read gives a stress mark for (spec §7: shown unmarked until the owner supplies them). One shot, 2026-10-28.

    python3 rounds/2026-10-28_naturalness/make_owner_stress_v1.py

Same columns, BOM and CRLF as rounds/2026-10-28_stress_forms/OWNER_SHEET_v1.csv; A1 first, then study order.
The source read is English Wiktionary as the kaikki.org Wiktextract dump (fetched 2026-10-28, the stress-forms
round). Not listed: kalbù (0778) — final_v1 called it unsourced, but the dump has the form-of entry "kalbu"
(head kalbù, "first-person singular present of kalbėti"), so the card carries it.
"""
import csv, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "OWNER_STRESS_v1.csv")
COLS = ["key", "level", "word", "headword (stressed)", "form type", "form on the card", "YOUR stressed form", "note",
        "why it is here", "options seen in the source"]
NS = "not in source (en.wiktionary, kaikki.org dump 2026-10-28)"
ROWS = [
    ["1169_sveik", "A1", "sveikti (imperative)", "", "headword", "Sveik!", "", "",
     NS + ": neither sveikti nor sveik has an entry; the second check proposed Sveĩk! from card 1277 sveĩkti "
          "(kirtis.info rule engine), not a source", ""],
    ["1243_minutele", "A2", "minutėlė", "minutė̃lė", "headword", "Minutėlę!", "", "",
     NS + ": the accusative is in no source read; the card's former pron minutė̃lė came from the kirtis.info rule "
          "engine; the second check proposed Minutė̃lę!", ""],
    ["2435_spustis", "A2", "spūstis", "", "headword", "spūstis", "", "", NS + " (new card)", ""],
    ["2435_spustis", "A2", "spūstis", "", "genitive", "spūsties", "", "", NS + " (new card; the genitive itself is "
                                                                             "not from a source either)", ""],
    ["2435_spustis", "A2", "spūstis", "", "plural (in the sentence Centre {spūstys}.)", "spūstys", "", "",
     NS + " (new card; for the recording — sentences carry no marks on the card)", ""],
    ["1589_pasinaudoti", "A2", "pasinaudoti", "", "headword", "pasinaudoti", "", "",
     NS + "; the card's former headword naudótis came from the kirtis.info rule engine", ""],
    ["1968_vieta_prie_praejimo", "A2", "vieta prie praėjimo", "", "headword", "vieta prie praėjimo", "", "",
     NS + ": praėjimas has no entry (vietà and prie do); the phrase pron stays empty until the whole phrase is marked",
     ""],
]


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"{OUT} exists (a new version gets a new name)")
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(COLS)
        w.writerows(ROWS)
    print(f"{OUT}: {len(ROWS)} forms")


if __name__ == "__main__":
    main()
