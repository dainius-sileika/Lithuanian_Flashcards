#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_index.py — write FILES.md, the complete inventory of the working directory (spec §13).

    python3 tools/make_index.py                 # rewrite FILES.md from git ls-files + tools/index_descriptions.csv
    python3 tools/make_index.py --untracked     # also recount the untracked folders (run on the owner's Mac, where
                                                #  the pictures, caches and round media are); otherwise the previous
                                                #  count section is kept as it was
    python3 tools/make_index.py --check         # exit 1 when a tracked file has no description, or FILES.md's
                                                #  tracked section is not what this script would write now
                                                #  (the pre-commit hook runs this, so the inventory cannot go stale)

Every tracked file (git ls-files, so staged additions count) must match one rule of tools/index_descriptions.csv:
an exact path, a glob (fnmatch over the whole path), or a folder prefix. Rules marked collapse=1 are written as one
row with a file count (the audio, the WebP masters, the golden pictures) instead of one row per file. The
untracked section lists folders with counts and sizes, never single pictures. Nothing here reads a file's content.
"""
from __future__ import annotations
import argparse, csv, datetime, fnmatch, os, re, subprocess, sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESC = os.path.join(ROOT, "tools", "index_descriptions.csv")
OUT = os.path.join(ROOT, "FILES.md")
TRACKED_HEAD = "## Tracked files"
UNTRACKED_HEAD = "## Untracked, only on the owner's Mac (counts per folder)"
STATUSES = ("live", "generated", "history", "cache", "secret", "source")
TOP_ORDER = ["(root)", "code", "data", "media", "docs", "reports", "rounds", "review_desk", "sources", "tools", "anki",
             "fonts", "style", "style_lab", "_archive", "a2_build"]
# untracked folders are counted at these depths (deeper files are folded into the nearest listed ancestor)
UNTRACKED_GROUP_DEPTH = {"media/images/_history": 3, "rounds": 3, "style_lab": 2, "_TO_DELETE": 2, "_archive": 3,
                         "reports": 2, "media/audio": 2, "media/images": 2}


class Rule:
    def __init__(self, pattern, status, collapse, purpose, io):
        self.pattern, self.status, self.collapse, self.purpose, self.io = pattern, status, collapse == "1", purpose, io
        if "*" in pattern:
            self.kind = "glob"
        elif pattern.endswith("/"):
            self.kind = "prefix"
        else:
            self.kind = "exact"
        self.literal = len(re.sub(r"[*?\[\]]", "", pattern))
        self.rank = ({"exact": 3, "glob": 2, "prefix": 1}[self.kind], self.literal)

    def matches(self, path):
        if self.kind == "exact":
            return path == self.pattern
        if self.kind == "prefix":
            return path.startswith(self.pattern)
        return fnmatch.fnmatchcase(path, self.pattern)


def load_rules():
    rules = []
    with open(DESC, encoding="utf-8") as fh:
        rows = [l for l in fh if l.strip() and not l.lstrip().startswith("#")]
    for r in csv.DictReader(rows):
        if r["status"] not in STATUSES:
            raise SystemExit(f"index_descriptions.csv: unknown status {r['status']!r} for {r['pattern']}")
        rules.append(Rule(r["pattern"], r["status"], r.get("collapse") or "", r["purpose"], r["io"]))
    rules.sort(key=lambda x: x.rank, reverse=True)
    return rules


def match(rules, path):
    for r in rules:
        if r.matches(path):
            return r
    return None


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return sorted(set(out.split("\0")) - {""})


def top_of(path):
    return path.split("/", 1)[0] if "/" in path else "(root)"


def esc(s):
    return s.replace("|", "\\|")


def tracked_section(rules, files):
    """-> (markdown text, missing paths)"""
    missing, by_top = [], OrderedDict()
    for t in TOP_ORDER:
        by_top[t] = []
    for p in files:
        r = match(rules, p)
        if r is None:
            missing.append(p)
            continue
        by_top.setdefault(top_of(p), []).append((p, r))
    lines = [TRACKED_HEAD, "",
             "Status: **live** = hand-kept data or code; **generated** = made by a tool, do not edit; **history** = closed "
             "record (append-only or frozen); **cache** = regenerate freely; **secret** = never shared; **source** = "
             "third-party input. Paths are relative to the working directory. A family row (`*`) stands for every file "
             "it matches, with the count.", ""]
    n_rows = n_files = 0
    for top, items in by_top.items():
        if not items:
            continue
        lines += [f"### {top}" if top == "(root)" else f"### {top}/", "", "| path | status | purpose | read / written by |", "|---|---|---|---|"]
        collapsed = OrderedDict()
        for p, r in items:
            n_files += 1
            if r.collapse:
                collapsed.setdefault(r.pattern, [r, 0])[1] += 1
                continue
            lines.append(f"| `{esc(p)}` | {r.status} | {esc(r.purpose)} | {esc(r.io)} |")
            n_rows += 1
        for pat, (r, n) in collapsed.items():
            lines.append(f"| `{esc(pat)}` ({n:,} files) | {r.status} | {esc(r.purpose)} | {esc(r.io)} |")
            n_rows += 1
        lines.append("")
    lines.insert(2, f"{n_files:,} tracked files in {n_rows:,} rows.")
    lines.insert(3, "")
    return "\n".join(lines).rstrip("\n") + "\n", missing


def human(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:,.0f} {unit}" if unit == "B" else f"{n:,.1f} {unit}"
        n /= 1024


def untracked_section(rules):
    tr = set(tracked())
    groups = OrderedDict()
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT).replace(os.sep, "/")
        if rel == ".":
            dns[:] = [d for d in dns if d != ".git"]
            rel = ""
        for f in fns:
            p = f"{rel}/{f}" if rel else f
            if p in tr or f == ".DS_Store":
                continue
            try:
                size = os.path.getsize(os.path.join(dp, f))
            except OSError:
                continue
            parts = p.split("/")
            depth = 1
            for pre, d in UNTRACKED_GROUP_DEPTH.items():
                if p.startswith(pre + "/"):
                    depth = max(depth, d)
            if len(parts) == 1:
                key = p                              # a loose file at the root (the release package, a secret)
            else:
                key = "/".join(parts[:min(depth, len(parts) - 1)]) + "/"
            g = groups.setdefault(key, [0, 0])
            g[0] += 1
            g[1] += size
    lines = [UNTRACKED_HEAD, "",
             f"Counted on {datetime.date.today().isoformat()} on host `{os.uname().nodename.split('.')[0]}` (files not in git, "
             f"`.DS_Store` ignored). Only the owner's Mac has all of these; a clone has none of the pictures.", "",
             "| folder or file | files | size | status | purpose |", "|---|---:|---:|---|---|"]
    for key in sorted(groups):
        n, size = groups[key]
        r = match(rules, key if key.endswith("/") else key) or match(rules, key + "x")
        st, purpose = (r.status, r.purpose) if r else ("?", "(no rule in tools/index_descriptions.csv)")
        lines.append(f"| `{esc(key)}` | {n:,} | {human(size)} | {st} | {esc(purpose)} |")
    lines.append("")
    return "\n".join(lines)


def read_sections(text):
    """(head, tracked, untracked) of an existing FILES.md"""
    i = text.find(TRACKED_HEAD)
    j = text.find(UNTRACKED_HEAD)
    if i < 0:
        return text, "", ""
    if j < 0:
        return text[:i], text[i:], ""
    return text[:i], text[i:j], text[j:]


def header(n_files):
    return ("# FILES — the complete inventory\n\n"
            "*Generated by `tools/make_index.py` from `git ls-files` and the hand-kept table "
            "`tools/index_descriptions.csv`. The pre-commit hook refuses a commit when a tracked file has no "
            "description here or this file is stale, so it is always current. `INDEX.md` is the short map; this is "
            "the long one. Do not edit by hand: edit the table, run the script.*\n\n"
            "Layout of 2026-10-24 (spec §13): `code/` modules, `data/` live data, `media/` card media, `docs/` the spec and "
            "guides, `reports/` manifests and audits, `rounds/` one dated folder per round of work, `tools/` maintenance "
            "tools, `_archive/` kept history; at the root only the three entry points, the recorder, the release, "
            "`README.md`, `INDEX.md`, this file, `LICENSE`, `.gitignore`, the secrets and the caches.\n\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--untracked", action="store_true", help="recount the untracked folders (on the Mac)")
    a = ap.parse_args(argv)
    rules = load_rules()
    files = tracked()
    tracked_md, missing = tracked_section(rules, files)
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    _, old_tracked, old_untracked = read_sections(old)
    if a.check:
        bad = 0
        for p in missing:
            print(f"make_index: no description for tracked file {p} (add a row to tools/index_descriptions.csv)")
            bad += 1
        if old_tracked.strip() != tracked_md.strip():
            print("make_index: FILES.md is stale (run python3 tools/make_index.py and commit it)")
            bad += 1
        if not bad:
            print(f"inventory OK ({len(files):,} tracked files described, FILES.md current)")
        return 1 if bad else 0
    if missing:
        for p in missing:
            print(f"make_index: no description for tracked file {p}")
        raise SystemExit(f"{len(missing)} tracked file(s) without a description; nothing written")
    untracked_md = untracked_section(rules) if a.untracked else (old_untracked or
        UNTRACKED_HEAD + "\n\n*(not counted yet: run `python3 tools/make_index.py --untracked` on the Mac)*\n")
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(header(len(files)) + tracked_md + "\n" + untracked_md.rstrip("\n") + "\n")
    print(f"FILES.md written: {len(files):,} tracked files" + (", untracked recounted" if a.untracked else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
