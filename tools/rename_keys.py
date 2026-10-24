#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rename_keys.py — one namespace for every card: NNNN_slug (a2_build/rename/PLAN_rename_v1.md).

    python3 tools/rename_keys.py                         # DRY RUN (default): derive the map, report, write nothing
    python3 tools/rename_keys.py --dry-run --out a2_build/rename/dryrun_v1.txt
    python3 tools/rename_keys.py --apply                 # write a2_build/rename/key_map_v<N>.csv, rewrite the live
                                                         # files, `git mv` the tracked media, then run --verify
    python3 tools/rename_keys.py --apply-media DIR [DIR ...]
                                                         # rename UNTRACKED media on disk (the Mac render folders)
                                                         # from the committed map; writes a per-run log
    python3 tools/rename_keys.py --verify                # fail loudly on any old-format key outside history,
                                                         # on data files whose keys are not all new-format, and on
                                                         # media missing under the new name
    python3 tools/rename_keys.py --map a2_build/rename/key_map_v1.csv --verify   # against a given map
                                                         # (no --map: every key_map_v*.csv composed, so an amendment
                                                         #  map such as key_map_v2 is checked together with v1)
    python3 tools/rename_keys.py --mint "šaukštelis"   # the key a new card gets: next free number + slug

WHAT THE MAP IS
  old_key -> new_key for every card in study_order.csv. The number is the card's position in the study
  order at the moment the map is derived (A1 block first, then A2), zero-padded to four digits; the slug is
  the ASCII-folded headword (phrases and sentences: their first words, at most four words / 32 chars). The
  slug is a reading aid, never an identifier: two cards may share a slug, the number tells them apart, and
  a slug is not re-derived when a headword is later corrected (after the lock a key never changes).
  Rows for cards NOT in the order are carried with an empty new_key and a status: merged-away ids
  (a2_build/merged_keys.csv), B1 deferrals (a2_build/deferred_B1.csv) and media-only aliases
  (build_apkg.IMAGE_ALIAS, e.g. 265_lupos -> the same new key as 265_lupa).

WHAT --apply REWRITES (and nothing else; see LIVE_TEXT below)
  every live data file and live script that carries a key, by whole-token replacement
  (001_suo in 001_suo.mp3, "001_suo", 001_suo_s, 001_suo_sf2.jpg all become the new key + suffix);
  master_wordlist.csv gains a `key` column. The Fluent Forever row number stays where it is (`#` in
  master_wordlist.csv, `number` in cards_anki.csv): the generator tables, the study-order pairs and the QA
  join are keyed by it. It is NOT the plate number any more — build_apkg takes that from the key (PLAN §6);
  the bare FF number in a2_build/restage_bubbles.csv `ids` (374 = galvoti) becomes the card's key.
  History (reports, audits, round folders, ledgers, gen logs, QA sheets, build manifests, _archive, the
  spec history) is NEVER rewritten: the map is how those names are read (tools/keymap.py).
  Tracked media (media/audio/, its _history/, the WebP masters under media/images/_history/images/,
  style/golden/) move with `git mv`. The untracked pictures (media/images/ and the rest of
  media/images/_history/) live only on the owner's Mac: run --apply-media there, after `git pull`,
  with Proton Drive sync paused (PLAN §8). (Before the tidy of 2026-10-24 the media sat in images/,
  audio/, audio_a2/ and six out_* batch folders; a2_build/tidy/moves_2026-10-24.csv maps old to new.)

GUARDS
  study_order.csv must be 1..N contiguous and its keys must equal cards_anki ∪ a2_wordlist ∪ sentences;
  new keys must be unique; a map file is never overwritten (the next run writes key_map_v<N+1>.csv);
  --apply refuses on a dirty git tree unless --allow-dirty; every git mv is hash-checked.
