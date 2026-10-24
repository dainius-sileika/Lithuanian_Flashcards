#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tidy_moves.py — the 2026-10-24 reorganisation of the working directory (a2_build/tidy/PLAN_tidy_2026-10-24.md).

    python3 a2_build/tidy/tidy_moves.py plan                 # on the Mac (full media): write moves_2026-10-24.csv
    python3 a2_build/tidy/tidy_moves.py apply --untracked    # on the Mac, in the Proton folder: rename untracked files
    python3 a2_build/tidy/tidy_moves.py apply --tracked      # in a clone outside Proton: git mv the tracked files
    python3 a2_build/tidy/tidy_moves.py verify               # every row: new path present with the planned sha1, old absent

WHAT THE PLAN DOES
  * media/images/<key>.<ext>          the ONE current picture of every card = the file build_apkg.py resolved
                                      first (its own find_image / find_a2_image, per card kind) before the move;
  * media/images/_history/<old path>  every other picture: shadowed renders, _rerolled/, _superseded/, the 1.x
                                      WebP masters of images/ (history keeps the old batch path, so every ledger,
                                      QA sheet and report still reads);
  * media/audio/<key>.mp3, <key>_s.mp3  audio/ + audio_a2/ merged (no key is in both);
  * media/audio/_history/             their _superseded/ takes;
  * media/generation/<batch>/         everything in a batch folder that is not a picture: ledger.csv, plan.json,
                                      cards.csv, gen_log.jsonl, QA sheets, README, gen.py and helpers, review_pub;
  * root: old packages -> _archive/builds/, superseded docs -> _archive/docs/, CHANGELOG.md -> docs/,
          retired script/data -> _archive/deprecated/, _archive/data/; .DS_Store -> _TO_DELETE/.
  Keys (NNNN_slug) and file names never change; only directories do. The plan is a CSV so it can be read
  back by anyone: old_path, new_path, kind, tracked, bytes, sha1.

THE METHOD (as tools/rename_keys.py --apply-media, a2_build/rename/APPLIED_v1.md)
  every file is hashed before and after its move; a destination that already exists stops the run unless
  it already holds the planned bytes (then the row is "done" — the apply is idempotent and can be re-run
  after a Proton Drive hiccup); nothing is deleted or overwritten; a log row per file goes to
  a2_build/tidy/move_log_<tracked|untracked>_<host>.tsv.
