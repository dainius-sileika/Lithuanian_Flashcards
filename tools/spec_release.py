#!/usr/bin/env python3
"""Release a version of the design spec: bump + changelog line + frozen snapshot + style lock + git tag.

  python3 tools/spec_release.py --bump minor --note "PANEL_CONTINUITY_RULE on every inset card"
  python3 tools/spec_release.py --bump patch --note "hair wording" --dry-run
  python3 tools/spec_release.py --set 3.0.0 --note "first versioned release"   # explicit version
  python3 tools/spec_release.py --tag                                          # tag HEAD with the current version

Bump rules (docs/DESIGN_SPEC_CURRENT.md §11): major = the look or the card format changes;
minor = a rule is added; patch = wording.

What one run does, in order:
  1. reads the version from the `**Spec version X.Y.Z**` header of docs/DESIGN_SPEC_CURRENT.md,
     computes the new one, rewrites the header (and its date) and adds a line to "## Spec changelog";
  2. freezes the result as docs/spec_history/DESIGN_SPEC_v<new>.md (refuses to overwrite);
  3. runs tools/style_lock.py update, so the lock records the new spec version and the current look;
  4. unless --no-commit: stages the spec, the snapshot, the lock and any modified style-source file
     (the files the lock is computed from), commits "Spec vX.Y.Z: <note>" and tags spec-vX.Y.Z.
     Other modified files are left alone and listed. `git push --tags` is left to you.
--dry-run prints the plan and writes nothing. Edit the spec's prose BEFORE running this, so the
frozen copy carries the change it versions.
"""
from __future__ import annotations
import argparse, datetime, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import style_lock  # noqa: E402

SPEC_REL = "docs/DESIGN_SPEC_CURRENT.md"
HIST_REL = "docs/spec_history"
HEADER_RE = re.compile(r"^\*\*Spec version (\d+)\.(\d+)\.(\d+)\*\* · dated (\d{4}-\d{2}-\d{2})", re.M)
CHANGELOG_HEAD = "## Spec changelog"


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check).stdout


def bump(ver, part):
    M, m, p = ver
    return {"major": (M + 1, 0, 0), "minor": (M, m + 1, 0), "patch": (M, m, p + 1)}[part]


def tag_head(ver_s, dry):
    tag = f"spec-v{ver_s}"
    if git("tag", "-l", tag).strip():
        print(f"tag {tag} already exists; not moved")
        return
    print(f"tag {tag} -> HEAD")
    if not dry:
        git("tag", "-a", tag, "-m", f"Design spec {ver_s}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Release a design-spec version")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--bump", choices=["major", "minor", "patch"])
    g.add_argument("--set", dest="set_version", metavar="X.Y.Z")
    g.add_argument("--tag", action="store_true", help="only tag HEAD with the spec's current version")
    ap.add_argument("--note", default="", help="one line for the spec changelog and the commit message")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-commit", action="store_true", help="write the files, stage nothing")
    a = ap.parse_args(argv)
    dry = a.dry_run

    spec_path = os.path.join(ROOT, SPEC_REL)
    text = open(spec_path, encoding="utf-8").read()
    m = HEADER_RE.search(text)
    if not m:
        sys.exit(f"{SPEC_REL}: header '**Spec version X.Y.Z** · dated YYYY-MM-DD' not found")
    cur = tuple(int(x) for x in m.groups()[:3])
    cur_s = ".".join(map(str, cur))

    if a.tag:
        tag_head(cur_s, dry)
        return 0
    if not a.note:
        sys.exit("--note is required: one line saying what changed")

    new = tuple(int(x) for x in a.set_version.split(".")) if a.set_version else bump(cur, a.bump)
    new_s = ".".join(map(str, new))
    if new <= cur and not a.set_version:
        sys.exit(f"new version {new_s} is not above {cur_s}")
    today = datetime.date.today().isoformat()
    snap_rel = f"{HIST_REL}/DESIGN_SPEC_v{new_s}.md"
    snap_path = os.path.join(ROOT, snap_rel)
    if os.path.exists(snap_path):
        sys.exit(f"{snap_rel} exists; a frozen spec is never overwritten")

    # 1. header + changelog line
    new_text = HEADER_RE.sub(f"**Spec version {new_s}** · dated {today}", text, count=1)
    if CHANGELOG_HEAD not in new_text:
        new_text = new_text.rstrip("\n") + f"\n\n{CHANGELOG_HEAD}\n"
    head_at = new_text.index(CHANGELOG_HEAD) + len(CHANGELOG_HEAD)
    entry = f"\n- **{new_s} — {today}.** {a.note.strip()}"
    new_text = new_text[:head_at] + entry + new_text[head_at:]
    if not new_text.endswith("\n"):
        new_text += "\n"
    print(f"spec {cur_s} -> {new_s} ({'set' if a.set_version else a.bump}), dated {today}")
    print(f"changelog: {entry.strip()}")
    print(f"snapshot: {snap_rel}")

    if dry:
        live = style_lock.fingerprint(style_lock.extract())
        lock = style_lock.load_lock()
        if lock:
            ch, ad, rm = style_lock.compare(live, lock)
            print(f"style lock: {len(ch)} changed, {len(ad)} new, {len(rm)} removed item(s) vs the lock; "
                  f"live style {live['style_hash_short']}")
        else:
            print(f"style lock: none yet; would be written with style {live['style_hash_short']}")
        print(f"commit: 'Spec v{new_s}: {a.note.strip()}'  tag: spec-v{new_s}" if not a.no_commit else "no commit")
        print("dry run: nothing written")
        return 0

    # 2. write spec + snapshot
    with open(spec_path, "w", encoding="utf-8") as fh:
        fh.write(new_text)
    os.makedirs(os.path.dirname(snap_path), exist_ok=True)
    frozen = (f"<!-- FROZEN copy of {SPEC_REL} at spec version {new_s} ({today}). Do not edit; the live spec is "
              f"{SPEC_REL}, the lock style/STYLE_LOCK.json. -->\n" + new_text)
    with open(snap_path, "w", encoding="utf-8") as fh:
        fh.write(frozen)

    # 3. style lock
    rc = style_lock.cmd_update(argparse.Namespace(force=False, note=f"spec {new_s}: {a.note.strip()}"))
    if rc not in (0,):
        sys.exit(f"style_lock update failed (rc {rc}); spec and snapshot were written, nothing committed")

    if a.no_commit:
        print("files written; stage and commit them yourself, then `tools/spec_release.py --tag`")
        return 0

    # 4. stage, commit, tag
    to_add = [SPEC_REL, snap_rel, "style/STYLE_LOCK.json"]
    status = git("status", "--porcelain")
    modified = [l[3:] for l in status.splitlines() if l[:2].strip() and not l.startswith("??")]
    for f in style_lock.SOURCE_FILES:
        if f in modified:
            to_add.append(f)
    git("add", *to_add)
    left = [f for f in modified if f not in to_add]
    msg = f"Spec v{new_s}: {a.note.strip()}"
    git("commit", "-m", msg)
    sha = git("rev-parse", "--short", "HEAD").strip()
    print(f"committed {sha}: {msg}\n  staged: {', '.join(to_add)}")
    if left:
        print(f"  left unstaged: {', '.join(left)}")
    tag_head(new_s, dry)
    print(f"now: git push origin HEAD --tags")
    return 0


if __name__ == "__main__":
    sys.exit(main())
