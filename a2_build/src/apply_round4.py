# -*- coding: utf-8 -*-
"""Round 4 data changes (2026-10-19), idempotent; run after apply_round3.py.
Source: a2_build/round4/plan.csv + answers.md (planner, commit 7e2da4b).
  §1 restores: 097 note (pre-test, 52fabca^), 106/107 notes (round3/old_staging_historical.json), A2-1326/A2-0085
     a2_staging notes; settings_assignments rows back to their pre-roll-out values (106 vilnius_vingis, 107 place-less,
     A2-1326 and A2-0085 had no row); settings_rows.csv marked REVERTED; 097 out of likeness_args `active`
  §2 new staging for the re-rolls: 055, 413 (card_notes.json), A2-0660 (a2_staging.json)
  §3 inset text for the masked edits: A2-1431, A2-1360, A2-0649 (a2_staging.json); A2-0649 settings note
  §4 restage rows (appended, superseding): 0359, 1162, 1167, 1172, 1184, 1185, 2010, 2022, 1191 (poster), 2026, 2029
  §5 card_text: A2-1191 "VELNIO NUOTAKA", A2-1360 "MILŽINO PAUNKSMĖ"
Log: a2_build/round4/data_applied.csv; the values replaced: a2_build/round4/old_staging.json.
Then: python3 a2_build/src/build_situations.py
    python3 a2_build/src/apply_round4.py"""
import csv, io, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
TODAY = "2026-10-19"; LOG = []; OLD = {}
R4 = "a2_build/round4"


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


def setnote(file, notes, key, new):
    old = notes.get(key, "")
    if old != new:
        LOG.append([file, key, "note", old, new]); OLD.setdefault(file, {}).setdefault(key, {}).setdefault("note", old)
        notes[key] = new


# ---------------------------------------------------------------------------- §1 + §2: card_notes.json
CN = "card_notes.json"; cn = jload(CN); N = cn["notes"]
hist_old = jload("a2_build/round3/old_staging_historical.json")["old"]
setnote(CN, N, "097_prezidentas",
        "Main picture: a man president at a podium draped with the tricolour speaking toward the hall with a raised hand, "
        "near-frontal; beside him a woman president seated at a side table signing a document, head bent to the page. "
        "Insets: the president shaking a hand before a crowd; the tricolour on a flagpole before a government building; "
        "a motorcade with small flags.")
setnote(CN, N, "106_zaidejas", hist_old["106_zaidejas"])
setnote(CN, N, "107_sirgalius", hist_old["107_sirgalius"])
setnote(CN, N, "055_bankas",
        "Main picture: a bank hall under a great triangular glass skylight, black marble columns and a coffered ceiling "
        "behind — a counter with a low brass grille whose bars stop at chest height, leaving a wide open arch above the "
        "counter ledge; the cashier, seen full-face through that open arch with nothing in front of her face, counts "
        "banknotes onto the ledge for a customer standing on the near side; the counter with its grille is the subject. "
        "Insets: the bank's pale neoclassical corner front with its tall columned entrance; a savings book stamped; coins "
        "stacked on the counter.")
setnote(CN, N, "413_tuoktis",
        "A wedding before a registry official, seen at mid-distance so the figures are full-length: the bride in a white "
        "dress and veil holds a large bouquet of flowers in both hands against her waist; the groom in a dark suit stands "
        "at her side with his near arm round her back, his far hand at his side; the official, a woman in a dark dress "
        "with a tricolour sash across her chest, stands behind a desk holding an open register, facing the viewer; two "
        "gold rings lie on a small cushion on the desk; a few guests behind. The couple before the official is the "
        "subject. Insets: the two gold rings in an open ring box; the couple seen from behind walking out of the registry "
        "doors under a shower of thrown grain; a wedding car with white ribbons tied to its bonnet.")
jsave(CN, cn)

