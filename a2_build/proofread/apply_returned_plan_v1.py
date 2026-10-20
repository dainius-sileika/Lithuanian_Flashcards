#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_returned_plan_v1.py — apply a2_build/proofread/returned_plan_v1.csv to the live data (one shot, 2026-10-20).

    python3 a2_build/proofread/apply_returned_plan_v1.py            # dry run: prints every field change
    python3 a2_build/proofread/apply_returned_plan_v1.py --apply

Runs on the tree as of key_map_v1 (the plan's `new_key` column). The re-slug of five keys (key_map_v2)
is a separate step, done afterwards with tools/rename_keys.py's token rewrite.

  EDIT / KEEP_TARGET_NEW_SENTENCE: example_lt + example_en (sentence card: lt + en) as given in the plan.
    0331: headword and lt_pron as given; 2410: the headword is the sentence ("Jau metus mokausi lietuvių
    kalbos", returned_plan_v1.md "EDIT rows that carry a data change").
  RETARGET (1006 užsiėmimas, 2360 apsidrausti): headword, gloss, lt_pron, pron_src, gen_sg/gender or
    pres3/past3, the stress source in `check`, and the sentence (returned_plan_v1.md "RETARGET data").
  2392_rakinti: pres3 rakìna, past3 rakìno (kirtis.info).
  id_map.csv: headword/gloss of the four cards whose headword changed.
  context_notes.csv: the usage note of 0331 described "Kuri valanda?" (the form the card no longer
    teaches); it is withdrawn from the back (confidence -> withdrawn), text kept.
Every changed row gets a line in `notes` (a2_wordlist) / `notes` (sentences).
"""
import csv, io, sys

PLAN = "a2_build/proofread/returned_plan_v1.csv"
WL = "a2_build/a2_wordlist.csv"
SENT = "a2_build/sentences/sentences.csv"
IDMAP = "a2_build/id_map.csv"
CTX = "a2_build/context_notes.csv"
TAG = "owner proofread 2026-10-20 (a2_build/proofread/returned_plan_v1)"

RETARGET = {
    "1006_veikla": dict(
        lithuanian_TARGET="užsiėmimas", english="activity; pastime (also: class, session)", lt_pron="užsiėmìmas",
        pron_src="kirtis.info", gen_sg="užsiėmimo", gender="M", fem="", pres3="", past3="",
        check="stress: kirtis.info — https://kirtis.info/api/krc/užsiėmimas (Užsiėmìmas, dktv., vyr.gim., vnsk., V.); "
              "https://kirtis.info/api/krc/užsiėmimo (Užsiėmìmo, K.); https://kirtis.info/api/krc/užsiėmimus "
              "(Užsiėmimùs, dgsk., G.); en.wiktionary: no entry (2026-10-20, returned_plan_v1)"),
    "2360_draustis": dict(
        lithuanian_TARGET="apsidrausti", english="to take out insurance; to get insured (perf.)", lt_pron="apsidraũsti",
        pron_src="kirtis.info", pres3="apsidraũdžia", past3="apsìdraudė", gen_sg="", fem="",
        check="stress: kirtis.info — https://kirtis.info/api/krc/apsidrausti (Apsidraũsti, vksm., sngr.); "
              "principal parts: https://kirtis.info/api/krc/apsidraudžia (Apsidraũdžia, esam.l. III asm.); "
              "https://kirtis.info/api/krc/apsidraudė (Apsìdraudė, būt.kart.l. III asm.); en.wiktionary: no entry "
              "(2026-10-20, returned_plan_v1)"),
}
EXTRA = {
    "0331_kuri_valanda": dict(lithuanian_TARGET="Kelinta valanda?", lt_pron="Kelintà valandà?", pron_src="kirtis.info",
                              check="stress: kirtis.info — https://kirtis.info/api/krc/kelinta (kelintà, nom. f.; as card "
                                    "2021_kelinta); https://kirtis.info/api/krc/valanda (Valandà V.) (2026-10-20, returned_plan_v1)"),
    "2410_metus_mokausi_lietuviu_kalbos": dict(lithuanian_TARGET="Jau metus mokausi lietuvių kalbos"),
    "2392_rakinti": dict(pres3="rakìna", past3="rakìno",
                         check_append="principal parts: kirtis.info — https://kirtis.info/api/krc/rakina (Rakìna, esam.l. "
                                      "III asm.); https://kirtis.info/api/krc/rakino (Rakìno, būt.kart.l. III asm.) "
                                      "(2026-10-20, returned_plan_v1)"),
}


def read(path):
    raw = open(path, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    rd = csv.DictReader(io.StringIO(raw))
    return rd.fieldnames, list(rd), eol, raw


def write(path, fields, rows, eol):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=fields, lineterminator=eol)
    w.writeheader(); w.writerows(rows)
    return out.getvalue()


def setf(r, f, v, log, key):
    if f not in r:
        raise SystemExit(f"{key}: no column {f}")
    if r[f] != v:
        log.append(f"{key:38} {f:18} {r[f]!r} -> {v!r}")
        r[f] = v


def main(apply):
    plan = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    wf, wrows, weol, wraw = read(WL)
    sf, srows, seol, sraw = read(SENT)
    wby = {r["id"]: r for r in wrows}; sby = {r["id"]: r for r in srows}
    log = []
    for p in plan:
        k, act = p["new_key"], p["action"]
        if act not in ("EDIT", "KEEP_TARGET_NEW_SENTENCE", "RETARGET"):
            raise SystemExit(f"{k}: unexpected action {act}")
        if k in sby:
            r = sby[k]
            setf(r, "lt", p["example_lt"], log, k); setf(r, "en", p["example_en"], log, k)
        elif k in wby:
            r = wby[k]
            setf(r, "example_lt", p["example_lt"], log, k); setf(r, "example_en", p["example_en"], log, k)
            if act == "RETARGET":
                rt = RETARGET[k]
                if rt["lithuanian_TARGET"] != p["new_headword"] or rt["english"] != p["new_gloss"]:
                    raise SystemExit(f"{k}: RETARGET table disagrees with the plan csv")
                for f, v in rt.items():
                    setf(r, f, v, log, k)
            elif p["new_headword"]:
                if p["new_gloss"] and p["new_gloss"] != r["english"]:
                    raise SystemExit(f"{k}: plan changes the gloss of an EDIT row; not expected")
            for f, v in EXTRA.get(k, {}).items():
                if f == "check_append":     # replaces the "principal parts: NOT FOUND" clause
                    if v not in r["check"]:
                        base = r["check"].replace("; principal parts: NOT FOUND — verb_flashcards.py / DLKŽ", "")
                        setf(r, "check", (base + "; " if base else "") + v, log, k)
                else:
                    setf(r, f, v, log, k)
            if k == "0331_kuri_valanda" and r["lithuanian_TARGET"] != p["new_headword"]:
                raise SystemExit("0331: headword not as planned")
        else:
            raise SystemExit(f"{k}: not in {WL} or {SENT}")
        note = f"{TAG}: {act}"
        if note not in r["notes"]:
            r["notes"] = (r["notes"] + "; " if r["notes"] else "") + note
    # 2392 is in the plan (KEEP_TARGET_NEW_SENTENCE) and in EXTRA; every EXTRA key must have been reached
    for k in EXTRA:
        if k not in {p["new_key"] for p in plan}:
            raise SystemExit(f"{k}: EXTRA row not in the plan")

    # id_map: headword + gloss of the cards whose headword changed
    if_, irows, ieol, iraw = read(IDMAP)
    for r in irows:
        if r["id"] in ("0331_kuri_valanda", "1006_veikla", "2360_draustis", "2410_metus_mokausi_lietuviu_kalbos"):
            w = wby[r["id"]]
            setf(r, "lithuanian_TARGET", w["lithuanian_TARGET"], log, "id_map " + r["id"])
            setf(r, "english", w["english"], log, "id_map " + r["id"])
    # context note of 0331 (described "Kuri valanda?")
    cf, crows, ceol, craw = read(CTX)
    for r in crows:
        if r["key"] == "0331_kuri_valanda":
            setf(r, "confidence", "withdrawn", log, "context_notes 0331")
            add = " [withdrawn 2026-10-20: the card now teaches Kelinta valanda? (returned_plan_v1); this note is about Kuri valanda?]"
            if add not in r["source_note"]:
                setf(r, "source_note", r["source_note"] + add, log, "context_notes 0331")

    for l in log:
        print(l)
    print(f"{len(log)} field changes")
    if apply:
        for path, f, rows, eol in ((WL, wf, wrows, weol), (SENT, sf, srows, seol), (IDMAP, if_, irows, ieol), (CTX, cf, crows, ceol)):
            open(path, "w", encoding="utf-8", newline="").write(write(path, f, rows, eol))
        print("written")


if __name__ == "__main__":
    main("--apply" in sys.argv)
