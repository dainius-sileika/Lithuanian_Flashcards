#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_layout.py — does the working directory still follow the layout of spec §13 / INDEX.md?

    python3 tools/check_layout.py            # print warnings, exit 0
    python3 tools/check_layout.py --strict   # exit 1 when a TRACKED file breaks the layout or INDEX.md misses
                                             # a top-level item (the pre-commit hook runs this)

What it checks (nothing is moved or deleted; this script only reports):
  root      the root holds the three entry points, recorder_A2.html, the current release package(s), README.md,
            INDEX.md, FILES.md, LICENSE, .gitignore and the secret key files — nothing else (ROOT_FILES /
            ROOT_PATTERNS below). A file at the root that is not one of these is clutter: a Proton "Edit conflict"
            copy, a stray export, a module that belongs in code/, a data file that belongs in data/.
  folders   every top-level folder is one of TOP_DIRS (each described in INDEX.md); code/ holds only Python
            modules, data/ only data files (no code), media/ only images/, audio/, generation/
  media     media/images holds only <key>.<ext> pictures (NNNN_slug) and the _history/ folder; media/audio only
            <key>.mp3 / <key>_s.mp3, _history/ and _inbox/ (recorder ZIPs); media/generation holds no pictures;
            no _history/, _rerolled/ or _superseded/ folder outside media/images/_history and media/audio/_history
  old homes the pre-2026-10-24 folders (images/, audio/, audio_a2/, out_*, a2_build/ beyond the inbox stub,
            a2_rebase/, build_reports/) must not come back, nor the root copies of the moved modules and data files
  index     every top-level item on disk is named in INDEX.md (so the map cannot silently go stale);
            FILES.md, the generated inventory, exists (tools/make_index.py --check keeps it current)
