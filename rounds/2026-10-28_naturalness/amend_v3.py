#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""amend_v3.py — key_map_v3.csv: re-slug the nine cards whose headword or sentence changed in the naturalness
round (rounds/2026-10-28_naturalness/final_v1.csv, applied by apply_v1.py), keeping their numbers. One shot,
2026-10-28; the same procedure as rounds/2026-10-20_rename/amend_v2.py (the proofreading round).

    python3 rounds/2026-10-28_naturalness/amend_v3.py            # dry run
    python3 rounds/2026-10-28_naturalness/amend_v3.py --apply    # writes data/key_maps/key_map_v3.csv, rewrites the
                                                                 # LIVE files (rename_keys.LIVE_TEXT, whole-token),
                                                                 # git mv's tracked media (hash-checked, logged)

Keys are not locked yet (spec §8, §12): the slug follows the headword. Six RETARGETs (0239 orai -> oras, 0778,
1169, 1589, 1968, 2422 puslitris -> bokalas) and three EDITs whose headword / sentence changed so that the slug
would mislead (1482 laisvų staliukų, 0856 eurą for litą, 1410 Man skambina draugas) — the same rule amend_v2 applied
to 0331, 2410 and 1543. EDITs whose slug is unchanged (0214, 0966, 1243, 1793, 2147) are not in the map.
The slug is derived exactly as tools/rename_keys.py derives it (rename_keys.slug) from the card's headword after
apply_v1 (a2_wordlist `lithuanian_TARGET`, sentences `lt`). Numbers do not change, so plate numbers and the study
position are unaffected; the GUID changes (guid_for(key)). Older names stay resolvable through tools/keymap.py.
Untracked media (the pictures on the Mac, the cloud's 1024 px copies) follow with
`python3 tools/rename_keys.py --map data/key_maps/key_map_v3.csv --apply-media <dirs>`.
"""
import os, sys
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import rename_keys as R   # noqa: E402  (chdir's to the repo root)

MAP = f"{R.RENAME_DIR}/key_map_v3.csv"
NOTE = "re-slug after the naturalness round (rounds/2026-10-28_naturalness/final_v1): {}; number kept"
WHY = {"0239_orai": "RETARGET orai -> oras",
       "0778_galiu_truputi_kalbeti": "RETARGET Galiu truputį kalbėti -> Truputį kalbu lietuviškai.",
       "1169_greitai_pasveik": "RETARGET Greitai pasveik! -> Sveik!",
       "1589_naudotis": "RETARGET naudotis -> pasinaudoti",
       "1968_vieta_prie_tako": "RETARGET vieta prie tako -> vieta prie praėjimo",
       "2422_puslitris": "RETARGET puslitris -> bokalas",
       "1482_ar_yra_laisvas_staliukas": "EDIT, headword Ar yra laisvas staliukas? -> Ar yra laisvų staliukų?",
       "0856_duona_kainuoja_viena_lita": "EDIT, sentence Duona kainuoja vieną litą -> Duona kainuoja vieną eurą",
       "1410_draugas_skambina_man": "EDIT, sentence Draugas skambina man -> Man skambina draugas"}
KEYS = list(WHY)


def rows_v3():
    wl = {r["id"]: r for r in R.rd(R.A2_LIST)}
    se = {r["id"]: r for r in R.rd(R.SENTENCES)}
    known = {}
    for p in R.all_map_paths():
        for r in R.load_map(p).values():
            if r["new_key"]:
                known[r["new_key"]] = r
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
                       kind=known[k]["kind"], status="renamed", note=NOTE.format(WHY[k]))
    taken = {r["id"] for r in wl.values()} | set(se)
    clash = [r["new_key"] for r in rows.values() if r["new_key"] in taken]
    if clash:
        raise SystemExit(f"new keys already in use: {clash}")
    return rows


def main(apply):
    if os.path.exists(MAP):
        raise SystemExit(f"{MAP} exists; nothing to do")
    rows = rows_v3()
    for r in rows.values():
        print(f"  {r['old_key']:34} -> {r['new_key']:34} {r['level']} {r['kind']:8} {r['headword']}")
    changes = R.plan_text_changes(rows, R.rd(R.A1_CARDS))
    for p, _, n, sp in changes:
        print(f"  {n:4d} tokens  {p}")
    fwd = R.forward(rows)
    all_tracked = set(R.git("ls-files", "-z").split("\0"))
    moves = R.plan_media(R.TRACKED_MEDIA_DIRS + R.UNTRACKED_MEDIA_DIRS, fwd)
    tracked = [(o, n) for o, n in moves if o in all_tracked]
    untracked = [(o, n) for o, n in moves if o not in all_tracked]
    for o, n in tracked:
        print(f"  git mv {o} -> {n}")
    print(f"  media here: {len(tracked)} tracked, {len(untracked)} untracked")
    if not apply:
        return 0
    R.write_map(rows, MAP)
    for p, new, n, sp in changes:
        open(p, "w", encoding="utf-8", newline="").write(new)
    log = f"{R.RENAME_DIR}/media_log_key_map_v3_tracked.tsv"
    if tracked:
        R.apply_media_moves(tracked, use_git=True, log_path=log)
    if untracked:
        R.apply_media_moves(untracked, use_git=False, log_path=log.replace("_tracked", "_untracked_here"))
    print(f"map {MAP}; rewrote {len(changes)} files; moved {len(tracked)} tracked + {len(untracked)} untracked media")
    return 0


if __name__ == "__main__":
    sys.exit(main("--apply" in sys.argv))
