# -*- coding: utf-8 -*-
"""Review page "Round 4 Fixes" (2026-10-19): every row of a2_build/round4/plan.csv, the picture the owner judged beside
the new one, his note, what was done, QA; OK / Redo + note per card. Opens with the planner's four answers.
db (capabilities db + user): collection "round4", general notes "round4_meta/general".
    python3 a2_build/round4/build_page.py        -> a2_build/round4/page/index.html + page/media/r4_*.jpg"""
import csv, datetime, glob, html, json, os, re
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
OUT = os.path.join(HERE, "page"); MEDIA = os.path.join(OUT, "media"); os.makedirs(MEDIA, exist_ok=True)
PLAN = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "plan.csv"), encoding="utf-8"))}
REG = json.load(open(os.path.join(HERE, "edit_regions.json"), encoding="utf-8"))
QA = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "qa_round4.csv"), encoding="utf-8"))}
EXTRA_QA = {}
for r in csv.DictReader(open(os.path.join(HERE, "qa_round4_extra.csv"), encoding="utf-8")):
    EXTRA_QA.setdefault(r["key"], {})[r["check"]] = json.loads(r["result"])
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
master = {r["#"].zfill(3): r for r in csv.DictReader(open("master_wordlist.csv", encoding="utf-8"))}
sent = {r["id"]: r for r in csv.DictReader(open("a2_build/sentences/sentences.csv", encoding="utf-8")) if r.get("id")}
CUT = datetime.datetime(2026, 10, 19, 10, 10).timestamp()      # round 4 started after this (VM clock, UTC)
used = set()


def word(k):
    if k.startswith("S-"):
        s = sent[k]; return s["lt"].replace("{", "").replace("}", ""), "", s["en"]
    if k.startswith("A2"):
        w = a2[k]; return w["lithuanian_TARGET"], w.get("lt_pron", ""), w["english"]
    m = master[k[:3]]; return m["lithuanian_TARGET"], m["lt_pron"], m["english"]


A2_IMG = {"A2-1326", "A2-0085", "A2-0660", "A2-1431", "A2-1360", "A2-0649"}


def folder(k):
    """Where this round wrote the card (the folder the build reads first for it)."""
    return "out_deck_f62" if k[0].isdigit() else "out_deck_a2" if k in A2_IMG else "out_phrases_v3"


def judged(k, d):
    """The picture the owner judged on Round 3 Fixes: the newest _rerolled version made before round 4."""
    old = [p for p in glob.glob(f"{d}/_rerolled/{k}.r*.png") if re.search(r"\.r\d+\.png$", p) and os.path.getmtime(p) < CUT]
    return max(old, key=os.path.getmtime)


def small(src, tag):
    name = f"r4_{tag}.jpg"; im = Image.open(src).convert("RGB"); im.thumbnail((800, 800)); im.save(f"{MEDIA}/{name}", "JPEG", quality=78)
    used.add(name); return name


def zoomimg(k, b, a, regions):
    pts = []
    for r in regions:
        if "rect" in r: pts += [r["rect"][:2], r["rect"][2:]]
        elif "ring" in r: pts += [r["ring"][:2], r["ring"][2:]]
        else: pts += r["poly"]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]; pad = 40
    bb = (max(0, min(xs) - pad), max(0, min(ys) - pad), min(1536, max(xs) + pad), min(1024, max(ys) + pad))
    A = Image.open(b).convert("RGB").crop(bb); B = Image.open(a).convert("RGB").crop(bb)
    s = 420 / max(A.size); A = A.resize((int(A.width * s), int(A.height * s))); B = B.resize(A.size)
    z = Image.new("RGB", (A.width * 2 + 8, A.height), (255, 255, 255)); z.paste(A, (0, 0)); z.paste(B, (A.width + 8, 0))
    name = f"r4_{k}_zoom.jpg"; z.save(f"{MEDIA}/{name}", "JPEG", quality=80); used.add(name); return name


data = []


