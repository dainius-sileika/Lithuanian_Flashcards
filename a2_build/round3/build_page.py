# -*- coding: utf-8 -*-
"""Review page "Round 3 Fixes" (2026-10-19): every restored original, hand-fix redo, anatomy fix and historical
roll-out card of a2_build/round3/README.md, before/after, the owner's note, QA, OK / Redo + note.
db (capabilities db + user): collection "round3", general notes "round3_meta/general".
    python3 a2_build/round3/build_page.py        -> a2_build/round3/page/index.html + page/media/r3_*.jpg"""
import csv, glob, json, os, re
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
OUT = os.path.join(HERE, "page"); MEDIA = os.path.join(OUT, "media"); os.makedirs(MEDIA, exist_ok=True)
REG = json.load(open(os.path.join(HERE, "edit_regions.json"), encoding="utf-8"))
BEFORE = json.load(open("a2_build/hand_fixes/before.json"))["before"]
a2 = {r["id"]: r for r in csv.DictReader(open("a2_build/a2_wordlist.csv", encoding="utf-8"))}
master = {r["#"].zfill(3): r for r in csv.DictReader(open("master_wordlist.csv", encoding="utf-8"))}
sent = {r["id"]: r for r in csv.DictReader(open("a2_build/sentences/sentences.csv", encoding="utf-8")) if r.get("id")}
qa = {}
for f in ("qa_items12.csv", "qa_historical.csv", "qa_restage.csv"):
    for r in csv.DictReader(open(os.path.join(HERE, f), encoding="utf-8")):
        qa[r["key"]] = r
used = set()

MERGED = {r["id"]: r for r in csv.DictReader(open("a2_build/merged_keys.csv", encoding="utf-8"))}
a2.update({k: v for k, v in MERGED.items() if k not in a2})

def word(k):
    if k.startswith("S-"):
        s = sent[k]; return s["lt"].replace("{", "").replace("}", ""), "", s["en"]
    if k.startswith("A2"):
        w = a2[k]; return w["lithuanian_TARGET"], w.get("lt_pron", ""), w["english"]
    m = master[k[:3]]; return m["lithuanian_TARGET"], m["lt_pron"], m["english"]

def nmax(pattern):
    fs = [p for p in glob.glob(pattern) if re.search(r"\.r(\d+)\.png$", p)]
    return max(fs, key=lambda p: int(re.search(r"\.r(\d+)\.png$", p).group(1)))

def prevs(k, d):
    out = []
    for line in open(f"{d}/gen_log.jsonl"):
        try: j = json.loads(line)
        except Exception: continue
        if j.get("key") == k and j.get("prev") and j.get("edit"): out.append(f"{d}/" + j["prev"])
    return out

def small(src, tag):
    name = f"r3_{tag}.jpg"; im = Image.open(src).convert("RGB"); im.thumbnail((800, 800)); im.save(f"{MEDIA}/{name}", "JPEG", quality=78)
    used.add(name); return name

def zoomimg(k, b, a):
    pts = []
    for r in REG[k]["regions"]:
        pts += [r["rect"][:2], r["rect"][2:]] if "rect" in r else r["poly"]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]; pad = 50
    bb = (max(0, min(xs) - pad), max(0, min(ys) - pad), min(1536, max(xs) + pad), min(1024, max(ys) + pad))
    A = Image.open(b).convert("RGB").crop(bb); B = Image.open(a).convert("RGB").crop(bb)
    s = 420 / max(A.size); A = A.resize((int(A.width * s), int(A.height * s))); B = B.resize(A.size)
    z = Image.new("RGB", (A.width * 2 + 8, A.height), (255, 255, 255)); z.paste(A, (0, 0)); z.paste(B, (A.width + 8, 0))
    name = f"r3_{k}_zoom.jpg"; z.save(f"{MEDIA}/{name}", "JPEG", quality=80); used.add(name); return name

data = []
def card(k, group, imgs, note, done, zoom="", extra=None):
    lt, pron, en = word(k); q = qa.get(k, {})
    data.append({"k": k, "group": group, "lt": lt, "pron": pron, "en": en, "imgs": imgs, "zoom": zoom,
                 "chips": extra or [], "facts": [["Owner said", note], ["Done", done]],
                 "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", "")})

