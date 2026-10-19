# -*- coding: utf-8 -*-
"""Round 6 extra QA for A2-0359: the unchanged qa_images.LIMBS_PROMPT, plus one BLIND question about the lower-right
inset (the round-5 check asked a leading question - "is the second the man leaving?" - and passed a man walking up to
the doors). The model is not told what the inset should show.
    python3 a2_build/round6/qa_r6_extra.py <image> <out.csv> [label]"""
import csv, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
sys.path.insert(0, ROOT)
import qa_images as q
from openai import OpenAI
os.environ.setdefault("OPENAI_API_KEY", open(".openai_key.txt").read().strip())
img, out = sys.argv[1], sys.argv[2]; label = sys.argv[3] if len(sys.argv) > 3 else "A2-0359"
BLIND = ("Look only at the LOWER inset on the right side of this picture. Describe the man in it: which way is he "
         "moving relative to the building and its doors, which way does his body face (toward the viewer, away from the "
         "viewer, sideways), is he going up or down the steps, what does he carry, and where are the doors relative to "
         "him? Then say whether a viewer would read the moment as ARRIVING at / entering the building or LEAVING it. "
         "Return strict JSON with keys \"moving\": short phrase, \"faces\": \"viewer\"|\"away\"|\"sideways\", "
         "\"steps\": \"up\"|\"down\"|\"none\", \"carries\": short phrase, \"doors\": \"behind him\"|\"in front of him\"|"
         "\"beside him\"|\"none\", \"reading\": \"entering\"|\"leaving\"|\"unclear\", \"looks_at_viewer\": true|false, "
         "\"note\": one line.")
c = OpenAI()
res = [("limbs", q._ask(c, img, q.LIMBS_PROMPT)), ("inset2_blind", q._ask(c, img, BLIND))]
new = not os.path.exists(out)
with open(out, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["image", "check", "result"])
    for k, r in res:
        w.writerow([label, k, json.dumps(r, ensure_ascii=False)]); print(label, k, json.dumps(r, ensure_ascii=False)[:400])
