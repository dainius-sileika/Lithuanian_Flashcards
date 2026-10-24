# -*- coding: utf-8 -*-
"""Round 5 data changes (2026-10-19), idempotent; run after apply_round4.py.
Source: the owner's Round 4 Fixes verdicts (executor brief, round 5). Working rule from now on: fix by WHOLE re-roll,
not masked edits, unless the owner asks for an edit.
  083   card_notes inset 3: the hand close-up -> a whole-family scene (no hand close-up)
  413   card_notes back to the FIRST round-3 staging (the ring being put on; ledger row 3 / round4/old_staging.json)
  0085  Kaunas station rows reinstated (settings_assignments row back, settings_rows REVERTED mark lifted); a2_staging =
        the round-3 note with the clerk's hands on her own counter behind the glass
  0660  restore: a2_staging back to the round-3 note (the picture the owner praised is restored, not re-rolled)
  restage rows appended (round 5): 0359 (main as rendered in round 4, new insets), 0925 (planner's fallback staging),
        1167 (round-4 main + the first version's insets), 2002 (right hand palm out, "7")
  0925 and 1167 rows were tightened after try 1 (QA: 0925 GAZE, both looked at the clock; 1167 CONTINUITY, coat vs jumper)
  1431, 2010: same staging, re-roll only (no data change).
Log: a2_build/round5/data_applied.csv; replaced values: a2_build/round5/old_staging.json.
Then: python3 a2_build/src/build_situations.py"""
import csv, io, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
TODAY = "2026-10-19"; LOG = []; OLD = {}
R5 = "a2_build/round5"


def rd(p):
    raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(raw)))
    return rows, (list(rows[0].keys()) if rows else next(csv.reader(io.StringIO(raw)))), nl


