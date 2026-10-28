#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""supersede_v1.py — set aside the recorded takes the naturalness round made stale (one shot, 2026-10-28).

    python3 rounds/2026-10-28_naturalness/supersede_v1.py            # dry run: lists the re-takes
    python3 rounds/2026-10-28_naturalness/supersede_v1.py --apply

Runs after apply_v1.py and amend_v3.py. For every card of final_v1.csv (its key followed through every key map to
the current key) and each of its takes (`<key>`; cloze/pair rows also `<key>_s`), the words the recorder would now
ask for are computed exactly as build_recorder.py does (read_script / script_text; sentences without the braces),
and compared with the `said` of the take's current audio_source.tsv row, accent-, case- and punctuation-blind
(build_recorder.said_key). A human take whose words no longer match is a RE-TAKE:
  * its mp3 moves (git mv, sha1 checked before and after) to media/audio/_history/<take>.<ms>.mp3 — set aside, never
    deleted (the naming tools/ingest_takes.py uses for a replaced take);
  * a row `<take>  superseded  media/audio/_history/<take>.<ms>.mp3  <old said>` is appended to data/audio_source.tsv
    (last row per key wins), so build_recorder.py lists the take as "retake" (was = the old words) and the package
    no longer ships the old recording.
Log: rounds/2026-10-28_naturalness/retakes_v1.tsv (take, card, old said, new say, old file, new file, bytes, sha1).
Cross-check: every card final_v1 marks recorded=y except the three English-only rows (0043, 0535, 0768) must give
at least one re-take, and no card marked n may have a human take that changes.
"""
import csv, hashlib, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(ROOT)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools"))
import build_recorder as BR   # noqa: E402  (read_script, script_text, said_key, load_audio_source)
import keymap                 # noqa: E402

PLAN = "rounds/2026-10-28_naturalness/final_v1.csv"
AUDIO_SOURCE = "data/audio_source.tsv"
LOG = "rounds/2026-10-28_naturalness/retakes_v1.tsv"
ENGLISH_ONLY = {"0043_atsiprasau", "0535_taciau", "0768_geros_keliones"}


def sha1(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def current_says():
    """take key -> what the recorder now asks for (A2 list + sentence cards; the plan has no cards_anki rows)."""
    out = {}
    for r in csv.DictReader(open("data/a2_wordlist.csv", encoding="utf-8")):
        k, route = r["id"], r.get("route", "")
        head = re.sub(r"\s*\(.*\)", "", r["lithuanian_TARGET"]).strip()
        pron = r.get("lt_pron", "") or head
        out[k] = (route, BR.script_text(BR.read_script(pron, r)))
        if route in ("CLOZE", "PAIR"):
            out[k + "_s"] = (route, r["example_lt"].replace("{", "").replace("}", ""))
    for r in csv.DictReader(open("data/sentences/sentences.csv", encoding="utf-8")):
        out[r["id"]] = ("SENT", r["lt"].replace("{", "").replace("}", ""))
    return out


def main(apply):
    plan = list(csv.DictReader(open(PLAN, encoding="utf-8")))
    says = current_says()
    asrc = BR.load_audio_source()
    retakes, problems = [], []
    for p in plan:
        old = p["key"]
        cur = keymap.canonical(old) or old
        if cur not in says:
            problems.append(f"{old} -> {cur}: not in the live lists"); continue
        takes = [cur] + ([cur + "_s"] if cur + "_s" in says else [])
        hits = []
        for t in takes:
            a = asrc.get(t)
            if not a or not a["source"].startswith("human"):
                continue
            if BR.said_key(a["said"]) != BR.said_key(says[t][1]):
                hits.append((t, a))
        if p["recorded"] == "y" and old not in ENGLISH_ONLY and not hits:
            problems.append(f"{cur}: final_v1 says recorded, but no take changed")
        if p["recorded"] != "y" and hits:
            problems.append(f"{cur}: final_v1 says not recorded, but {len(hits)} human take(s) changed: {[h[0] for h in hits]}")
        for t, a in hits:
            src = a["file"] or f"media/audio/{t}.mp3"
            if not os.path.exists(src):
                problems.append(f"{t}: {src} missing"); continue
            retakes.append(dict(take=t, card=cur, old_said=a["said"], new_say=says[t][1], old_file=src))
    for r in retakes:
        print(f"  RE-TAKE {r['take']:34} was: {r['old_said']!r:48} now: {r['new_say']!r}")
    print(f"{len(retakes)} re-takes from {len({r['card'] for r in retakes})} cards")
    for x in problems:
        print("  PROBLEM", x)
    if problems:
        raise SystemExit("problems found; nothing moved")
    if not apply:
        return 0
    ms = int(time.time() * 1000)
    raw = open(AUDIO_SOURCE, encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    if not raw.endswith(eol):
        raise SystemExit(f"{AUDIO_SOURCE} does not end with a newline; refusing to append")
    rows = []
    for r in retakes:
        new = f"media/audio/_history/{r['take']}.{ms}.mp3"
        if os.path.exists(new):
            raise SystemExit(f"{new} exists")
        h, size = sha1(r["old_file"]), os.path.getsize(r["old_file"])
        subprocess.run(["git", "mv", r["old_file"], new], check=True)
        if sha1(new) != h:
            raise SystemExit(f"hash mismatch after move: {r['old_file']} -> {new}")
        r.update(new_file=new, bytes=size, sha1=h)
        rows.append("\t".join([r["take"], "superseded", new, r["old_said"]]))
    with open(AUDIO_SOURCE, "a", encoding="utf-8", newline="") as f:
        f.write(eol.join(rows) + eol)
    with open(LOG, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter="\t", lineterminator="\n")
        w.writerow(["take", "card", "old_said", "new_say", "old_file", "new_file", "bytes", "sha1"])
        for r in retakes:
            w.writerow([r[c] for c in ("take", "card", "old_said", "new_say", "old_file", "new_file", "bytes", "sha1")])
    print(f"moved {len(retakes)} takes to media/audio/_history/; {len(rows)} superseded rows appended; log {LOG}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