# ---------------------------------------------------------------------------- a2_staging.json
ST = "a2_build/a2_staging.json"; st = jload(ST); S = st["notes"]
setnote(ST, S, "A2-1326", hist_old["A2-1326"])
setnote(ST, S, "A2-0085", hist_old["A2-0085"])
setnote(ST, S, "A2-0660",
        "Main picture: a zebra crossing seen at an angle — bold white stripes across the asphalt; a mother and her small "
        "boy walk across the stripes from the viewer's LEFT toward the RIGHT, both seen in profile heading right, the boy "
        "holding the strap of the mother's handbag; a man a few steps behind them also heading right; a Zhiguli stopped "
        "at the line on the near side; a crossing sign post. The striped crossing with people on it is the subject. "
        "Insets: the pedestrian signal light with only the green walking figure lit; a child's shoes stopping at the "
        "white kerb line; the stripes from above.")


def swap(key, old, new):
    cur = S[key]
    if old in cur:
        setnote(ST, S, key, cur.replace(old, new))
    else:
        assert new in cur, (key, old)


swap("A2-1431", "a foot pushed into a new shoe with a shoehorn", "a foot sliding into a new shoe, laces loose, the shoe box beside it")
swap("A2-1360", "a playbill frame left blank", "a playbill for the play (declared lettering)")
swap("A2-0649", "the post office front — a smooth pale flat-roofed modernist block with very large windows in carved "
                "wooden frames and a round clock",
     "a plain blue post box on its post beside the door, a bundle of letters going into the slot")
jsave(ST, st)

# ---------------------------------------------------------------------------- settings
SA = "style_lab/research/settings_assignments.csv"; rows, F, nl = rd(SA)
PRE = {"106_zaidejas": ("vilnius_vingis", "exterior", "players on the park sports ground (stadium 1954), pines behind"),
       "107_sirgalius": ("", "", "figure card with arrows; a place would compete with the subject")}
keep = []
for r in rows:
    k = r["key"]
    if k in PRE:
        lid, mode, why = PRE[k]
        setv(SA, r, k, "location_id", lid); setv(SA, r, k, "mode", mode); setv(SA, r, k, "why", why)
    if k in ("A2-1326", "A2-0085"):      # no row before the A5 roll-out (git show 52fabca^:...)
        LOG.append([SA, k, "row", ",".join(r[f] for f in F), "(deleted: pre-roll-out value is no row)"])
        OLD.setdefault(SA, {})[k] = dict(r)
        continue
    if k == "A2-0649" and "exterior inset dropped" not in r["why"]:
        setv(SA, r, k, "why", r["why"] + f" Round 4: exterior inset dropped {TODAY} (owner); inset 1 is a post box.")
    keep.append(r)
wr(SA, keep, F, nl)

SR = "a2_build/historical/implementation/settings_rows.csv"; rows, F, nl = rd(SR)
for r in rows:
    k = r["key"]
    if k in ("106_zaidejas", "107_sirgalius", "A2-1326", "A2-0085") and not r["why"].startswith("REVERTED"):
        setv(SR, r, k, "why", f"REVERTED {TODAY} (owner): " + r["why"])
    if k == "A2-0649" and "exterior inset dropped" not in r["why"]:
        setv(SR, r, k, "why", r["why"] + f" | exterior inset dropped {TODAY} (owner)")
wr(SR, rows, F, nl)

LA = "a2_build/historical/implementation/likeness_args.json"; la = jload(LA)
if "097_prezidentas" in la["active"]:
    LOG.append([LA, "097_prezidentas", "active", "listed", "removed"])
    la["active"] = [k for k in la["active"] if k != "097_prezidentas"]
    la["_about"] += (f" {TODAY} (round 4, owner 'go back to the original'): 097_prezidentas removed from active; the "
                     "shipped picture (no likeness, no Vytis) is back and its entry stays here for the record.")
jsave(LA, la)

# ---------------------------------------------------------------------------- §4 restage rows
RB = "a2_build/restage_bubbles.csv"; rows, F, nl = rd(RB)
last = {}
for r in rows:
    for i in [x.strip() for x in r["ids"].split(",") if x.strip()]:
        if r["render"].strip().startswith("yes"):
            last[i] = r
MARK = "round 4 (owner review 2026-10-19; a2_build/round4/plan.csv)"