build_apkg.py runs the non-strict form at the start of every build.
"""
from __future__ import annotations
import argparse, fnmatch, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_RE = re.compile(r"^\d{4}_[a-z][a-z0-9_]*$")

ROOT_FILES = {
    # entry points and the owner's recording sheet
    "build_apkg.py", "build_recorder.py", "build_study_order_v3.py", "recorder_A2.html",
    # the front page, the map, the inventory, the licence, git
    "README.md", "INDEX.md", "FILES.md", "LICENSE", ".gitignore",
    # secrets (gitignored; scripts read them from the root; never share, never move)
    ".azure_key.txt", ".openai_key.txt", ".github_token", ".huggingface_token",
    # OS / editor noise that is not worth a warning
    ".DS_Store",
}
ROOT_PATTERNS = ["Lietuviu_Flashcards_v*.apkg"]      # the current release package(s); older ones -> _archive/builds/
# every top-level folder, and the one line that says what it is (INDEX.md §1 has the long form)
TOP_DIRS = {
    "code": "the pipeline modules (Python only)",
    "data": "the live data files (no code)",
    "docs": "the design spec, registers, guides, plans, decisions",
    "media": "card media: images/, audio/, generation/",
    "reports": "build manifests, verify reports, audits, QA results",
    "rounds": "one dated folder per round of work (YYYY-MM-DD_<name>)",
    "review_desk": "the owner's Review Desk sources",
    "sources": "external word lists and frequency tables",
    "tools": "maintenance tools and the hooks",
    "anki": "card CSS and the note-type notes",
    "fonts": "the shipped font files",
    "style": "the style lock and the golden set",
    "style_lab": "the style experiments (owner: kept as a record)",
    "_archive": "kept history: retired code, documents, data, packages",
    "_TO_DELETE": "junk sorted by reason, for the owner to delete",
    "a2_build": "forwarding stub for the old audio inbox (a2_build/audio/inbox/README.md) — remove after the current recording session",
}
ROOT_DIRS_IGNORED = {".git", "__pycache__", "_apkg_media", "_qa", "_cloud_media", "_cloud_out", "_transfer"}  # caches and cloud scratch
OLD_HOMES = ["images", "audio", "audio_a2", "out_deck", "out_deck_f62", "out_deck_a2", "out_deck_sent",
             "out_phrases", "out_phrases_v3", "out_phrases_a2", "images_a2", "images_sent",
             "a2_rebase", "build_reports"]
# root files that moved on 2026-10-24 (deep tidy): a copy coming back at the root is a mistake, not a new file
MOVED_FROM_ROOT = {
    "card_frame.py": "code/", "frame_crop.py": "code/", "frame_preview.py": "code/", "go_generator.py": "code/",
    "go_grammars.py": "code/", "go_settings.py": "code/", "deck_builder.py": "code/", "verb_flashcards.py": "code/",
    "situations.py": "code/", "gen_phrases.py": "code/", "historical.py": "code/", "qa_images.py": "code/",
    "cards_anki.csv": "data/", "master_wordlist.csv": "data/", "card_notes.json": "data/", "study_order.csv": "data/",
    "audio_source.tsv": "data/", "wordlist_a2_pending.csv": "data/",
}
A2_BUILD_STUB = {"a2_build/audio/inbox/README.md"}      # the only tracked file a2_build/ may still hold
IMG_EXT = {".png", ".webp", ".jpg", ".jpeg"}
DATA_EXT = {".csv", ".tsv", ".json", ".txt", ".md"}
VERSION_DIRS = {"_history", "_rerolled", "_superseded"}
ROUND_RE = re.compile(r"^\d{4}-\d{2}-\d{2}_[a-z0-9_]+$")
INDEX = os.path.join(ROOT, "INDEX.md")
FILES_MD = os.path.join(ROOT, "FILES.md")


def tracked():
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        return set(out.split("\0")) - {""}
    except Exception:
        return set()


def check(strict=False):
    warn, fail = [], []
    tr = tracked()

    def report(path, msg):
        (fail if (strict and path in tr) else warn).append(f"{path}: {msg}")

    def report_dir(rel, msg):
        """a folder-level problem: strict-fail when any tracked file sits under it"""
        if strict and any(t.startswith(rel.rstrip("/") + "/") for t in tr):
            fail.append(f"{rel}: {msg}")
        else:
            warn.append(f"{rel}: {msg}")

    # --- root ---------------------------------------------------------------------------------
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p):
            if name in ROOT_DIRS_IGNORED:
                continue
            if name in OLD_HOMES and any(True for _ in os.scandir(p)):
                report_dir(name + "/", "a pre-2026-10-24 folder is back; pictures belong in media/images/, audio in "
                                       "media/audio/, batch records in media/generation/<batch>/, reports in reports/, "
                                       "rounds in rounds/ (spec §13)")
            elif name not in TOP_DIRS:
                report_dir(name + "/", "unexpected top-level folder (spec §13: every top-level folder is one of the "
                                       "named ones; a new one needs a line in INDEX.md and in tools/check_layout.TOP_DIRS)")
            continue
        if name in MOVED_FROM_ROOT:
            report(name, f"moved to {MOVED_FROM_ROOT[name]} on 2026-10-24; the copy at the root is stale")
        elif name in ROOT_FILES or any(fnmatch.fnmatch(name, pat) for pat in ROOT_PATTERNS):
            continue
        elif "Edit conflict" in name:
            report(name, "a Proton Drive 'Edit conflict' copy; compare with the original, then move it to _TO_DELETE/")
        else:
            report(name, "unexpected file at the root (INDEX.md says what belongs here; code -> code/, data -> data/, "
                         "docs -> docs/, superseded -> _archive/, junk -> _TO_DELETE/<reason>/)")

    # --- code/ and data/ ---------------------------------------------------------------------
    code = os.path.join(ROOT, "code")
    if os.path.isdir(code):
        for name in sorted(os.listdir(code)):
            if name in ("__pycache__", ".DS_Store", "README.md"):
                continue
            if not name.endswith(".py"):
                report(f"code/{name}", "code/ holds Python modules only (data -> data/, documents -> docs/)")
    data = os.path.join(ROOT, "data")
    if os.path.isdir(data):
        for dp, dns, fns in os.walk(data):
            dns[:] = [d for d in dns if d not in ("__pycache__",)]
            rel = os.path.relpath(dp, ROOT).replace(os.sep, "/")
            for f in fns:
                if f == ".DS_Store":
                    continue
                if os.path.splitext(f)[1].lower() not in DATA_EXT:
                    report(f"{rel}/{f}", "data/ holds data files only (csv, tsv, json, txt, md); code -> code/ or tools/")

    # --- a2_build/ stub -----------------------------------------------------------------------
    stub = os.path.join(ROOT, "a2_build")
    if os.path.isdir(stub):
        for dp, dns, fns in os.walk(stub):
            rel = os.path.relpath(dp, ROOT).replace(os.sep, "/")
            for f in fns:
                q = f"{rel}/{f}"
                if q in A2_BUILD_STUB or f == ".DS_Store":
                    continue
                if f.lower().endswith(".zip") and rel == "a2_build/audio/inbox":
                    warn.append(f"{q}: a recorder ZIP in the OLD inbox; ingest it (python3 tools/ingest_takes.py {q}); "
                                "the inbox is media/audio/_inbox/ since 2026-10-24")
                else:
                    report(q, "a2_build/ was dissolved on 2026-10-24 (data -> data/, rounds -> rounds/, docs -> docs/, "
                              "reports -> reports/); only the inbox forwarding note may stay here")

    # --- rounds/ ------------------------------------------------------------------------------
    rounds = os.path.join(ROOT, "rounds")
    if os.path.isdir(rounds):
        for name in sorted(os.listdir(rounds)):
            if name == ".DS_Store":
                continue
            if not os.path.isdir(os.path.join(rounds, name)):
                report(f"rounds/{name}", "rounds/ holds dated folders only (YYYY-MM-DD_<name>/)")
            elif not ROUND_RE.match(name):
                report_dir(f"rounds/{name}/", "a round folder is named YYYY-MM-DD_<lower_snake_name>")

    # --- media --------------------------------------------------------------------------------
    media = os.path.join(ROOT, "media")
    if os.path.isdir(media):
        for sub in sorted(os.listdir(media)):
            if sub not in ("images", "audio", "generation") and sub != ".DS_Store":
                report(f"media/{sub}", "unexpected item in media/ (only images/, audio/, generation/)")
        img = os.path.join(media, "images")
        if os.path.isdir(img):
            for name in sorted(os.listdir(img)):
                p = os.path.join(img, name)
                if os.path.isdir(p):
                    if name != "_history":
                        report(f"media/images/{name}/", "only _history/ may be a folder under media/images/")
                    continue
                stem, ext = os.path.splitext(name)
                if name == ".DS_Store":
                    continue
                if ext.lower() not in IMG_EXT or not KEY_RE.match(stem):
                    report(f"media/images/{name}", "not a <key>.png|webp|jpg picture (NNNN_slug); history goes to _history/, "
                                                  "records to media/generation/")
            seen = {}
            for name in os.listdir(img):
                stem, ext = os.path.splitext(name)
                if ext.lower() in IMG_EXT and KEY_RE.match(stem):
                    seen.setdefault(stem, []).append(name)
            for stem, names in sorted(seen.items()):
                if len(names) > 1:
                    report(f"media/images/{stem}.*", f"two current pictures for one key: {sorted(names)} (the build takes "
                                                      "webp, then png, then jpg); move the loser to _history/")
        aud = os.path.join(media, "audio")
        if os.path.isdir(aud):
            for name in sorted(os.listdir(aud)):
                p = os.path.join(aud, name)
                if os.path.isdir(p):
                    if name == "_inbox":
                        for z in sorted(os.listdir(p)):
                            if z.lower().endswith(".zip"):
                                warn.append(f"media/audio/_inbox/{z}: a recorder ZIP waiting to be ingested "
                                            f"(python3 tools/ingest_takes.py media/audio/_inbox/{z})")
                            elif z not in (".gitkeep", "README.md", ".DS_Store"):
                                report(f"media/audio/_inbox/{z}", "the inbox holds recorder ZIPs only")
                    elif name != "_history":
                        report(f"media/audio/{name}/", "only _history/ and _inbox/ may be folders under media/audio/")
                    continue
                if name == ".DS_Store":
                    continue
                stem, ext = os.path.splitext(name)
                if ext.lower() != ".mp3" or not KEY_RE.match(stem[:-2] if stem.endswith("_s") else stem):
                    report(f"media/audio/{name}", "not a <key>.mp3 / <key>_s.mp3 take")
        gen = os.path.join(media, "generation")
        if os.path.isdir(gen):
            for dp, dns, fns in os.walk(gen):
                dns[:] = [d for d in dns if d != "__pycache__"]
                rel = os.path.relpath(dp, ROOT).replace(os.sep, "/")
                for d in dns:
                    if d in VERSION_DIRS:
                        report(f"{rel}/{d}/", "a version folder under media/generation/; pictures and their history live under media/images/")
                for f in fns:
                    if os.path.splitext(f)[1].lower() in IMG_EXT:
                        report(f"{rel}/{f}", "a picture under media/generation/; current -> media/images/, old -> media/images/_history/<batch>/")
    # version folders outside the two history homes (media/ and the root only; fonts/_superseded is the retired font pair)
    for dp, dns, _ in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT).replace(os.sep, "/")
        if rel == ".":
            dns[:] = [d for d in dns if d in ("media",) or d in OLD_HOMES]
        for d in list(dns):
            if d in VERSION_DIRS and not (rel == "media/images" and d == "_history") and not (rel == "media/audio" and d == "_history") \
                    and not rel.startswith("media/images/_history"):
                report(f"{rel}/{d}/", "version folder outside media/images/_history and media/audio/_history (spec §13)")

    # --- index --------------------------------------------------------------------------------
    if not os.path.exists(INDEX):
        fail.append("INDEX.md: missing at the root (spec §13)")
    else:
        text = open(INDEX, encoding="utf-8").read()
        for name in sorted(os.listdir(ROOT)):
            if name in ROOT_DIRS_IGNORED or name == ".DS_Store" or "Edit conflict" in name:
                continue
            p = os.path.join(ROOT, name)
            if os.path.isdir(p):
                if f"`{name}/`" not in text and f"`{name}`" not in text:
                    fail.append(f"INDEX.md: top-level folder `{name}/` is not described in INDEX.md (spec §13: a new top-level item "
                                "means a new line in the index, in the same commit)")
            elif name in ROOT_FILES and name != ".DS_Store" and f"`{name}`" not in text:
                warn.append(f"INDEX.md: root file `{name}` is not mentioned in INDEX.md")
    if not os.path.exists(FILES_MD):
        fail.append("FILES.md: missing at the root (the generated inventory; python3 tools/make_index.py writes it)")
    return warn, fail


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="print nothing when clean")
    a = ap.parse_args(argv)
    warn, fail = check(a.strict)
    for w in warn:
        print("layout WARN", w)
    for f in fail:
        print("layout FAIL", f)
    if not (warn or fail) and not a.quiet:
        print("layout OK (spec §13 / INDEX.md)")
    return 1 if (fail and a.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
