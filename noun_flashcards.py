#!/usr/bin/env python3
"""
Noun flashcards (files 1.6) — grammar DEMO app over the GO Generator.

1.6: compose_noun now returns an `insets` flag (attribute/chart classes carry
their whole composition in the phrase). NOTE: the full wordlist-driven run now
lives in deck_builder.py — this file remains the quick per-grammar demo/spot
check (one noun per class).

1.2: the single generic noun treatment is replaced by per-category VISUAL
GRAMMARS (go_grammars.py). Each word's `category` selects a semantic class
(creature / food / place / vehicle / garment / body_part / object / nature /
material / person / beverage), which supplies the main composition and the
supporting insets. The frozen house-style (palette, print feel, red bars, no
text, flag-only, black boots) stays constant across every category.

Text OFF the image; cards.csv holds the correct vocabulary for the Anki layer.

Run:  export OPENAI_API_KEY=sk-... ; pip install openai
      python noun_flashcards.py trial      |      python noun_flashcards.py full
"""
import sys, os
from go_generator import GOGenerator
from go_grammars import compose_noun

BACKEND = "openai"
RATIO   = "4:3"
BASE_NUMBER = 301
OUT_TRIAL = "./out_nouns_trial"
OUT_FULL  = "./out_nouns"

# (key, lithuanian, english, category, subject)  — one per grammar class, to
# demonstrate the range. The full run is deck_builder.py (reads master_wordlist).
NOUNS = [
    ("suo",        "šuo",       "dog",       "Animal",         "a dog"),
    ("obuolys",    "obuolys",   "apple",     "Food",           "an apple"),
    ("ligonine",   "ligoninė",  "hospital",  "Location",       "a hospital building"),
    ("sunkvezimis","sunkvežimis","truck",    "Transportation", "a truck"),
    ("ranka",      "ranka",     "hand",      "Body",           "a human hand"),
    ("gydytojas",  "gydytojas", "doctor",    "Job",            "a doctor"),
    ("kava",       "kava",      "coffee",    "Beverages",      "a cup of coffee"),
    ("paltas",     "paltas",    "coat",      "Clothing",       "a coat"),
    ("telefonas",  "telefonas", "telephone", "Electronics",    "a telephone"),
    ("medis",      "medis",     "tree",      "Nature",         "a tree"),
    ("mediena",    "mediena",   "wood",      "Materials",      "timber wood"),
    ("knyga",      "knyga",     "book",      "Home",           "a book"),
]
TRIAL = NOUNS[:6]   # dog·apple·hospital·truck·hand·doctor — six different grammars


def run(words, out_dir):
    gen = GOGenerator(backend=BACKEND, ratio=RATIO)
    lf, lw = GOGenerator.open_ledger(os.path.join(out_dir, "ledger.csv"))
    cf, cw = GOGenerator.open_cards(os.path.join(out_dir, "cards.csv"))
    for i, (key, lt, en, cat, subject) in enumerate(words):
        number = BASE_NUMBER + i
        scene, inset_note, cls, people, insets = compose_noun(cat)
        dest, seed, prompt = gen.generate(
            subject, scene=scene, inset_note=inset_note, insets=insets,
            text=False, people=people, out_dir=out_dir, filename=f"{key}.png")
        lw.writerow([key, subject, seed, gen.backend, gen.size,
                     os.path.basename(dest), prompt]); lf.flush()
        cw.writerow([key, lt, en, "", "", number, cat, f"{key}.png"]); cf.flush()
        print(f"    {number}  {lt} ({en})  [{cat} -> {cls}, {people}]")
    lf.close(); cf.close()
    print(f"done -> {out_dir}  (images + ledger.csv + cards.csv)")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "trial"
    run(TRIAL if mode == "trial" else NOUNS,
        OUT_TRIAL if mode == "trial" else OUT_FULL)
