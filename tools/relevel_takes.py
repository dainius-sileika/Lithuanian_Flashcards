#!/usr/bin/env python3
"""relevel_takes.py — re-process shipped human takes that are far too quiet, from their raw masters, with the same
click-safe processing as every new take (tools/process_take.py: linear gain only, no limiter).

    python3 tools/relevel_takes.py --masters DIR [--masters DIR ...] --log-dir _archive/takes/<name>
                                   [--below -30] [--proc-dir DIR] [--apply]

Why (docs/LESSONS_LEARNED.md, Audio, 2026-10-28): 63 July takes (numbers, question words: 0079_trys, 0150_kaip ...)
were shipped at -36 to -48 LUFS, 20-30 dB below the rest of the deck; their raw masters were kept on the Mac
(_archive/deprecated/recordings_raw/session_0726/, session_0728/) under the card names of July (A2-0044, 471_tylus).

  1. MEASURE every take whose current data/audio_source.tsv row is human (integrated loudness and true peak, ffmpeg
     ebur128) -> <log-dir>/loudness_before.tsv. A take below --below LUFS (default -30; the shipped set has a gap
     from -35.9 to -21.9) is SELECTED.
  2. MASTER: every older name of the key (tools/keymap.py aliases()) and the key itself, looked up as <name>.webm in
     each --masters folder. None, or two different files -> the take is LEFT ALONE.
  3. WORDS: when the master's folder has a manifest.tsv (key, word), its word must equal the first form of the take's
     `said` (or the whole `said`), accent-, case- and punctuation-blind (build_recorder.said_key) -> else LEFT ALONE.
  4. IDENTITY: the shipped mp3 must be this very recording: normalised cross-correlation of the shipped take against
     the master >= 0.99 at the best lag -> else LEFT ALONE. (This is what proves the words for a master without a
     manifest: the shipped take's `said` is the record of what this recording says.)
  5. PROCESS with tools/process_take.process(master, out, said): its cuts, flags and self-check decide; a FAIL is
     LEFT ALONE.
  6. --apply: the shipped mp3 moves to media/audio/_history/<key>.<ms>.mp3 (never overwritten, never deleted), the
     processed one is written to the same dest, and a row is APPENDED to data/audio_source.tsv (the file is append-
     only; the last row of a key wins, as for ingest_takes.py):  key  human:<log-dir name>  <dest>  <said, unchanged>
     The source value names the folder of this run's process log (_archive/takes/<log-dir name>/process_log.csv);
     every reader tests source.startswith("human").
Logs in <log-dir>: loudness_before.tsv, process_log.csv (ingest_takes.PLOG_FIELDS plus master, alias, sha256,
words check, identity r and lag, shipped loudness, history path), relevel_log.tsv (every selected take: action and
reason). Without --apply nothing outside <log-dir> is touched. --proc-dir keeps a copy of every processed mp3 there
(for tools/audio_review_page.py --relevel).
"""
import argparse
import csv
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

import numpy as np
from scipy.signal import fftconvolve

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, ROOT)
import keymap  # noqa: E402
import process_take  # noqa: E402
from ingest_takes import PLOG_FIELDS  # noqa: E402
from build_recorder import said_key  # noqa: E402

AUDIO_SOURCE = os.path.join(ROOT, "data", "audio_source.tsv")
HISTORY = os.path.join(ROOT, "media", "audio", "_history")
IDENTITY_MIN = 0.99
XC_SR = 16000


