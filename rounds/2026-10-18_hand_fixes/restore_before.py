# -*- coding: utf-8 -*-
"""Put the pre-fix picture (before.json) back as the current file before a fresh edit, so the endpoint
never sees a failed patch. The failed version moves to <dir>/_rerolled/<key>.r<n>.<ext> like any re-roll.
    python3 a2_build/hand_fixes/restore_before.py KEY ..."""
import glob, json, os, re, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(os.path.dirname(os.path.dirname(HERE)))
B = json.load(open(os.path.join(HERE, "before.json")))["before"]
for k in sys.argv[1:]:
    b = B[k]; d = b.split("/_rerolled/")[0]; ext = os.path.splitext(b)[1]; cur = f"{d}/{k}{ext}"
    n = 1
    while os.path.exists(f"{d}/_rerolled/{k}.r{n}{ext}"):
        n += 1
    os.replace(cur, f"{d}/_rerolled/{k}.r{n}{ext}"); shutil.copyfile(b, cur)
    print(k, "restored from", b, "| failed edit ->", f"_rerolled/{k}.r{n}{ext}")