"""
from __future__ import annotations
import argparse
import csv
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter, OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

STUDY_ORDER = os.environ.get("STUDY_ORDER", "study_order.csv")
A1_CARDS = "cards_anki.csv"
MASTER = "master_wordlist.csv"
A2_LIST = os.environ.get("A2_LIST", "a2_build/a2_wordlist.csv")
SENTENCES = os.environ.get("SENTENCES", "a2_build/sentences/sentences.csv")
MERGED = "a2_build/merged_keys.csv"
DEFERRED = "a2_build/deferred_B1.csv"
RENAME_DIR = "a2_build/rename"
WIDTH = 4                      # NNNN; 9,999 cards is far above any plan for this deck
SLUG_WORDS, SLUG_CHARS = 4, 32

# A 3-digit base key cannot match inside a new NNNN_slug key: the token regexes forbid a digit before
# the match, so 0001_suo never matches as 001_suo (token_re below is built from the map's exact keys).
NEW_KEY_RE = re.compile(r"^\d{%d}_[a-z][a-z0-9_]*$" % WIDTH)
MEDIA_SUFFIX = r"(_s|_sf\d+|\.r\d+|\.edit_raw\d+|\.prompt)?"   # .edit_rawN: raw outputs of edit_inset.py in _rerolled/
MEDIA_EXT = r"\.(png|jpg|jpeg|webp|mp3|m4a|webm|ogg|txt|src)"

# ---------------------------------------------------------------------------------------------
# LIVE files: rewritten by --apply. Everything else that mentions a key is history (left alone) or
# generated (rebuilt by its own tool after the rename). Keep this list honest: --verify reports any
# tracked file outside LIVE ∪ HISTORY ∪ GENERATED that still carries an old-format key.
# ---------------------------------------------------------------------------------------------
LIVE_TEXT = [
    # data
    A1_CARDS, MASTER, A2_LIST, SENTENCES, STUDY_ORDER,
    MERGED, "a2_build/id_map.csv",
    "audio_source.tsv", "a2_build/context_notes.csv",
    "a2_build/study_order/retag_A1.csv", "a2_build/study_order/retier_v3.csv",
    "a2_build/restage_bubbles.csv", "a2_build/a2_staging.json", "card_notes.json",
    "a2_build/sentences/staging.json", "a2_build/audio/recorder_A2_afb2ebe2_script.json",
    "a2_build/stress_58_resolved.csv", "a2_build/deck_fixes.csv",
    "a2_build/historical/implementation/likeness_args.json",
    "style_lab/research/settings_assignments.csv",
    "style/golden/manifest.csv",
    "review_desk/items.json",
    # code with hand-listed keys
    "build_apkg.py", "build_study_order_v3.py", "deck_builder.py", "frame_crop.py", "frame_preview.py",
    "qa_images.py", "situations.py", "a2_build/src/build_situations.py",
    "media/generation/out_phrases_v3/gen.py", "media/generation/out_deck_sent/gen.py",
    "media/generation/out_deck_a2/a2_adapter.py",
    "card_frame.py", "anki/templates.md", "a2_build/RECORDING_GUIDE.md",
    "style/golden/README.md",
] + sorted(glob.glob("style/golden/*.prompt.txt"))     # golden prompts carry `key:` and `file:` lines
# Regenerated after --apply by their own tools (listed so --verify does not flag them as unclassified):
GENERATED = [
    "a2_build/recording_list.csv",                 # build_recorder.py A2
    "a2_build/study_order/recording_order_v3.csv", # build_study_order_v3.py
    "recorder_A2.html",                            # build_recorder.py A2 (gitignored)
    "build_reports/frame_bands.csv", "build_reports/frame_flags.csv",   # next build_apkg run
]
# Append-only / closed records: never rewritten, read through tools/keymap.py.
HISTORY_PREFIXES = (
    "_archive/", "docs/spec_history/", "build_reports/", "a2_build/round", "a2_build/rollout",
    "a2_build/pilot_round2/", "a2_build/additions_round2/", "a2_build/hand_fixes/", "a2_build/phrase_additions/",
    "a2_build/review_", "a2_build/review_template/", "a2_build/data_checks", "a2_build/benchmark_en/",
    "a2_build/backs_audit/", "a2_build/historical/", "a2_build/audio/reconciliation_", "a2_build/a1_redo/",
    "a2_build/src/", "a2_build/study_order/AUDIT", "a2_build/study_order/REPORT", "a2_build/study_order/dep37",
    "a2_build/audio/backfill_", "a2_rebase/", "style_lab/", "tools/",
    "media/generation/",     # ledgers, plans, QA sheets and gen logs of every render batch (was out_*/)
    "a2_build/rename/",
    "a2_build/tidy/",        # the 2026-10-24 move table names files by whatever name they had
    "a2_build/proofread/",   # sheet out with the owner under the old keys; the returned sheet is mapped via keymap.py
)
HISTORY_FILES = {
    "docs/CHANGELOG.md", "docs/VERSIONS.md", "docs/ANKIWEB_DESCRIPTION_A1_v3.0.md", "INDEX.md",
    "docs/DESIGN_SPEC_CURRENT.md",      # prose edited by hand in the spec release, not by regex
    "a2_build/A1_WRAPUP.md", "a2_build/BACKS_AUDIT.md", "a2_build/CLOUD_ROUND_2026-10-11.md", "a2_build/PILOT_24.md",
    "a2_build/PLAN_A2_completion.md", "a2_build/PRASOM_SWITCH_2026-10-18.md", "a2_build/README.md",
    "a2_build/RESTAGE_PROPOSAL.md", "a2_build/merges_2026-10-19.md", "a2_build/data_checks_A1.md",
    "a2_build/sentences/design.md", "a2_build/deck_fixes_applied.csv",
    "wordlist_a2_pending.csv",                                  # input of the retired build_a2.py (accents_todo_kirtis.csv
                                                                # and build_study_order_v2.py are in _archive/ since 2026-10-24)
    DEFERRED,                                                   # pre-rename ids by design (status deferred in the map)
}
# Live exceptions inside history prefixes (they are read by live code):
LIVE_IN_HISTORY = {"a2_build/historical/implementation/likeness_args.json", "style_lab/research/settings_assignments.csv",
                   "media/generation/out_phrases_v3/gen.py", "media/generation/out_deck_sent/gen.py",
                   "media/generation/out_deck_a2/a2_adapter.py",
                   "a2_build/src/build_situations.py"}

# Tracked media folders (git mv). The untracked pictures are --apply-media's job on the Mac.
# Layout since 2026-10-24 (spec §13, INDEX.md): media/images/<key>.<ext> is the one current picture,
# media/images/_history/<old batch path>/ every other version, media/audio/<key>.mp3 the one current take.
IMAGE_DIR = "media/images"
AUDIO_DIR = "media/audio"
TRACKED_MEDIA_DIRS = [AUDIO_DIR, f"{AUDIO_DIR}/_history", f"{IMAGE_DIR}/_history/images", "style/golden"]
VERSION_SUBDIRS = ["_rerolled", "_superseded"]


def _history_dirs():
    """Every folder under media/images/_history (the old batch paths), so old names are found wherever they sit."""
    out = []
    for dp, dns, _ in os.walk(f"{IMAGE_DIR}/_history"):
        dns.sort()
        out.append(dp.replace(os.sep, "/"))
    return out


UNTRACKED_MEDIA_DIRS = [IMAGE_DIR] + [d for d in _history_dirs() if d != f"{IMAGE_DIR}/_history/images"] + \
                       ["_cloud_media/f62", "_cloud_media/a2", "_cloud_media/phrases"]   # 1024 px copies in a cloud clone


# ---------------------------------------------------------------------------------------------
# slug
# ---------------------------------------------------------------------------------------------
def slug(headword: str, max_words=SLUG_WORDS, max_chars=SLUG_CHARS) -> str:
    """'gydytojas/gydytoja' -> gydytojas; 'žemė (dirvožemis)' -> zeme; 'Vyras {geria} kavą.' -> vyras_geria_kava;
    'Ar galite ką nors parekomenduoti?' -> ar_galite_ka_nors. Stress marks and Lithuanian letters fold to ASCII."""
    s = headword.split("/")[0]
    s = re.sub(r"\([^)]*\)", " ", s).replace("{", "").replace("}", "")
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    words = [w for w in re.split(r"[^a-z0-9]+", s) if w]
    out = []
    for w in words[:max_words]:
        if out and len("_".join(out + [w])) > max_chars:
            break
        out.append(w)
    return "_".join(out) or "x"


def rd(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------------------------
# the map
# ---------------------------------------------------------------------------------------------
KIND_OF_ROUTE = {"IMG": "picture", "PHRASE": "phrase", "CLOZE": "cloze", "PAIR": "cloze"}
MAP_COLUMNS = ["old_key", "new_key", "number", "slug", "headword", "level", "kind", "status", "note"]


def derive_map():
    """Rows of the key map (OrderedDict old_key -> row) + a list of guard failures."""
    errors = []
    order = rd(STUDY_ORDER)
    pos = {}
    for r in order:
        k, n = r["key"].strip(), int(r["order"])
        if k in pos:
            errors.append(f"study order: key listed twice: {k}")
        pos[k] = n
    expect = list(range(1, len(order) + 1))
    if sorted(pos.values()) != expect:
        errors.append(f"study order: positions are not 1..{len(order)} contiguous")

    a1 = rd(A1_CARDS); a2 = rd(A2_LIST); sents = rd(SENTENCES)
    src = OrderedDict()
    for r in a1:
        src[r["key"]] = dict(headword=r["lithuanian"], level=(r.get("level") or "A1").strip() or "A1", kind="picture")
    for r in a2:
        src[r["id"]] = dict(headword=r["lithuanian_TARGET"], level=(r.get("level") or "A2").strip() or "A2",
                            kind=KIND_OF_ROUTE.get(r.get("route", ""), r.get("route", "").lower() or "?"))
    for r in sents:
        src[r["id"]] = dict(headword=r["lt"], level=(r.get("level") or "A2").strip() or "A2", kind="sentence")
    missing = sorted(set(src) - set(pos)); extra = sorted(set(pos) - set(src))
    if missing:
        errors.append(f"{len(missing)} card(s) not in the study order: {missing[:10]}")
    if extra:
        errors.append(f"{len(extra)} study-order key(s) not in any list: {extra[:10]}")

    rows = OrderedDict()
    for k, n in sorted(pos.items(), key=lambda kv: kv[1]):
        if k not in src:
            continue
        s = src[k]
        new = f"{n:0{WIDTH}d}_{slug(s['headword'])}"
        rows[k] = dict(old_key=k, new_key=new, number=str(n), slug=slug(s["headword"]), headword=s["headword"],
                       level=s["level"], kind=s["kind"], status="renamed" if k != new else "unchanged", note="")
    dup = [k for k, c in Counter(r["new_key"] for r in rows.values()).items() if c > 1]
    if dup:
        errors.append(f"new keys not unique: {dup[:10]}")
    for r in rows.values():
        if not NEW_KEY_RE.match(r["new_key"]):
            errors.append(f"bad new key {r['new_key']!r}")

    # carried, without a number
    if os.path.exists(MERGED):
        for r in rd(MERGED):
            tgt = (r.get("merged_into") or "").strip()
            tnew = rows.get(tgt, {}).get("new_key", "")
            rows[r["id"]] = dict(old_key=r["id"], new_key="", number="", slug="", headword=r.get("lithuanian_TARGET", ""),
                                 level=r.get("level", ""), kind=KIND_OF_ROUTE.get(r.get("route", ""), ""), status="merged",
                                 note=f"merged into {tgt} -> {tnew or '?'} ({r.get('merged_on', '')})")
    if os.path.exists(DEFERRED):
        for r in rd(DEFERRED):
            rows[r["id"]] = dict(old_key=r["id"], new_key="", number="", slug="", headword=r.get("lithuanian_TARGET", ""),
                                 level="B1", kind=KIND_OF_ROUTE.get(r.get("route", ""), ""), status="deferred",
                                 note="B1 deferral; gets an appended key if ever promoted")
    try:
        sys.path.insert(0, ROOT)
        import build_apkg as B   # noqa: E402  (IMAGE_ALIAS: render files that sit under another stem)
        for k, alias in getattr(B, "IMAGE_ALIAS", {}).items():
            if k in rows and rows[k]["new_key"] and alias not in rows:
                rows[alias] = dict(old_key=alias, new_key=rows[k]["new_key"], number=rows[k]["number"], slug="",
                                   headword=rows[k]["headword"], level=rows[k]["level"], kind="picture",
                                   status="alias", note=f"media stem of {k} (build_apkg.IMAGE_ALIAS)")
    except Exception as e:   # the build module needs genanki; the alias is also hard-coded below
        if "265_lupa" in rows and "265_lupos" not in rows:
            rows["265_lupos"] = dict(old_key="265_lupos", new_key=rows["265_lupa"]["new_key"], number=rows["265_lupa"]["number"],
                                     slug="", headword=rows["265_lupa"]["headword"], level=rows["265_lupa"]["level"],
                                     kind="picture", status="alias", note="media stem of 265_lupa (build_apkg.IMAGE_ALIAS)")
        errors.append(f"note: build_apkg not importable here ({e.__class__.__name__}); IMAGE_ALIAS taken from the known value")
    return rows, errors


def next_map_path():
    n = 1
    for p in glob.glob(f"{RENAME_DIR}/key_map_v*.csv"):
        n = max(n, int(p.rsplit("_v", 1)[1].split(".")[0]) + 1)
    return f"{RENAME_DIR}/key_map_v{n}.csv"


def write_map(rows, path):
    if os.path.exists(path):
        raise SystemExit(f"refusing to overwrite {path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=MAP_COLUMNS)
        w.writeheader()
        for r in rows.values():
            w.writerow(r)
    return path


def load_map(path):
    rows = OrderedDict()
    for r in rd(path):
        rows[r["old_key"]] = r
    return rows


def all_map_paths():
    return sorted(glob.glob(f"{RENAME_DIR}/key_map_v*.csv"), key=lambda p: int(p.rsplit("_v", 1)[1].split(".")[0]))


def load_all_maps():
    """Every map in version order, composed: an old name maps to the CURRENT key (chains followed), so
    --verify without --map checks the names of every earlier map at once (key_map_v2 amends v1)."""
    rows = OrderedDict()
    for p in all_map_paths():
        for k, r in load_map(p).items():
            rows[k] = dict(r)
    cur = {k: r["new_key"] for k, r in rows.items() if r["new_key"] and r["new_key"] != k}
    for r in rows.values():
        seen = set()
        while r["new_key"] in cur and r["new_key"] not in seen:
            seen.add(r["new_key"]); r["new_key"] = cur[r["new_key"]]
    return rows


def forward(rows):
    """old -> new for the rows that rename (status renamed/alias)."""
    return {k: r["new_key"] for k, r in rows.items() if r["new_key"] and r["new_key"] != k}


def mint(headword):
    """The key for a new card: one above the highest number in use (live lists, study order, every map)."""
    used = []
    for p, col in ((A1_CARDS, "key"), (A2_LIST, "id"), (SENTENCES, "id"), (STUDY_ORDER, "key")):
        if os.path.exists(p):
            used += [r[col] for r in rd(p)]
    for p in glob.glob(f"{RENAME_DIR}/key_map_v*.csv"):
        used += [r["new_key"] for r in rd(p)]
    nums = [int(k[:WIDTH]) for k in used if NEW_KEY_RE.match(k or "")]
    if not nums:
        raise SystemExit("no NNNN_slug keys in the data yet: --mint is for after the rename has been applied")
    return f"{max(nums) + 1:0{WIDTH}d}_{slug(headword)}"


# ---------------------------------------------------------------------------------------------
# text rewriting
# ---------------------------------------------------------------------------------------------
def token_re(fwd):
    keys = sorted(fwd, key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z0-9])(" + "|".join(re.escape(k) for k in keys) + r")(?![A-Za-z0-9])")


def rewrite_text(text, rx, fwd):
    n = [0]

    def sub(m):
        n[0] += 1
        return fwd[m.group(1)]
    return rx.sub(sub, text), n[0]


def _eol(text):
    """Keep the file's own line terminator (the Mac-written CSVs are CRLF)."""
    return "\r\n" if "\r\n" in text else "\n"


