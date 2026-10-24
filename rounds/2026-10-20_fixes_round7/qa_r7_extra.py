# -*- coding: utf-8 -*-
"""Round 7 extra QA for A2-0359: the unchanged qa_images.LIMBS_PROMPT plus three BLIND questions. The model is never
told what any panel should show or which panel is under suspicion:
  panels       - an inventory of the main scene and of EVERY inset (position, people, action, every object, and whether
                 any flower/bouquet/vase/petal/flower pattern is visible there); asked of all panels alike, so the
                 flower question does not single out inset 1;
  main_blind   - in the main scene, what passes from one person to the other and how the giver holds it (one or both hands);
  inset2_blind - round 6's blind movement question, pointed at the inset that shows a building entrance (located by
                 content, since the layout can move), unchanged otherwise.
    python3 a2_build/round7/qa_r7_extra.py <image> <out.csv> [label]"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
import qa_images as q
from openai import OpenAI
img, out = sys.argv[1], sys.argv[2]; label = sys.argv[3] if len(sys.argv) > 3 else "A2-0359"
PANELS = ("This illustration has one large main scene and some small framed inset panels. Give one entry for the main "
          "scene and one for EACH inset. Look carefully at every surface, hand, table, wall and bed in each panel. "
          "Return strict JSON: {\"panels\": [{\"where\": \"main\" or the inset's position (e.g. \"upper-left\", "
          "\"lower-right\"), \"people\": short phrase, \"action\": one line, \"objects\": [every object visible in that "
          "panel, including small ones on tables, in hands, on walls and on bedding], \"flowers\": true|false - any "
          "flower, bouquet, vase of flowers, petal, or flower-patterned fabric visible anywhere in that panel, "
          "\"flowers_where\": short phrase or \"\"}]}")
MAIN = ("Look only at the MAIN (largest) scene. Is anything being passed from one person to another? If so, what is "
        "it, who holds it out, who receives it, and how does the giver hold it - with one hand or with both hands? "
        "Describe where each of the giver's hands is. Return strict JSON with keys \"passed\": short phrase or \"\", "
        "\"giver\": short phrase, \"receiver\": short phrase, \"giver_hands\": \"one\"|\"both\"|\"none\", "
        "\"hands_note\": one line, \"note\": one line.")
INSET2 = ("Look only at the small inset panel that shows the entrance of a building. Describe the man in it: which way "
          "is he moving relative to the building and its doors, which way does his body face (toward the viewer, away "
          "from the viewer, sideways), is he going up or down the steps, what does he carry, and where are the doors "
          "relative to him? Then say whether a viewer would read the moment as ARRIVING at / entering the building or "
          "LEAVING it. Return strict JSON with keys \"where\": the inset's position, \"moving\": short phrase, \"faces\": "
          "\"viewer\"|\"away\"|\"sideways\", \"steps\": \"up\"|\"down\"|\"none\", \"carries\": short phrase, \"doors\": "
          "\"behind him\"|\"in front of him\"|\"beside him\"|\"none\", \"reading\": \"entering\"|\"leaving\"|\"unclear\", "
          "\"looks_at_viewer\": true|false, \"note\": one line.")
c = OpenAI()
res = [("limbs", q._ask(c, img, q.LIMBS_PROMPT)), ("panels_blind", q._ask(c, img, PANELS)),
       ("main_blind", q._ask(c, img, MAIN)), ("inset2_blind", q._ask(c, img, INSET2))]
new = not os.path.exists(out)
with open(out, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["image", "check", "result"])
    for k, r in res:
        w.writerow([label, k, json.dumps(r, ensure_ascii=False)]); print(label, k, json.dumps(r, ensure_ascii=False))
