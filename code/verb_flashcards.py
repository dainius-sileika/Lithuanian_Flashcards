#!/usr/bin/env python3
"""
Verb flashcards (files 1.6) — verb DEMO app over the GO Generator.

1.6: scene_for() takes an actor dress class so non-labour verbs (dance, kiss,
marry, play) stop rendering as coverall workers; the demo verbs below are all
worker verbs so their output is unchanged. Full run: deck_builder.py.

Text OFF the image; cards.csv holds the correct vocabulary for the Anki layer.
1.1: legacy supporting-label lists removed (they were for baked-in image text,
     dropped back in 0.7). Data is now just what the card actually needs.

Verb treatment (locked at 1.0):
  DEFAULT context C — floating main figure in a real institutional space + a
    clean motion sequence in small panels.
  ACCENT context D — verbs with a natural destination/result carry a
    `consequence` string that becomes one context panel.

Run:  export OPENAI_API_KEY=sk-... ; pip install openai
      python verb_flashcards.py trial      |      python verb_flashcards.py full
"""
import sys, os
from go_generator import GOGenerator

BACKEND = "openai"
RATIO   = "4:3"                 # landscape default; "3:4" = portrait (phone)
BASE_NUMBER = 101
OUT_TRIAL = "./out_verbs_trial"
OUT_FULL  = "./out_verbs"

# per-verb directional arrow + staging emphasis. kelti (raise, vertical) vs
# nešti (carry, horizontal) are pulled apart onto different axes so they read
# as clearly different verbs.
ARROW = {
    "eiti":  "one bold arrow showing the forward direction of walking",
    "begti": "one bold arrow showing the forward direction of running",
    "kelti": "one bold UPWARD arrow showing the crate being raised straight up",
}
EMPHASIS = {
    "nesti": "Emphasise horizontal transport: the worker walks and carries the crate across a distance, holding it steady — this is CARRYING, not lifting.",
    "kelti": "Emphasise the vertical upward lift: the worker raises the crate straight up from the floor — this is LIFTING/RAISING, not walking with it.",
}

# (key, lithuanian, english, action-phrase, institutional setting, category, consequence)
VERBS = [
    ("plauti",  "plauti",  "to wash",  "a worker washing their hands",
        "a tiled factory or institutional washroom", "VEIKSMAI IR POREIKIAI", ""),
    ("valgyti", "valgyti", "to eat",   "a worker eating with a spoon",
        "a plain workers' canteen with long tables and others eating in the background",
        "VEIKSMAI IR POREIKIAI", ""),
    ("gerti",   "gerti",   "to drink", "a worker drinking from a glass",
        "a workers' canteen or rest area with a water station", "VEIKSMAI IR POREIKIAI", ""),
    ("eiti",    "eiti",    "to walk",  "a worker walking forward in mid-stride",
        "a long institutional corridor", "VEIKSMAI IR JUDESIAI", ""),
    ("nesti",   "nešti",   "to carry", "a worker carrying a wooden crate forward across the room with both arms, mid-stride",
        "a supply depot or storeroom hall with tall shelves of crates and a few workers in the background",
        "VEIKSMAI IR JUDESIAI", "a cargo truck being loaded with the carried crates"),
    ("kelti",   "kelti",   "to lift",  "a worker lifting a heavy crate straight up from the floor and raising it toward a high shelf",
        "a supply depot or storeroom with tall shelves of crates", "VEIKSMAI IR JUDESIAI",
        "the crate lifted and set up onto the high shelf"),
    ("begti",   "bėgti",   "to run",   "a worker running at full stride",
        "a plain institutional courtyard or street", "VEIKSMAI IR JUDESIAI", ""),
    ("miegoti", "miegoti", "to sleep", "a worker asleep on a cot",
        "a plain barracks or dormitory bunk room", "VEIKSMAI IR POREIKIAI", ""),
    ("statyti", "statyti", "to build", "a worker hammering a plank",
        "a workshop or construction site with a workbench", "VEIKSMAI IR JUDESIAI",
        "the finished assembled wooden structure or frame"),
    ("gesinti", "gesinti", "to extinguish", "a worker aiming a fire extinguisher",
        "a depot yard beside a small contained fire, with fire-safety equipment",
        "VEIKSMAI IR JUDESIAI", "the fire safely put out, with only faint smoke remaining"),
]
TRIAL = VERBS[:6]


ACTOR_NOUN = {"worker": "worker", "professional": "person", "civilian": "person"}


def scene_for(setting, arrow="", emphasis="", people="worker"):
    actor = ACTOR_NOUN.get(people, "figure")
    s = (f"Show the {actor} performing the action large and clear in the "
         "foreground, floating on the cream paper WITHOUT any hard box or border "
         f"around the main scene, set within {setting}, with a little quiet "
         "civic activity in the background that fades softly into the paper.")
    if emphasis:
        s += " " + emphasis
    if arrow:
        s += " Include " + arrow + "."
    return s


def inset_for(consequence=""):
    if consequence:
        return ("Beneath or beside the main scene, in small bordered panels, "
                "include a clean two-panel motion sequence of the action plus one "
                f"context panel showing {consequence}. You MAY add one small "
                "Lithuanian tricolor flag. Nothing else — keep it uncluttered.")
    return ("Beneath the main scene, in small bordered panels, include a clean "
            "civic procedural sequence of two or three panels showing the simple "
            "motion of the action step by step. You MAY add one small Lithuanian "
            "tricolor flag. Nothing else — keep it uncluttered.")


def run(words, out_dir):
    gen = GOGenerator(backend=BACKEND, ratio=RATIO)
    lf, lw = GOGenerator.open_ledger(os.path.join(out_dir, "ledger.csv"))
    cf, cw = GOGenerator.open_cards(os.path.join(out_dir, "cards.csv"))
    for i, (key, lt, en, action, setting, cat, consequence) in enumerate(words):
        number = BASE_NUMBER + i
        scene = scene_for(setting, arrow=ARROW.get(key, ""), emphasis=EMPHASIS.get(key, ""))
        dest, seed, prompt = gen.generate(
            action, scene=scene, inset_note=inset_for(consequence), insets=True,
            text=False, people="worker", out_dir=out_dir, filename=f"{key}.png")
        lw.writerow([key, action, seed, gen.backend, gen.size,
                     os.path.basename(dest), prompt]); lf.flush()
        cw.writerow([key, lt, en, "", "", number, cat, f"{key}.png"]); cf.flush()
        print(f"    {number}  {lt} ({en})  ({'C+D' if consequence else 'C'})")
    lf.close(); cf.close()
    print(f"done -> {out_dir}  (images + ledger.csv + cards.csv)")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "trial"
    run(TRIAL if mode == "trial" else VERBS,
        OUT_TRIAL if mode == "trial" else OUT_FULL)
