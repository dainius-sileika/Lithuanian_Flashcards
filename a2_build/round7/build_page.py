# -*- coding: utf-8 -*-
"""Review page "Round 7 Fixes" (2026-10-20): A2-0359 re-rolled whole so the first inset (the patient in bed, days
before his discharge) shows no flowers (owner on Round 6 Fixes). Same template as rounds 3-6
(a2_build/review_template); the new picture spans the full width, the Round 6 picture sits below it for comparison.
db (capabilities db + user): collection "round7", general notes "round7_meta/general".
Images are not in git: PHRASES_OUT points at the out_phrases_v3 folder that holds them (default out_phrases_v3).
    PHRASES_OUT=<project>/out_phrases_v3 python3 a2_build/round7/build_page.py
        -> a2_build/round7/page/index.html + page/media/r7_*.jpg"""
import csv, json, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
OUT = os.path.join(HERE, "page"); MEDIA = os.path.join(OUT, "media"); os.makedirs(MEDIA, exist_ok=True)
QA = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "qa_round7.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
used = set()
V3 = os.environ.get("PHRASES_OUT", "out_phrases_v3")
K = "A2-0359"
JUDGED, NEW = f"{V3}/_rerolled/{K}.r8.png", f"{V3}/{K}.png"


def small(src, tag, px=800):
    name = f"r7_{tag}.jpg"; im = Image.open(src).convert("RGB"); im.thumbnail((px, px))
    im.save(f"{MEDIA}/{name}", "JPEG", quality=80); used.add(name); return name, im.width, im.height


def zoom2(a, b, box):
    A = Image.open(a).convert("RGB").crop(box); B = Image.open(b).convert("RGB").crop(box)
    h = 400; A = A.resize((int(A.width * h / A.height), h)); B = B.resize((int(B.width * h / B.height), h))
    z = Image.new("RGB", (A.width + B.width + 8, h), (255, 255, 255)); z.paste(A, (0, 0)); z.paste(B, (A.width + 8, 0))
    name = f"r7_{K}_zoom.jpg"; z.save(f"{MEDIA}/{name}", "JPEG", quality=82); used.add(name); return name


w = a2[K]; q = QA.get(K, {})
pics = [(NEW, "New (Round 7): no flowers before the discharge", 1536, "after"),
        (JUDGED, "Round 6 (judged): flowers by the bed", 800, "")]
imgs = []
for i, (s, l, px, cls) in enumerate(pics):
    n, wd, ht = small(s, f"{K}_{i}", px)
    imgs.append({"src": n, "label": l, "w": wd, "h": ht, **({"cls": cls} if cls else {})})
data = [{"k": K, "group": "Re-rolled whole", "lt": w["lithuanian_TARGET"], "pron": w.get("lt_pron", ""), "en": w["english"],
         "imgs": imgs, "zoom": zoom2(JUDGED, NEW, (1085, 55, 1515, 460)), "chips": ["1 try"],
         "facts": [["Your note", "Can't be flowers in the first insert, because the flowers come after his release; redo"],
                   ["Done", "Whole re-roll. Only the first inset's text changed: the patient sits up in bed in plain white "
                            "sheets, the nurse beside him holds her clipboard, and the bedside table has only a glass of "
                            "water and a folded towel. The main scene (flowers handed over with both hands) and the last "
                            "inset (leaving down the front steps) are staged word for word as in Round 6. The first try "
                            "passed every check."],
                   ["Extra check", "Blind questions, with no hint of what any panel should show. A list of every object "
                                   "in each panel: the new first inset has no flowers (Round 6: a vase with a bouquet "
                                   "on the bedside table). Main scene: a bouquet handed to the nurse with both hands. "
                                   "Last inset: down the steps, doors behind him, read as leaving. Hands and limbs ok."],
                   ["Look at", "In the main scene one of his hands is clearly seen; the other is under the paper wrap, and "
                               "the nurse's hand meets his at the stems. The blind check reads it as both hands. Round 6's "
                               "main scene was the same."]],
         "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", "")}]
extra = {"col": "round7", "title": "Round 7 fixes",
         "hints": {"Re-rolled whole": "the new picture full width, the Round 6 picture you judged below it; the close-up shows the first inset, Round 6 | new"},
         "lead": ["One card from your Round 6 Fixes verdicts: A2-0359 Labai ačiū. The first inset (him in the hospital bed "
                  "some days earlier) now has no flowers anywhere. Every earlier version is kept in out_phrases_v3/_rerolled.",
                  f"QA (cold read, hands and limbs, and blind checks of every panel): {q.get('status', '?')}. Mark OK or Redo; "
                  "a note on a Redo says what to change."]}
TPL = open("a2_build/review_template/template_review.html", encoding="utf-8").read()
CSS = ("\n.pair figure.after{grid-column:1/-1}\n.pair img,.zoom img{width:100%;height:auto}\n</style>")
assert TPL.count("</style>") == 1
doc = (TPL.replace("__TITLE__", "Round 7 Fixes").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
       .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False))
       .replace("</style>", CSS)
       .replace("Close-up of the repainted area · before | after", "Close-up of the first inset · Round 6 | new")
       .replace("close-up of the repainted area, before and after", "close-up of the first inset, Round 6 and new"))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
json.dump(sorted(used), open(os.path.join(OUT, "media_list.json"), "w"))
print(len(data), "card", len(used), "media", "QA", q.get("status"))