def rewrite_master(text, rows, a1_rows):
    """Add a `key` column (after `#`) holding the card's new key; rows without a card (superseded colours,
    category-multi) stay blank."""
    buf = io.StringIO(text); rd_ = csv.DictReader(buf)
    if "key" in rd_.fieldnames:
        fields = rd_.fieldnames
    else:
        fields = list(rd_.fieldnames); fields.insert(fields.index("#") + 1, "key")
    bynum = {}
    for r in a1_rows:           # cards_anki (old keys): number -> old key -> new key
        m = rows.get(r["key"])
        if m and m["new_key"]:
            bynum[str(int(r.get("ff_no") or r["number"]))] = m["new_key"]
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=fields, lineterminator=_eol(text))
    w.writeheader(); n = 0
    for r in rd_:
        k = bynum.get(str(int(r["#"])) if r["#"].strip() else "", "")
        if k and r.get("key") != k:
            r["key"] = k; n += 1
        w.writerow({f: r.get(f, "") for f in fields})
    return out.getvalue(), n


def rewrite_restage_ids(text, rows, a1_rows):
    """a2_build/restage_bubbles.csv `ids`: a bare Fluent Forever number (374) is an A1 card -> its key."""
    bynum = {}
    for r in a1_rows:
        m = rows.get(r["key"])
        if m and m["new_key"]:
            bynum[str(int(r.get("ff_no") or r["number"]))] = m["new_key"]
    buf = io.StringIO(text); rd_ = csv.DictReader(buf)
    out = io.StringIO(); w = csv.DictWriter(out, fieldnames=rd_.fieldnames, lineterminator=_eol(text))
    w.writeheader(); n = 0
    for r in rd_:
        ids = [i.strip() for i in r["ids"].split(",") if i.strip()]
        new = [bynum.get(str(int(i)), i) if i.isdigit() else i for i in ids]
        if new != ids:
            n += 1
        r["ids"] = ",".join(new) if ids else r["ids"]
        w.writerow(r)
    return out.getvalue(), n


