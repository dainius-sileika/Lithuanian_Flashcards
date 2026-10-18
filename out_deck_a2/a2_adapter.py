# -*- coding: utf-8 -*-
"""a2_adapter.py — thin adapter from an a2_build/a2_wordlist.csv IMG row to the
kwargs deck_builder.build_call would produce, so the A2 pictures go through the
SAME production prompt path (go_generator.build_prompt) as the A1 deck.

Differences from the A1 wordlist, handled here and nowhere else:
  - categories are the A2 list's ('Nouns', 'Home', 'Time', 'Numbers', ...); they are
    mapped onto go_grammars' CAT2CLASS names, and the catch-all 'Nouns' is split by
    a small keyword list into place / person / food / creature / garment / object
    (the class only tunes insets, dress and vignette-vs-scene; the staging line
    carries the picture).
  - every verb has a staging line in a2_staging.json, so verbs take the F6.2
    default verb insets (deck_builder.VERB_INSET_DEFAULT) instead of VERB_STAGING.
  - adjectives (type A, incl. ordinals) get the A1 adjective insets rule
    (deck_builder.adj_inset_note); cardinal numerals (type NUM) are routed
    'attribute' with the staging's own insets.
  - card_text of the cardinal numerals A2-0041..0071 reads 'the numeral for "zero"'
    in the list — the quoted word is English and would be lettered as such. The
    adapter rewrites it to the digit string ("0", "1", ... "100", "1000",
    "1 000 000"); listed in README for the A2 builder to fix at source.
  - no bank Setting line (settings_assignments.csv knows only A1 keys).
"""
import csv, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import deck_builder as db
from go_grammars import route, compose_class, SCENE_TAIL

A2_LIST = os.path.join(ROOT, "a2_build", "a2_wordlist.csv")
A2_STAGING = os.path.join(ROOT, "a2_build", "a2_staging.json")

CATMAP = {"Nouns": "Misc", "Home": "Home", "Time": "Misc", "Nature": "Nature", "Food": "Food",
          "Location": "Location", "Work & culture": "Misc", "Clothing": "Clothing",
          "Transportation": "Transportation", "Society": "Misc", "Travel": "Misc", "Body": "Body",
          "Health": "Misc", "Work & school": "Misc", "Shopping": "Misc", "Technology": "Electronics",
          "People": "People", "Money & admin": "Misc", "Feelings": "Adjectives", "Abstract": "Misc",
          "Art": "Art", "Beverages": "Beverages", "Jobs": "Job", "Numbers": "Misc", "Adjectives": "Adjectives"}

PLACE_WORDS = ("hall", "shop", "station", "café", "cafe", "factory", "workshop", "cloakroom", "dormitory",
               "corridor", "cellar", "storeroom", "warehouse", "kindergarten", "canteen", "hairdresser's",
               "optician's", "bookshop", "port", "harbour", "crossroads", "old town", "playground",
               "building site", "flower bed", "gym", "bank branch", "square", "office", "museum", "cinema",
               "stadium", "cemetery", "stop", "car park", "embassy", "railway", "entrance", "exit", "hallway",
               "toilet", "summer house", "block of flats", "fitting room", "avenue", "fair (market)",
               "village", "post office", "pharmacy", "repair shop", "concert hall", "reception", "room",
               "consulting", "lift", "crossing", "pavement", "petrol", "castle", "monument", "seimas",
               "cathedral", "parliament")
PERSON_WORDS = ("receptionist", "administrator", "nanny", "singer", "worker", "electrician", "hairdresser",
                "craftsman", "repairman", "pupil", "postman", "shop assistant", "plumber", "judge", "athlete",
                "pharmacist", "cook", "chef", "dancer", "customs officer", "ticket inspector", "thief",
                "farmer", "musician", "writer", "scientist", "nurse", "tourist", "guide", "engineer",
                "builder", "inspector", "officer", "firefighter", "teenager", "guest", "couple")
FOOD_WORDS = ("rolls", "bun", "potato", "cepelinai", "vegetables", "sausages", "sour cream", "roast", "steak",
              "eggs", "kefir", "meat", "ice cream", "groceries", "dairy", "pastry", "cake", "pie", "soured milk",
              "sweet", "candy", "biscuit", "herring", "curd", "fruit", "šakotis", "soup", "chocolate",
              "slice", "salmon", "carp", "coffee", "vodka", "water", "drinks", "pill", "drops (medicine)")
CREATURE_WORDS = ("carp", "salmon", "herring")
GARMENT_WORDS = ("goggles", "footwear", "work clothes", "jeans", "overalls", "blouse", "trainers", "uniform",
                 "jacket", "helmet", "handbag", "rucksack")

