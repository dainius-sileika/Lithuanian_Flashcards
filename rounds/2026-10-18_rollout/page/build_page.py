# -*- coding: utf-8 -*-
"""Review page "Roll-out Review" (2026-10-18): the six owner-requested redraws (new picture, the
previous one small, the owner's note), then the 133 roll-out cards grouped by QA result, with the
QA findings on every card. OK / Redo + a note per card; db (capabilities db + user):
collection "rollout" (doc per key, with `by`), general notes "rollout_meta/general".

    python3 a2_build/rollout/page/build_page.py      # writes page/index.html + page/media/*.jpg
media/: <key>.jpg (800 px, q80) and <key>_old.jpg (480 px, q75) for the redraws; not committed.
"""
import csv, glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
os.chdir(ROOT); sys.path.insert(0, ROOT)
from PIL import Image
from situations import SITUATIONS
MEDIA = os.path.join(HERE, "media"); os.makedirs(MEDIA, exist_ok=True)
STAGING = json.load(open("a2_build/a2_staging.json", encoding="utf-8"))["notes"]
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
sit = {}
for en, s in SITUATIONS.items():
    for i in (s["ids"] or []):
        sit["374_galvoti" if i == "374" else i] = dict(s, en=en)
sit.setdefault("yes_no", dict(SITUATIONS.get("Yes / no", {}), en="Yes / no"))

def jpg(src, dst, w, q):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
        return
    im = Image.open(src).convert("RGB"); im.thumbnail((w, w)); im.save(dst, "JPEG", quality=q, optimize=True)

def latest_old(d, k):
    vs = [(int(re.search(r"\.r(\d+)\.png$", p).group(1)), p) for p in glob.glob(f"{d}/_rerolled/{k}.r*.png")]
    return max(vs)[1] if vs else None

data = []
# --- the six redraws
qa_r = {r["key"]: r for r in csv.DictReader(open("a2_build/rollout/qa_redraws.csv", encoding="utf-8"))}
REDRAW = [("A2-0352", "out_phrases_v3/round2", "Man in the doorway has feet inside the door frame", "the host's legs and shoes, the threshold"),
          ("A2-0377", "out_phrases_v3/round2", "Purse panels have an extra finger", "the purse hand in the main picture and the purse inset"),
          ("A2-0895", "out_phrases_v3/round2", "Hand holding child's hand is weird", "the mother's and the boy's clasped hands"),
          ("A2-1894", "out_deck_a2", "Woman's hand in main panel is strange", "both of the woman's hands"),
          ("A2-1911", "out_deck_a2", "Gerbil cage shows AI anomalies", "the cage, its wheel and house, the hamster, the girl's fingers"),
          ("A2-1915", "out_deck_a2", "Now it's two kings in the painting; one must be a queen, on the left, and then a king, on the right",
           "the painting on the wall and the upper inset: a Čiurlionis-style fairy tale, queen left, king right")]
for k, d, note, path in REDRAW:
    w = a2.get(k, {}); s = sit.get(k, {}); q = qa_r.get(k, {})
    jpg(f"{d}/{k}.png", f"{MEDIA}/{k}.jpg", 800, 80)
    old = latest_old(d, k); jpg(old, f"{MEDIA}/{k}_old.jpg", 480, 75)
    data.append({"k": k, "group": "The six redraws", "lt": w.get("lithuanian_TARGET") or s.get("lithuanian", ""),
                 "pron": w.get("lt_pron", ""), "en": s.get("en") or w.get("english", ""),
                 "staging": s.get("scene") or STAGING.get(k, "").split(" Insets:")[0],
                 "insets": "" if s else (STAGING.get(k, "").split(" Insets:") + [""])[1].strip(),
                 "cue": s.get("cue", ""), "conf": s.get("confusables", []),
                 "path": path, "owner": note, "edit": 1, "qa": q.get("status", ""), "fails": q.get("fails", ""),
                 "warns": q.get("warnings", ""), "guess": q.get("guess", ""), "nb": q.get("neighbour", ""),
                 "img": f"{k}.jpg", "old": f"{k}_old.jpg", "rr": 0})
# --- the roll-out
qa = list(csv.DictReader(open("out_phrases_v3/qa_rollout.csv", encoding="utf-8")))
picks = {}
if os.path.exists("out_phrases_v3/picks.jsonl"):
    for l in open("out_phrases_v3/picks.jsonl"):
        p = json.loads(l); picks[p["key"]] = p
GROUP = {"FAIL": "Roll-out · QA fail after two re-rolls", "WARN": "Roll-out · QA warnings", "PASS": "Roll-out · QA pass"}
order = {k: i for i, k in enumerate(json.load(open("out_phrases_v3/plan.json"))["jobs"][j]["key"] for j in range(167))}
for q in sorted(qa, key=lambda r: (["FAIL", "WARN", "PASS"].index(r["status"]), order.get(r["key"], 999))):
    k = q["key"]; s = sit.get(k, {}); w = a2.get(k, {})
    jpg(f"out_phrases_v3/{k}.png", f"{MEDIA}/{k}.jpg", 800, 80)
    n = len(glob.glob(f"out_phrases_v3/_rerolled/{k}.r*.png"))
    rr = n - 1 if k in picks else n
    hist = ""
    if k in picks:
        hist = f"3 rolls; the 2nd roll scored best and is shown (the 3rd is kept in _rerolled)"
    elif n:
        hist = f"{n + 1} rolls; the last is shown, earlier ones kept in _rerolled"
    data.append({"k": k, "group": GROUP[q["status"]], "lt": s.get("lithuanian") or w.get("lithuanian_TARGET", "") or ("Taip / ne" if k == "yes_no" else ""),
                 "pron": w.get("lt_pron", ""), "en": s.get("en") or w.get("english", ""),
                 "staging": s.get("scene", ""), "cue": s.get("cue", ""), "conf": s.get("confusables", []),
                 "fmt": {"situation": "single scene", "situation_2": "two panels", "sequence": "three panels"}.get(s.get("format"), ""),
                 "qa": q["status"], "fails": q["fails"], "warns": q["warnings"], "guess": q["guess"], "nb": q["neighbour"],
                 "img": f"{k}.jpg", "old": "", "rr": n, "hist": hist})
extra = {"title": "Roll-out review", "col": "rollout", "meta": "rollout_meta/general", "lead": [
    "First the six cards you sent back on 18 October, each repainted only where your note pointed (a masked edit; the rest of the "
    "picture is unchanged). Your earlier picture and note sit small under each one.",
    "Then the 133 remaining bubble cards, drawn without bubbles under the round-2 rules (conversation gaze, panel continuity, "
    "hands and props) with their insets kept. Every card went through QA; a hard fail was drawn again up to twice. They are grouped "
    "by the machine's result, fails first, and each card lists what QA flagged. Most remaining fails are staging questions "
    "(a neighbour phrase the picture can pass for, a staging that asks for sound lines or a downward look), not drawing faults.",
    "Mark OK or Redo; a note on a Redo says what to change. The 69 benchmark phrases are not here: they wait for staging."]}
TPL = open(os.path.join(HERE, "template_rollout.html"), encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Roll-out Review").replace("/*__MODE__*/", json.dumps("rollout"))
          .replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
          .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(doc)
from collections import Counter
print(len(data), "cards", Counter(c["group"] for c in data), len(os.listdir(MEDIA)), "media files",
      round(sum(os.path.getsize(os.path.join(MEDIA, f)) for f in os.listdir(MEDIA)) / 1e6, 1), "MB")