def plan_text_changes(rows, a1_rows):
    """[(path, new_text, n_tokens, n_special)] for every LIVE file that would change."""
    fwd = forward(rows); rx = token_re(fwd)
    out = []
    for p in LIVE_TEXT:
        if not os.path.exists(p):
            continue
        text = open(p, encoding="utf-8", newline="").read()      # newline="": keep CRLF files CRLF
        new, n = rewrite_text(text, rx, fwd)
        sp = 0
        if p == MASTER:
            new, sp = rewrite_master(new, rows, a1_rows)
        elif p == "a2_build/restage_bubbles.csv":
            new, sp = rewrite_restage_ids(new, rows, a1_rows)
        if new != text:
            out.append((p, new, n, sp))
    return out


# ---------------------------------------------------------------------------------------------
# media
# ---------------------------------------------------------------------------------------------
def media_rx(fwd):
    keys = sorted(fwd, key=len, reverse=True)
    return re.compile(r"^(" + "|".join(re.escape(k) for k in keys) + r")" + MEDIA_SUFFIX + MEDIA_EXT + r"$")


def plan_media(dirs, fwd, with_versions=True):
    """[(old_path, new_path)] for files under dirs (and their _rerolled/_superseded) named by an old key."""
    rx = media_rx(fwd); out = []
    seen = set()
    for d in dirs:
        cands = [d] + ([os.path.join(d, v) for v in VERSION_SUBDIRS] if with_versions else [])
        for c in cands:
            if not os.path.isdir(c) or c in seen:
                continue
            seen.add(c)
            for f in sorted(os.listdir(c)):
                m = rx.match(f)
                if not m:
                    continue
                new = fwd[m.group(1)] + f[len(m.group(1)):]
                out.append((os.path.join(c, f), os.path.join(c, new)))
    return out


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check).stdout