D1 = lambda k: "out_deck_a2" if k.startswith("A2") else "out_deck_f62"
# 1a restored originals
REST = {l.split()[0]: l for l in open(os.path.join(HERE, "restore_log.txt")) if " restored from " in l}
for k, note in [("174_vynas", "Original is better"), ("388_sokti", "Original is better"), ("456_karstas", "Original is better"), ("472_laimingas", "Original is better"),
                ("A2-0473", "Original is better"), ("A2-0568", "Original is better"), ("A2-1411", "Original is OK"), ("A2-1817", "Original is OK")]:
    d = D1(k); rej = d + "/_rerolled/" + re.search(r"_rerolled/(\S+)", REST[k].split("failed edit ->")[1]).group(1)
    card(k, "Originals restored", [{"src": small(rej, k + "_before"), "label": "Rejected hand-fix edit"},
                                   {"src": small(f"{d}/{k}.png", k + "_after"), "label": "Original, restored", "cls": "after"}],
         note + " (your verdict on Hand Fixes)", "The original picture is the current file again; the edit is kept in _rerolled/.")
# 1b redos
RED = {"083_tevas": ("The father's hands are too huge in insert 3", "Masked edit of inset 3 only (the inset-1 fix stays): the father's hand in natural proportion."),
       "271_nugara": ("redo is garbled", "Re-roll. The hand-on-back inset is replaced by a man bending to lift a crate by its handles."),
       "413_tuoktis": ("Both are corrupted", "Re-roll. One ring hand meets one flat, still hand; the hand close-up inset became rings in an open box."),
       "459_vesus": ("Redo", "Re-roll. The man holds a mug in both hands, legs uncrossed."),
       "A2-0660": ("both mangled", "Re-roll. No clasped hands: the child holds the handbag strap; inset 2 is shoes stopping at the kerb line; the signal shows only green."),
       "A2-1309": ("No hanging medal", "Re-roll. Nobody hangs a medal: it is already worn; insets: the medal close, a medal in its case, the podium."),
       "A2-1416": ("Both are mangled", "Re-roll. The dance-hold inset became two dancers with hands on their own hips."),
       "A2-1431": ("Not a mirror image", "Re-roll. No mirror anywhere, in the main picture or the hat inset.")}
for k, (note, done) in RED.items():
    d = D1(k); orig = BEFORE[k]
    rej = prevs(k, d)[-1] if k == "083_tevas" else nmax(f"{d}/_rerolled/{k}.r*.png")
    card(k, "Hand-fix redos", [{"src": small(orig, k + "_orig"), "label": "Original"}, {"src": small(rej, k + "_before"), "label": "Rejected redo"},
                               {"src": small(f"{d}/{k}.png", k + "_after"), "label": "New", "cls": "after"}], note, done,
         zoom=zoomimg(k, rej, f"{d}/{k}.png") if k == "083_tevas" else "")
# 2 anatomy
NOTES2 = {"A2-0359": "Main image man's fingers are mangled", "A2-0377": "Insert 1, thumb goes through the wallet", "A2-0888": "Young woman's glass is invisible",
          "A2-0894": "Man's right hand has a thumb and five knuckles", "A2-0895": "Boys and mothers hands are AI nonsense", "A2-0917": "slightly mangled finger in the first insert",
          "A2-0925": "Weird things going on with the man's arms", "A2-1162": "Main panel door has no frame", "A2-1167": "AI nonsense, man merged with the door in the first main image",
          "A2-1184": "AI nonsense, multiple hands in main image", "A2-1185": "first insert is weird", "S-0051": "Toy in last insert is mangled and not clear",
          "A2-1934": "Hand on shoulder is mangled", "A2-2002": "Main woman's hand is garbled", "A2-2010": "taxi man's hand is garbled; he's also reaching out from the back seat",
          "A2-2022": "Main panel, right-most man, has garbled hands", "A2-2026": "First insert is garbled"}