"""
from __future__ import annotations
import argparse, csv, hashlib, os, socket, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
HERE = "a2_build/tidy"
PLAN = f"{HERE}/moves_2026-10-24.csv"
DATE = "2026-10-24"

IMG_EXT = (".png", ".webp", ".jpg", ".jpeg")
VERSION_SUBDIRS = ("_rerolled", "_superseded")
# the batch folders build_apkg.py used to search (first hit wins) and their non-picture residents
BATCHES = ["out_phrases_v3/round2", "out_phrases_v3", "out_deck_f62", "out_deck_a2", "out_phrases_a2", "out_deck_sent"]
ROOT_MOVES = {
    "Lietuviu_Flashcards_v2.1_A1.apkg": "_archive/builds/Lietuviu_Flashcards_v2.1_A1.apkg",
    "Lietuviu_Flashcards_v2.1_A2.apkg": "_archive/builds/Lietuviu_Flashcards_v2.1_A2.apkg",
    "ANKIWEB_DESCRIPTION.md": "_archive/docs/ANKIWEB_DESCRIPTION.md",      # superseded 2026-10-19 (its own header says so)
    "VERSIONS.md": "_archive/docs/VERSIONS.md",                            # superseded by docs/VERSIONS.md (header says so)
    "CHANGELOG.md": "docs/CHANGELOG.md",
    "build_study_order_v2.py": "_archive/deprecated/build_study_order_v2.py",   # v1 is already there
    "accents_todo_kirtis.csv": "_archive/data/accents_todo_kirtis.csv",         # closed: no FILL_ME left (data_checks_A1.md)
}


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check).stdout


def tracked_set():
    return set(git("ls-files", "-z").split("\0")) - {""}


def is_key_media(name):
    stem, ext = os.path.splitext(name)
    return ext.lower() in IMG_EXT and len(stem) > 5 and stem[:4].isdigit() and stem[4] == "_"


# ---------------------------------------------------------------------------------------------
def winners():
    """{path: (key, kind)} — the picture build_apkg.py resolves for every card, with its own functions and
    its own search order, before anything moves. Also the audio the build reads, to prove the merge of
    audio/ and audio_a2/ changes nothing (no key may have a file in the folder the build does not read)."""
    sys.path.insert(0, ROOT)
    import build_apkg as B
    win, aud_used, aud_clash = {}, [], []
    for r in csv.DictReader(open("cards_anki.csv", encoding="utf-8")):
        k = r["key"]
        p = B.find_image(k, B.A1_IMAGE_DIRS)
        if p:
            win[p] = (k, "A1 picture")
        if os.path.exists(f"audio/{k}.mp3"):
            aud_used.append(f"audio/{k}.mp3")
        if os.path.exists(f"audio_a2/{k}.mp3"):
            aud_clash.append(f"audio_a2/{k}.mp3 (A1 row {k}: the build reads audio/ only)")
    for r in csv.DictReader(open(B.A2_LIST, encoding="utf-8")):
        k, route = r["id"], r.get("route", "")
        if route in ("IMG", "PHRASE"):
            p = B.find_a2_image(k)
            if p:
                win[p] = (k, "A2-list " + route)
        for suffix in ("", "_s"):
            if os.path.exists(f"{B.A2_AUDIO_DIR}/{k}{suffix}.mp3"):
                aud_used.append(f"{B.A2_AUDIO_DIR}/{k}{suffix}.mp3")
            if os.path.exists(f"audio/{k}{suffix}.mp3"):
                aud_clash.append(f"audio/{k}{suffix}.mp3 (A2-list row {k}: the build reads {B.A2_AUDIO_DIR}/ only)")
    for r in csv.DictReader(open(B.SENTENCES, encoding="utf-8")):
        k = r["id"]
        p = B.find_image(k, B.SENT_IMAGE_DIRS)
        if p:
            win[p] = (k, "sentence")
        if os.path.exists(f"{B.A2_AUDIO_DIR}/{k}.mp3"):
            aud_used.append(f"{B.A2_AUDIO_DIR}/{k}.mp3")
        if os.path.exists(f"audio/{k}.mp3"):
            aud_clash.append(f"audio/{k}.mp3 (sentence {k}: the build reads {B.A2_AUDIO_DIR}/ only)")
    return win, aud_used, aud_clash


def walk(d):
    for dp, dns, fns in os.walk(d):
        dns.sort()
        for f in sorted(fns):
            yield os.path.join(dp, f).replace(os.sep, "/")


def plan_rows():
    win, aud_used, aud_clash = winners()
    if aud_clash:
        print("AUDIO CLASH — merging audio/ and audio_a2/ would change the package; stop and look:")
        for c in aud_clash:
            print("  ", c)
        raise SystemExit(2)
    tr = tracked_set()
    win_keys = {k for k, _ in win.values()}
    rows, seen_dst = [], {}

    def add(old, new, kind):
        if new in seen_dst:
            raise SystemExit(f"two files would land on {new}: {seen_dst[new]} and {old}")
        seen_dst[new] = old
        rows.append({"old_path": old, "new_path": new, "kind": kind, "tracked": int(old in tr),
                     "bytes": os.path.getsize(old), "sha1": sha1(old)})

    # 1. pictures and generation records in the batch folders
    for b in BATCHES:
        if not os.path.isdir(b):
            continue
        for p in walk(b):
            rel = p[len(b) + 1:]
            parts = rel.split("/")
            name = parts[-1]
            if b == "out_phrases_v3" and parts[0] == "round2":
                continue                                   # handled as its own batch (listed first)
            if name == ".DS_Store" or "__pycache__" in parts:
                add(p, f"_TO_DELETE/junk_{DATE}/{p}", "junk")
            elif len(parts) == 1 and p in win:
                add(p, f"media/images/{name}", f"image current ({win[p][1]} {win[p][0]})")
            elif len(parts) == 1 and is_key_media(name):
                k = os.path.splitext(name)[0]
                add(p, f"media/images/_history/{p}",
                    "image history (shadowed by the build's first hit)" if k in win_keys
                    else "image history (no card uses it: its key has no picture route)")
            elif parts[0] in VERSION_SUBDIRS:
                add(p, f"media/images/_history/{p}", f"image history ({parts[0]})")
            elif os.path.splitext(name)[1].lower() in IMG_EXT:
                add(p, f"media/images/_history/{p}", "image history (not a card key)")
            else:
                add(p, f"media/generation/{p}", "generation record")
    # 2. the 1.x WebP masters (tracked): all history — the build's first hit for every A1 card is elsewhere
    for p in walk("images"):
        name = os.path.basename(p)
        if name == ".DS_Store":
            add(p, f"_TO_DELETE/junk_{DATE}/{p}", "junk")
        elif p in win:
            add(p, f"media/images/{name}", f"image current ({win[p][1]} {win[p][0]})")
        else:
            add(p, f"media/images/_history/{p}", "image history (1.x WebP master)")
    # 3. audio
    for d in ("audio", "audio_a2"):
        for p in walk(d):
            rel = p[len(d) + 1:]
            name = os.path.basename(p)
            if name == ".DS_Store":
                add(p, f"_TO_DELETE/junk_{DATE}/{p}", "junk")
            elif rel.startswith("_superseded/"):
                add(p, f"media/audio/_history/{name}", "audio history (_superseded)")
            elif "/" in rel:
                raise SystemExit(f"unexpected sub-folder in {d}: {p}")
            else:
                add(p, f"media/audio/{name}", "audio current" + (" (read by the build)" if p in aud_used else " (not referenced by any card)"))
    # 4. root
    for old, new in ROOT_MOVES.items():
        if os.path.exists(old):
            add(old, new, "root tidy")
    return rows, win


def cmd_plan(a):
    rows, win = plan_rows()
    os.makedirs(HERE, exist_ok=True)
    with open(PLAN, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["old_path", "new_path", "kind", "tracked", "bytes", "sha1"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    c = Counter(r["kind"].split(" (")[0] for r in rows)
    print(f"{len(rows)} moves planned -> {PLAN}")
    for k, v in sorted(c.items()):
        print(f"  {v:5d}  {k}")
    print(f"  current pictures resolved by the build: {len(win)}")
    print(f"  tracked {sum(r['tracked'] for r in rows)}, untracked {sum(1 - r['tracked'] for r in rows)}, "
          f"{sum(r['bytes'] for r in rows) / 2**30:.2f} GiB")
    return 0


def load_plan():
    return list(csv.DictReader(open(PLAN, encoding="utf-8")))


def cmd_apply(a):
    rows = [r for r in load_plan() if int(r["tracked"]) == (1 if a.tracked else 0)]
    tag = "tracked" if a.tracked else "untracked"
    log_path = f"{HERE}/move_log_{tag}_{socket.gethostname().split('.')[0]}.tsv"
    if a.tracked:
        tr = tracked_set()
    done = moved = 0
    pending = []
    for r in rows:
        old, new, h = r["old_path"], r["new_path"], r["sha1"]
        if os.path.exists(new):
            if sha1(new) == h and not os.path.exists(old):
                done += 1
                continue
            if sha1(new) == h and os.path.exists(old) and sha1(old) == h:
                raise SystemExit(f"both old and new exist with the same bytes (a sync copy?); sort it out by hand: {old}")
            raise SystemExit(f"destination exists with other bytes, nothing moved: {new}")
        if not os.path.exists(old):
            raise SystemExit(f"source missing and destination absent: {old}")
        if a.tracked and old not in tr:
            raise SystemExit(f"planned as tracked but not in git here: {old}")
        if sha1(old) != h:
            # a tracked file edited in this clone for the new layout (gen.py, a2_adapter.py): the committed
            # content must still be the planned one; the move then carries the edit along
            blob = subprocess.run(["git", "show", f"HEAD:{old}"], cwd=ROOT, capture_output=True).stdout if a.tracked else b""
            if not (a.tracked and hashlib.sha1(blob).hexdigest() == h):
                raise SystemExit(f"source changed since the plan was written (sha1 differs): {old}")
            h = sha1(old) + " (edited in tree; HEAD blob = planned sha1)"
        pending.append((old, new, h, r["bytes"]))
    print(f"{tag}: {len(rows)} rows, {done} already done, {len(pending)} to move")
    if a.dry_run:
        for old, new, _, _ in pending[:20]:
            print("  ", old, "->", new)
        return 0
    first = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        if first:
            w.writerow(["old_path", "new_path", "bytes", "sha1", "method"])
        for old, new, h, size in pending:
            os.makedirs(os.path.dirname(new), exist_ok=True)
            if a.tracked:
                git("mv", old, new)
            else:
                os.rename(old, new)
            if not os.path.exists(new) or sha1(new) != h.split(" ")[0]:
                raise SystemExit(f"hash mismatch after move: {old} -> {new}")
            w.writerow([old, new, size, h, "git mv" if a.tracked else "rename"])
            fh.flush()
            moved += 1
    print(f"moved {moved}; log {log_path}")
    return 0


def cmd_verify(a):
    rows = load_plan()
    tr = tracked_set()
    ok = missing = stale = bad = skipped = 0
    for r in rows:
        old, new, h = r["old_path"], r["new_path"], r["sha1"]
        if a.tracked_only and not int(r["tracked"]):
            skipped += 1
            continue
        if os.path.exists(old):
            stale += 1
            print("OLD STILL THERE", old)
        if not os.path.exists(new):
            if int(r["tracked"]) or not a.tracked_only:
                missing += 1
                print("MISSING", new)
            continue
        if sha1(new) != h:
            bad += 1
            print("BYTES DIFFER", new)
        else:
            ok += 1
        if int(r["tracked"]) and new not in tr:
            bad += 1
            print("NOT TRACKED AT NEW PATH", new)
    print(f"verify: {ok} ok, {missing} missing, {stale} old paths still present, {bad} wrong, {skipped} skipped")
    return 0 if not (missing or stale or bad) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("plan")
    p = sub.add_parser("apply")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tracked", action="store_true")
    g.add_argument("--untracked", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    v = sub.add_parser("verify")
    v.add_argument("--tracked-only", action="store_true", help="in a clone without the Mac media")
    a = ap.parse_args(argv)
    return {"plan": cmd_plan, "apply": cmd_apply, "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
