#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""move_files.py — move files of the working directory by a rules table, verifiably (spec §13).

    python3 tools/move_files.py plan   RULES.csv  PLAN.csv [--scan-root DIR]   # expand rules to one row per file
    python3 tools/move_files.py apply  PLAN.csv --tracked   [--dry-run]        # in a clone outside Proton: git mv
    python3 tools/move_files.py apply  PLAN.csv --untracked [--dry-run]        # on the Mac, in the Proton folder: os.rename
    python3 tools/move_files.py verify PLAN.csv [--tracked-only]               # every row: new path present with the planned
                                                                               # sha1, old path gone

RULES.csv: `old,new,why`. `old` is a file, or a folder when it ends with `/` (every file under it, tracked or
not, moves to `new/` + its relative path). A file rule beats the folder rule that contains it. Lines starting
with `#` are comments. `.DS_Store` files and `__pycache__/` under a folder rule go to _TO_DELETE/junk_<date>/.

PLAN.csv (written by `plan`, the record of the move): old_path, new_path, kind, tracked, bytes, sha1 — one row
per file, computed before anything moves. `--scan-root` says where to look for the files (the Proton folder
with the untracked pictures and pages) when the plan is written from a clone; tracked/untracked comes from
`git ls-files` in the repo this script sits in.

THE METHOD (as tools/rename_keys.py --apply-media and rounds/2026-10-24_tidy/tidy_moves.py)
  * every file is hashed (sha1) before it moves and checked after; a mismatch stops the run;
  * idempotent: a row whose new path already holds the planned bytes and whose old path is gone is "done";
  * a tracked file edited in the tree for the new layout is accepted when its committed blob is the planned one;
  * the log of what actually moved, per host: <plan dir>/move_log_<tracked|untracked>_<host>.tsv (append-only).
