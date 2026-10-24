# -*- coding: utf-8 -*-
"""Round 5 extra QA: the unchanged qa_images.LIMBS_PROMPT on this round's situation cards and on the three 413 tries,
plus one plain question per card where the owner's note names a specific check. qa_images.py is untouched (style lock).
    python3 a2_build/round5/qa_r5_extra.py <img_dir> <out.csv>"""
import csv, json, os, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
import qa_images as q
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
D, OUT = sys.argv[1], sys.argv[2]
J = lambda s: s + " Return strict JSON with the keys named, plus \"note\": one line."
LIMBS = {k: os.path.join(D, k + ".png") for k in ["A2-0359", "A2-0925", "A2-1167", "A2-2002", "A2-2010"]}
LIMBS.update({"413_try1": "out_deck_f62/_rerolled/413_tuoktis.r6.png", "413_try2": "out_deck_f62/_rerolled/413_tuoktis.r7.png",
              "413_try3": "out_deck_f62/_rerolled/413_tuoktis.r8.png"})
ASK = {
    "083_tevas": J("Look at the third (lowest) inset on the right. Is it a close-up of hands? What does it show? Keys: "
                   "\"hand_closeup\": true|false, \"shows\": short phrase."),
    "A2-0085": J("Look at the ticket clerk behind the window glass in the main picture. Does any part of her hand or arm pass "
                 "through or in front of the glass, or are her hands on the counter on her own side? Keys: "
                 "\"through_glass\": true|false, \"hands_on_counter\": true|false."),
    "A2-1431": J("Look at the top inset on the right (the shoe). Is there a shoehorn, and is any hand in it malformed or "
                 "bleeding outside the inset frame? Keys: \"shoehorn\": true|false, \"hand_ok\": true|false, "
                 "\"bleeds_outside\": true|false."),
    "A2-2002": J("The old woman's raised RIGHT hand points at the number plate: is the palm turned out toward the viewer, "
                 "with one index finger extended, and is the hand anatomically natural? Is her left hand natural too? Keys: "
                 "\"palm_out\": true|false, \"natural\": true|false, \"left_ok\": true|false."),
    "A2-2010": J("Is the taxi driver's offered hand anatomically a RIGHT hand (thumb side, palm up)? Are the car seats and "
                 "the open door drawn whole and undistorted? Keys: \"hand\": \"right\"|\"left\"|\"unclear\", "
                 "\"seats_ok\": true|false."),
    "A2-0359": J("What do the two insets on the right show? Is the first the man earlier as a patient in bed, and the "
                 "second the man leaving the hospital? Keys: \"inset1\": short phrase, \"inset2\": short phrase, "
                 "\"matches\": true|false."),
    "A2-1167": J("Is the flat's door of ordinary height compared with the people, and is the host standing clear of the "
                 "door frame? Keys: \"door_normal\": true|false, \"host_clear\": true|false."),
}
c = OpenAI()
jobs = [(k, "limbs", p, q.LIMBS_PROMPT) for k, p in LIMBS.items()] + [(k, "ask", os.path.join(D, k + ".png"), t) for k, t in ASK.items()]
def run(j):
    k, kind, p, t = j
    try:
        return k, kind, q._ask(c, p, t)
    except Exception as e:
        return k, kind, {"error": str(e)[:200]}
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(run, jobs))
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["key", "check", "result"])
    for k, kind, r in sorted(res):
        w.writerow([k, kind, json.dumps(r, ensure_ascii=False)]); print(k, kind, json.dumps(r, ensure_ascii=False)[:330])