NUMWORD = {"zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6",
           "seven": "7", "eight": "8", "nine": "9", "ten": "10", "eleven": "11", "twelve": "12",
           "thirteen": "13", "fourteen": "14", "fifteen": "15", "sixteen": "16", "seventeen": "17",
           "eighteen": "18", "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40", "fifty": "50",
           "sixty": "60", "seventy": "70", "eighty": "80", "ninety": "90", "hundred": "100",
           "thousand": "1000", "million": "1 000 000"}
CARD_TEXT_FIXES = {}   # id -> (original, used); filled by fix_card_text()


def fix_card_text(r):
    ct = (r.get("card_text") or "").strip()
    m = re.fullmatch(r'the numeral for "([a-z]+)"', ct)
    if m and m.group(1) in NUMWORD:
        new = f'the numeral "{NUMWORD[m.group(1)]}" written once, very large, as the subject of the card'
        CARD_TEXT_FIXES[r["id"]] = (ct, new)
        return new
    return ct


def _has(en, words):
    return any(re.search(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])", en) for w in words)


def classify(r):
    """(semantic class, people dress) for an A2 IMG row."""
    en = (r["english"] or "").lower(); cat = r["category"]; t = r["type"]
    if t == "V":
        return "verb", "civilian"
    if t == "A" or cat in ("Adjectives", "Feelings"):
        return "attribute", "civilian"
    if t == "NUM":
        return "attribute", "civilian"
    if cat == "Nouns" or cat in ("Work & culture", "Society", "Travel", "Work & school", "Shopping",
                                 "Health", "Money & admin", "Abstract", "Time"):
        if _has(en, PERSON_WORDS):
            return "person", "professional"
        if _has(en, CREATURE_WORDS):
            return "creature", "civilian"
        if _has(en, FOOD_WORDS):
            return "food", "civilian"
        if _has(en, GARMENT_WORDS):
            return "garment", "civilian"
        if _has(en, PLACE_WORDS):
            return "place", "civilian"
        return "object", "civilian"
    cls = route(CATMAP.get(cat, "Misc"), "N", "")
    people = "professional" if cls == "person" and cat == "Jobs" else "civilian"
    return cls, people


def load_rows():
    rows = [r for r in csv.DictReader(open(A2_LIST, encoding="utf-8")) if r.get("route") == "IMG"]
    staging = json.load(open(A2_STAGING, encoding="utf-8"))["notes"]
    return rows, staging


def build_call_a2(r, staging):
    key = r["id"]; subject = r["subject_phrase_EN"].strip()
    note = staging.get(key, "")
    cls, people = classify(r)
    exact = fix_card_text(r)
    if cls == "verb":
        comp = "vignette"
        return dict(subject=subject, scene="" if note.startswith("Main picture:") else SCENE_TAIL.strip(),
                    inset_note=db.VERB_INSET_DEFAULT, insets=True, text=False, people=people,
                    glyph=False, composition=comp, staging=note, setting="", motion_strip=False,
                    exact_text=exact, exclude=r["lithuanian_TARGET"].strip(), flag="lt",
                    filename=f"{key}.png"), cls
    scene, inset_note, _, _, insets = compose_class(cls, CATMAP.get(r["category"], "Misc"))
    if cls == "attribute":
        insets = True
        if r["type"] == "NUM":
            inset_note = ("Include 2 to 3 small supporting insets, each a clearly different everyday "
                          "example of the same number of things.")
        else:
            inset_note = db.adj_inset_note(r["english"])
    comp = "scene" if cls == "place" else "vignette"
    if comp == "scene":
        scene = scene.replace(SCENE_TAIL, "")
    if note.startswith("Main picture:"):
        scene = "" if comp == "scene" else SCENE_TAIL.strip()
    return dict(subject=subject, scene=scene, inset_note=inset_note, insets=insets, text=False,
                people=people, composition=comp, staging=note, setting="", motion_strip=False,
                glyph=False, exact_text=exact, exclude=r["lithuanian_TARGET"].strip(), flag="lt",
                filename=f"{key}.png"), cls



# 2026-10-18 historical places and figures: precedent= / likeness= for the A2 cards active in
# a2_build/historical/implementation/likeness_args.json (historical.py); others unchanged.
import historical as _hist
_build_call_a2_base = build_call_a2


def build_call_a2(r, staging):
    kw, cls = _build_call_a2_base(r, staging)
    kw.update(_hist.hist_args(r["id"]))
    return kw, cls


if __name__ == "__main__":
    import go_generator as g
    rows, staging = load_rows()
    want = set(sys.argv[1:])
    import collections
    cc = collections.Counter()
    for r in rows:
        kw, cls = build_call_a2(r, staging); cc[cls] += 1
        if r["id"] in want:
            pk = {k: v for k, v in kw.items() if k != "filename"}
            print(f"\n--- {r['id']} [{cls}] {r['lithuanian_TARGET']} ({r['english']})\n{g.build_prompt(backend='openai', **pk)}")
    print(cc, len(CARD_TEXT_FIXES), "card_text rewrites")