Nothing is ever deleted: a move is a rename; junk goes to _TO_DELETE/<reason>/ for the owner.
"""
from __future__ import annotations
import argparse, csv, datetime, hashlib, os, socket, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JUNK_NAMES = {".DS_Store"}
JUNK_DIRS = {"__pycache__"}


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git(*args, cwd=ROOT, check=True):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=check).stdout


def tracked_set(cwd=ROOT):
    return set(git("ls-files", "-z", cwd=cwd).split("\0")) - {""}


def read_rules(path):
    files, folders = {}, []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip() or line.lstrip().startswith("#") or line.startswith("old,new"):
                continue
            old, new, why = next(csv.reader([line.rstrip("\n")]))
            if old.endswith("/"):
                folders.append((old, new if new.endswith("/") else new + "/", why))
            else:
                files[old] = (new, why)
    folders.sort(key=lambda t: -len(t[0]))      # the most specific folder first
    return files, folders


def walk_files(scan_root, top):
    """every file under scan_root/top (relative paths with '/'), symlinks skipped"""
    base = os.path.join(scan_root, top)
    for dp, dns, fns in os.walk(base):
        dns.sort()
        for f in sorted(fns):
            p = os.path.join(dp, f)
            if os.path.islink(p):
                continue
            yield os.path.relpath(p, scan_root).replace(os.sep, "/")


def cmd_plan(a):
    scan = os.path.abspath(a.scan_root or ROOT)
    files, folders = read_rules(a.rules)
    tr = tracked_set()
    junk_dir = f"_TO_DELETE/junk_{datetime.date.today().isoformat()}"
    rows, seen = [], set()

    def add(old, new, kind):
        if old in seen:
            return
        seen.add(old)
        src = os.path.join(scan, old)
        if not os.path.exists(src):
            if old in tr:
                raise SystemExit(f"plan: tracked file missing at the scan root: {old}")
            print(f"  (skip, not present here: {old})")
            return
        rows.append({"old_path": old, "new_path": new, "kind": kind, "tracked": int(old in tr),
                     "bytes": os.path.getsize(src), "sha1": sha1(src)})

    for old, (new, why) in files.items():
        add(old, new, why)
    for old, new, why in folders:
        if not os.path.isdir(os.path.join(scan, old)):
            print(f"  (no such folder here: {old})")
            continue
        for rel in walk_files(scan, old):
            if rel in files:            # a file rule inside the folder wins
                continue
            parts = rel.split("/")
            if parts[-1] in JUNK_NAMES or any(d in JUNK_DIRS for d in parts[:-1]):
                add(rel, f"{junk_dir}/{rel}", "junk")
                continue
            add(rel, new + rel[len(old):], why)
    # a new path must not already exist, and two rows must not share one
    dests = {}
    for r in rows:
        if r["new_path"] in dests:
            raise SystemExit(f"plan: two files would land on {r['new_path']}: {dests[r['new_path']]} and {r['old_path']}")
        dests[r["new_path"]] = r["old_path"]
        if os.path.exists(os.path.join(scan, r["new_path"])):
            raise SystemExit(f"plan: destination already exists: {r['new_path']} (for {r['old_path']})")
    os.makedirs(os.path.dirname(os.path.abspath(a.plan)) or ".", exist_ok=True)
    with open(a.plan, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["old_path", "new_path", "kind", "tracked", "bytes", "sha1"])
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} moves planned -> {a.plan}  (tracked {sum(r['tracked'] for r in rows)}, "
          f"untracked {sum(1 - r['tracked'] for r in rows)}, {sum(r['bytes'] for r in rows) / 2**20:.1f} MiB)")
    return 0


def load_plan(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def cmd_apply(a):
    os.chdir(ROOT)
    rows = [r for r in load_plan(a.plan) if int(r["tracked"]) == (1 if a.tracked else 0)]
    tag = "tracked" if a.tracked else "untracked"
    log_path = os.path.join(os.path.dirname(os.path.abspath(a.plan)), f"move_log_{tag}_{socket.gethostname().split('.')[0]}.tsv")
    tr = tracked_set() if a.tracked else set()
    done, pending = 0, []
    for r in rows:
        old, new, h = r["old_path"], r["new_path"], r["sha1"]
        if os.path.exists(new):
            hn = sha1(new)
            if hn == h and not os.path.exists(old):
                done += 1
                continue
            if a.tracked and new in tr and not os.path.exists(old):
                blob = subprocess.run(["git", "show", f"HEAD:{new}"], cwd=ROOT, capture_output=True).stdout
                if hashlib.sha1(blob).hexdigest() == hn:
                    done += 1          # edited at the new path and committed there already
                    continue
            if hn == h and os.path.exists(old) and sha1(old) == h:
                raise SystemExit(f"both old and new exist with the same bytes (a sync copy?); sort it out by hand: {old}")
            raise SystemExit(f"destination exists with other bytes, nothing moved: {new}")
        if not os.path.exists(old):
            if not a.tracked:
                # git brought the tracked moves in; an untracked row can only be missing if it never existed here
                raise SystemExit(f"source missing and destination absent: {old}")
            raise SystemExit(f"source missing and destination absent: {old}")
        if a.tracked and old not in tr:
            raise SystemExit(f"planned as tracked but not in git here: {old}")
        if sha1(old) != h:
            blob = subprocess.run(["git", "show", f"HEAD:{old}"], cwd=ROOT, capture_output=True).stdout if a.tracked else b""
            if not (a.tracked and hashlib.sha1(blob).hexdigest() == h):
                raise SystemExit(f"source changed since the plan was written (sha1 differs): {old}")
            h = sha1(old) + " (edited in tree; HEAD blob = planned sha1)"
        pending.append((old, new, h, r["bytes"]))
    print(f"{tag}: {len(rows)} rows, {done} already done, {len(pending)} to move")
    if a.dry_run:
        for old, new, _, _ in pending[:30]:
            print("  ", old, "->", new)
        return 0
    first = not os.path.exists(log_path)
    moved = 0
    with open(log_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        if first:
            w.writerow(["old_path", "new_path", "bytes", "sha1", "method", "when"])
        for old, new, h, size in pending:
            os.makedirs(os.path.dirname(new) or ".", exist_ok=True)
            if a.tracked:
                git("mv", old, new)
            else:
                os.rename(old, new)
            if not os.path.exists(new) or sha1(new) != h.split(" ")[0]:
                raise SystemExit(f"hash mismatch after move: {old} -> {new}")
            w.writerow([old, new, size, h, "git mv" if a.tracked else "rename", datetime.datetime.now().isoformat(timespec="seconds")])
            fh.flush()
            moved += 1
    print(f"moved {moved}; log {os.path.relpath(log_path, ROOT)}")
    return 0


def cmd_verify(a):
    os.chdir(ROOT)
    rows = load_plan(a.plan)
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
            missing += 1
            print("MISSING", new)
            continue
        hn = sha1(new)
        if hn != h:
            # a tracked file edited for the new layout: fine when the file is exactly what git holds at the new
            # path (committed, HEAD) or what is staged for the commit being prepared (the index)
            blobs = [subprocess.run(["git", "show", f"{ref}{new}"], cwd=ROOT, capture_output=True).stdout
                     for ref in ("HEAD:", ":")] if int(r["tracked"]) else []
            if any(b and hashlib.sha1(b).hexdigest() == hn for b in blobs):
                ok += 1
                print("EDITED (matches git at the new path)", new)
            else:
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
    p = sub.add_parser("plan")
    p.add_argument("rules"); p.add_argument("plan")
    p.add_argument("--scan-root", help="directory holding the files (default: this repo)")
    p = sub.add_parser("apply")
    p.add_argument("plan")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--tracked", action="store_true")
    g.add_argument("--untracked", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p = sub.add_parser("verify")
    p.add_argument("plan")
    p.add_argument("--tracked-only", action="store_true", help="in a clone without the Mac media")
    a = ap.parse_args(argv)
    return {"plan": cmd_plan, "apply": cmd_apply, "verify": cmd_verify}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