def card(k, group, imgs, done, zoom="", chips=None, extra_facts=None):
    lt, pron, en = word(k); q = QA.get(k, {})
    facts = [["Your note", PLAN[k]["owner_note"]], ["Done", done]] + (extra_facts or [])
    data.append({"k": k, "group": group, "lt": lt, "pron": pron, "en": en, "imgs": imgs, "zoom": zoom, "chips": chips or [],
                 "facts": facts, "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""),
                 "guess": q.get("guess", "")})


def pair(k, d, blabel, alabel):
    b = judged(k, d)
    return b, [{"src": small(b, k + "_before"), "label": blabel}, {"src": small(f"{d}/{k}.png", k + "_after"), "label": alabel, "cls": "after"}]


def xq(k):
    """One line from the extra checks (qa_round4_extra.csv)."""
    e = EXTRA_QA.get(k, {}); out = []
    lm = e.get("limbs")
    if lm:
        bad = [n for n in ("limbs_ok", "props_ok", "hands_ok") if lm.get(n) is False]
        out.append("hands and limbs: " + ("ok" if not bad else "; ".join(lm.get(n.replace("_ok", "_note"), n) for n in bad)))
    a = e.get("ask")
    if a:
        out.append("specific check: " + (a.get("note") or json.dumps(a, ensure_ascii=False)))
    return " · ".join(out)


# ---------------------------------------------------------------- 1 restores
REST = {"097_prezidentas": "The shipped picture is back: an anonymous man president, no likeness, no Vytis. 097 is out of the likeness list; the emblem allowance stays routed to 097 but is now dormant, so no card in the deck shows a Vytis.",
        "106_zaidejas": "The shipped picture is back (football field). The staging note and the settings row went back to their old values (Vingis park sports ground), so the State Stadium will not return on a re-roll.",
        "107_sirgalius": "The shipped picture is back (stadium stand). The settings row is place-less again (\"a place would compete with the subject\").",
        "A2-1326": "The shipped picture is back, with its letterbox inset. The optional post-office settings row was removed.",
        "A2-0085": "Restored on the planner's recommendation: the change was for the location (the 1953 Kaunas station hall), which is the weakest real place in the bank for a free-1981 deck and unrecognisable at card size. Staging and settings row reverted. Say Redo if you would rather keep the station-hall version."}
for k, done in REST.items():
    d = folder(k); b, imgs = pair(k, d, "Round 3 render (rejected)", "Original, restored")
    card(k, "Originals restored", imgs, done, chips=(["planner's recommendation"] if k == "A2-0085" else []))

# ---------------------------------------------------------------- 2 re-rolls
RR = {"055_bankas": "Re-roll in the same Bank of Lithuania hall. The brass grille now stops at chest height with an open arch above the ledge, so nothing crosses the cashier's face. First roll.",
      "413_tuoktis": "Re-roll: bride holding a large bouquet, groom's arm round her back, the official with a sash and the register, rings on a cushion. Hands are small and occupied. The new roll drew its third inset as a hand close-up, so one masked edit replaced it with the wedding car the staging asks for.",
      "A2-0660": "Re-roll with the same scene: the mother and the boy cross from left to right, both in profile heading right; strap, shoes inset and green-only signal kept.",
      "A2-0359": "Re-roll with a new scene: the discharged patient holds out flowers in a paper wrap with both hands; the nurse takes them with one hand, clipboard in the other. No clasp, no deep bow.",
      "A2-1162": "Re-roll: the man with the rod stands two steps outside the open office door, so the door and its frame are behind him; his colleague waves from the threshold.",
      "A2-1167": "Re-roll: an ordinary-height door open flat against the wall, the host two paces inside the hallway, clear of the frame, sweeping his arm in; the visitor with a cake tin on the mat.",
      "A2-1172": "Your scenario, set at the Sartai trotting races on the frozen lake: one man points at the leading horse, his friend gives a firm nod and a flat decisive chop. Insets: the leading trotter; the betting slip (blank).",
      "A2-1184": "Re-roll: letter in her left hand, right hand flat over her mouth, eyes wide; both hands named, so no extra arm. Insets: the torn envelope; a postman cycling past the window.",
      "A2-1185": "New scenario: a girl stands stiff over a broken plate, hands on her cheeks; her grandmother, crouching with the dustpan, smiles and lays a hand on her shoulder. No scolding.",
      "A2-2010": "Re-roll with your staging, handedness pinned. One correction to the plan: it put the driver's thumb on the kerb side, but a right hand turned palm-up and reaching back to the rear door has its thumb toward the back of the car, away from the kerb. The staging says that; QA reads the offered hand as a right hand.",
      "A2-2022": "Re-roll: the speaker's hand flat on his chest, half under the lapel; everyone across the table holds papers upright or keeps hands below the edge, so no hands rest on the table."}
