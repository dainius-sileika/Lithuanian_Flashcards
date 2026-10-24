# -*- coding: utf-8 -*-
"""Review page "Additions Round 2" (2026-10-18): the 14 redrawn cards of
a2_build/additions_round2/redraw_list.csv (A2-1917 held for the likeness rules), each new
picture beside the previous one (small) and the owner's note, with OK / Redo and a note.
db (capabilities db + user): collection "adds2", general notes "adds2_meta/general".

    python3 build_page.py <repo root> <out dir>    # media/: <key>_new.jpg (1024 px), <key>_old.jpg (480 px)
"""
import csv, json, os, sys
ROOT, OUT = sys.argv[1], sys.argv[2]
R = lambda p: os.path.join(ROOT, p)
HERE = os.path.dirname(os.path.abspath(__file__))
red = {r["key"]: r for r in csv.DictReader(open(R("a2_build/additions_round2/redraw_list.csv"), encoding="utf-8"))}
qa = {r["key"]: r for r in csv.DictReader(open(R("a2_build/additions_round2/qa_adds2.csv"), encoding="utf-8"))}
a2 = {r["id"]: r for r in csv.DictReader(open(R("a2_build/a2_wordlist.csv"), encoding="utf-8"))}
master = {r["#"]: r for r in csv.DictReader(open(R("master_wordlist.csv"), encoding="utf-8"))}
EDIT = {"A2-1879": "edit: lower inset", "A2-1883": "edit: lower inset", "A2-1884": "edit: lower inset",
        "A2-1892": "edit: lower inset", "A2-1898": "edit: both insets", "A2-1899": "edit: both insets",
        "A2-1911": "edit: both insets", "A2-1915": "edit: the painting on the wall + upper inset",
        "A2-1918": "edit: upper inset only", "A2-1926": "edit: all three insets",
        "338_peda": "full re-roll", "A2-1894": "full re-roll", "A2-1923": "full re-roll", "A2-1924": "full re-roll"}
data = []
for k, r in red.items():
    if k == "A2-1917":
        continue
    q = qa.get(k, {})
    if k == "338_peda":
        m = master["338"]; lt, pron, en, ct = m["lithuanian_TARGET"], m["lt_pron"], m["english"], m["card_text"]
    else:
        w = a2[k]; lt, pron, en, ct = w["lithuanian_TARGET"], w["lt_pron"], w["english"], w.get("card_text", "")
    st = r["new_staging"]
    data.append({"k": k, "group": "Edited insets (rest of the picture unchanged)" if EDIT[k].startswith("edit") else "Re-rolled with the new staging",
                 "lt": lt, "pron": pron, "en": en, "staging": st.split(" Insets:")[0],
                 "insets": st.split(" Insets:")[1].strip() if " Insets:" in st else "",
                 "path": EDIT[k], "ct": ct, "note": r["planner_note"], "owner": r["owner_note"],
                 "qa": q.get("status", ""), "fails": q.get("fails", ""), "warns": q.get("warnings", ""), "guess": q.get("guess", ""),
                 "img": f"{k}_new.jpg", "old": f"{k}_old.jpg", "rr": 0})
data.sort(key=lambda c: (not c["group"].startswith("Edited"), c["k"]))
extra = {"lead": [
    "The 14 cards you sent back from the 17 October additions review, redrawn from your notes. Where you kept the main picture, only the named inset boxes were repainted "
    "(the gpt-image edit endpoint with a mask, pasted back so nothing else moves); the other four were drawn again from the new staging line. "
    "Your earlier picture and note sit small under each new one.",
    "A2-1915 shows Čiurlionis's Karalių pasaka on the gallery wall, as you chose. A2-1917 (pilot, Darius and Girėnas) is held back until the likeness rules exist. "
    "Mark OK or Redo; a note on a Redo says what to change."]}
TPL = open(os.path.join(HERE, "template_adds2.html"), encoding="utf-8").read()
doc = (TPL.replace("__TITLE__", "Additions Round 2").replace("/*__MODE__*/", json.dumps("adds2"))
          .replace("/*__DATA__*/", json.dumps(data, ensure_ascii=False))
          .replace("/*__EXTRA__*/", json.dumps(extra, ensure_ascii=False)))
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(doc)
print("adds2", len(data), "cards")
