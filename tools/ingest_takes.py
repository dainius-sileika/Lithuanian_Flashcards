#!/usr/bin/env python3
"""ingest_takes.py — bring the owner's recorder exports (ZIP) into the deck's audio.

    python3 tools/ingest_takes.py lt_A2_takes_2026-10-21-09-30_all.zip [more.zip ...] [--dry-run]
    python3 tools/ingest_takes.py --inbox [--dry-run]        # every ZIP in media/audio/_inbox/ (and in the old
                                                              # a2_build/audio/inbox/, kept as a forwarding stub)

For each ZIP exported by recorder_A2.html ("Export all" / "Export new"):
  * reads manifest.tsv (key, dest, level, status, said, english, file);
  * maps `key` through tools/keymap.py, so a ZIP exported before the key rename of 2026-10-20
    (A2-0348.webm, 001_suo.webm, A2-0002_s.webm) lands under the current key
    (media/audio/0021_labas.mp3 ...);
  * takes the destination from the CURRENT data/recording_list.csv by the canonical take key,
    never from the manifest (its `dest` may predate the rename or a re-tier);
  * keeps the untouched original of EVERY clip in the ZIP: _archive/takes/<zip-stem>/raw/<file> (gitignored:
    the masters stay on the owner's Mac, beside the ZIP itself), plus the ZIP's manifest.tsv;
  * processes each take with tools/process_take.py (since 2026-10-28; before that a bare ffmpeg -q:a 4
    conversion): key clicks removed at both ends without ever cutting speech, EBU R128 loudness to the July
    takes, 24 kHz mono 64 kbit/s mp3 — and its self-check. A take that fails the self-check is NOT ingested
    (no dest, no audio_source row: it stays on the sheet) and is reported;
  * an existing file at the dest moves to media/audio/_history/<key>.<ms>.mp3 first (a take is never deleted;
    tidy of 2026-10-24, before that <dir>/_superseded/);
  * appends `key  human  <dest>  <said>` to audio_source.tsv (said = the manifest's `said`), so the next
    `build_recorder.py A2` drops the take from the sheet;
  * clips under off_list/ and superseded/ (and takes no longer on the sheet) are not shipped; their manifest rows
    go to _archive/takes/<zip-stem>/manifest_kept.tsv (the clips themselves are in raw/ like every other);
  * writes _archive/takes/<zip-stem>/process_log.csv (one row per processed take: cuts and margins in ms,
    clicks, loudness before/after, energy kept, flags) and ingest_log.tsv (every action);
  * a ZIP that was found in an inbox moves to _archive/takes/<zip-stem>/ once its clips are archived and checked.
Idempotent per take: skipped when audio_source.tsv already has the key as `human` with the same `said`
and the dest file exists.
    --process-only DIR   process every take of the ZIP into DIR/<take>.mp3 and write DIR/process_log.csv, touching
                         nothing else (for a review page before ingesting: tools/audio_review_page.py)
    --hold FILE          takes NOT to ingest although they pass (they stay on the sheet, e.g. for a re-recording): a TSV
                         with a `mixed_take` column (tools/check_mixed_takes.py) or a `take` column; logged as held and
                         written to manifest_kept.tsv with the reason; their raw clips are archived like every other
"""
import csv
import datetime
import hashlib
import io
import os
import shutil
import sys
import tempfile
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import keymap  # noqa: E402
import process_take  # noqa: E402

LIST = os.path.join(ROOT, "data", "recording_list.csv")
AUDIO_SOURCE = os.path.join(ROOT, "data", "audio_source.tsv")
KEEP = os.path.join(ROOT, "_archive", "takes")
INBOXES = [os.path.join(ROOT, "media", "audio", "_inbox"),          # since 2026-10-24 (spec §13)
           os.path.join(ROOT, "a2_build", "audio", "inbox")]        # the old path; a ZIP dropped there is still found


def said_key(s):
    sys.path.insert(0, ROOT)
    from build_recorder import said_key as sk
    return sk(s)


def load_sheet():
    """canonical take key -> recording_list row (file_name is '<take>.mp3')."""
    out = {}
    for r in csv.DictReader(open(LIST, encoding="utf-8")):
        out[r["file_name"][:-4]] = r
    return out


