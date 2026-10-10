"""Real-Lithuanian-place settings for card scenes (F6.1, 2026-10-11).

Owner, F6 review: "not always, but 2/3 to 3/4 of the time, set the setting in a
real Lithuanian location." Locations, 1981 counterfactual notes and the rotation
rule come from style_lab/research/location_bank.json (Fable researcher; sources
and unverified points are listed there and in lithuanian_locations_fable.md).

assign() reads the curated table style_lab/research/settings_assignments.csv and
returns {key: "Setting: ..."}; suggest() drafts candidates for new cards by
keyword. The table is the source of truth, so re-rolls keep their place.
"""
from __future__ import annotations
import hashlib, json, os, re

BANK_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "style_lab", "research", "location_bank.json")
SHARE = 0.70          # of eligible cards (owner: 2/3 to 3/4)
CAP = 0.08            # no location above 8 % of located cards
FAMOUS_MAX = 1 / 3    # famous silhouettes at most a third of located cards
FAMOUS = {"vilnius_gediminas_hill", "vilnius_cathedral", "vilnius_tv_tower",
          "kaunas_resurrection_church", "trakai_castle", "hill_of_crosses",
          "nida_curonian_spit", "palanga", "kernave"}
# classes whose cards draw a scene with a background; everything else
# (objects, clothing, animals alone, food, body parts, attributes, charts)
# stays generic, per the bank's always_generic list
SCENE_CLASSES = {"place", "vehicle", "nature", "person", "verb"}

# first match wins; matched against the English gloss + subject phrase (+ the
# verb's staged setting), so a setting only lands where it fits the scene. The
# bank's own category_map is too coarse for vehicles (a train beside a ferry, a
# bus on a funicular), so the routes below name compatible locations directly.
# An empty list means "stays generic" (no airport in the bank).
ROUTES = [
    ("air", r"plane|airport|aircraft|pilot", []),
    ("rail", r"\btrain|railway|station|platform|carriage", ["kaunas_railway_station"]),
    ("boat", r"ferry|\bboat|\bship|\bport\b|harbou?r|sailor|fisherm|\boar",
     ["klaipeda_port_ferry", "nemunas_valley", "aukstaitija_lakes", "trakai_castle",
      "nida_curonian_spit"]),
    ("hospital", r"hospital|clinic|doctor|nurse|patient|pharmac|ambulance|dentist",
     ["vilnius_antakalnis", "druskininkai", "kaunas_modernism"]),
    ("school", r"school|classroom|pupil|teacher|student|lesson|blackboard|chalkboard",
     ["vilnius_lazdynai", "vilnius_zverynas", "kaunas_modernism", "aukstaitija_village"]),
    ("church", r"church|wedding|priest|funeral|cemetery|christmas|easter|chapel",
     ["vilnius_gate_of_dawn", "kaunas_pazaislis", "zemaitija_village", "vilnius_old_town",
      "aukstaitija_lakes", "kaunas_resurrection_church", "hill_of_crosses"]),
    ("market", r"\bshop|market|store|counter|\bbuy|\bsell|customer|kiosk|cashier|bakery",
     ["vilnius_kalvariju_market", "kaunas_laisves_aleja", "siauliai", "vilnius_old_town"]),
    ("farm", r"\bfarm|field|barn|\bcow|horse|\bpig|harvest|garden|tractor|village|\bhay\b|"
             r"potato|\bcrop|orchard|livestock|farmhouse|\bhouse\b|\bwell\b",
     ["rumsiskes_farmstead", "zemaitija_village", "suvalkija_farm", "dzukija_village",
      "aukstaitija_village"]),
    ("road", r"\bbus\b|\btram|trolleybus|\bcar\b|taxi|traffic|lorry|truck|bicycle|"
             r"motorcycle|driver|\broad\b",
     ["kaunas_laisves_aleja", "vilnius_lazdynai", "siauliai", "kaunas_modernism",
      "vilnius_neris_embankment", "vilnius_tv_tower"]),
    ("home", r"kitchen|\bhome\b|\broom\b|\btable\b|family|apartment|\bbed\b|\bmeal|"
             r"grandmother|grandfather|mother|father|\bbaby|parents",
     ["zemaitija_village", "dzukija_village", "suvalkija_farm", "trakai_karaim_street",
      "vilnius_zverynas", "vilnius_lazdynai"]),
    ("water", r"river|\blake|\bsea\b|beach|\brain|\bsnow|\bsun\b|weather|\bwind|cloud|"
              r"\bswim|winter|summer|autumn|spring|\bice\b|storm|shore|bridge",
     ["aukstaitija_lakes", "neris_valley", "nemunas_valley", "palanga", "nida_curonian_spit",
      "vilnius_neris_embankment", "trakai_castle"]),
    ("nature", r"forest|\btree|\bwood\b|woods|mushroom|\bbog\b|\bhill|mountain|flower|"
               r"meadow|nature|valley",
     ["dzukija_pine_forest", "cepkeliai_bog", "aukstaitija_lakes", "neris_valley", "kernave",
      "vilnius_gediminas_hill"]),
    ("work", r"factory|workshop|construction|builder|carpenter|craftsman|smith|warehouse",
     ["klaipeda_old_town", "panevezys", "vilnius_uzupis", "rumsiskes_farmstead"]),
    ("leisure", r"\bpark\b|dancing|\bdance|\bclub\b|theat|concert|\bstage\b|museum|cinema|"
                r"holiday|picnic|\bspa\b",
     ["palanga", "trakai_castle", "druskininkai", "vilnius_vingis", "aukstaitija_lakes"]),
    ("street", r"street|\bcity|\btown|square|crowd|pedestrian|courtyard|pavement|boulevard",
     ["vilnius_old_town", "kaunas_laisves_aleja", "kaunas_modernism", "klaipeda_old_town",
      "siauliai", "vilnius_zverynas", "vilnius_lazdynai", "vilnius_uzupis",
      "vilnius_cathedral", "vilnius_gediminas_hill"]),
]
# prompt-phrase repairs: never prime the model with the word "lettering"
PHRASE_FIX = {"1930s lettering-free facade": "plain 1930s facade"}
INTERIOR = re.compile(r"kitchen|\broom\b|\btable\b|apartment|\bbed\b|\bmeal|indoors|classroom|\bhall\b")


