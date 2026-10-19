# -*- coding: utf-8 -*-
"""Review page "Round 5 Fixes" (2026-10-19): the owner's Round 4 Fixes verdicts, done by whole re-roll (no masked edits).
Each card: the picture he judged beside the new one (and the other tries), his note, what was done, QA; OK / Redo + note.
Opens with the answer to his 055 bankas question. Same template as rounds 3-4 (a2_build/review_template).
db (capabilities db + user): collection "round5", general notes "round5_meta/general".
    python3 a2_build/round5/build_page.py        -> a2_build/round5/page/index.html + page/media/r5_*.jpg"""
import csv, html, json, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
OUT = os.path.join(HERE, "page"); MEDIA = os.path.join(OUT, "media"); os.makedirs(MEDIA, exist_ok=True)
QA = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "qa_round5.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
master = {r["#"].zfill(3): r for r in csv.DictReader(open("master_wordlist.csv", encoding="utf-8"))}
used = set()
F62, A2D, V3 = "out_deck_f62", "out_deck_a2", "out_phrases_v3"


def word(k):
    if k.startswith("A2"):
        w = a2[k]; return w["lithuanian_TARGET"], w.get("lt_pron", ""), w["english"]
    m = master[k[:3]]; return m["lithuanian_TARGET"], m["lt_pron"], m["english"]


def small(src, tag):
    name = f"r5_{tag}.jpg"; im = Image.open(src).convert("RGB"); im.thumbnail((800, 800))
    im.save(f"{MEDIA}/{name}", "JPEG", quality=78); used.add(name); return name


def zoom2(k, a, abox, b, bbox):
    A = Image.open(a).convert("RGB").crop(abox); B = Image.open(b).convert("RGB").crop(bbox)
    h = 360; A = A.resize((int(A.width * h / A.height), h)); B = B.resize((int(B.width * h / B.height), h))
    z = Image.new("RGB", (A.width + B.width + 8, h), (255, 255, 255)); z.paste(A, (0, 0)); z.paste(B, (A.width + 8, 0))
    name = f"r5_{k}_zoom.jpg"; z.save(f"{MEDIA}/{name}", "JPEG", quality=80); used.add(name); return name


def imgs(k, pairs):
    out = []
    for i, (src, label) in enumerate(pairs):
        out.append({"src": small(src, f"{k}_{i}"), "label": label, **({"cls": "after"} if label.startswith(("New", "Restored", "Try 1")) else {})})
    return out


data = []


def card(k, group, note, done, pics, zoom="", chips=None, extra=None):
    lt, pron, en = word(k); q = QA.get(k, {})
    facts = [["Your note", note], ["Done", done]] + ([["Extra check", extra]] if extra else [])
    data.append({"k": k, "group": group, "lt": lt, "pron": pron, "en": en, "imgs": imgs(k, pics), "zoom": zoom,
                 "chips": chips or [], "facts": facts, "qa": q.get("status", ""), "fails": q.get("fails", ""),
                 "warns": q.get("warnings", ""), "guess": q.get("guess", "")})


G1, G2, G3 = "Re-rolled whole", "Restored", "Your question"
R = lambda d, k, n: f"{d}/_rerolled/{k}.r{n}.png"

card("083_tevas", G1, "replace the third panel with an image that isn't a closeup of the hands",
     "Whole re-roll. Inset 3 is now the family: father, mother and the boy on a bench before their house. No hand close-up anywhere. The main picture is new too, since nothing is patched any more.",
     [(R(F62, "083_tevas", 9), "Round 4 (judged)"), (f"{F62}/083_tevas.png", "New")],
     extra="inset 3 read as a family on a bench, not a hand close-up; hands and limbs ok")
card("413_tuoktis", G1, "I like the staging of the first, failed, roll - the putting on of the ring. Let's try again, hopefully, no hand glitches",
     "The first round-3 staging is back word for word (the groom slides the ring on, her hand held out flat and still; insets: ring box, signing the register, guests throwing grain). Three whole re-rolls; try 1 has the cleanest hands and the insets as staged, so it is the card. Try 3 drew a hand close-up inset again. All three are kept.",
     [(R(F62, "413_tuoktis", 5), "Round 4 (judged)"), (f"{F62}/413_tuoktis.png", "Try 1 · picked"),
      (R(F62, "413_tuoktis", 7), "Try 2"), (R(F62, "413_tuoktis", 8), "Try 3")],
     chips=["3 tries"], extra="hands and limbs ok on all three tries")