def wr(p, rows, fields, nl):
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(out.getvalue())


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def jsave(p, d):
    open(p, "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))


def setv(file, d, key, field, new):
    old = d.get(field, "")
    if old != new:
        LOG.append([file, key, field, old, new]); OLD.setdefault(file, {}).setdefault(key, {}).setdefault(field, old)
        d[field] = new


R4OLD = jload("a2_build/round4/old_staging.json")["old"]

# ---------------------------------------------------------------- card_notes.json
CN = "card_notes.json"; cn = jload(CN); N = cn["notes"]
cur = N["083_tevas"]
if "a father's large hand holding a small one" in cur:
    new = cur.replace("a father's large hand holding a small one",
                      "the whole family seen at full length — the father, the mother and the boy sitting side by side on a "
                      "bench before their house, the boy between his parents")
    LOG.append([CN, "083_tevas", "note", cur, new]); OLD.setdefault(CN, {}).setdefault("083_tevas", {"note": cur}); N["083_tevas"] = new
r3_413 = R4OLD["card_notes.json"]["413_tuoktis"]["note"]
if N["413_tuoktis"] != r3_413:
    LOG.append([CN, "413_tuoktis", "note", N["413_tuoktis"], r3_413])
    OLD.setdefault(CN, {}).setdefault("413_tuoktis", {"note": N["413_tuoktis"]}); N["413_tuoktis"] = r3_413
jsave(CN, cn)

# ---------------------------------------------------------------- a2_staging.json
ST = "a2_build/a2_staging.json"; st = jload(ST); S = st["notes"]
NEW_0085 = ("Main picture: a small ticket window in the tiled wall of a tall station hall with square pilasters and a coffered "
            "ceiling; behind the glass a woman clerk sits at her desk, both her hands resting on the counter on her own side of "
            "the glass, pushing a ticket and some change out through the low arched slot at the foot of the window; on the near "
            "side a traveller with a suitcase picks them up from the brass dish below the slot; the glass is whole and nothing "
            "passes through it except at the slot; two people queued behind. The window with the exchange of ticket and money "
            "is the subject. Insets: a punched ticket; the brass window counter with coins; the queue seen from behind under "
            "the high hall.")
R3_0660 = R4OLD[ST]["A2-0660"]["note"]
for k, new in (("A2-0085", NEW_0085), ("A2-0660", R3_0660)):
    if S[k] != new:
        LOG.append([ST, k, "note", S[k], new]); OLD.setdefault(ST, {}).setdefault(k, {"note": S[k]}); S[k] = new
jsave(ST, st)

# ---------------------------------------------------------------- settings: Kaunas station back for A2-0085
SA = "style_lab/research/settings_assignments.csv"; rows, F, nl = rd(SA)
if not any(r["key"] == "A2-0085" for r in rows):
    r0 = dict(R4OLD[SA]["A2-0085"]); r0["why"] += f" Reinstated {TODAY} (round 5, owner: 'try the kaunas train station again')."
    rows.append(r0); LOG.append([SA, "A2-0085", "row", "(none)", ",".join(r0[f] for f in F)])
    wr(SA, rows, F, nl)
SR = "a2_build/historical/implementation/settings_rows.csv"; rows, F, nl = rd(SR)
for r in rows:
    if r["key"] == "A2-0085" and r["why"].startswith("REVERTED"):
        setv(SR, r, "A2-0085", "why", f"REINSTATED {TODAY} (round 5, owner) after a round-4 revert: "
             + r["why"].split("(owner): ", 1)[-1])
wr(SR, rows, F, nl)

# ---------------------------------------------------------------- restage rows (appended, superseding)
RB = "a2_build/restage_bubbles.csv"; rows, F, nl = rd(RB)
last = {}
for r in rows:
    for i in [x.strip() for x in r["ids"].split(",") if x.strip()]:
        if r["render"].strip().startswith("yes"):
            last[i] = r
MARK = "round 5 (owner review 2026-10-19; whole re-roll)"


def restage(i, staging, cue=None, conf=None, gaze=None):
    base = last[i]
    if base["old_format"] == MARK:
        new = base
    else:
        new = dict(base); new["old_format"] = MARK; new["render"] = "yes — round 5 (supersedes the earlier rows)"
        rows.append(new); LOG.append([RB, i, "row", "", "appended (round 5)"])
    setv(RB, new, i, "new_staging", staging)
    if cue is not None: setv(RB, new, i, "distinguishing_cue", cue)
    if conf is not None: setv(RB, new, i, "confusables", conf)
    if gaze is not None: setv(RB, new, i, "gaze", gaze)
    last[i] = new


restage("A2-0359",
        "a long hospital corridor with pale green walls below a white dado line, closed doors on both sides and a tall "
        "window at the far end; a discharged patient, a middle-aged man with greying hair in a long brown overcoat and a "
        "checked scarf, holds out a large bunch of red and white flowers in a white paper wrap to a nurse with BOTH hands, "
        "the paper wrap covering his fingers, head slightly inclined, eyes on her face; the nurse, in a white coat and a "
        "white cap, receives it with her RIGHT hand on the stems and smiles at him; her LEFT hand holds a dark clipboard "
        "against her hip; an older man in a dark jacket sits on a wooden bench by the wall behind them; nobody bows to the "
        "floor, no clasped hands. Insets: the same man some days earlier as a patient in striped pyjamas, sitting up in a "
        "hospital bed, the same nurse standing beside the bed; the same man in his brown overcoat walking out through the "
        "hospital's front doors onto the steps, seen from behind")
restage("A2-0925",
        "a hallway; a man with BOTH arms already in the sleeves of his overcoat buttons it at the chest with his RIGHT "
        "hand, his LEFT hand at his side holding a flat cap; a woman beside him points with her RIGHT hand at a round wall "
        "clock whose hands stand at exactly three and looks at him; he looks back at her. "
        "Insets: the clock face at three; the man going "
        "out through the front door, seen from behind",
        "clock at three")
restage("A2-1167",
        "a flat's hallway seen from inside; an ordinary flat door of normal height, its top just above head height, stands "
        "open flat against the wall; the host, a middle-aged man in a cardigan, has stepped back two paces INTO the "
        "hallway, clear of the door and its frame, and sweeps his RIGHT arm inward toward the room, LEFT hand at his side; "
        "the visitor, a woman in a grey winter coat over a red jumper, a red scarf at her neck, holding a cake tin, stands "
        "outside on the doormat in the doorway, one foot on the threshold; they look at each other. Insets (the same two "
        "people, same hair, same clothes; the coat comes off indoors and the red jumper shows): the visitor hanging her coat on a hook in the hallway, the host standing beside "
        "her; the host and the visitor sitting at a table with a white cloth over cups of tea, a teapot and a plate of "
        "biscuits")
restage("A2-2002",
        "a village street; a postman with a parcel under his LEFT arm asks an old woman at her gate; she raises her RIGHT "
        "hand toward the enamel number plate on her house wall, the PALM turned OUT toward the viewer, the index finger "
        "extended up at the plate and the other three fingers folded under the thumb, the wrist turning naturally from her "
        "brown cardigan sleeve; her LEFT hand rests on the top rail of the gate; the plate reads the numeral declared in "
        "card_text; he looks where she points. Insets: the number plate close; the parcel")
wr(RB, rows, F, nl)

# ---------------------------------------------------------------- log
os.makedirs(R5, exist_ok=True)
logp = f"{R5}/data_applied.csv"
prev = list(csv.reader(open(logp, encoding="utf-8"))) if os.path.exists(logp) else [["date", "file", "key", "field", "old", "new"]]
with open(logp, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerows(prev); w.writerows([[TODAY] + l for l in LOG])
oldp = f"{R5}/old_staging.json"
if OLD:
    base = jload(oldp)["old"] if os.path.exists(oldp) else {}
    for fi, d in OLD.items():
        for k, v in d.items():
            base.setdefault(fi, {}).setdefault(k, v)
    jsave(oldp, {"_about": "Values replaced by a2_build/src/apply_round5.py (first run), by file and key.", "old": base})
print(len(LOG), "changes")