def load_sources():
    out = {}
    if os.path.exists(AUDIO_SOURCE):
        for r in csv.DictReader(open(AUDIO_SOURCE, encoding="utf-8"), delimiter="\t"):
            out[r["key"]] = r          # later rows win (the file is appended to)
    return out


def archive_raw(z, keep_dir):
    """Every clip of the ZIP, untouched, to <keep_dir>/raw/<path in the ZIP>, read back and compared byte for
    byte; plus the ZIP's manifest.tsv. Refuses to overwrite a different file of the same name."""
    raw_dir = os.path.join(keep_dir, "raw")
    for name in z.namelist():
        if name.endswith("/") or ".." in name.split("/") or name.startswith("/"):
            continue
        data = z.read(name)
        p = os.path.join(raw_dir if name != "manifest.tsv" else keep_dir, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        if os.path.exists(p):
            if open(p, "rb").read() != data:
                raise SystemExit(f"{p} exists with different content; not overwriting")
            continue
        open(p, "wb").write(data)
        if hashlib.sha256(open(p, "rb").read()).digest() != hashlib.sha256(data).digest():
            raise SystemExit(f"{p}: archived copy differs from the ZIP")


PLOG_FIELDS = ["take", "file", "dest", "said", "status", "flags", "note", "dur_ms", "onset_ms", "offset_ms",
               "head_cut_ms", "tail_cut_ms", "head_margin_ms", "tail_margin_ms", "removed_head_ms", "removed_tail_ms",
               "kept_ms", "head_clicks", "tail_clicks", "attenuated", "noise_cut", "groups", "floor_bb_db",
               "floor_hi_db", "energy_kept_pct", "identical_window_ms", "identical", "margins_ok", "raw_I", "raw_TP",
               "kept_I", "kept_TP", "gain_db", "out_I", "out_TP", "out_LRA", "src"]


def write_process_log(path, rows):
    if not rows:
        return
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["run"] + PLOG_FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        run = datetime.datetime.now().isoformat(timespec="seconds")
        for r in rows:
            w.writerow(dict(r, run=run))


def load_hold(path):
    """take -> reason, from a check_mixed_takes.py table (mixed_take, contains) or any TSV with a `take` column."""
    out = {}
    if path:
        for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
            k = (r.get("mixed_take") or r.get("take") or "").strip()
            if k:
                why = f"two recordings in one take (contains {r['contains']}): re-record" if r.get("contains") else (r.get("reason") or "held")
                out[k] = (out[k] + "; " + why) if k in out else why
    return out


def ingest(zpath, dry, process_dir=None, hold=None):
    stem = os.path.splitext(os.path.basename(zpath))[0]
    keep_dir = os.path.join(KEEP, stem)
    z = zipfile.ZipFile(zpath)
    man = list(csv.DictReader(io.StringIO(z.read("manifest.tsv").decode("utf-8")), delimiter="\t"))
    sheet, src = load_sheet(), load_sources()
    log, kept, done, plog, failed = [], [], 0, [], []
    tmp = tempfile.mkdtemp()
    if not dry and not process_dir:
        archive_raw(z, keep_dir)
    for m in man:
        old, name = m["key"].strip(), m["file"].strip()
        take = keymap.canonical_take(old)
        said = (m.get("said") or "").strip()
        row = sheet.get(take)
        if name.startswith(("off_list/", "superseded/")) or m.get("status") in ("off-list", "superseded") or not row:
            kept.append(dict(m, canonical_key=take, reason="off list / superseded" if row else "not on the current sheet"))
            log.append([old, take, name, "", "kept (not shipped)"])
            continue
        dest = os.path.join(ROOT, row["dest"])
        a = src.get(take)
        if a and a["source"].startswith("human") and said_key(a.get("said", "")) == said_key(said) and os.path.exists(dest):
            log.append([old, take, name, row["dest"], "skip: already ingested"])
            continue
        if said and said_key(said) != said_key(row["say"]):
            kept.append(dict(m, canonical_key=take, reason=f"said '{said}' but the sheet now says '{row['say']}'"))
            log.append([old, take, name, row["dest"], "kept: script changed since recording"])
            continue
        if hold and take in hold and not process_dir:
            kept.append(dict(m, canonical_key=take, reason="held: " + hold[take]))
            log.append([old, take, name, row["dest"], "held (not ingested, stays on the sheet): " + hold[take]])
            continue
        if dry:
            log.append([old, take, name, row["dest"], "ingest" + (" (renamed from old key)" if take != old else "")])
            continue
        raw = os.path.join(tmp, os.path.basename(name))
        open(raw, "wb").write(z.read(name))
        out = os.path.join(process_dir or tmp, take + ".mp3")
        p = process_take.process(raw, out, said or row["say"])
        plog.append(dict(take=take, file=name, dest=row["dest"], said=said, **p))
        if p["status"] != "ok":
            failed.append(take)
            log.append([old, take, name, row["dest"], "NOT ingested: " + p["flags"]])
            continue
        log.append([old, take, name, row["dest"], "ingest" + (" (renamed from old key)" if take != old else "")
                    + (" [flag: " + p["flags"] + "]" if p["flags"] else "")])
        if process_dir:
            continue
        if os.path.exists(dest):
            sup = os.path.join(os.path.dirname(dest), "_history")
            os.makedirs(sup, exist_ok=True)
            shutil.move(dest, os.path.join(sup, f"{take}.{int(time.time() * 1000)}.mp3"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(out, dest)
        with open(AUDIO_SOURCE, "a", encoding="utf-8", newline="") as fh:
            fh.write("\t".join([take, "human", row["dest"], said or row["say"]]) + "\n")
        done += 1
    if process_dir:
        write_process_log(os.path.join(process_dir, "process_log.csv"), plog)
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"{os.path.basename(zpath)}: processed {len(plog)} takes into {process_dir}; "
              f"{len(failed)} failed the self-check; {sum(1 for r in plog if r['flags'])} flagged")
        return log
    if not dry:
        os.makedirs(keep_dir, exist_ok=True)
        write_process_log(os.path.join(keep_dir, "process_log.csv"), plog)
        if kept:
            with open(os.path.join(keep_dir, "manifest_kept.tsv"), "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(kept[0].keys()), delimiter="\t"); w.writeheader(); w.writerows(kept)
        with open(os.path.join(keep_dir, "ingest_log.tsv"), "a", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["# " + datetime.datetime.now().isoformat(timespec="seconds"), zpath])
            w.writerow(["manifest_key", "take_key", "zip_file", "dest", "action"])
            w.writerows(log)
    shutil.rmtree(tmp, ignore_errors=True)
    if not dry and os.path.abspath(os.path.dirname(zpath)) in [os.path.abspath(d) for d in INBOXES]:
        dst = os.path.join(keep_dir, os.path.basename(zpath))
        z.close()
        shutil.move(zpath, dst)
        print(f"  ZIP moved to {os.path.relpath(dst, ROOT)}")
    if failed:
        print(f"  NOT ingested (self-check failed, still on the sheet): {' '.join(failed)}")
    flagged = [r["take"] for r in plog if r["flags"] and r["status"] == "ok"]
    if flagged:
        print(f"  ingested with a flag (listen): {' '.join(flagged)}")
    renamed = sum(1 for l in log if "renamed" in l[4])
    held = [l[1] for l in log if l[4].startswith("held")]
    if held:
        print(f"  held (not ingested, still on the sheet): {' '.join(held)}")
    print(f"{os.path.basename(zpath)}: {len(man)} manifest rows; ingested {done if not dry else sum(1 for l in log if l[4].startswith('ingest'))}"
          f" ({renamed} via the key map); kept aside {len(kept)}; skipped {sum(1 for l in log if l[4].startswith('skip'))}"
          + (" [dry run]" if dry else ""))
    return log


def main(argv):
    dry = "--dry-run" in argv
    process_dir = None
    if "--process-only" in argv:
        i = argv.index("--process-only")
        process_dir = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
        os.makedirs(process_dir, exist_ok=True)
    hold = None
    if "--hold" in argv:
        i = argv.index("--hold")
        hold = load_hold(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    zips = [a for a in argv[1:] if not a.startswith("--")]
    if "--inbox" in argv:
        for d in INBOXES:
            if os.path.isdir(d):
                zips += sorted(os.path.join(d, z) for z in os.listdir(d) if z.lower().endswith(".zip"))
        if not zips:
            print("no ZIP in", " or ".join(os.path.relpath(d, ROOT) for d in INBOXES)); return 0
    if not zips:
        print(__doc__); return 2
    if not dry and not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found")
    for zp in zips:
        ingest(zp, dry, process_dir, hold)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
