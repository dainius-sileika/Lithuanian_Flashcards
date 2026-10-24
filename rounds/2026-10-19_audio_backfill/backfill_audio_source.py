#!/usr/bin/env python3
"""One-off (2026-10-19): give audio_source.tsv a `file` and a `said` column and put the
existing human takes where build_apkg.py looks for them.

Why: build_recorder.py decides which cards still need a take by comparing what was SAID on
the existing take with what the card's script says now (accent-blind). The July takes never
stored their script, so it is reconstructed here from the data at the commit that brought
each take in (b05d2c9 = 1.8.0, 5db589d = 071_melynas, 7aea15e = 1.9.1 "57 clips merged"),
with the recorder's own read_script(): headword (pron) + gen_sg / pres3 / past3 / fem.

Moves (git mv, nothing deleted):
  * audio/A2-####.mp3 whose script is unchanged -> audio_a2/ (build_apkg reads A2-list audio
    only from A2_AUDIO_DIR, so these 150 owner takes were never shipped);
  * takes whose words are now WRONG for the card -> <dir>/_superseded/, source "superseded",
    so no package ships them; the recorder lists them as re-takes:
    265_lupa (lūpa -> lūpos), 249_mobilusis_telefonas (gen. mobilusis telefono -> mobiliojo
    telefono), A2-0033 (gen. rugsėjio -> rugsėjo), A2-0104 (kvitas -> čekis),
    A2-0902 / A2-0903 (Pakartokite/Užrašykite, prašau -> Prašom + infinitive).
  The ten colour takes (said "raudonas · raudono", card now "raudonas ♂ · raudona ♀") are
  correct Lithuanian, so they stay in use; the recorder lists them as re-takes all the same.
Run from the repo root; idempotent (a second run changes nothing).
"""
import csv, io, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from build_recorder import read_script, strip_accents, said_key  # noqa: E402

TSV = "audio_source.tsv"
WRONG = {"265_lupa", "249_mobilusis_telefonas", "A2-0033", "A2-0104", "A2-0902", "A2-0903"}


def show(commit, path):
    return list(csv.DictReader(io.StringIO(subprocess.check_output(["git", "show", f"{commit}:{path}"], text=True))))


_TOUCHED = {}


def take_commit(k):
    """Last recording commit (not a reprocessing pass) that touched audio/<k>.mp3."""
    if not _TOUCHED:
        for h in ["b05d2c9", "5db589d", "7aea15e"]:     # oldest first; later ones win
            for f in subprocess.check_output(["git", "show", "--format=", "--name-only", h, "--", "audio/"],
                                             text=True).split("\n"):
                if f.endswith(".mp3"):
                    _TOUCHED[f[len("audio/"):-4]] = h
    return _TOUCHED.get(k)


rows = list(csv.reader(open(TSV, encoding="utf-8"), delimiter="\t"))
head, body = rows[0], rows[1:]
if head[:4] == ["key", "source", "file", "said"]:
    print("already migrated"); sys.exit(0)
cache = {}
out = []
for r in body:
    k, src = r[0], r[1]
    if not src.startswith("human"):
        out.append([k, src, f"audio/{k}.mp3" if os.path.exists(f"audio/{k}.mp3") else "", ""]); continue
    c = take_commit(k)
    if c not in cache:
        cache[c] = ({x["key"]: x for x in show(c, "cards_anki.csv")},
                    {x["id"]: x for x in show(c, "wordlist_a2_pending.csv")})
    if k.startswith("A2-"):
        o = cache[c][1][k]; sc = read_script(o.get("lt_pron") or o["lithuanian_TARGET"], o)
    else:
        o = cache[c][0][k]; sc = read_script(o.get("pron") or o["lithuanian"], o)
    said = strip_accents(" · ".join(f["form"] for f in sc))
    a2 = k.startswith("A2-")
    srcf = f"audio/{k}.mp3"
    if k in WRONG:
        dst = f"{'audio_a2' if a2 else 'audio'}/_superseded/{k}.mp3"; source = "superseded"
    else:
        dst = f"audio_a2/{k}.mp3" if a2 else srcf; source = "human"
    if dst != srcf and os.path.exists(srcf):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst):
            raise SystemExit(f"refusing to overwrite {dst}")
        subprocess.check_call(["git", "mv", srcf, dst])
    out.append([k, source, dst, said])
with open(TSV, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter="\t", lineterminator="\n")
    w.writerow(["key", "source", "file", "said"]); w.writerows(out)
print(f"{TSV}: {len(out)} rows; superseded {sum(1 for r in out if r[1]=='superseded')}; "
      f"moved to audio_a2 {sum(1 for r in out if r[2].startswith('audio_a2/A2-'))}")
