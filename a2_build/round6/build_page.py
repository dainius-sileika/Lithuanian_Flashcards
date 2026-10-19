# -*- coding: utf-8 -*-
"""Review page "Round 6 Fixes" (2026-10-19): A2-0359 re-rolled whole so the last inset shows the man LEAVING the
hospital (owner on Round 5 Fixes). Same template as rounds 3-5 (a2_build/review_template).
db (capabilities db + user): collection "round6", general notes "round6_meta/general".
    python3 a2_build/round6/build_page.py        -> a2_build/round6/page/index.html + page/media/r6_*.jpg"""
import csv, json, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
OUT = os.path.join(HERE, "page"); MEDIA = os.path.join(OUT, "media"); os.makedirs(MEDIA, exist_ok=True)
QA = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "qa_round6.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
used = set()
V3 = "out_phrases_v3"
K = "A2-0359"
JUDGED, TRY1, NEW = f"{V3}/_rerolled/{K}.r6.png", f"{V3}/_rerolled/{K}.r7.png", f"{V3}/{K}.png"


def small(src, tag):
    name = f"r6_{tag}.jpg"; im = Image.open(src).convert("RGB"); im.thumbnail((800, 800))
    im.save(f"{MEDIA}/{name}", "JPEG", quality=78); used.add(name); return name


def zoom2(a, b, box):
    A = Image.open(a).convert("RGB").crop(box); B = Image.open(b).convert("RGB").crop(box)
    h = 360; A = A.resize((int(A.width * h / A.height), h)); B = B.resize((int(B.width * h / B.height), h))
    z = Image.new("RGB", (A.width + B.width + 8, h), (255, 255, 255)); z.paste(A, (0, 0)); z.paste(B, (A.width + 8, 0))
    name = f"r6_{K}_zoom.jpg"; z.save(f"{MEDIA}/{name}", "JPEG", quality=80); used.add(name); return name


w = a2[K]; q = QA.get(K, {})
pics = [(JUDGED, "Round 5 (judged): walking in"), (TRY1, "Try 1 (QA gaze fail)"), (NEW, "New: walking out")]
data = [{"k": K, "group": "Re-rolled whole", "lt": w["lithuanian_TARGET"], "pron": w.get("lt_pron", ""), "en": w["english"],
         "imgs": [{"src": small(s, f"{K}_{i}"), "label": l, **({"cls": "after"} if l.startswith(("New", "Try 1")) else {})}
                  for i, (s, l) in enumerate(pics)],
         "zoom": zoom2(JUDGED, NEW, (1050, 490, 1515, 950)), "chips": ["2 tries"],
         "facts": [["Your note", "Final panel should be a man leaving the hospital, not entering it"],
                   ["Done", "Whole re-roll. The main scene and the bed inset are staged as before. The last inset is "
                            "rewritten so it cannot be read the other way. He comes down the front steps toward you, "
                            "coat on, scarf on, a brown bag in his right hand. The glass doors are behind him at the top "
                            "of the steps. Round 5 had him seen from behind going up to the doors. Try 1 failed QA "
                            "because he looked straight out at the viewer. Try 2 has his eyes on the steps."],
                   ["Extra check", "A blind question about the last inset only, without saying what it should show. "
                                   "New: moving away from the building, down the steps, facing the viewer, doors "
                                   "behind him, read as leaving. Round 5: up the steps, doors in front of him, read "
                                   "as entering. Hands and limbs ok."]],
         "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", "")}]
extra = {"col": "round6", "title": "Round 6 fixes",
         "hints": {"Re-rolled whole": "the picture you judged, the failed try and the new one; the zoom shows the last inset before and after"},
         "lead": ["One card from your Round 5 Fixes verdicts: A2-0359 Labai ačiū. The last inset now shows the man leaving the hospital. "
                  "Every earlier version is kept in out_phrases_v3/_rerolled.",
                  f"QA (cold read, hands and limbs, and a blind check of the last inset): {q.get('status', '?')}. Mark OK or Redo; "
                  "a note on a Redo says what to change."]}
TPL = open("a2_build/review_template/template_review.html", encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Round 6 Fixes").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
       .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
json.dump(sorted(used), open(os.path.join(OUT, "media_list.json"), "w"))
print(len(data), "card", len(used), "media", "QA", q.get("status"))