def restage(i, staging=None, cue=None, conf=None, gaze=None, replace=None):
    base = last[i]
    if base["old_format"] == MARK:
        new = base                       # already applied: update in place (idempotent)
    else:
        new = dict(base); new["old_format"] = MARK; new["render"] = "yes — round 4 (supersedes the earlier rows)"
        rows.append(new); LOG.append([RB, i, "row", "", "appended (round 4)"])
    s = base["new_staging"] if staging is None else staging
    if replace:
        old, rep = replace
        if rep not in s:
            assert old in s, (i, old)
            s = s.replace(old, rep)
    setv(RB, new, i, "new_staging", s)
    if cue is not None: setv(RB, new, i, "distinguishing_cue", cue)
    if conf is not None: setv(RB, new, i, "confusables", conf)
    if gaze is not None: setv(RB, new, i, "gaze", gaze)
    last[i] = new


restage("A2-0359",
        "a hospital corridor; a discharged patient in his coat holds out a large bunch of flowers in a paper wrap to a nurse "
        "with BOTH hands, the paper wrap covering his fingers, head slightly inclined, eyes on her face; she receives it "
        "with her RIGHT hand on the stems and smiles at him; her LEFT hand holds a clipboard against her hip; nobody bows "
        "to the floor, no clasped hands. Insets: the bouquet close; the corridor door",
        "flowers offered with both hands — thanks at full strength",
        "Thank you (A2-0358, one hand flat on the chest, slight bow); You're welcome (A2-0360, glove, wave-off)",
        "conversation")
restage("A2-1162",
        "an office corridor on a Friday evening; a man in a coat with a fishing rod over his RIGHT shoulder stands in the "
        "corridor two steps outside the open office door, the open door and its painted frame BEHIND him, slightly to one "
        "side, so he overlaps nothing; inside the room, framed by the doorway, a woman colleague at the threshold raises "
        "her RIGHT hand in a parting wave; his LEFT hand holds a small tackle bag; they look at each other. Insets: the rod "
        "and tackle bag; a desk calendar with the Friday column (ticks only, no digits)",
        "fishing rod, open office door behind him", "Have a nice day (A2-0894, baker and loaf)", "conversation")
restage("A2-1167",
        "a flat's hallway seen from inside; an ordinary flat door of normal height, its top just above head height, stands "
        "open flat against the wall; the host, a middle-aged man in a cardigan, has stepped back two paces INTO the "
        "hallway, clear of the door and its frame, and sweeps his RIGHT arm inward toward the room, LEFT hand at his side; "
        "the visitor, a woman with a cake tin, stands outside on the doormat in the doorway, one foot on the threshold; "
        "they look at each other. Insets: the doormat with the visitor's shoes on it; the cake tin",
        "arm sweeping in from inside the flat", "Welcome! (A2-0886, both arms wide, family with suitcases)", "conversation")
restage("A2-1172",
        "the Sartai races: a wide frozen lake under a white winter sky, an oval track marked on the ice with fir branches, "
        "a crowd of spectators in sheepskin coats, felt boots and fur hats along a rope rail; on the track three trotting "
        "horses pulling light two-wheeled sulkies with drivers, one horse clearly a length ahead; at the rail a man in a "
        "fur hat points with his RIGHT arm fully extended at the leading horse, looking at it; beside him his friend, "
        "holding a betting slip in his LEFT hand, gives one firm nod, chin tucked, and brings his RIGHT hand down flat in "
        "a short decisive chop, palm vertical; both men look at the horses; no raised index finger, no table, no clock. "
        "Insets: the leading trotter and sulky close; the betting slip as a plain blank ticket",
        "the leading horse pointed out and the companion's flat decisive chop — certainty about an outcome",
        "Of course (A2-0883, librarian + book); aišku (A2-1148, mud trail); I understand (A2-0372)", "default")
restage("A2-1184",
        "a kitchen; a woman at the table has just opened a letter: she holds the unfolded letter in her LEFT hand at chest "
        "height and presses her RIGHT hand flat over her mouth, eyes wide, eyebrows high; the torn envelope lies on the "
        "table; two arms only, each joined to its own shoulder; nobody else in the room. Insets: the torn envelope on the "
        "table; the kitchen window with a postman's bicycle passing",
        "letter and the hand over the mouth", "interesting; I wonder (A2-1155 įdomu)", "default")
