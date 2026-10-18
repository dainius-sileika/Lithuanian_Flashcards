# -*- coding: utf-8 -*-
"""Review page "Hand Fixes" (2026-10-18): the 40 cards of build_reports/hand_scan/fix_plan.csv,
the picture the hand scan judged beside the fixed one, a close-up of the repainted area, the fix,
the QA read (qa_handfix.csv, with the --limbs check) and OK / Redo + note per card.
db (capabilities db + user): collection "handfix", general notes "handfix_meta/general".

    python3 a2_build/hand_fixes/build_page.py <repo root> <out dir>
    # media/ (from make_pairs.py): <key>_before.jpg, <key>_after.jpg (800 px), <key>_zoom.jpg
"""
import csv, json, os, re, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(ROOT, p)
HERE = os.path.dirname(os.path.abspath(__file__))
plan = list(csv.DictReader(open(R("build_reports/hand_scan/fix_plan.csv"), encoding="utf-8")))
qa = {r["key"]: r for r in csv.DictReader(open(os.path.join(HERE, "qa_handfix.csv"), encoding="utf-8"))}
reg = json.load(open(os.path.join(HERE, "edit_regions.json"), encoding="utf-8"))
a2 = {r["id"]: r for r in csv.DictReader(open(R("a2_build/a2_wordlist.csv"), encoding="utf-8"))}
master = {r["#"].zfill(3): r for r in csv.DictReader(open(R("master_wordlist.csv"), encoding="utf-8"))}
tries = {}
for line in open(os.path.join(HERE, "edit_log.txt"), encoding="utf-8"):
    m = re.match(r"(OK|ERR) (\S+)", line)
    if m:
        tries[m.group(2)] = tries.get(m.group(2), 0) + 1
# what happened, where it did not go to plan
NOTE = {
    "083_tevas": "Removal needed a blurred pre-fill (the endpoint redrew the hand it could see) and a wider mask so the boy's sleeve runs on unbroken.",
    "091_senelis": "Second pass with a blurred pre-fill; the first pass repainted the hand.",
    "156_lenktynes": "The hand now ends at the tape; nothing passes through it.",
    "271_nugara": "First pass left a grey box on the shirt; redone with colour matching to the surrounding shirt.",
    "400_sprogti": "The endpoint removed the pale second hand rather than recolouring its sleeve: one man, one hand on the plunger.",
    "512_jis": "Three edits each erased the open hand instead of repainting it. Original kept; a re-roll or an OK as is is your call.",
    "A2-0268": "Mask kept clear of the declared “10 Lt”, “20 Lt” and “50 ct”; the first pass painted over the notes and was discarded.",
    "A2-0568": "No figure owns the spoon hand, so it now comes down from the top edge in a sleeve (third attempt).",
    "A2-0660": "Whole-inset edits came back empty; done with a smaller mask over the clasp.",
    "A2-1231": "Dormitory card: the tea strainer was dropped; one hand on the kettle, the other holding the mug.",
    "A2-1252": "The edit endpoint refused this card (safety filter, bare shoulders). Unchanged; a re-roll with the same staging may meet the same refusal.",
    "A2-1309": "Whole inset redrawn: the presenter, seen from behind, hangs the medal at the athlete's chest.",
    "A2-1416": "Whole-inset edits came back black; done with a mask over the dancers' arms.",
    "A2-1433": "Three edits either repainted a full glove or erased it with a seam. Original kept; your call.",
    "035_teismas": "Covered by the historical re-roll (A5, Palace of Justice); not touched here.",
}
data = []
for r in plan:
    k = r["key"]
    if k.startswith("A2"):
        w = a2[k]; lt, pron, en = w["lithuanian_TARGET"], w["lt_pron"], w["english"]
    else:
        m = master[k[:3]]; lt, pron, en = m["lithuanian_TARGET"], m["lt_pron"], m["english"]
    fix = r["fix"]
    kept = k in ("512_jis", "A2-1433", "A2-1252")
    if k == "035_teismas":
        group = "Covered elsewhere"
    elif kept:
        group = "Not fixed: original kept"
    elif fix.startswith("reroll"):
        group = "Re-rolled with a staging tweak"
    else:
        group = "Masked edits"
    q = qa.get(k, {})
    imgs = []
    if os.path.exists(os.path.join(OUT, "media", f"{k}_before.jpg")):
        imgs.append({"src": f"{k}_before.jpg", "label": "Before (as scanned)"})
    if os.path.exists(os.path.join(OUT, "media", f"{k}_after.jpg")):
        imgs.append({"src": f"{k}_after.jpg", "label": "Unchanged" if kept else "After", "cls": "" if kept else "after"})
    zoom = f"{k}_zoom.jpg" if os.path.exists(os.path.join(OUT, "media", f"{k}_zoom.jpg")) else ""
    chips = [r["verdict"], "where: " + r["where"]]
    if k in tries:
        chips.append(f"{tries[k]} edit call{'s' if tries[k] > 1 else ''}")
    data.append({"k": k, "group": group, "lt": lt, "pron": pron, "en": en, "imgs": imgs, "zoom": zoom,
                 "chips": chips, "facts": [["Scan found", r["region (edit_regions.json entry)"] if not fix.startswith("reroll") else r["note"] or "—"],
                                            ["Fix asked", r["instruction / staging tweak"]],
                                            ["Done", (reg.get(k) or {}).get("instruction", "") if group == "Masked edits" else ""],
                                            ["Executor", NOTE.get(k, "")]],
                 "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", "")})
order = ["Masked edits", "Re-rolled with a staging tweak", "Not fixed: original kept", "Covered elsewhere"]
data.sort(key=lambda c: (order.index(c["group"]), c["k"]))
n = {g: sum(c["group"] == g for c in data) for g in order}
extra = {"col": "handfix", "title": "Hand fixes", "hints": {
    "Masked edits": "only the masked area was repainted; everything else is the old picture",
    "Re-rolled with a staging tweak": "drawn again from the old staging plus one sentence on the hands",
    "Not fixed: original kept": "the edit failed or was refused"},
    "lead": [
    f"The 40 cards from the 18 October hand scan. {n['Masked edits']} were fixed with a masked edit (the gpt-image edit endpoint repaints only the area over the hand and the result is pasted back, so nothing else moves), "
    f"{n['Re-rolled with a staging tweak']} were drawn again with one added sentence on the hands, {n['Not fixed: original kept']} could not be fixed by an edit and keep their picture, and 035 teismas waits for the historical re-roll.",
    "Each card shows the scanned picture, the fixed one and a close-up of the repainted area. QA ran the usual cold read plus a hands-and-limbs check; "
    "its continuity notes are about insets that show different people by design, not about the edits. Mark OK or Redo; a note on a Redo says what to change."]}
TPL = open(os.path.join(ROOT, "a2_build", "review_template", "template_review.html"), encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Hand Fixes").replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
          .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
print("handfix", len(data), "cards", n)