for k, done in RR.items():
    d = folder(k); b, imgs = pair(k, d, "Round 3 picture (judged)", "Re-rolled")
    card(k, "Re-rolls", imgs, done, extra_facts=[["Extra check", xq(k)]] if xq(k) else None,
         chips=(["Sartai races"] if k == "A2-1172" else ["deviation from plan"] if k == "A2-2010" else []))

# ---------------------------------------------------------------- 3 masked edits
ED = {"083_tevas": "Your option 2: the joined hands of the father and boy were cropped from the main picture (which you passed) and placed in inset 3, then one edit of the seam band only so the paper and ink match. No hands were generated.",
      "A2-0925": "One tight edit of the hand at his collar: the sleeve cuff now hangs over the knuckles so only the fingertips show. If it still reads wrong, the fallback re-roll staging is written in the plan.",
      "A2-1431": "Inset 1 only: a foot in a dark sock sliding into a new shoe, laces loose, the box beside it. No hand, no shoehorn.",
      "A2-2002": "Her right hand only (the left hand was fenced off): palm turned out, index finger up at the plate. The declared \"7\" still reads back.",
      "A2-2026": "Inset 1 replaced as you asked: the man's hand passes two folded banknotes to the clerk through the round opening in the glass.",
      "A2-2029": "Inset 1 no longer shows a hand from the front window. The plan's view out of the rear side window was drawn first, but QA then read the whole card as \"On the right\" twice (round 3 passed). So the round-3 inset is back, with only the arm removed: the taxi at the kerb, no hand.",
      "S-0051": "Last inset replaced: the same boy blowing out the candles, hands out of sight. Two attempts drew four candles; the third has five.",
      "A2-1191": "The blank poster now shows Velnio nuotaka (1974, dir. Arūnas Žebriūnas), a folk-fantasy musical two young men could well have judged \"so-so\" in 1981. The same poster appears small in the lower inset. Title declared in card_text and read back exactly by QA.",
      "A2-1360": "The blank playbill now shows Balys Sruoga's Milžino paunksmė (1932), with Ž and Ė read back exactly by QA. Title declared in card_text.",
      "A2-0649": "Inset 1 (the plain modernist front) replaced by a man posting letters into the blue post box. The Kaunas hall with the linen-weave floor stays as the main picture."}
for k, done in ED.items():
    d = folder(k); b, imgs = pair(k, d, "Round 3 picture (judged)", "After the edit")
    regs = REG[k]["regions"]
    if k == "A2-2029":   # show the whole inset, not only the last small region
        regs = [{"rect": [20, 700, 597, 960]}]
    card(k, "Masked edits", imgs, done, zoom=zoomimg(k, b, f"{d}/{k}.png", regs),
         extra_facts=[["Extra check", xq(k)]] if xq(k) else None,
         chips=(["lettering declared"] if k in ("A2-1191", "A2-1360", "A2-2002") else ["deviation from plan"] if k == "A2-2029" else []))

