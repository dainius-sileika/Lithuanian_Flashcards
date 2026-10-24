#!/usr/bin/env python3
"""ingest_takes.py — bring the owner's recorder exports (ZIP) into the deck's audio.

    python3 tools/ingest_takes.py lt_A2_takes_2026-10-21-09-30_all.zip [more.zip ...] [--dry-run]

For each ZIP exported by recorder_A2.html ("Export all" / "Export new"):
  * reads manifest.tsv (key, dest, level, status, said, english, file);
  * maps `key` through tools/keymap.py, so a ZIP exported before the key rename of 2026-10-20
    (A2-0348.webm, 001_suo.webm, A2-0002_s.webm) lands under the current key
    (media/audio/0021_labas.mp3 ...);
  * takes the destination from the CURRENT a2_build/recording_list.csv by the canonical take key,
    never from the manifest (its `dest` may predate the rename or a re-tier);
  * converts with ffmpeg (-codec:a libmp3lame -q:a 4) to that dest; an existing file there moves to
    media/audio/_history/<key>.<ms>.mp3 first (a take is never deleted; tidy of 2026-10-24, before
    that <dir>/_superseded/);
  * appends `key  human  <dest>  <said>` to audio_source.tsv (said = the manifest's `said`), so the next
    `build_recorder.py A2` drops the take from the sheet;
  * clips under off_list/ and superseded/ (and takes no longer on the sheet) are copied to
    _archive/takes/<zip-stem>/ with their manifest rows (manifest_kept.tsv); they are not shipped.
Idempotent per take: skipped when audio_source.tsv already has the key as `human` with the same `said`
and the dest file exists. A log of every action goes to _archive/takes/<zip-stem>/ingest_log.tsv.
"""
import csv
import datetime
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import keymap  # noqa: E402

LIST = os.path.join(ROOT, "a2_build", "recording_list.csv")
AUDIO_SOURCE = os.path.join(ROOT, "audio_source.tsv")
KEEP = os.path.join(ROOT, "_archive", "takes")


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


def ingest(zpath, dry):
    stem = os.path.splitext(os.path.basename(zpath))[0]
    keep_dir = os.path.join(KEEP, stem)
    z = zipfile.ZipFile(zpath)
    man = list(csv.DictReader(io.StringIO(z.read("manifest.tsv").decode("utf-8")), delimiter="\t"))
    sheet, src = load_sheet(), load_sources()
    log, kept, done = [], [], 0
    tmp = tempfile.mkdtemp()
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
        log.append([old, take, name, row["dest"], "ingest" + (" (renamed from old key)" if take != old else "")])
        if dry:
            continue
        raw = os.path.join(tmp, os.path.basename(name))
        open(raw, "wb").write(z.read(name))
        if os.path.exists(dest):
            sup = os.path.join(os.path.dirname(dest), "_history")
            os.makedirs(sup, exist_ok=True)
            shutil.move(dest, os.path.join(sup, f"{take}.{int(time.time() * 1000)}.mp3"))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-codec:a", "libmp3lame", "-q:a", "4", dest], check=True)
        with open(AUDIO_SOURCE, "a", encoding="utf-8", newline="") as fh:
            fh.write("\t".join([take, "human", row["dest"], said or row["say"]]) + "\n")
        done += 1
    if not dry:
        os.makedirs(keep_dir, exist_ok=True)
        for k in kept:
            if k.get("file") and k["file"] in z.namelist():
                p = os.path.join(keep_dir, k["file"])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "wb").write(z.read(k["file"]))
        if kept:
            with open(os.path.join(keep_dir, "manifest_kept.tsv"), "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(kept[0].keys()), delimiter="\t"); w.writeheader(); w.writerows(kept)
        with open(os.path.join(keep_dir, "ingest_log.tsv"), "a", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(["# " + datetime.datetime.now().isoformat(timespec="seconds"), zpath])
            w.writerow(["manifest_key", "take_key", "zip_file", "dest", "action"])
            w.writerows(log)
    shutil.rmtree(tmp, ignore_errors=True)
    renamed = sum(1 for l in log if "renamed" in l[4])
    print(f"{os.path.basename(zpath)}: {len(man)} manifest rows; ingested {done if not dry else sum(1 for l in log if l[4].startswith('ingest'))}"
          f" ({renamed} via the key map); kept aside {len(kept)}; skipped {sum(1 for l in log if l[4].startswith('skip'))}"
          + (" [dry run]" if dry else ""))
    return log


def main(argv):
    dry = "--dry-run" in argv
    zips = [a for a in argv[1:] if not a.startswith("--")]
    if not zips:
        print(__doc__); return 2
    if not dry and not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg not found")
    for zp in zips:
        ingest(zp, dry)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
