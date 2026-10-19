# -*- coding: utf-8 -*-
"""Round 4 extra QA (a2_build/round4/plan.csv asks for checks qa_images.py does not make). qa_images.py and its
prompts are untouched (style lock); this calls the same model through qa_images._ask with
  1. the unchanged LIMBS_PROMPT on the situation cards of this round (qa_images --limbs only gives it to
     non-situation cards, and the situation FIT call has no hands_ok item), and
  2. one plain question per card where the plan names a specific check.
    python3 a2_build/round4/qa_r4_extra.py <img_dir> <out.csv>"""
import csv, json, os, sys
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
import qa_images as q
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
D, OUT = sys.argv[1], sys.argv[2]
SIT = ["A2-0359", "A2-0925", "A2-1162", "A2-1167", "A2-1172", "A2-1184", "A2-1185", "A2-1191", "A2-2002", "A2-2010",
       "A2-2022", "A2-2026", "A2-2029", "S-0051"]
ASK = {
    "A2-2010": "Look at the taxi driver's hand that offers coins (main picture and the inset with coins on a palm). "
               "Is it anatomically a RIGHT hand, judged by the side the thumb is on given that the palm faces up? "
               "Return strict JSON {\"answer\": \"right\"|\"left\"|\"unclear\", \"note\": one line}.",
    "S-0051": "Count the lit candles on the cake in the main picture and in the inset where the boy blows them out. "
              "Return strict JSON {\"main\": n, \"inset\": n, \"note\": one line}.",
    "A2-0660": "In the main picture, which way do the woman and the small boy walk across the crossing, as the viewer sees "
               "it? Return strict JSON {\"direction\": \"left-to-right\"|\"right-to-left\"|\"toward viewer\"|\"away\", "
               "\"note\": one line}.",
    "055_bankas": "Is anything (bars, grille, glass frame) drawn across the cashier's face, and are the grille bars fused "
                  "or broken anywhere? Return strict JSON {\"face_clear\": true|false, \"bars_ok\": true|false, "
                  "\"note\": one line}.",
    "413_tuoktis": "Is there a close-up of hands anywhere (main picture or insets)? Return strict JSON "
                   "{\"hand_closeup\": true|false, \"note\": one line}.",
    "A2-2002": "The old woman's raised RIGHT hand points at the number plate: is the palm turned out toward the viewer, "
               "with one index finger extended, and is the hand anatomically natural? Return strict JSON "
               "{\"palm_out\": true|false, \"natural\": true|false, \"note\": one line}.",
    "A2-1162": "Is the door frame of the office door in front of the man (overlapping him) or behind him? Return strict "
               "JSON {\"frame\": \"behind\"|\"in front\"|\"unclear\", \"note\": one line}.",
    "A2-1167": "Is the flat's door of ordinary height compared with the people, and is the host standing clear of the "
               "door frame? Return strict JSON {\"door_normal\": true|false, \"host_clear\": true|false, \"note\": one line}.",
    "A2-2029": "In the lower-left inset, does any hand or arm come out of a car window? Return strict JSON "
               "{\"hand_out_of_window\": true|false, \"note\": one line}.",
}
c = OpenAI()
jobs = [(k, "limbs", q.LIMBS_PROMPT) for k in SIT] + [(k, "ask", t) for k, t in ASK.items()]
def run(j):
    k, kind, t = j
    try:
        return k, kind, q._ask(c, os.path.join(D, k + ".png"), t)
    except Exception as e:
        return k, kind, {"error": str(e)[:200]}
with ThreadPoolExecutor(8) as ex:
    res = list(ex.map(run, jobs))
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["key", "check", "result"])
    for k, kind, r in sorted(res):
        w.writerow([k, kind, json.dumps(r, ensure_ascii=False)]); print(k, kind, json.dumps(r, ensure_ascii=False)[:260])