DONE2 = {"A2-0359": "Masked edit of the clasped hands.", "A2-0377": "Masked edit of inset 1: both hands grip the purse frame from outside.",
         "A2-0917": "Masked edit, third try (fingers only); the first two left a seam on the forearm.", "A2-0925": "Masked edit of both arms: one in its sleeve, the other pulling the collar.",
         "A2-1162": "Masked edit: a door jamb added on the hinge side.", "A2-1167": "Masked edit: the door edge is a clean line beside him, his hand on the handle.",
         "A2-1184": "Masked edit: the third hand (at the mouth) removed; her mouth is open in disbelief.", "A2-1185": "Masked edit: the stray hand behind the young man removed.",
         "S-0051": "Masked edit, second try: a clear red tipper lorry and no extra hands.", "A2-1934": "Masked edit of the hand on the shoulder.",
         "A2-2002": "Masked edit of both of the old woman's hands.", "A2-2022": "Masked edit of the clasped hands.", "A2-2026": "Masked edit, third try: the clerk's hand on the ticket roll.",
         "A2-0888": "The edit could not add her glass; re-rolled twice with staging that names four glasses in four hands.",
         "A2-0894": "Two edits erased the hand; re-rolled: the customer holds the loaf against his chest, string bag on his arm.",
         "A2-0895": "Re-roll (the roll-out edit had already failed): no clasped hands, the boy waves a paper tricolour.",
         "A2-2010": "Re-roll with your staging: the driver sits front left behind the wheel and reaches back to the open rear door."}
V3 = lambda k: "out_phrases_v3/round2" if k in ("A2-0377", "A2-0895") else "out_phrases_v3"
for k in NOTES2:
    d = V3(k)
    if k in ("A2-0888", "A2-0894"):
        b = prevs(k, d)[0]; grp = "Anatomy fixes: re-rolls"; z = ""
    elif k in ("A2-0895", "A2-2010"):
        b = nmax(f"{d}/_rerolled/{k}.r*.png"); grp = "Anatomy fixes: re-rolls"; z = ""
    else:
        b = prevs(k, d)[-1]; grp = "Anatomy fixes: masked edits"; z = zoomimg(k, b, f"{d}/{k}.png")
    card(k, grp, [{"src": small(b, k + "_before"), "label": "Before"}, {"src": small(f"{d}/{k}.png", k + "_after"), "label": "After", "cls": "after"}],
         NOTES2[k], DONE2[k], zoom=z)
# 3 historical
CP = {l.split(":")[0]: l for l in open(os.path.join(HERE, "historical_copyin.txt"))}
H_ADOPT = {"012_lektuvas": "Lituanica: passed, with faces. Use it.", "097_prezidentas": "Adamkus with the Vytis: ok. Use it.",
           "A2-1297": "Sports Hall: passed.", "A2-1769": "Freedom Statue: ok."}
for k, note in H_ADOPT.items():
    d = D1(k); b = d + "/_rerolled/" + re.search(r"_rerolled/(\S+)", CP[k]).group(1)
    card(k, "Historical: test renders adopted", [{"src": small(b, k + "_before"), "label": "Shipped card"}, {"src": small(f"{d}/{k}.png", k + "_after"), "label": "Test render, now in the deck", "cls": "after"}],
         note, "Copied from the Historical Test into the deck folder.")
H_NEW = {"035_teismas": ("redo: Don't use the cross for the courthouse, use the flag", "Re-roll: a large tricolour behind the bench and no other emblem; the emblem rule now reaches 097 only."),
         "048_ligonine": ("(plan) 1939 Kaunas Clinics", "Long pale wing, brick chimney, pines, canopied entrance with the ambulance."),
         "055_bankas": ("(plan) Bank of Lithuania", "The hall under the glass skylight with black columns; the columned corner front as an inset."),
         "106_zaidejas": ("(plan) State Stadium", "Grass pitch, cinder track, low wooden grandstand and oaks."),
         "107_sirgalius": ("(plan) State Stadium", "Fans in the covered wooden grandstand with a tricolour scarf."),
         "138_komanda": ("Yes, the 1939 basketball team", "Ten players in white kit with the diagonal tricolour band under the four steel arches, a coach; the tall centre as the Lubinas nod."),
         "113_gydytojas": ("All three (likeness: Basanavičius)", "The man doctor in Basanavičius's likeness: long white beard, high bald forehead, frock coat under the white coat."),
         "122_menininkas": ("All three (likeness: Čiurlionis)", "The man artist in Čiurlionis's likeness, painting two crowned figures over a glowing globe."),
         "A2-0782": ("All three (likeness: Gustaitis)", "The engineer in Gustaitis's likeness at a drawing of a small low-wing monoplane.")}
for k in ["A2-0085", "A2-0645", "A2-0649", "A2-0652", "A2-0653", "A2-0656", "A2-0658", "A2-0812", "A2-1260", "A2-1282", "A2-1293", "A2-1360", "A2-1747", "A2-0667", "A2-1326", "A2-1357"]:
    opt = k in ("A2-0667", "A2-1326", "A2-1357")
    H_NEW[k] = ("(plan) A2 place from settings_rows.csv" + (", optional row" if opt else ""), "Rendered from the planner's staging line" + (" (completed by the executor from a partial line)" if opt else "") + ".")
