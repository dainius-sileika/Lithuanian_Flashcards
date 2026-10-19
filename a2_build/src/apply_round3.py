# -*- coding: utf-8 -*-
"""Round 3 data changes (2026-10-19), idempotent; run after apply_benchmark.py.
  §1 the 58 resolved phrase stresses (a2_build/stress_58_resolved.csv) -> a2_wordlist.csv lt_pron
  §2 A2-0964 -> "Ar galite ką nors parekomenduoti?" (rollout_round3/NOTE_0964_parekomenduoti.md)
  §3 the four merges of a2_build/merges_2026-10-19.md (merged_keys.csv, id_map merged_into, context notes,
     restage rows, recording list, benchmark notes); the three overlaps (2007, 2012, 2020) back to render = yes
  §4 the 20 round-3 stagings (a2_build/rollout_round3/restage.csv) appended to restage_bubbles.csv
Log: a2_build/round3/data_applied.csv.  Then: python3 a2_build/src/build_situations.py; python3 build_study_order_v2.py
    python3 a2_build/src/apply_round3.py"""
import csv, io, os, re
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); os.chdir(ROOT)
TODAY = "2026-10-19"; LOG = []

def rd(p):
    raw = open(p, encoding="utf-8", newline="").read(); nl = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.DictReader(io.StringIO(raw))); return rows, (list(rows[0].keys()) if rows else next(csv.reader(io.StringIO(raw)))), nl
def wr(p, rows, fields, nl):
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=nl); w.writeheader(); w.writerows(rows)
    open(p, "w", encoding="utf-8", newline="").write(out.getvalue())
def setf(file, r, key, field, new):
    if r.get(field, "") != new:
        LOG.append([file, key, field, r.get(field, ""), new]); r[field] = new
def addto(file, r, key, field, text, sep="; "):
    if text not in r.get(field, ""):
        setf(file, r, key, field, (r[field] + sep if r.get(field) else "") + text)

WL = "a2_build/a2_wordlist.csv"; W, WF, WN = rd(WL); BY = {r["id"]: r for r in W}
# §1 stresses
for s in csv.DictReader(open("a2_build/stress_58_resolved.csv", encoding="utf-8")):
    r = BY.get(s["id"])
    if not r:
        continue
    assert r["lithuanian_TARGET"].strip() == s["phrase"].strip(), s["id"]
    if r["lt_pron"] != s["stressed"]:
        setf(WL, r, s["id"], "lt_pron", s["stressed"])
        addto(WL, r, s["id"], "check", f"stress: {s['confidence']} — {s['source'][:160]} ({TODAY}, stress_58_resolved.csv)")
# §2 A2-0964
NEW964 = "Ar galite ką nors parekomenduoti?"
r = BY["A2-0964"]
setf(WL, r, "A2-0964", "lithuanian_TARGET", NEW964); setf(WL, r, "A2-0964", "example_lt", NEW964)
setf(WL, r, "A2-0964", "lt_pron", "Ar̃ gãlite ką̃ nórs parekomendúoti?")
addto(WL, r, "A2-0964", "notes", "owner 2026-10-19: perfective; LKŽ parekomenduoti")
addto(WL, r, "A2-0964", "english_alt", "Ar galite ką nors pasiūlyti? (everyday variant)", " | ")
addto(WL, r, "A2-0964", "check", f"stress: ar̃ en.wiktionary; gãlite, ką̃ kirtis; nórs, parekomendúoti LKŽ ({TODAY})")
# §3 merges
M = {"A2-1187": ("A2-0354", "owner 2026-10-19: Sudie absorbed into Viso gero with a back-of-card note"),
     "A2-1149": ("A2-0385", "owner 2026-10-19: one card for the adverb and the warning; icy-walk picture"),
     "A2-1944": ("A2-1995", "owner 2026-10-19: same phrase (P-082); 1995 carries both phrasings"),
     "A2-1958": ("A2-1991", "owner 2026-10-19: same meaning (P-096); 1991 is the sentence form")}
SURV = {"A2-0354": [("english_alt", "goodbye (solemn, final: Sudie)"), ("notes", "absorbs A2-1187 Sudie (owner 2026-10-19; back-of-card note)")],
        "A2-0385": [("english_alt", "carefully; careful!"), ("notes", "absorbs A2-1149 atsargiai (adverb); one picture: icy walk — rollout_round3/restage.csv")],
        "A2-1995": [("english_alt", "to spell"), ("notes", "absorbs A2-1944 (P-082 'to spell'); benchmark coverage of P-082 is this card")],
        "A2-1991": [("english_alt", "would prefer; prefer"), ("notes", "absorbs A2-1958 (P-096) 2026-10-19")]}
for k, adds in SURV.items():
    for f, t in adds:
        addto(WL, BY[k], k, f, t, " | " if f == "english_alt" else "; ")
setf(WL, BY["A2-0385"], "A2-0385", "lt_pron", "Atsargiaĩ!")
addto(WL, BY["A2-0385"], "A2-0385", "check", "stress: LKŽ adverb form, 2026-10-19 (http://lkz.lt/?zodis=atsargus&lns=-1&les=-1)")
if not BY["A2-1995"]["lt_pron"]:
    setf(WL, BY["A2-1995"], "A2-1995", "lt_pron", "Kaip rãšoma? / Paraidžiui, prašaũ.")
    addto(WL, BY["A2-1995"], "A2-1995", "check", "stress: rãšoma from A2-1944, prašaũ kirtis; paraidžiui unverified (2026-10-19)")