def tracked(paths):
    have = set(git("ls-files", "-z").split("\0"))
    return [p for p in paths if p in have]


def apply_media_moves(moves, use_git, log_path):
    """Rename, hash-checked; a log row per file. Refuses when a destination exists."""
    for old, new in moves:
        if os.path.exists(new):
            raise SystemExit(f"destination exists, nothing renamed: {new}")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    first = not os.path.exists(log_path)
    with open(log_path, "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t")
        if first:
            w.writerow(["old_path", "new_path", "bytes", "sha1", "method"])
        for old, new in moves:
            h = sha1(old); size = os.path.getsize(old)
            if use_git:
                git("mv", old, new)
            else:
                os.rename(old, new)
            if not os.path.exists(new) or sha1(new) != h:
                raise SystemExit(f"hash mismatch after rename: {old} -> {new}")
            w.writerow([old, new, size, h, "git mv" if use_git else "rename"])


# ---------------------------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------------------------
TEXT_EXT = {".csv", ".tsv", ".json", ".jsonl", ".md", ".py", ".txt", ".html", ".css", ".yaml", ".yml", ".sh"}


def classify(path):
    import fnmatch
    if path in LIVE_IN_HISTORY or path in LIVE_TEXT or fnmatch.fnmatch(path, "style/golden/*.prompt.txt"):
        return "live"
    if path in GENERATED:
        return "generated"
    if path in HISTORY_FILES or path.startswith(HISTORY_PREFIXES):
        return "history"
    return "unclassified"