for k, (note, done) in H_NEW.items():
    d = D1(k); b = nmax(f"{d}/_rerolled/{k}.r*.png")
    card(k, "Historical: new renders", [{"src": small(b, k + "_before"), "label": "Shipped card"}, {"src": small(f"{d}/{k}.png", k + "_after"), "label": "New", "cls": "after"}],
         note, done, extra=(["likeness, face words unverified"] if k in ("113_gydytojas", "122_menininkas", "A2-0782", "138_komanda") else []))
card("123_autorius", "Historical: kept as shipped", [{"src": small("out_deck_f62/123_autorius.png", "123_autorius_after"), "label": "Shipped card, unchanged"}],
     "Keep original", "Not changed; the test staging was taken back out and 123 no longer gets a likeness.")

# 5 planner round 3: restaged scenes, overlaps, merges, stresses, A2-0964
import datetime
CUT = datetime.datetime(2026, 10, 18, 23, 40).timestamp()
PICKS = {}
for line in open("out_phrases_v3/picks.jsonl"):
    try: j = json.loads(line); PICKS[j["key"]] = j["restored"]
    except Exception: pass
RS = {r["ids"].split()[0]: r for r in csv.DictReader(open("a2_build/rollout_round3/restage.csv", encoding="utf-8"))}
for k, r in RS.items():
    d = "out_phrases_v3"
    if k in ("A2-2001", "A2-2003"):
        b = prevs(k, d)[0]; done = ("Masked edit of the kiosk inset (the same young man now phones from it), then a second pass emptied the kiosk behind the bench." if k == "A2-2001"
                                    else "Masked edit: a sun disc added high in the right panel's sky.")
    else:
        old = [p for p in glob.glob(f"{d}/_rerolled/{k}.r*.png") if re.search(r"\.r\d+\.png$", p) and os.path.getmtime(p) < CUT]
        b = max(old, key=os.path.getmtime)
        if k in PICKS:   # pick_best had restored an earlier roll: the judged picture went back into the vacated slot
            b = f"{d}/_rerolled/{PICKS[k]}"
        n_new = len([p for p in glob.glob(f"{d}/_rerolled/{k}.r*.png") if re.search(r"\.r\d+\.png$", p) and os.path.getmtime(p) >= CUT]) + 1
        done = "Re-rolled with the planner's new scene" + (f" ({n_new} rolls; QA picked the last)" if n_new > 1 else "") + ": " + r["new_staging"][:400] + ("…" if len(r["new_staging"]) > 400 else "")
        if k == "A2-0385":
            done = "Merged card (absorbs A2-1149 atsargiai). " + done
    card(k, "Restaged scenes (planner round 3)", [{"src": small(b, k + "_before"), "label": "Before"}, {"src": small(f"{d}/{k}.png", k + "_after"), "label": "After", "cls": "after"}],
         r["owner_note (review page, verbatim)"] or "(merge: one picture for both senses)", done, zoom=zoomimg(k, b, f"{d}/{k}.png") if k == "A2-2003" else "")
for k, note in [("A2-2007", "Overlap with A2-0917 kept"), ("A2-2012", "Overlap with A2-0964 kept"), ("A2-2020", "Overlap with A2-0374 kept")]:
    card(k, "Overlaps kept: first render", [{"src": small(f"out_phrases_v3/{k}.png", k + "_after"), "label": "First render", "cls": "after"}],
         note, "Back to render = yes and drawn for the first time from its existing staging.")
for gone, surv, note, done in [("A2-1187", "A2-0354", "Sudie into Viso gero, with a back note", "Viso gero keeps its card and picture; its usage line now ends: \"Sudie — a solemn, final goodbye (from su Dievu, 'with God'); the old word, kept today for long or last partings.\" Sudie's row moved to merged_keys.csv."),
                               ("A2-1149", "A2-0385", "atsargiai into Atsargiai!", "Atsargiai! keeps its card (pron Atsargiaĩ!, LKŽ adverb form) and gets the icy-pavement picture above; 1149's row moved to merged_keys.csv."),
                               ("A2-1944", "A2-1995", "1944 into 1995 (same phrase)", "A2-1995 survives with both phrasings; pron Kaip rãšoma? / Paraidžiui, prašaũ. (paraidžiui not yet checked)."),
                               ("A2-1958", "A2-1991", "1958 into 1991 (same meaning)", "A2-1991, the sentence form, survives; english_alt gains 'would prefer; prefer'.")]:
    d = V3(surv) if os.path.exists(f"{V3(surv)}/{surv}.png") else "out_phrases_v3"
    lt, pron, en = word(gone)
    card(surv, "Merges applied", [{"src": small(f"{d}/{surv}.png", surv + "_merge"), "label": f"{surv} (survives)", "cls": "after"}],
         note, f"Absorbed: {gone} {lt} ({en}). " + done)
    data[-1]["k"] = f"merge-{gone}"