MK = "a2_build/merged_keys.csv"; MF = WF + ["merged_into", "merged_on", "merge_note"]
mk = list(csv.DictReader(open(MK, encoding="utf-8"))) if os.path.exists(MK) else []
have = {x["id"] for x in mk}
for k, (into, why) in M.items():
    if k in BY:
        row = dict(BY[k]); row.update({"merged_into": into, "merged_on": TODAY, "merge_note": why})
        if k not in have: mk.append(row)
        LOG.append([WL, k, "(row)", "present", f"moved to merged_keys.csv (merged into {into})"])
W = [r for r in W if r["id"] not in M]
wr(WL, W, WF, WN); wr(MK, mk, MF, "\n")
IM = "a2_build/id_map.csv"; I, IF, IN = rd(IM)
if "merged_into" not in IF: IF = IF + ["merged_into"]
for r in I:
    r.setdefault("merged_into", "")
    if r["id"] in M: setf(IM, r, r["id"], "merged_into", M[r["id"]][0])
    if r["id"] == "A2-0964": setf(IM, r, "A2-0964", "lithuanian_TARGET", NEW964)
wr(IM, I, IF, IN)
CN = "a2_build/context_notes.csv"; C, CF, CNL = rd(CN); cby = {r["key"]: r for r in C}
if "A2-1187" in cby:
    s1187 = cby["A2-1187"]
    addto(CN, cby["A2-0354"], "A2-0354", "context_line", "Sudie — a solemn, final goodbye (from su Dievu, 'with God'); the old word, kept today for long or last partings.", " ")
    addto(CN, cby["A2-0354"], "A2-0354", "source_note", "Sudie: " + s1187["source_note"], " | ")
    C = [r for r in C if r["key"] != "A2-1187"]; LOG.append([CN, "A2-1187", "(row)", "present", "removed (folded into A2-0354)"])
r = next((x for x in C if x["key"] == "A2-0964"), None)
if r:
    setf(CN, r, "A2-0964", "lithuanian", NEW964)
    setf(CN, r, "A2-0964", "variant_tu_jus", "tu: Ar gali ką nors parekomenduoti?")
    addto(CN, r, "A2-0964", "context_line", "Everyday speech often says pasiūlyti instead.", " ")
    addto(CN, r, "A2-0964", "source_note", "parekomenduoti: LKŽ s.v. rekomenduoti (http://lkz.lt/?zodis=rekomenduoti&lns=-1&les=-1); pasiūlyti as the everyday verb: Tatoeba lemma search (rollout_round3/NOTE_0964_parekomenduoti.md)", " | ")
wr(CN, C, CF, CNL)
RB = "a2_build/restage_bubbles.csv"; R, RF, RN = rd(RB)
for r in R:
    k = r["ids"]
    if k in ("A2-1187", "A2-1149"):
        into = M[k][0]
        setf(RB, r, k, "render", f"no (merged into {into})"); setf(RB, r, k, "merge_with", into); setf(RB, r, k, "new_staging", f"MERGED into {into}")
    if k in ("A2-2007", "A2-2012", "A2-2020") and r["render"].startswith("hold"):
        setf(RB, r, k, "render", "yes"); setf(RB, r, k, "merge_with", "")
        m = re.search(r"If kept:\s*(.*)$", r["new_staging"], re.S)
        if m: setf(RB, r, k, "new_staging", m.group(1).strip())
    if k == "A2-0964": setf(RB, r, k, "lithuanian", NEW964)
# §4 round-3 stagings, appended (build_situations takes the LAST "yes" row per gloss)
gloss = {}
for r in R:
    gloss.setdefault(r["ids"], r["english"])
FMT = {"single scene": "single scene", "single scene + one sequence inset": "single scene", "two panels (two different people and places by design)": "two panels"}
for s in csv.DictReader(open("a2_build/rollout_round3/restage.csv", encoding="utf-8")):
    k = s["ids"].split()[0]; tag = f"round 3 (owner review 2026-10-19; rollout_round3/restage.csv)"
    if any(r["ids"] == k and r["old_format"] == tag for r in R):
        continue
    fmt = FMT.get(s["new_format"], "single scene")
    gz = s["gaze"].split()[0] if s["gaze"] else ""
    R.append({"ids": k, "english": gloss[k], "lithuanian": s["lithuanian"], "old_format": tag, "new_format": fmt,
              "new_staging": s["new_staging"], "merge_with": "", "distinguishing_cue": s["distinguishing_cue"],
              "confusables": s["confusables"], "source_file": next(r["source_file"] for r in R if r["ids"] == k),
              "render": "yes — round 3 (supersedes the earlier rows)", "gaze": gz})
    LOG.append([RB, k, "(row)", "", "round-3 staging appended"])
wr(RB, R, RF, RN)
RL = "a2_build/recording_list.csv"; L, LF, LN = rd(RL)
for r in L:
    if r["file_name"] == "A2-0964.mp3":
        setf(RL, r, "A2-0964", "lithuanian", NEW964); setf(RL, r, "A2-0964", "say", NEW964)
drop = [r for r in L if r["file_name"][:-4] in M]
for r in drop: LOG.append([RL, r["file_name"][:-4], "(take)", r["take"], "dropped (merged)"])
wr(RL, [r for r in L if r["file_name"][:-4] not in M], LF, LN)
AV = "a2_build/benchmark_en/additions_verified.csv"; A, AF, AN = rd(AV)
for r in A:
    if r["proposal_id"] == "P-082": addto(AV, r, "P-082", "notes", "merged into A2-1995 2026-10-19")
    if r["proposal_id"] == "P-096": addto(AV, r, "P-096", "notes", "merged into A2-1991 2026-10-19")
wr(AV, A, AF, AN)
os.makedirs("a2_build/round3", exist_ok=True)
lp = "a2_build/round3/data_applied.csv"; new = not os.path.exists(lp)
with open(lp, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if new: w.writerow(["file", "key", "field", "old", "new"])
    w.writerows(LOG)
print(len(LOG), "changes logged")
