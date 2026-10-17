# -*- coding: utf-8 -*-
"""Apply the owner-approved English-benchmark proposals (a2_build/benchmark_en/, 2026-10-17)
to the A2 data. Idempotent: run it again after any rebuild of a2_wordlist.csv by build_a2.py
(which does not know these rows) and it restores the same state.

    python3 a2_build/src/apply_benchmark.py

1. ADDITIONS — every row of benchmark_en/additions_verified.csv whose status is verified or
   corrected is appended to a2_wordlist.csv under its new_id (A2-1863…, recorded in
   id_map.csv; existing ids are never renumbered). Forms come from the verification record
   (kirtis.info / en.wiktionary), the rest from proposed_additions.csv. Phase P-L.
   Failed rows are left out (none on 2026-10-17). P-078 kaimynystė is also on the deferral
   list ("B1 pack"), so it goes straight to deferred_B1.csv with its new id.
2. GLOSS ALIGNMENTS — the 67 English headwords of gloss_alignments.csv are written to a new
   column `english_alt` (alternative English glosses; `english`, the caption, is unchanged)
   in a2_wordlist.csv, or in master_wordlist.csv for A1 cards.
3. DEFERRALS — rows of proposed_deferrals.csv whose reason says "B1 pack" leave a2_wordlist.csv
   for a2_build/deferred_B1.csv, keeping their ids and every column. Rows marked "keep … owner
   call" stay. wool/vilna stays (its deferral is conditional). A1 (Fluent Forever) rows on the
   list are not moved: they belong to the A1 deck.
"""
import csv, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
B = os.path.join(ROOT, "a2_build")
A2 = os.path.join(B, "a2_wordlist.csv")
MASTER = os.path.join(ROOT, "master_wordlist.csv")
IDMAP = os.path.join(B, "id_map.csv")
DEFER = os.path.join(B, "deferred_B1.csv")
BE = os.path.join(B, "benchmark_en")
TODAY = "2026-10-17"

PHASE, PHASE_NAME = "P-L", "English benchmark additions"
CAT = {"N": "Nouns", "V": "Verbs", "V impers.": "Verbs", "V phrase": "Verbs", "A": "Adjectives",
       "A (participle)": "Adjectives", "A (pred.)": "Adjectives", "ADV": "Adverbs", "ADV phrase": "Adverbs",
       "PRON": "Pronouns", "PREP": "Prepositions", "PHRASE": "Functions", "SENT": "Extended patterns"}
TYPE = {"N": "N", "V": "V", "V impers.": "V", "V phrase": "V", "A": "A", "A (participle)": "A",
        "A (pred.)": "A", "ADV": "ADV", "ADV phrase": "ADV", "PRON": "P", "PREP": "PREP",
        "PHRASE": "PHRASE", "SENT": "SENTENCE"}
DEFER_TO_B1_ADDITIONS = {"P-078"}          # kaimynystė: on the deferral list as "B1 pack"
KEEP_ON_A2 = {"vilna"}                     # "B1 pack (keep vilna if sweaters are a topic)"
DEFER_BY_ENGLISH = {"fuel": "kuras"}       # deferral row says degalai; our fuel card is kuras


def read(p):
    with open(p, encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(p, cols, rows):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)
    os.replace(tmp, p)


def gender_code(g, pos, fem):
    g = (g or "").strip()
    if pos.startswith("A") and not pos.startswith("ADV"):
        return "M/F" if fem else ""
    m = re.match(r"(m|f)( pl)?(?: \((\S+) f\))?", g)
    if not m:
        return ""
    if m.group(3):
        return "M/F"                       # person noun with a feminine pair, as A1 job nouns
    return m.group(1).upper() + (" pl" if m.group(2) else "")


def build_row(p, v, cols):
    pos = p["pos"]; route = p["route"]
    if route == "SENT":
        route = "CLOZE" if "{" in p["example_lt"] else "PHRASE"
    card_type = {"IMG": "image", "CLOZE": "cloze", "PHRASE": "phrase"}[route]
    fem = v["fem"] if (pos.startswith("A") and not pos.startswith("ADV")) else ""
    fpair = re.search(r"\((\S+) f\)", p["gender"]) if pos == "N" else None
    rank = re.search(r"PERLSI rank (\d+)", p["source"])
    notes = [f"benchmark addition {p['proposal_id']} ({p['en_source']}; {p['entry_rule']})",
             f"Lithuanian {v['status']} {TODAY} — a2_build/benchmark_en/additions_verified.csv"]
    if fpair: notes.append(f"feminine {fpair.group(1)}")
    if p["tu_jus"]: notes.append(f"tu/jūs: {p['tu_jus']}")
    if p["aspect_partner"]: notes.append(f"aspect partner {p['aspect_partner']}")
    if p["notes"]: notes.append(p["notes"])
    row = {c: "" for c in cols}
    row.update({
        "id": v["new_id"], "phase": PHASE, "phase_name": PHASE_NAME, "level": p["level"],
        "category": CAT.get(pos, "Nouns"), "english": p["english"], "type": TYPE.get(pos, pos),
        "card_type": card_type, "image_possible": "yes" if route in ("IMG", "PHRASE") else "no",
        "lithuanian_TARGET": p["lithuanian_TARGET"], "lt_pron": v["lt_pron"], "pron_src": v["pron_src"],
        "gen_sg": v["gen_sg"], "fem": fem, "gender": gender_code(v["gender"], pos, fem),
        "subject_phrase_EN": p["subject_phrase_EN"] if route in ("IMG", "PHRASE") else "",
        "status": "pending", "dup_check": ("sense card beside existing lemma" if p["already_in_deck"] else ""),
        "notes": "; ".join(notes), "source": "benchmark_en", "freq_rank": rank.group(1) if rank else "",
        "route": route, "check": (v["notes"] or "verified: kirtis.info / en.wiktionary"),
        "example_lt": p["example_lt"] or (p["lithuanian_TARGET"] if route == "PHRASE" else ""),
        "example_en": p["example_en"] or (p["english"] if route == "PHRASE" else ""),
        "pres3": v["pres3"], "past3": v["past3"]})
    return row