order = ["Originals restored", "Re-rolls", "Masked edits"]
data.sort(key=lambda c: order.index(c["group"]))
n = {g: sum(c["group"] == g for c in data) for g in order}
nf = sum(c["qa"] == "FAIL" for c in data); nw = sum(c["qa"] == "WARN" for c in data)
extra = {"col": "round4", "title": "Round 4 fixes", "hints": {
    "Originals restored": "you preferred the original; the round-3 render is kept in _rerolled",
    "Re-rolls": "the picture you judged beside the new one",
    "Masked edits": "only the area over the problem was repainted; the close-up shows it"},
    "lead": [f"Everything done on your Round 3 Fixes verdicts, following the planner's round-4 plan: {n['Originals restored']} originals restored, {n['Re-rolls']} re-rolls and {n['Masked edits']} masked edits, including the two period posters.",
             f"QA (cold read plus the hands-and-limbs check, and the same hands check on every phrase card): {nf} fail, {nw} with notes; no limb, prop or hand finding. The notes are guess wording and stray acts. Mark OK or Redo; a note on a Redo says what to change."]}

ANSWERS = [
    ("A2-0667 banko skyrius: is this a historical bank?",
     "Half of it. The hall the people stand in is an invented branch office. The building seen through the window is real: the Bank of Lithuania head office in Kaunas (Mykolas Songaila, opened 1928). Its own hall is already the main picture of 055 bankas, so the two bank cards share one real place. No verified interwar branch interior exists to use instead. Planner's advice: leave 0667 as it is."),
    ("A2-0649 paštas: a prettier historical post office, or drop the outside inset?",
     "The Kaunas Central Post Office (Vizbaras, 1931) is famous for its hall, with the floor tiled like a woven linen towel, not for its plain flat-roofed front. Done as recommended: the hall stays as the main picture and the outside inset is now a post box. Lithuania's one pretty historic post-office front is Klaipėda's red-brick building of 1893; if you want it, it belongs on a different card, so the two post offices on one card are not different buildings."),
    ("122 menininkas (Čiurlionis): does the Vilnius setting suit him?",
     "Yes. He lived in Vilnius in 1907–08, in a room in the Old Town a few hundred metres from the Vilnia and Užupis, and Karalių pasaka (1909) belongs to that period. The one liberty is the easel on the riverbank: he painted indoors from imagination, and the outdoor easel is there so the card reads as \"artist\". Druskininkai would suit him better only on a fresh re-roll, which would put the face you liked at risk. Planner's advice: leave the card."),
    ("Direction of movement: should \"main actors head right\" become a standing rule?",
     "The planner proposes yes, as a default at re-roll only: figures who walk, ride, drive or carry something travel left to right, and the place they head for lies to their right. Exceptions: cards whose meaning is a side or direction (left, right, back, return), two-panel conversations, and scenes whose goal sits on the left. QA would flag it as a note, not a fail. Nothing has been added to the code or the spec: this is your decision (answers.md §4, also on the Review Desk). A2-0660 already heads right."),
]
ans_html = ('<section class="answers" aria-labelledby="ans-h"><h2 id="ans-h">The planner\'s four answers</h2><dl>'
            + "".join(f"<dt>{html.escape(q)}</dt><dd>{html.escape(a)}</dd>" for q, a in ANSWERS) + "</dl></section>")
ans_css = (".answers{max-width:70ch;margin:0 0 1.6em;padding:12px 16px;border:1px solid var(--rule);border-radius:2px}"
           ".answers h2{font-family:var(--narrow);font-size:1rem;text-transform:uppercase;letter-spacing:.06em;margin:0 0 .6em}"
           ".answers dl{margin:0;display:grid;gap:.4em}.answers dt{font-weight:700;margin-top:.5em}.answers dd{margin:0}"
           ".pic img{width:100%;height:auto}\n</style>")
TPL = open("a2_build/review_template/template_review.html", encoding="utf-8").read()
assert '<section class="lead" id="lead"></section>' in TPL and "</style>" in TPL
doc = (TPL.replace("__TITLE__", "Round 4 Fixes").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
       .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False))
       .replace('<section class="lead" id="lead"></section>', '<section class="lead" id="lead"></section>\n  ' + ans_html)
       .replace("</style>", ans_css, 1))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
json.dump(sorted(used), open(os.path.join(OUT, "media_list.json"), "w"))
print(len(data), "cards", n, len(used), "media", "QA fail", nf, "warn", nw)