restage("A2-1185",
        "a kitchen; a small girl stands stiff over a broken plate on the floor, both hands pressed to her own cheeks, "
        "looking at her grandmother; the grandmother, already crouching with a dustpan in her LEFT hand, smiles up at the "
        "girl and lays her RIGHT hand on the girl's shoulder; shards on the floor, a cat watching from a chair. Insets: the "
        "shards and dustpan; the cat on the chair",
        "the smile and the hand on the shoulder over the broken plate — no scolding",
        "Atsargiai! (A2-0385, before the fall, a warning); You're welcome (A2-0360, glove, wave-off palm); Atsiprašau "
        "(A2-0362, raised flat hand in a trolleybus)", "conversation")
# 2010: the planner's sentence put the thumb on the kerb side; a right hand turned palm-up and reaching back toward the
# rear right door has its thumb toward the back of the car, on the side of the palm away from the kerb (f x n, checked
# on the review page). The executor states the side that a right hand actually has.
restage("A2-2010", replace=("with a few coins on his open RIGHT palm;",
        "with a few coins on his open RIGHT palm — the palm faces up and the fingers point toward the open rear door; as "
        "on any right hand turned palm-up and reaching back, the THUMB lies on the side of the palm away from the viewer, "
        "toward the back of the car; one hand, one thumb, four fingers;"))
restage("A2-2022",
        "a conference room; a man has risen from his chair at a long table and lays his RIGHT hand flat on his chest, "
        "fingers together and half tucked under his jacket lapel so only the edge of the hand shows, his LEFT hand resting "
        "on the chair back; the four people across the table look at him, their hands BELOW the table edge or holding "
        "papers upright in front of them; a blank name card stands on the table before him. Insets: the blank name card; "
        "the empty pushed-back chair",
        "standing up at a table with the hand on his own chest",
        "My name is… (A2-0367, parish-hall circle; A2-0910, pointing at own chest while writing); This is… (A2-1983)",
        "conversation")
restage("A2-1191", replace=("a poster frame with a blank picture beside the door",
        "a printed film poster in the frame beside the door — a dark windmill on a hill against a stormy sky, a girl in "
        "white and a small horned silhouette, the title across the top in bold plain capitals"))
restage("A2-2026", replace=("Insets: the ticket coming out of the slot; the clerk's hand on the roll",
        "Insets: through the round opening cut in the ticket-window glass, the man's hand passing two folded banknotes "
        "to the clerk; the ticket coming out of the slot"))
restage("A2-2029", replace=("not on the dashboard", "not on the dashboard. Insets: the shop doorway through the REAR "
                            "side window, no hand"))
wr(RB, rows, F, nl)

# ---------------------------------------------------------------------------- §5 card_text
WL = "a2_build/a2_wordlist.csv"; rows, F, nl = rd(WL); BY = {r["id"]: r for r in rows}
setv(WL, BY["A2-1191"], "A2-1191", "card_text", '"VELNIO NUOTAKA" on the cinema poster')
setv(WL, BY["A2-1360"], "A2-1360", "card_text", '"MILŽINO PAUNKSMĖ" on the playbill')
wr(WL, rows, F, nl)

# ---------------------------------------------------------------------------- log
os.makedirs(R4, exist_ok=True)
logp = f"{R4}/data_applied.csv"
prev = list(csv.reader(open(logp, encoding="utf-8"))) if os.path.exists(logp) else [["date", "file", "key", "field", "old", "new"]]
with open(logp, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerows(prev); w.writerows([[TODAY] + l for l in LOG])
oldp = f"{R4}/old_staging.json"
if OLD:
    base = jload(oldp)["old"] if os.path.exists(oldp) else {}
    for fi, d in OLD.items():
        for k, v in d.items():
            base.setdefault(fi, {}).setdefault(k, v)
    jsave(oldp, {"_about": "Values replaced by a2_build/src/apply_round4.py (first run), by file and key.", "old": base})
print(len(LOG), "changes")
