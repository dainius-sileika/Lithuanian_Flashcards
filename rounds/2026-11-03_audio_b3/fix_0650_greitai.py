#!/usr/bin/env python3
"""fix_0650_greitai.py — the owner's word-order correction of 2026-11-03, applied BEFORE audio batch 3 is ingested.

Owner (verbatim): "Autobusas atvažios greitai - i'm pretty sure that means it will arrive 'fastly' as it were, whereas
I hear lithuanians saying 'greitai atvažios' to mean soon, quickly."

Card 0650_greitai (A1 cloze, gloss "soon"):
  data/a2_wordlist.csv   example_lt  "Autobusas atvažiuos {greitai}."  ->  "Autobusas {greitai} atvažiuos."
                         check       ""  ->  "owner 2026-11-03: word order, greitai before the verb = soon"
                         example_en  "The bus will come soon." (unchanged)
  data/recording_list.csv  the 0650_greitai_s row's `lithuanian` and `say` get the new words, exactly what
                         `build_recorder.py A2` writes for that row (checked by --verify against a regeneration to
                         scratch; a CLOZE take needs no picture, so the cloud clone can regenerate it). The ingest
                         compares each take's recorded words with `say` here, so a take of the OLD words is kept aside
                         (manifest_kept.tsv) and never shipped. The sheet itself is regenerated on the Mac afterwards.

Only these cells change; every other byte of both files is kept (CRLF, quoting). Idempotent: a second run changes
nothing. Run from the repository root:  python3 rounds/2026-11-03_audio_b3/fix_0650_greitai.py [--verify]
"""
import csv
import io
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WL = os.path.join(ROOT, "data", "a2_wordlist.csv")
RL = os.path.join(ROOT, "data", "recording_list.csv")
KEY = "0650_greitai"
OLD_S, NEW_S = "Autobusas atvažiuos {greitai}.", "Autobusas {greitai} atvažiuos."
CHECK = "owner 2026-11-03: word order, greitai before the verb = soon"
EN = "The bus will come soon."


def rewrite_line(path, match, change, lineterminator):
    """Re-serialise the one line whose first field is `match` after change(fields, header) -> fields."""
    raw = open(path, "rb").read().decode("utf-8")
    lines = raw.splitlines(keepends=True)
    header = next(csv.reader([lines[0]]))
    hits = [i for i, l in enumerate(lines) if next(csv.reader([l]), [""])[0] == match]
    if len(hits) != 1:
        raise SystemExit(f"{path}: {len(hits)} lines for {match}")
    i = hits[0]
    old = next(csv.reader([lines[i]]))
    new = change(list(old), header)
    if new == old:
        return False
    buf = io.StringIO()
    csv.writer(buf, lineterminator=lineterminator).writerow(new)
    lines[i] = buf.getvalue()
    open(path, "wb").write("".join(lines).encode("utf-8"))
    back = list(csv.reader(io.StringIO(open(path, encoding="utf-8").read())))
    assert back[i] == new, "re-read differs"
    return True


def wl_change(f, h):
    c = {n: j for j, n in enumerate(h)}
    if f[c["example_lt"]] == NEW_S and f[c["check"]] == CHECK:
        return f
    assert f[c["example_lt"]] == OLD_S, f[c["example_lt"]]
    assert f[c["example_en"]] == EN, f[c["example_en"]]
    assert f[c["check"]] in ("", CHECK), f[c["check"]]
    f[c["example_lt"]], f[c["check"]] = NEW_S, CHECK
    return f


def rl_change(f, h):
    c = {n: j for j, n in enumerate(h)}
    plain = NEW_S.replace("{", "").replace("}", "")
    f[c["lithuanian"]] = plain
    f[c["say"]] = plain
    return f


def verify():
    """Regenerate the list to scratch and compare the 0650 rows (all columns but the running take number)."""
    tmp = tempfile.mkdtemp()
    env = dict(os.environ, RECORDING_LIST_OUT=os.path.join(tmp, "rl.csv"), RECORDER_OUT=os.path.join(tmp, "r.html"))
    subprocess.run([sys.executable, "build_recorder.py", "A2"], cwd=ROOT, env=env, check=True, capture_output=True)
    gen = {r["file_name"]: r for r in csv.DictReader(open(os.path.join(tmp, "rl.csv"), encoding="utf-8"))}
    live = {r["file_name"]: r for r in csv.DictReader(open(RL, encoding="utf-8"))}
    ok = True
    for fn in (KEY + ".mp3", KEY + "_s.mp3"):
        a, b = dict(gen.get(fn, {})), dict(live.get(fn, {}))
        a.pop("take", None); b.pop("take", None)
        print(f"{fn}: {'same as a regeneration' if a == b else 'DIFFERS'}  say={b.get('say')!r}")
        ok &= a == b
    return ok


def main(argv):
    os.chdir(ROOT)
    nl = "\r\n" if b"\r\n" in open(WL, "rb").read(4096) else "\n"
    a = rewrite_line(WL, KEY, wl_change, nl)
    # recording_list.csv lines start with the running take number: find the take's number, then rewrite that line
    nl2 = "\r\n" if b"\r\n" in open(RL, "rb").read(4096) else "\n"
    r = [x for x in csv.DictReader(open(RL, encoding="utf-8")) if x["file_name"] == KEY + "_s.mp3"]
    if len(r) != 1:
        raise SystemExit(f"{RL}: {len(r)} rows for {KEY}_s")
    b = rewrite_line(RL, r[0]["take"], lambda f, h: rl_change(f, h) if f[1] == KEY + "_s.mp3" else f, nl2)
    print(f"a2_wordlist.csv: {'changed' if a else 'already applied'}; "
          f"recording_list.csv: {'changed' if b else 'already applied'}")
    if "--verify" in argv and not verify():
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