def main():
    cols, a2 = read(A2)
    if "english_alt" not in cols:
        cols = cols + ["english_alt"]
    have = {r["id"] for r in a2}
    _, prop = read(os.path.join(BE, "proposed_additions.csv"))
    _, ver = read(os.path.join(BE, "additions_verified.csv"))
    pv = {p["proposal_id"]: p for p in prop}
    dcols = None
    deferred = read(DEFER)[1] if os.path.exists(DEFER) else []
    dkeys = {r["id"] for r in deferred}

    # 1. additions
    added, failed, to_defer = [], [], []
    for v in ver:
        p = pv[v["proposal_id"]]
        if v["status"] not in ("verified", "corrected"):
            failed.append(v); continue
        row = build_row(p, v, cols)
        if v["proposal_id"] in DEFER_TO_B1_ADDITIONS:
            row["deferred_reason"] = "benchmark addition, but on proposed_deferrals.csv as 'Oxford B1; B1 pack'"
            row["deferred_on"] = TODAY
            to_defer.append(row); continue
        if row["id"] not in have:
            a2.append(row); have.add(row["id"]); added.append(row["id"])

    # id_map: reserve every new id (incl. the deferred one)
    icols, imap = read(IDMAP)
    iids = {r["id"] for r in imap}
    for v in ver:
        if v["status"] in ("verified", "corrected") and v["new_id"] not in iids:
            imap.append({"id": v["new_id"], "lithuanian_TARGET": v["lithuanian_TARGET"],
                         "english": pv[v["proposal_id"]]["english"]})
    write(IDMAP, icols, imap)

    # 2. gloss alignments -> english_alt
    mcols, master = read(MASTER)
    if "english_alt" not in mcols:
        mcols = mcols + ["english_alt"]
    _, gl = read(os.path.join(BE, "gloss_alignments.csv"))
    unmatched = []
    def variants(lt):
        out = {lt.strip().lower()}
        base = re.sub(r"\(.*?\)", "", lt).strip().lower()
        out.add(base)
        for inner in re.findall(r"\((.*?)\)", lt):
            if not inner.startswith("+"):
                out.add(inner.strip().lower())
        return {o for o in out if o}
    def add_alt(r, en):
        cur = [x.strip() for x in (r.get("english_alt") or "").split(" | ") if x.strip()]
        if en.strip().lower() != (r.get("english") or "").strip().lower() and en not in cur:
            cur.append(en)
        r["english_alt"] = " | ".join(cur)
    for g in gl:
        vs = variants(g["our_lithuanian"])
        def tv(t):   # target variants: "marškinėliai (maikė)", "žurnalistas/žurnalistė"
            t = re.sub(r"\(.*?\)", "", t).strip().lower()
            return {t} | {x.strip() for x in t.split("/") if x.strip()}
        hits = [r for r in a2 if tv(r["lithuanian_TARGET"]) & vs]
        hits += [r for r in master if tv(r["lithuanian_TARGET"]) & vs]
        if not hits:
            unmatched.append(g["our_lithuanian"]); continue
        for r in hits:
            add_alt(r, g["english_list_word"])
    write(MASTER, mcols, master)

    # 3. deferrals
    _, dl = read(os.path.join(BE, "proposed_deferrals.csv"))
    moved = []
    keep = []
    for r in a2:
        reason = None
        for d in dl:
            if "B1 pack" not in d["reason"]:
                continue
            lts = {x.strip().lower() for x in d["lithuanian"].split("/")}
            lt = r["lithuanian_TARGET"].strip().lower()
            if (lt in lts or DEFER_BY_ENGLISH.get(d["english"]) == lt) and lt not in KEEP_ON_A2:
                reason = f"{d['english']} — {d['reason']}"
                break
        if reason:
            r = dict(r); r["deferred_reason"] = reason; r["deferred_on"] = TODAY
            to_defer.append(r); moved.append(r["id"])
        else:
            keep.append(r)
    dcols = cols + ["deferred_reason", "deferred_on"]
    for r in to_defer:
        if r["id"] not in dkeys:
            deferred.append(r); dkeys.add(r["id"])
    write(DEFER, dcols, deferred)
    write(A2, cols, keep)
    print(f"added {len(added)} | failed {len(failed)} | deferred now {len(deferred)} "
          f"(moved this run {len(moved)}) | a2 rows {len(keep)} | gloss unmatched: {unmatched}")


if __name__ == "__main__":
    main()