def _h(s: str) -> int:
    return int(hashlib.md5(s.encode("utf-8")).hexdigest(), 16)


def route_for(text: str):
    """(route name, location ids) for the first matching route, or None."""
    t = text.lower()
    for name, pat, ids in ROUTES:
        if re.search(pat, t):
            return name, ids
    return None


def _line(loc: dict, interior: bool) -> str:
    phrase = loc["prompt_phrase"]
    for a, b in PHRASE_FIX.items():
        phrase = phrase.replace(a, b)
    name = loc.get("name", "")
    named = (f" ({name})" if loc.get("naming_the_place_helps") and name.isascii()
             else "")
    if interior:
        return (f"Setting: Lithuania, 1981; the place outside is {phrase}{named}, "
                "glimpsed through a window or shown in one small inset.")
    return f"Setting: Lithuania, 1981, {phrase}{named}."


ASSIGN_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "style_lab", "research", "settings_assignments.csv")


def _line_mode(loc: dict, mode: str) -> str:
    if mode == "inset":
        phrase = loc["prompt_phrase"]
        for a, b in PHRASE_FIX.items():
            phrase = phrase.replace(a, b)
        return ("Setting: one of the small insets shows the subject in its place "
                f"in Lithuania, 1981: {phrase}.")
    return _line(loc, mode == "interior")


def assign(work=None, verb_settings=None, bank_path: str = BANK_PATH,
           skip=(), assign_path: str = ASSIGN_PATH):
    """Curated table first: style_lab/research/settings_assignments.csv
    (key, location_id, mode, why), hand-made against the bank by the Fable
    researcher 2026-10-11 — keyword matching alone paired a town with the Hill
    of Crosses and a park with a bog. Returns {key: "Setting: ..."}. Cards not
    in the table (new rows) get nothing; use suggest() to draft entries."""
    import csv
    bank = json.load(open(bank_path, encoding="utf-8"))
    locs = {l["id"]: l for l in bank["locations"]}
    out = {}
    if not os.path.exists(assign_path):
        return out
    for row in csv.DictReader(open(assign_path, encoding="utf-8")):
        k, lid = row["key"].strip(), row["location_id"].strip()
        if not lid or k in skip:
            continue
        if lid not in locs:
            raise ValueError(f"settings_assignments.csv: unknown location {lid!r} for {k}")
        out[k] = _line_mode(locs[lid], row.get("mode", "exterior").strip() or "exterior")
    return out


def suggest(work, verb_settings=None):
    """Keyword draft for NEW cards only ({key: (route, [location ids])}); a
    human or the researcher picks from it into settings_assignments.csv."""
    verb_settings = verb_settings or {}
    out = {}
    for key, r, cls in work:
        text = " ".join([r["english"], r["subject_phrase_EN"],
                         verb_settings.get(int(r["#"]), "")])
        hit = route_for(text)
        if hit and hit[1]:
            out[key] = hit
    return out