S58 = {r["id"]: r for r in csv.DictReader(open("a2_build/stress_58_resolved.csv", encoding="utf-8"))}
for k in ("A2-0356", "A2-0900", "A2-0910"):
    s = S58[k]
    card(k, "Stresses to confirm (medium confidence)", [], "Confirm or correct the stress", f"Applied: {s['stressed']}. Source: {s['source']}. {s['note']}".strip())
    data[-1]["k"] = f"stress-{k}"; data[-1].update(qa="", fails="", warns="", guess="")
card("A2-0964", "A2-0964 wording", [], "I think it's 'parekomenduoti'", "Now \"Ar galite ką nors parekomenduoti?\" (pron Ar̃ gãlite ką̃ nórs parekomendúoti?), also in the cloze example, recording list and usage note (tu: Ar gali ką nors parekomenduoti?; everyday speech often says pasiūlyti). Planner verdict and sources: rollout_round3/NOTE_0964_parekomenduoti.md.")
data[-1]["k"] = "word-A2-0964"; data[-1].update(qa="", fails="", warns="", guess="")

order = ["Originals restored", "Hand-fix redos", "Anatomy fixes: masked edits", "Anatomy fixes: re-rolls", "Historical: test renders adopted", "Historical: new renders", "Historical: kept as shipped", "Restaged scenes (planner round 3)", "Overlaps kept: first render", "Merges applied", "Stresses to confirm (medium confidence)", "A2-0964 wording"]
data.sort(key=lambda c: order.index(c["group"]))
n = {g: sum(c["group"] == g for c in data) for g in order}
extra = {"col": "round3", "title": "Round 3 fixes", "hints": {
    "Originals restored": "you preferred the original on the Hand Fixes page",
    "Hand-fix redos": "original, the redo you rejected, and the new picture",
    "Anatomy fixes: masked edits": "only the area over the problem was repainted; the close-up shows it",
    "Anatomy fixes: re-rolls": "drawn again with staging that keeps the hands simple",
    "Historical: test renders adopted": "the renders you passed on the Historical Test",
    "Historical: new renders": "the rest of the A5 plan",
    "Historical: kept as shipped": "your call: keep the original",
    "Restaged scenes (planner round 3)": "the planner's new scenes for your scenario redos",
    "Overlaps kept: first render": "you kept these as separate cards",
    "Merges applied": "the surviving card; the absorbed key is gone from the build",
    "Stresses to confirm (medium confidence)": "3 of the 58 resolved stresses; the other 55 are high confidence and applied",
    "A2-0964 wording": "your suggestion, checked"},
    "lead": [f"Everything done on your verdicts from the Roll-out, Phrase Additions, Hand Fixes and Historical Test pages: {n['Originals restored']} originals restored, {n['Hand-fix redos']} hand-fix redos, {n['Anatomy fixes: masked edits'] + n['Anatomy fixes: re-rolls']} anatomy fixes and {n['Historical: test renders adopted'] + n['Historical: new renders'] + n['Historical: kept as shipped']} historical cards; then the planner's round-3 plans: {n['Restaged scenes (planner round 3)']} restaged scenes, {n['Overlaps kept: first render']} first renders of the overlaps you kept, the 4 merges, the 58 phrase stresses (3 to confirm) and the A2-0964 wording.",
             "Each card shows the picture you judged beside the new one, your note and what was done. QA ran the cold read plus the hands-and-limbs check: no limb, prop or hand finding anywhere; the remaining FAILs are the known gaze, neighbour and inset-continuity reads. Mark OK or Redo; a note on a Redo says what to change."]}
TPL = open("a2_build/review_template/template_review.html", encoding="utf-8").read()
doc = TPL.replace("__TITLE__", "Round 3 Fixes").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False)).replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False))
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
json.dump(sorted(used), open(os.path.join(OUT, "media_list.json"), "w"))
print(len(data), "cards", n, len(used), "media")
