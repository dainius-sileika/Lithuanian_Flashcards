#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amend_v2.py — key_map_v2.csv: re-slug five cards whose content changed in the proofreading return
(a2_build/proofread/returned_plan_v1.*), keeping their numbers. One shot, 2026-10-20.

    python3 a2_build/rename/amend_v2.py            # dry run
    python3 a2_build/rename/amend_v2.py --apply    # writes key_map_v2.csv, rewrites the LIVE files
                                                   # (rename_keys.LIVE_TEXT, whole-token), git mv's tracked media

The slug is derived exactly as tools/rename_keys.py derives it (rename_keys.slug) from the card's
headword after the proofreading return (a2_wordlist `lithuanian_TARGET`, sentences `lt`). The number does
not change, so plate numbers and the study position are unaffected; the GUID changes (guid_for(key)).
Older names stay resolvable: tools/keymap.py follows A2-1193 -> 0331_kuri_valanda (v1) -> 0331_kelinta_valanda (v2).
Untracked media (the Mac render folders) follow with `tools/rename_keys.py --map a2_build/rename/key_map_v2.csv
--apply-media <dirs>`.
"""
import os, sys
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import rename_keys as R   # noqa: E402  (chdir's to the repo root)

KEYS = ["0331_kuri_valanda", "1006_veikla", "2360_draustis", "2410_metus_mokausi_lietuviu_kalbos", "1543_ryte_as_geriu_kava"]
MAP = f"{R.RENAME_DIR}/key_map_v2.csv"
NOTE = "re-slug after the proofreading return (a2_build/proofread/returned_plan_v1): {}; number kept"
WHY = {"0331_kuri_valanda": "EDIT, headword Kuri valanda? -> Kelinta valanda?",
       "1006_veikla": "RETARGET veikla -> užsiėmimas",
       "2360_draustis": "RETARGET draustis -> apsidrausti",
       "2410_metus_mokausi_lietuviu_kalbos": "EDIT, headword gains Jau",
       "1543_ryte_as_geriu_kava": "EDIT, sentence Ryte aš geriu kavą -> Rytais geriu kavą"}


def rows_v2():
    wl = {r["id"]: r for r in R.rd(R.A2_LIST)}
    se = {r["id"]: r for r in R.rd(R.SENTENCES)}
    v1 = R.load_map(f"{R.RENAME_DIR}/key_map_v1.csv")
    v1_new = {r["new_key"]: r for r in v1.values() if r["new_key"]}
    rows = OrderedDict()
    for k in KEYS:
        if k in wl:
            hw, lv = wl[k]["lithuanian_TARGET"], wl[k]["level"]
        elif k in se:
            hw, lv = se[k]["lt"], se[k]["level"]
        else:
            raise SystemExit(f"{k}: not a live key (already amended?)")
        s = R.slug(hw)
        new = f"{k[:R.WIDTH]}_{s}"
        if not R.NEW_KEY_RE.match(new) or new == k:
            raise SystemExit(f"{k}: bad or unchanged new key {new}")
        rows[k] = dict(old_key=k, new_key=new, number=str(int(k[:R.WIDTH])), slug=s, headword=hw, level=lv,
                       kind=v1_new[k]["kind"], status="renamed", note=NOTE.format(WHY[k]))
    return rows


def main(apply):
    if os.path.exists(MAP):
        raise SystemExit(f"{MAP} exists; nothing to do")
    rows = rows_v2()
    for r in rows.values():
        print(f"  {r['old_key']:36} -> {r['new_key']:34} {r['level']} {r['kind']:8} {r['headword']}")
    changes = R.plan_text_changes(rows, R.rd(R.A1_CARDS))
    for p, _, n, sp in changes:
        print(f"  {n:4d} tokens  {p}")
    fwd = R.forward(rows)
    all_tracked = set(R.git("ls-files", "-z").split("\0"))
    moves = R.plan_media(R.TRACKED_MEDIA_DIRS + R.UNTRACKED_MEDIA_DIRS, fwd)
    tracked = [(o, n) for o, n in moves if o in all_tracked]
    untracked = [(o, n) for o, n in moves if o not in all_tracked]
    print(f"  media here: {len(tracked)} tracked, {len(untracked)} untracked")
    if not apply:
        return 0
    R.write_map(rows, MAP)
    for p, new, n, sp in changes:
        open(p, "w", encoding="utf-8", newline="").write(new)
    log = f"{R.RENAME_DIR}/media_log_key_map_v2_tracked.tsv"
    if tracked:
        R.apply_media_moves(tracked, use_git=True, log_path=log)
    if untracked:
        R.apply_media_moves(untracked, use_git=False, log_path=log.replace("_tracked", "_untracked_here"))
    print(f"map {MAP}; rewrote {len(changes)} files; moved {len(tracked)} tracked + {len(untracked)} untracked media")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
