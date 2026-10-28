#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""apply_v1.py — apply final_v1.csv (the owner-approved, second-checked naturalness round) to the live data.
One shot, 2026-10-28.

    python3 rounds/2026-10-28_naturalness/apply_v1.py            # dry run: prints every field change
    python3 rounds/2026-10-28_naturalness/apply_v1.py --apply

Runs on the keys of key_map_v2 (final_v1's `key` column). The re-slug of the retargeted and re-worded cards
(key_map_v3) is a separate step afterwards: amend_v3.py (tools/rename_keys.py's token rewrite + hash-checked
media moves). The re-takes are a third step: supersede_v1.py.

What it writes (CSV quoting and CRLF kept; every changed row gets a line in `notes`):
  EDIT (67)     data/a2_wordlist.csv example_lt / example_en; phrase cards also lithuanian_TARGET / english /
                lt_pron where final_v1's `field(s)` names them; the four gloss edits of `extra_fields`;
                sentence cards (0856, 1410): data/sentences/sentences.csv lt / en (0856's words_used: euras for litas).
  RETARGET (6)  headword, gloss, pron, pron_src, forms, sentence and the stress source in `check` (RETARGET below).
                Spec §7: stress marks are sourced, never generated. A pron final_v1 marks UNSOURCED is left unmarked
                (empty lt_pron, as for every other unsourced headword) and goes to OWNER_STRESS_v1.csv.
                One correction to final_v1, by a source read: kalbù (0778) IS in the en.wiktionary dump — the form-of
                entry "kalbu" (head kalbù, "first-person singular present of kalbėti"); it is marked, not listed.
  NEW_CARD (2)  keys minted with tools/rename_keys.mint (= `--mint`), "Ką daryti?" first, then "spūstis" (minted
                on the file state after the first was written); rows appended to data/a2_wordlist.csv; each
                inserted into data/study_order.csv straight after its anchor (0340, 1514), later positions +1,
                old_order = the position before this run; id_map.csv rows.
  id_map.csv    headword / gloss of every card whose headword or gloss changed.
  context_notes 1169: the usage note is about "Greitai pasveik!" (pasveik / pasveikite); the card now teaches
                "Sveik!", so the note is withdrawn from the back (confidence -> withdrawn, text kept), as 0331 was
                on 2026-10-20.
  study_order   the `lithuanian` column of every card whose headword changed.
"""
import csv, io, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, ROOT)
import rename_keys as R          # noqa: E402  (slug, mint)

PLAN = "rounds/2026-10-28_naturalness/final_v1.csv"
WL = "data/a2_wordlist.csv"
SENT = "data/sentences/sentences.csv"
IDMAP = "data/id_map.csv"
CTX = "data/context_notes.csv"
ORDER = "data/study_order.csv"
TAG = "naturalness 2026-10-28 (rounds/2026-10-28_naturalness/final_v1)"
OWNER_SHEET = "rounds/2026-10-28_naturalness/OWNER_STRESS_v1.csv"

# Prons of EDIT rows (final_v1 extra_fields lt_pron=…); each word's mark is the card's own sourced mark.
EDIT_PRON = {
    "0214_cia_mano_draugas": "Čià màno draũgas. / Susipažìnkite, taĩ màno draũgas.",
    "0966_iki_greito": "Ikì greĩto!",
    # 1243: final_v1 proposes Minutė̃lę! — the accusative is in no source read: unmarked (empty), owner sheet.
    "1243_minutele": "",
}
# final_v1 gives 1501's new sentence without cloze braces ("Veikiantis liftas – kairėje."): as written the build
# would drop the card (cloze_text finds no gap). The gap is the card's own target, as in every other row.
CLOZE_FIX = {"1501_veikiantis": ("Veikiantis liftas – kairėje.", "{Veikiantis} liftas – kairėje.")}
# Gloss edits of EDIT rows (final_v1 extra_fields english=…)
EDIT_GLOSS = {
    "1006_uzsiemimas": "class, session (also: activity, pastime)",
    "1733_nesveikas": "unhealthy",
    "1852_dinges": "missing; lost",
    "1399_tvarka": "order; tidiness",
}

RETARGET = {
    "0239_orai": dict(
        lithuanian_TARGET="oras", english="weather (also: air)", lt_pron="óras",
        pron_src="en.wiktionary (kaikki dump: óras m, stress pattern 3)", gen_sg="óro", gender="M",
        check="stress, gen_sg, gender: en.wiktionary via the kaikki.org dump (óras m, lt-noun-m-as-3; gen. óro), "
              "read 2026-10-28 (naturalness retarget orai -> oras)",
        notes_add="retarget orai -> oras 2026-10-28 (naturalness); 1200_oras 'air' @1200 keeps its card"),
    "2422_puslitris": dict(
        lithuanian_TARGET="bokalas", english="beer mug; a (mug of) beer", lt_pron="bokãlas",
        pron_src="en.wiktionary (kaikki dump: bokãlas m, stress pattern 2, 'mug, jug (chiefly for drinking beer)')",
        gen_sg="bokãlo", gender="M",
        check="stress, gen_sg: en.wiktionary via the kaikki.org dump (bokãlas m, lt-noun-m-as-2; gen. bokãlo), "
              "read 2026-10-28 (naturalness retarget puslitris -> bokalas)",
        notes_add="retarget puslitris -> bokalas 2026-10-28: owner has never heard puslitris at a bar; bokalas is the word"),
    "1589_naudotis": dict(
        lithuanian_TARGET="pasinaudoti", english="to use, make use of (perf. of naudotis; +instr.)", lt_pron="",
        pron_src="owner (pending: rounds/2026-10-28_naturalness/OWNER_STRESS_v1.csv)",
        check="stress: UNSOURCED (pasinaudoti is not in the kaikki.org en.wiktionary dump, 2026-10-28) — shown "
              "unmarked, on OWNER_STRESS_v1.csv",
        notes_add="retarget naudotis -> pasinaudoti 2026-10-28 (the cloze lemma; naudotis stays in the gloss)"),
    "1968_vieta_prie_tako": dict(
        lithuanian_TARGET="vieta prie praėjimo", lt_pron="",
        check="stress: UNSOURCED (praėjimas is not in the kaikki.org en.wiktionary dump, 2026-10-28) — shown "
              "unmarked, on OWNER_STRESS_v1.csv",
        notes_add="retarget vieta prie tako -> vieta prie praėjimo 2026-10-28 (takas is a footpath; airlines say praėjimas)"),
    "0778_galiu_truputi_kalbeti": dict(
        lithuanian_TARGET="Truputį kalbu lietuviškai.", english="I speak a little Lithuanian.",
        lt_pron="Trupùtį kalbù lietùviškai.",
        check="stress: trupùtį = 0455_truputi's pron (kirtis.info per word, 2026-10-18); kalbù: en.wiktionary via the "
              "kaikki.org dump, form-of entry 'kalbu' (head kalbù, 'first-person singular present of kalbėti'); "
              "lietùviškai: en.wiktionary via the kaikki.org dump (adverb) — read 2026-10-28",
        notes_add="phrase replaced 2026-10-28 (naturalness: 'Galiu truputį kalbėti' is a calque of 'I can speak a little')"),
    "1169_greitai_pasveik": dict(
        lithuanian_TARGET="Sveik!", english="Get well! (to someone who is ill)", lt_pron="",
        check="stress: UNSOURCED (Sveĩk! proposed in the second check: imperative of sveikti, card 1277 sveĩkti from "
              "the kirtis.info engine; neither sveikti nor sveik is in the kaikki.org dump) — shown unmarked, on "
              "OWNER_STRESS_v1.csv",
        notes_add="retarget Greitai pasveik! -> Sveik! 2026-10-28 (owner wording)"),
}

NEW = [   # (mint headword, anchor key, row)
    ("Ką daryti?", "0340_padaryti", dict(
        phase="P-L", phase_name="English benchmark additions", level="A1", category="Functions",
        english="What can you do? (resigned shrug; also: what should I do?)", type="PHRASE", card_type="phrase",
        image_possible="yes", lithuanian_TARGET="Ką daryti?", lt_pron="Ką̃ darýti?",
        pron_src="per word: ką̃ (0283_ka, en.wiktionary), darýti (0307_daryti, en.wiktionary)", status="pending",
        notes=f"{TAG}: NEW_CARD (owner note on 0340: 'a classic line … less a question and more of a what can you "
              "do?'); no picture yet — a phrase card enters the build and the recorder once it has one",
        source="owner 2026-10-28", route="PHRASE",
        check="stress: ką̃ = kas acc. sg. in the en.wiktionary declension table (kaikki.org dump) and card 0283_ka; "
              "darýti = en.wiktionary (kaikki.org dump) and card 0307_daryti — read 2026-10-28",
        example_lt="Ką daryti?", example_en="What can you do? (resigned shrug; also: what should I do?)")),
    ("spūstis", "1514_eismas", dict(
        phase="P-F", phase_name="Vocabulary expansion", level="A2", category="Transportation", english="traffic jam",
        type="N", card_type="cloze", image_possible="no", lithuanian_TARGET="spūstis", lt_pron="",
        pron_src="owner (pending: rounds/2026-10-28_naturalness/OWNER_STRESS_v1.csv)", gen_sg="spūsties", gender="F",
        status="pending",
        notes=f"{TAG}: NEW_CARD (owner note on 1514: 'spūstys' is the word for heavy traffic in the centre; LRT / "
              "Reidas: 'nestrigti spūstyse')", source="owner 2026-10-28", route="CLOZE",
        check="stress: UNSOURCED (spūstis is not in the kaikki.org en.wiktionary dump, 2026-10-28) — headword, "
              "gen_sg spūsties and the plural spūstys shown unmarked, on OWNER_STRESS_v1.csv; gender: F (owner, "
              "final_v1); gen_sg: not from a source either",
        example_lt="Centre {spūstys}.", example_en="There are traffic jams in the centre.")),
]


def read(path):
    raw = open(path, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    rd = csv.DictReader(io.StringIO(raw))
    return rd.fieldnames, list(rd), eol


def dump(fields, rows, eol):
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=fields, lineterminator=eol)
    w.writeheader(); w.writerows(rows)
    return out.getvalue()


def setf(r, f, v, log, key):
    if f not in r:
        raise SystemExit(f"{key}: no column {f}")
    if r[f] != v:
        log.append(f"{key:34} {f:17} {r[f]!r} -> {v!r}")
        r[f] = v


def add_note(r, text, log, key, col="notes"):
    line = f"{TAG}: {text}"
    if line not in r[col]:
        setf(r, col, (r[col] + "; " if r[col] else "") + line, log, key)


def short(s, n=70):
    return s if len(s) <= n else s[:n - 1] + "…"


def extra(p, field):
    """the value of `field=` in final_v1's extra_fields (up to the next ' | ')."""
    for part in p["extra_fields"].split(" | "):
        if part.startswith(field + "="):
            return part[len(field) + 1:]
    return None


def main(apply):
    plan = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    wf, wrows, weol = read(WL); sf, srows, seol = read(SENT)
    if_, irows, ieol = read(IDMAP); cf, crows, ceol = read(CTX); of, orows, oeol = read(ORDER)
    wby = {r["id"]: r for r in wrows}; sby = {r["id"]: r for r in srows}
    log, counts = [], {"EDIT": 0, "RETARGET": 0, "NEW_CARD": 0}
    headword_changed = set()
    for p in plan:
        k, act = p["key"], p["action"]
        fields = [f.strip() for f in p["field(s)"].split(";")]
        if act == "NEW_CARD":
            continue
        counts[act] += 1
        if k in sby:                                            # sentence cards
            r = sby[k]
            if r["lt"] != p["old"]:
                raise SystemExit(f"{k}: sentence on disk is not final_v1's `old`")
            setf(r, "lt", p["new"], log, k); setf(r, "en", p["new_english"], log, k)
            if k == "0856_duona_kainuoja_viena_lita":
                setf(r, "words_used", r["words_used"].replace("0609_litas", "0262_euras"), log, k)
            headword_changed.add(k)
            add_note(r, f"{act} '{p['old']}' -> '{p['new']}'", log, k)
            continue
        if k not in wby:
            raise SystemExit(f"{k}: not in {WL} or {SENT}")
        r = wby[k]
        old_lt = r["example_lt"]
        if "example_lt" in fields and r["example_lt"] != p["old"] and r["lithuanian_TARGET"] != p["old"]:
            raise SystemExit(f"{k}: example on disk {r['example_lt']!r} is not final_v1's `old` {p['old']!r}")
        if act == "EDIT":
            if "example_lt" in fields:
                new = p["new"]
                if k in CLOZE_FIX:
                    if CLOZE_FIX[k][0] != new:
                        raise SystemExit(f"{k}: CLOZE_FIX does not match final_v1")
                    new = CLOZE_FIX[k][1]
                setf(r, "example_lt", new, log, k)
            if "example_en" in fields:
                setf(r, "example_en", p["new_english"], log, k)
            if r["route"] == "PHRASE":
                if "lithuanian_TARGET" in fields:
                    setf(r, "lithuanian_TARGET", p["new"], log, k); headword_changed.add(k)
                if "english" in fields:
                    setf(r, "english", p["new_english"], log, k)
            if "lt_pron" in fields:
                setf(r, "lt_pron", EDIT_PRON[k], log, k)
            g = extra(p, "english")
            if g is not None:
                if EDIT_GLOSS.get(k) != g:
                    raise SystemExit(f"{k}: EDIT_GLOSS disagrees with final_v1")
                setf(r, "english", g, log, k)
            what = []
            if "example_lt" in fields and old_lt != r["example_lt"]:
                what.append(f"sentence '{short(old_lt)}' -> '{short(r['example_lt'])}'")
            if any(f in fields for f in ("english", "example_en")) or g:
                what.append("English" + (f" (gloss '{g}')" if g else ""))
            if "lithuanian_TARGET" in fields:
                what.append(f"headword -> '{r['lithuanian_TARGET']}'")
            if "lt_pron" in fields:
                what.append(f"pron {('-> ' + r['lt_pron']) if r['lt_pron'] else 'unmarked (form unsourced; OWNER_STRESS_v1)'}")
            if k in CLOZE_FIX:
                what.append("cloze gap {Veikiantis} added (final_v1 had none)")
            add_note(r, "EDIT " + "; ".join(what), log, k)
        else:                                                   # RETARGET
            rt = RETARGET[k]
            if rt["lithuanian_TARGET"] != (extra(p, "lithuanian_TARGET") or p["new"]):
                raise SystemExit(f"{k}: RETARGET headword disagrees with final_v1")
            old_head = r["lithuanian_TARGET"]
            for f, v in rt.items():
                if f not in ("notes_add",):
                    setf(r, f, v, log, k)
            ex = extra(p, "example_lt") or p["new"]
            setf(r, "example_lt", ex, log, k)
            if r["route"] == "PHRASE" or "example_en" in fields:
                if not extra(p, "example_en"):
                    setf(r, "example_en", p["new_english"], log, k)
            headword_changed.add(k)
            add_note(r, f"RETARGET '{old_head}' -> '{r['lithuanian_TARGET']}'; sentence '{short(old_lt)}' -> "
                        f"'{short(r['example_lt'])}'; {rt['notes_add']}", log, k)
    if counts != {"EDIT": 67, "RETARGET": 6, "NEW_CARD": 0}:
        raise SystemExit(f"unexpected counts {counts}")

    # id_map: headword + gloss
    for r in irows:
        w = wby.get(r["id"])
        if w and (r["lithuanian_TARGET"] != w["lithuanian_TARGET"] or r["english"] != w["english"]) and \
                r["id"] in {p["key"] for p in plan}:
            setf(r, "lithuanian_TARGET", w["lithuanian_TARGET"], log, "id_map " + r["id"])
            setf(r, "english", w["english"], log, "id_map " + r["id"])
    # context note of 1169 (about Greitai pasveik!)
    for r in crows:
        if r["key"] == "1169_greitai_pasveik":
            setf(r, "confidence", "withdrawn", log, "context_notes 1169")
            add = (" [withdrawn 2026-10-28: the card now teaches Sveik! (naturalness final_v1); this note is about "
                   "Greitai pasveik! / pasveikite]")
            if add not in r["source_note"]:
                setf(r, "source_note", r["source_note"] + add, log, "context_notes 1169")
    # study order: headword column
    lt_of = {k: (sby[k]["lt"] if k in sby else wby[k]["lithuanian_TARGET"]) for k in headword_changed}
    for r in orows:
        if r["key"] in lt_of:
            setf(r, "lithuanian", lt_of[r["key"]], log, "study_order " + r["key"])

    for l in log:
        print(l)
    print(f"{len(log)} field changes; {counts}")
    if not apply:
        print("dry run: new cards would be minted next:", R.mint(NEW[0][0]), "then +1")
        return 0
    for path, f, rows, eol in ((WL, wf, wrows, weol), (SENT, sf, srows, seol), (IDMAP, if_, irows, ieol),
                               (CTX, cf, crows, ceol), (ORDER, of, orows, oeol)):
        open(path, "w", encoding="utf-8", newline="").write(dump(f, rows, eol))

    # NEW_CARD: mint on the file state, write, mint the next
    import build_study_order_v3 as SO
    minted = []
    pre = {r["key"]: r["order"] for r in read(ORDER)[1]}      # positions before this run -> old_order
    for head, anchor, row in NEW:
        key = R.mint(head)
        wf, wrows, weol = read(WL); of, orows, oeol = read(ORDER); if_, irows, ieol = read(IDMAP)
        if key in {r["id"] for r in wrows}:
            raise SystemExit(f"{key}: already in {WL}")
        full = {f: "" for f in wf}; full.update(row); full["id"] = key
        wrows.append(full)
        open(WL, "w", encoding="utf-8", newline="").write(dump(wf, wrows, weol))
        # study order: straight after the anchor; columns as the builder computes them
        cards = SO.load_cards({}, {}); SO.score_cards(cards, *SO.load_sources())
        c = next(c for c in cards if c["key"] == key)
        ai = next(i for i, r in enumerate(orows) if r["key"] == anchor)
        block = orows[ai]["block"]
        if not block.startswith(row["level"]):
            raise SystemExit(f"{key}: level {row['level']} but anchor {anchor} is in {block}")
        new = dict(order="", key=key, block=block, lithuanian=row["lithuanian_TARGET"], category=row["category"],
                   lane=c["lane"], route=row["route"], tier=c["tier"], sub_rank=c["sub"], press_rank=c["press"] or "",
                   score=f"{c['score']:.3f}", old_order="")
        orows.insert(ai + 1, new)
        for i, r in enumerate(orows, 1):
            r["order"] = str(i)
            r["old_order"] = pre.get(r["key"], "")
        open(ORDER, "w", encoding="utf-8", newline="").write(dump(of, orows, oeol))
        irows.append({"id": key, "lithuanian_TARGET": row["lithuanian_TARGET"], "english": row["english"], "merged_into": ""})
        open(IDMAP, "w", encoding="utf-8", newline="").write(dump(if_, irows, ieol))
        minted.append((key, ai + 2, anchor))
        print(f"minted {key} ({head!r}); study order @{ai + 2}, after {anchor}")
    print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