def ebur128(path):
    """(integrated LUFS, true peak dBTP) by ffmpeg's ebur128 filter."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null",
                          "-"], capture_output=True, text=True).stderr
    s = err[err.rindex("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf)", s).group(1)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf)", s).group(1)
    return float(i), float(p)


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(XC_SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def identity(shipped, master):
    """(r, lag_ms): normalised correlation of the overlap at the best lag. shipped[t] = master[t - lag]: lag -150 means
    the shipped take begins 150 ms into the master (the July processing had cut its first 150 ms)."""
    x, y = decode(master), decode(shipped)
    c = fftconvolve(y, x[::-1], mode="full")
    lag = int(np.argmax(np.abs(c))) - (len(x) - 1)
    if lag >= 0:
        ys = y[lag:lag + len(x)]
        xs = x[:len(ys)]
    else:
        xs = x[-lag:-lag + len(y)]
        ys = y[:len(xs)]
    r = float(np.dot(xs, ys) / np.sqrt(np.dot(xs, xs) * np.dot(ys, ys) + 1e-20))
    return round(r, 5), int(round(lag * 1000 / XC_SR))


def current_sources():
    out = {}
    for r in csv.DictReader(open(AUDIO_SOURCE, encoding="utf-8"), delimiter="\t"):
        out[r["key"]] = r                      # the last row of a key wins
    return out


def manifest_words(folder):
    p = os.path.join(folder, "manifest.tsv")
    if not os.path.exists(p):
        return None
    return {r["key"]: r.get("word", "") for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t")}


def rel(path):
    """A master's path as the project knows it (from _archive/ on), whatever the mount it was read from."""
    i = path.rfind("/_archive/")
    return path[i + 1:] if i >= 0 else os.path.basename(path)


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--masters", action="append", required=True)
    ap.add_argument("--log-dir", required=True)
    ap.add_argument("--below", type=float, default=-30.0)
    ap.add_argument("--proc-dir")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args(argv[1:])
    log_dir = os.path.abspath(a.log_dir)
    os.makedirs(log_dir, exist_ok=True)
    name = os.path.basename(log_dir.rstrip("/"))
    src = current_sources()
    human = sorted(k for k, r in src.items() if r["source"].startswith("human") and os.path.exists(os.path.join(ROOT, r["file"])))
    meas = {}
    for k in human:
        meas[k] = ebur128(os.path.join(ROOT, src[k]["file"]))
    with open(os.path.join(log_dir, "loudness_before.tsv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["key", "file", "I_LUFS", "TP_dBTP", "selected"])
        for k in sorted(human, key=lambda k: meas[k][0]):
            w.writerow([k, src[k]["file"], meas[k][0], meas[k][1], "yes" if meas[k][0] < a.below else ""])
    sel = sorted((k for k in human if meas[k][0] < a.below), key=lambda k: meas[k][0])
    words = {d: manifest_words(d) for d in a.masters}
    actions, plog = [], []
    tmp = tempfile.mkdtemp()
    run = datetime.datetime.now().isoformat(timespec="seconds")
    for k in sel:
        r = src[k]
        said, dest = r["said"], os.path.join(ROOT, r["file"])
        names = keymap.aliases(k) + [k]
        found = [(n, d, os.path.join(d, n + ".webm")) for n in names for d in a.masters
                 if os.path.exists(os.path.join(d, n + ".webm"))]
        if not found:
            actions.append([k, "", "left alone", "no raw master under any of its names: " + " ".join(names)]); continue
        if len({sha256(p) for _, _, p in found}) > 1:
            actions.append([k, " ".join(rel(p) for _, _, p in found), "left alone", "two different raw masters"]); continue
        alias, folder, master = found[0]
        wmap = words[folder]
        if wmap is not None and alias in wmap:
            w0 = said_key(wmap[alias])
            ok = w0 in (said_key(said.split("·")[0]), said_key(said))
            wcheck = f"manifest word '{wmap[alias]}' = said" if ok else f"manifest word '{wmap[alias]}' != said '{said}'"
            if not ok:
                actions.append([k, rel(master), "left alone", wcheck]); continue
        else:
            wcheck = "no manifest entry: words proven by identity with the shipped take"
        idr, lag = identity(dest, master)
        if idr < IDENTITY_MIN:
            actions.append([k, rel(master), "left alone", f"the shipped take is not this recording (r={idr})"]); continue
        out = os.path.join(a.proc_dir or tmp, k + ".mp3")
        if a.proc_dir:
            os.makedirs(a.proc_dir, exist_ok=True)
        p = process_take.process(master, out, said)
        row = dict(take=k, file=rel(master), dest=r["file"], said=said, **p)
        row.update(master=rel(master), alias=alias, master_sha256=sha256(master), words_check=wcheck,
                   identity_r=idr, identity_lag_ms=lag, shipped_I=meas[k][0], shipped_TP=meas[k][1], history="")
        if p["status"] != "ok":
            plog.append(row)
            actions.append([k, rel(master), "left alone", "process_take: " + p["flags"]]); continue
        if a.apply:
            os.makedirs(HISTORY, exist_ok=True)
            hist = os.path.join(HISTORY, f"{k}.{int(time.time() * 1000)}.mp3")
            if os.path.exists(hist):
                raise SystemExit(f"{hist} exists")
            shutil.move(dest, hist)
            shutil.copyfile(out, dest)
            with open(AUDIO_SOURCE, "a", encoding="utf-8", newline="") as fh:
                fh.write("\t".join([k, "human:" + name, r["file"], said]) + "\n")
            row["history"] = os.path.relpath(hist, ROOT)
            actions.append([k, rel(master), "re-levelled", f"{meas[k][0]} -> {p['out_I']} LUFS"
                            + (f" [flag: {p['flags']}]" if p["flags"] else "")])
        else:
            actions.append([k, rel(master), "would re-level", f"{meas[k][0]} -> {p['out_I']} LUFS"
                            + (f" [flag: {p['flags']}]" if p["flags"] else "")])
        plog.append(row)
    shutil.rmtree(tmp, ignore_errors=True)
    extra = ["master", "alias", "master_sha256", "words_check", "identity_r", "identity_lag_ms", "shipped_I", "shipped_TP",
             "history"]
    with open(os.path.join(log_dir, "process_log.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["run"] + PLOG_FIELDS + extra, extrasaction="ignore")
        w.writeheader()
        for r in plog:
            w.writerow(dict(r, run=run))
    with open(os.path.join(log_dir, "relevel_log.tsv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["# " + run, "apply" if a.apply else "dry run", f"below {a.below} LUFS", " ".join(rel(d) for d in a.masters)])
        w.writerow(["key", "master", "action", "detail"])
        w.writerows(actions)
    n = lambda s: sum(1 for x in actions if x[2] == s)
    print(f"{len(human)} human takes measured; {len(sel)} below {a.below} LUFS; "
          f"{n('re-levelled') or n('would re-level')} {'re-levelled' if a.apply else 'would be re-levelled'}; "
          f"{n('left alone')} left alone; {sum(1 for r in plog if r['flags'] and r['status'] == 'ok')} flagged")
    for x in actions:
        if x[2] == "left alone":
            print("  left alone:", x[0], x[3])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