def verify(rows, media_dirs=None, quiet=False):
    """Returns (failures, report lines)."""
    fails, rep = [], []
    fwd = forward(rows)
    # merged-away and deferred ids have no new key and may stay where the data records them
    # (from every map: an amendment map such as key_map_v2 carries only its own renamed rows)
    allowed_old = {k for p in all_map_paths() for k, r in load_map(p).items() if r["status"] in ("merged", "deferred")}
    allowed_old |= {k for k, r in rows.items() if r["status"] in ("merged", "deferred")}
    # 1. live data files: every key new-format
    checks = [(A1_CARDS, "key"), (A2_LIST, "id"), (SENTENCES, "id"), (STUDY_ORDER, "key"),
              ("audio_source.tsv", "key"), ("a2_build/context_notes.csv", "key"), (MERGED, "merged_into"),
              ("a2_build/id_map.csv", "id"), ("style_lab/research/settings_assignments.csv", "key"),
              ("style/golden/manifest.csv", "key")]
    for p, col in checks:
        if not os.path.exists(p):
            continue
        delim = "\t" if p.endswith(".tsv") else ","
        bad = []
        for r in csv.DictReader(open(p, encoding="utf-8"), delimiter=delim):
            v = (r.get(col) or "").strip()
            if not v or v in allowed_old:
                continue
            for part in v.split():
                stem = re.sub(r"(_s)?$", "", part) if col == "key" else part
                if not NEW_KEY_RE.match(stem):
                    bad.append(v)
                    break
        if bad:
            fails.append(f"{p}: {len(bad)} {col} value(s) not of the form NNNN_slug, e.g. {bad[:5]}")
        else:
            rep.append(f"ok   {p}: every `{col}` is NNNN_slug")
    # 2. old keys (exact tokens of the map) anywhere outside history
    hits = Counter(); unclassified = Counter()
    rx = token_re({k: k for k in rows if k not in allowed_old})
    for p in git("ls-files", "-z").split("\0"):
        if not p or os.path.splitext(p)[1].lower() not in TEXT_EXT or not os.path.exists(p):
            continue
        cls = classify(p)
        if cls == "history":
            continue
        try:
            text = open(p, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        found = rx.findall(text)
        if found:
            (hits if cls != "unclassified" else unclassified)[p] = len(found)
    for p, n in sorted(hits.items()):
        if classify(p) == "generated":
            rep.append(f"WARN generated file still carries {n} old key(s), regenerate it: {p}")
        else:
            fails.append(f"live file still carries {n} old key(s): {p}")
    for p, n in sorted(unclassified.items()):
        fails.append(f"UNCLASSIFIED file carries {n} old key(s) (add it to LIVE_TEXT or HISTORY in tools/rename_keys.py): {p}")
    # 3. media: nothing left under an old name; every renamed card has its media where the build looks
    dirs = media_dirs if media_dirs is not None else TRACKED_MEDIA_DIRS + UNTRACKED_MEDIA_DIRS
    leftovers = plan_media(dirs, fwd)
    if leftovers:
        fails.append(f"{len(leftovers)} media file(s) still under an old name, e.g. {[o for o, _ in leftovers[:5]]}")
    present = Counter()
    exts = ("png", "jpg", "webp", "mp3")
    counted = set()
    for r in rows.values():
        if r["status"] not in ("renamed", "unchanged") or r["new_key"] in counted:
            continue
        k = r["new_key"]; counted.add(k)
        img = any(os.path.exists(os.path.join(d, f"{k}.{e}")) for d in dirs if os.path.isdir(d) for e in exts[:3])
        aud = os.path.exists(os.path.join(AUDIO_DIR, f"{k}.mp3"))
        present["image" if img else "no image here"] += 1
        present["audio" if aud else "no audio here"] += 1
    rep.append("media under the new names in this checkout: " + ", ".join(f"{k} {v}" for k, v in sorted(present.items())))
    rep.append("(a cloud clone holds only the tracked media; the full check is the one run on the Mac after --apply-media)")
    return fails, rep


# ---------------------------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------------------------
def report(rows, errors, changes, tracked_moves, untracked_moves, out):
    w = out.write
    renamed = [r for r in rows.values() if r["status"] == "renamed"]
    w("rename_keys.py — DRY RUN (nothing written)\n")
    w(f"source order: {STUDY_ORDER} ({len(renamed)} cards) | lists: {A1_CARDS}, {A2_LIST}, {SENTENCES}\n\n")
    if errors:
        w("GUARDS\n")
        for e in errors:
            w(f"  ! {e}\n")
        w("\n")
    st = Counter(r["status"] for r in rows.values())
    w("MAP\n")
    w("  rows by status: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items())) + "\n")
    fam = Counter(("base NNN_slug" if re.match(r"^\d{3}_", r["old_key"]) else r["old_key"].split("-")[0] + "-####")
                  for r in renamed)
    w("  old families renamed: " + ", ".join(f"{k} {v}" for k, v in sorted(fam.items())) + "\n")
    lv = Counter((r["level"], r["kind"]) for r in renamed)
    w("  by level/kind: " + ", ".join(f"{a} {b} {n}" for (a, b), n in sorted(lv.items())) + "\n")
    a1n = [int(r["number"]) for r in renamed if r["level"] == "A1"]
    a2n = [int(r["number"]) for r in renamed if r["level"] == "A2"]
    if a1n and a2n:
        w(f"  numbers: A1 {min(a1n)}–{max(a1n)}, A2 {min(a2n)}–{max(a2n)} "
          f"({'contiguous blocks' if max(a1n) < min(a2n) else 'BLOCKS INTERLEAVE — check study_order.csv'})\n")
    w("  slug collisions (same slug, different numbers — allowed): "
      + str(sum(1 for s, c in Counter(r["slug"] for r in renamed).items() if c > 1)) + "\n\n")
    w("SAMPLE (first 12, then one of each family and kind)\n")
    shown = set()
    for r in renamed[:12]:
        w(f"  {r['old_key']:>24} -> {r['new_key']:<32} {r['level']} {r['kind']:<8} {r['headword']}\n"); shown.add(r["old_key"])
    want = [("A2-", "picture"), ("A2-", "phrase"), ("A2-", "cloze"), ("S-", "sentence")]
    for pref, kind in want:
        for r in renamed:
            if r["old_key"].startswith(pref) and r["kind"] == kind and r["old_key"] not in shown:
                w(f"  {r['old_key']:>24} -> {r['new_key']:<32} {r['level']} {r['kind']:<8} {r['headword']}\n")
                shown.add(r["old_key"]); break
    for r in renamed[-3:]:
        w(f"  {r['old_key']:>24} -> {r['new_key']:<32} {r['level']} {r['kind']:<8} {r['headword']}\n")
    for r in rows.values():
        if r["status"] in ("merged", "alias", "deferred") and r["status"] not in shown:
            w(f"  {r['old_key']:>24} -> {r['new_key'] or '(none)':<32} {r['status']}: {r['note']}\n"); shown.add(r["status"])
    w("\nLIVE TEXT FILES THAT CHANGE (tokens replaced, column rewrites)\n")
    for p, _, n, sp in changes:
        w(f"  {n:6d} {('+' + str(sp) + ' col') if sp else '':>9}  {p}\n")
    w(f"  {sum(n for _, _, n, _ in changes)} token replacements in {len(changes)} files\n")
    w("\nTRACKED MEDIA (git mv)\n")
    by = Counter(os.path.dirname(o) for o, _ in tracked_moves)
    for d, n in sorted(by.items()):
        w(f"  {n:6d}  {d}/\n")
    for o, nn in tracked_moves[:4]:
        w(f"         {o} -> {nn}\n")
    w(f"  {len(tracked_moves)} files\n")
    w("\nUNTRACKED MEDIA FOUND IN THIS CHECKOUT (the Mac has the rest; run --apply-media there)\n")
    by = Counter(os.path.dirname(o) for o, _ in untracked_moves)
    for d, n in sorted(by.items()):
        w(f"  {n:6d}  {d}/\n")
    w(f"  {len(untracked_moves)} files here\n")
    w("\nEXPECTED ON THE MAC (from the ledgers' last row per key; one picture per picture card):\n")
    for d in ("out_deck_f62", "out_deck_a2", "out_phrases_v3", "out_phrases_v3/round2", "out_deck_sent"):
        p = f"media/generation/{d}/ledger.csv"
        if os.path.exists(p):
            keys = {r["key"] for r in rd(p)}
            w(f"  {len(keys & set(rows)):6d}  {d}/  (ledger keys that are cards: {len(keys & set(rows))} of {len(keys)})\n")
    w("\nGENERATED FILES TO REBUILD AFTERWARDS: " + ", ".join(GENERATED) + "\n")
    w("HISTORY IS NOT REWRITTEN: " + ", ".join(HISTORY_PREFIXES[:8]) + ", … (tools/keymap.py resolves old names)\n")


# ---------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="derive and report, write nothing (the default)")
    ap.add_argument("--apply", action="store_true", help="write the map, rewrite LIVE files, git mv tracked media, verify")
    ap.add_argument("--apply-media", nargs="+", metavar="DIR", help="rename untracked media under DIR(s) from --map")
    ap.add_argument("--verify", action="store_true", help="check for dangling old keys and missing media")
    ap.add_argument("--map", help="an existing key map (default: the newest a2_build/rename/key_map_v*.csv)")
    ap.add_argument("--out", help="write the dry-run report here as well as to stdout")
    ap.add_argument("--allow-dirty", action="store_true")
    ap.add_argument("--mint", metavar="HEADWORD", help="print the key a NEW card gets: the next free number + slug "
                                                       "(after the lock, keys only ever append)")
    a = ap.parse_args(argv)

    if a.mint:
        print(mint(a.mint)); return 0

    if a.apply_media or (a.verify and not a.apply):
        path = a.map or (sorted(glob.glob(f"{RENAME_DIR}/key_map_v*.csv"),
                                key=lambda p: int(p.rsplit("_v", 1)[1].split(".")[0])) or [None])[-1]
        if not path or not os.path.exists(path):
            raise SystemExit("no key map found; run --apply first (or pass --map)")
        rows = load_map(path) if (a.map or a.apply_media) else load_all_maps()
        if a.apply_media:
            fwd = forward(rows)
            moves = plan_media(a.apply_media, fwd)
            if not moves:
                print("nothing to rename under", a.apply_media); return 0
            import socket, datetime
            log = f"{RENAME_DIR}/media_log_{os.path.basename(path)[:-4]}_{socket.gethostname()}_{datetime.date.today()}.tsv"
            apply_media_moves(moves, use_git=False, log_path=log)
            print(f"renamed {len(moves)} files; log {log}")
        fails, rep = verify(rows, media_dirs=a.apply_media if a.apply_media else None)
        for l in rep:
            print(l)
        for f in fails:
            print("FAIL", f)
        return 1 if fails else 0

    rows, errors = derive_map()
    a1_rows = rd(A1_CARDS)
    hard = [e for e in errors if not e.startswith("note:")]
    changes = plan_text_changes(rows, a1_rows)
    fwd = forward(rows)
    all_tracked = set(git("ls-files", "-z").split("\0"))
    moves = plan_media(TRACKED_MEDIA_DIRS + UNTRACKED_MEDIA_DIRS, fwd)
    tracked_moves = [(o, n) for o, n in moves if o in all_tracked]
    untracked_moves = [(o, n) for o, n in moves if o not in all_tracked]

    buf = io.StringIO()
    report(rows, errors, changes, tracked_moves, untracked_moves, buf)
    print(buf.getvalue())
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        open(a.out, "w", encoding="utf-8").write(buf.getvalue())
        print("report written to", a.out)
    if not a.apply:
        return 1 if hard else 0
    if hard:
        raise SystemExit("guards failed; nothing applied")
    if not a.allow_dirty and git("status", "--porcelain", "--untracked-files=no").strip():
        raise SystemExit("git tree is dirty; commit or stash first (or --allow-dirty)")
    path = write_map(rows, next_map_path())
    print("map written", path)
    for p, new, n, sp in changes:
        open(p, "w", encoding="utf-8", newline="").write(new)
    print(f"rewrote {len(changes)} files")
    log = f"{RENAME_DIR}/media_log_{os.path.basename(path)[:-4]}_tracked.tsv"
    apply_media_moves(tracked_moves, use_git=True, log_path=log)
    print(f"git mv {len(tracked_moves)} tracked media files; log {log}")
    if untracked_moves:
        apply_media_moves(untracked_moves, use_git=False, log_path=log.replace("_tracked", "_untracked_here"))
        print(f"renamed {len(untracked_moves)} untracked media files present in this checkout")
    fails, rep = verify(rows)
    for l in rep:
        print(l)
    for f in fails:
        print("FAIL", f)
    print("next: regenerate", ", ".join(GENERATED), "; then the code changes of PLAN §6, the spec release, the build.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