card("A2-0085", G1, "Let's try the kaunas train station again, but re-roll, since in the kaunas station one, the vendor is reaching through the glass",
     "The Kaunas station rows round 4 reverted are back (settings row and staging: the 1953 hall with square pilasters and a coffered ceiling). Re-rolled with the clerk seated behind the glass, both hands on her own counter, pushing the ticket and change out through the slot at the foot of the window.",
     [(R(A2D, "A2-0085", 2), "Round 3 station (hand through the glass)"), (f"{A2D}/A2-0085.png", "New")],
     chips=["Kaunas station"], extra="clerk's hands stay on her side of the glass, on the counter")
card("A2-0359", G1, "first insert should show man when he was a patient, second insert should show him exiting the hospital, main image stays",
     "Masked edits are off, so the whole picture was re-rolled with the main scene written as it was drawn in round 4 and the two new insets: the same man earlier in pyjamas in a hospital bed with the same nurse; the same man walking out through the hospital's front doors. The main scene came out close to round 4 but is a new drawing, so both are shown.",
     [(R(V3, "A2-0359", 5), "Round 4 (main you kept)"), (f"{V3}/A2-0359.png", "New")],
     extra="insets read as the patient in bed and the man leaving the hospital; hands and limbs ok")
card("A2-0925", G1, "Even worse - stop editing and just reroll",
     "Re-rolled with the planner's fallback staging: both arms already in the coat sleeves, buttoning it with his right hand, a cap in his left; she points at the clock at three. Try 1 failed QA (both looked at the clock instead of at each other); try 2 has them look at each other.",
     [(R(V3, "A2-0925", 3), "Round 4 (judged)"), (R(V3, "A2-0925", 4), "Try 1 (QA gaze fail)"), (f"{V3}/A2-0925.png", "New")],
     chips=["2 tries"], extra="hands and limbs ok")
card("A2-1167", G1, "panels in first image were better, while main image of reroll is without error; model the panels after the first image",
     "Round-4 main scene kept as staged (normal-height door, host two paces inside, visitor with a cake tin) with the first version's insets: she hangs her coat while he stands by; the two of them at tea with a teapot and biscuits. Try 1 failed QA continuity (coat in the main picture, red jumper in the insets); try 2 names the red jumper under her coat.",
     [(R(V3, "A2-1167", 4), "First version (panels you liked)"), (R(V3, "A2-1167", 5), "Round 4 (main you liked)"),
      (f"{V3}/A2-1167.png", "New")],
     chips=["2 tries"], extra="door of ordinary height, host clear of the frame; hands and limbs ok")
card("A2-1431", G1, "Imperfect masking, bleeds outside of borders",
     "Whole re-roll with the same staging. Inset 1 is a foot sliding into a new shoe with the laces loose and the box beside it; no shoehorn.",
     [(R(A2D, "A2-1431", 4), "Round 4 (judged)"), (f"{A2D}/A2-1431.png", "New")],
     extra="no shoehorn; the hand in the shoe inset is whole and nothing crosses a frame")
card("A2-2002", G1, "reroll, this patching of images isn't working; staging is good otherwise",
     "Whole re-roll with the same staging, the right hand written in: raised at the plate, palm turned out, index finger up, the other fingers folded; her left hand rests on the gate. The declared \"7\" reads back.",
     [(R(V3, "A2-2002", 3), "Round 4 (judged)"), (f"{V3}/A2-2002.png", "New")],
     zoom=zoom2("A2-2002", R(V3, "A2-2002", 3), (740, 230, 920, 420), f"{V3}/A2-2002.png", (380, 100, 560, 320)),
     chips=["lettering declared"], extra="palm out, natural; left hand natural")
card("A2-2010", G1, "Hand is good, but now the chair is mangled",
     "Whole re-roll, same staging: the driver in the front-left seat reaches back with his right hand, palm up, coins on it; the passenger waves them off.",
     [(R(V3, "A2-2010", 3), "Round 4 (judged)"), (f"{V3}/A2-2010.png", "New")],
     extra="the offered hand reads as a right hand; seats and door whole")
card("A2-0660", G2, "Original is better - the angle is odd in the re-roll, and the man crossing the street seems to be coming out of the car, and the car is on the crosswalk",
     "The round-3 picture is back: the one you judged \"faces and hands are good\" on Round 3 Fixes and saw on the left of Round 4 Fixes. Its staging note went back with it. The round-4 re-roll is kept. The very first render (October 11) is also kept, untouched.",
     [(R(A2D, "A2-0660", 6), "Round 4 re-roll (rejected)"), (f"{A2D}/A2-0660.png", "Restored: round 3")])
