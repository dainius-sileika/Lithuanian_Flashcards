#!/usr/bin/env python3
"""path_map.py — old path -> new path, as text, for the deep tidy of 2026-10-24.

    python3 rounds/2026-10-24_deep_tidy/path_map.py FILE...   # rewrite every old path mention in FILE (in place)
    python3 rounds/2026-10-24_deep_tidy/path_map.py --check FILE...   # list the mentions still there, exit 1 if any

Derived from moves.csv (one rule per file or folder, longest first) so a comment or docstring that names an old
location names the new one. Used on the live code and the live documents only; round folders, ledgers and
other records keep the paths of their time (spec §12 / §13)."""
import csv, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FOLDERS = []
for line in open(os.path.join(HERE, "move_rules.csv"), encoding="utf-8"):
    if not line.strip() or line.startswith("#") or line.startswith("old,new"):
        continue
    old, new, _ = next(csv.reader([line.rstrip("\n")]))
    FOLDERS.append((old, new))
# the root data files and modules, by bare name, are NOT in this map (too ambiguous as text); edit those by hand
MAP = [(o, n) for o, n in FOLDERS if "/" in o]
MAP += [("a2_build/study_order/", "reports/study_order/"),    # whatever is left of that folder: the audits
        ("build_reports/", "reports/"), ("a2_rebase/", "rounds/2026-10-10_a2_rebase/"),
        ("a2_build/audio/inbox", "media/audio/_inbox"), ("a2_build/src/", "_archive/deprecated/a2_src_2026-10/")]
MAP += [("a2_build/rename/key_map_v", "data/key_maps/key_map_v"), ("a2_build/rename/topic_map", "data/key_maps/topic_map")]
MAP.sort(key=lambda t: -len(t[0]))
# paths are matched only when preceded by a non-path character (start, space, quote, backtick, paren, comma)
PAT = re.compile("(?<![A-Za-z0-9_./-])(" + "|".join(re.escape(o) for o, _ in MAP) + ")")
LOOK = dict(MAP)


def rewrite(text):
    def rep(m):
        o = m.group(1)
        n = LOOK[o]
        if o.endswith("/") and not n.endswith("/"):
            n += "/"
        return n
    return PAT.sub(rep, text)


def main(argv):
    check = "--check" in argv
    files = [a for a in argv if a != "--check"]
    bad = 0
    for f in files:
        t = open(f, encoding="utf-8").read()
        if check:
            for i, line in enumerate(t.splitlines(), 1):
                for m in PAT.finditer(line):
                    print(f"{f}:{i}: {m.group(1)}")
                    bad += 1
            continue
        new = rewrite(t)
        if new != t:
            open(f, "w", encoding="utf-8").write(new)
            print("rewritten", f, sum(1 for _ in PAT.finditer(t)), "mention(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