card("055_bankas", G3, "Is the outside building historical? If it is, fine, but otherwise, it looks like it could be a courthouse",
     "Answered at the top of the page. OK keeps the card as it is; Redo re-rolls it whole with the outside inset rewritten (say in the note: the real corner, or another bank detail instead).",
     [(f"{F62}/055_bankas.png", "Current card")])

nf = sum(c["qa"] == "FAIL" for c in data); nw = sum(c["qa"] == "WARN" for c in data)
extra = {"col": "round5", "title": "Round 5 fixes", "hints": {
    G1: "the picture you judged beside the new one; nothing was patched",
    G2: "you preferred the earlier picture; the rejected one is kept",
    G3: "your question; the answer is above"},
    "lead": ["Everything done on your Round 4 Fixes verdicts. As you asked, nothing was patched: 9 cards were re-rolled whole and A2-0660 is back to its round-3 picture. Every earlier version is kept in the _rerolled folders.",
             f"QA (cold read, hands and limbs, plus the specific check your note asked for): {nf} fail, {nw} with notes. Two first tries failed (0925 gaze, 1167 coat colour) and were re-rolled once more. Spec 3.1.0 now carries the direction rule, main actors only, for new renders, and the whole-re-roll working rule. Mark OK or Redo; a note on a Redo says what to change."]}

Q055 = "055 bankas: is the outside building historical?"
A055 = ("<p><b>The building it is meant to be is historical; the drawing does not show it.</b> The card's settings row and "
        "staging place it in the <b>Bank of Lithuania</b> in Kaunas (Maironio g. 25 / K. Donelaičio g. 85; architect "
        "Mykolas Songaila; cornerstone 12 March 1925, opened 8 December 1928). The main picture is drawn as that bank's "
        "Operations Hall under its triangular skylight, which you called a good location. The outside inset was written "
        "loosely (\"the bank's pale neoclassical corner front with its tall columned entrance\") and the engine drew a "
        "generic portico: six columns under a flat entablature on a square corner.</p>"
        "<p>The real building has a <b>rounded corner</b> at the crossing of the two streets, a granite base, and "
        "<b>Kajetonas Sklėrius's sculpture group</b> (allegories of Agriculture, Industry and Warfare) on the pediment "
        "above the attic on the Maironio street side. None of that is in the inset. No source I read describes a "
        "columned portico outside; the deck's own location entry already lists the façade's column order as unverified. "
        "So your courthouse reading is fair, and it matters here: 035 teismas is staged with the Kaunas Palace of Justice "
        "front in an inset, so a columned front on 055 points at the court card.</p>"
        "<p>Sources: <a href=\"https://www.pinigumuziejus.lt/en/news/bank-of-lithuania-buildings-in-kaunas\">Money Museum, "
        "Bank of Lithuania buildings in Kaunas</a> (rounded corner, granite, sculpture group); "
        "<a href=\"https://www.pinigumuziejus.lt/en/eguide/the-bank-of-lithuanias-building-in-kaunas\">Money Museum e-guide</a> "
        "(architect, dates, corner of Donelaičio and Maironio). I could not check a photograph of the façade from here.</p>"
        "<p>Your call on the 055 card below: <b>OK</b> keeps it. <b>Redo</b> re-rolls it whole with the inset rewritten "
        "to the verified marks (rounded corner, sculpture group on the pediment), or with that inset replaced by another "
        "bank detail such as the vault door; say which in the note.</p>")
ans_html = (f'<section class="answers" aria-labelledby="ans-h"><h2 id="ans-h">Your question</h2>'
            f'<h3>{html.escape(Q055)}</h3>{A055}</section>')
ans_css = (".answers{max-width:70ch;margin:0 0 1.6em;padding:12px 16px;border:1px solid var(--rule);border-radius:2px}"
           ".answers h2{font-family:var(--narrow);font-size:1rem;text-transform:uppercase;letter-spacing:.06em;margin:0 0 .6em}"
           ".answers h3{font-size:1.05rem;margin:0 0 .5em}.answers p{margin:0 0 .7em}.answers a{color:var(--teal)}"
           ".pic img{width:100%;height:auto}\n</style>")
TPL = open("a2_build/review_template/template_review.html", encoding="utf-8").read()
assert '<section class="lead" id="lead"></section>' in TPL and "</style>" in TPL
# the answer to the owner's question goes at the very top, above the lead
doc = (TPL.replace("__TITLE__", "Round 5 Fixes").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
       .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False))
       .replace('<section class="lead" id="lead"></section>', ans_html + '\n  <section class="lead" id="lead"></section>')
       .replace("</style>", ans_css, 1))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
json.dump(sorted(used), open(os.path.join(OUT, "media_list.json"), "w"))
print(len(data), "cards", len(used), "media", "QA fail", nf, "warn", nw)
