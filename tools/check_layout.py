#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_layout.py — does the working directory still follow the layout of spec §13 / INDEX.md?

    python3 tools/check_layout.py            # print warnings, exit 0
    python3 tools/check_layout.py --strict   # exit 1 when a TRACKED file breaks the layout or INDEX.md misses
                                             # a top-level item (the pre-commit hook runs this)

What it checks (nothing is moved or deleted; this script only reports):
  root      every file at the root is one of the expected entry points, modules, live data files or caches
            (ROOT_FILES / ROOT_PATTERNS below); anything else is clutter: a Proton "Edit conflict" copy, a
            stray export, a document that belongs in docs/ or _archive/
  media     media/images holds only <key>.<ext> pictures (NNNN_slug) and the _history/ folder;
            media/audio holds only <key>.mp3 / <key>_s.mp3 and _history/; media/generation holds no pictures;
            no _history/, _rerolled/ or _superseded/ folder outside media/images/_history and media/audio/_history
  old homes the pre-2026-10-24 folders (images/, audio/, audio_a2/, out_*) must not come back
  index     every top-level item on disk is named in INDEX.md (so the map cannot silently go stale)
build_apkg.py runs the non-strict form at the start of every build.
"""
from __future__ import annotations
import argparse, fnmatch, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEY_RE = re.compile(r"^\d{4}_[a-z][a-z0-9_]*$")

ROOT_FILES = {
    # entry points
    "build_apkg.py", "build_recorder.py", "build_study_order_v3.py", "recorder_A2.html",
    "README.md", "INDEX.md", "LICENSE", ".gitignore",
    # pipeline modules imported by the entry points and the gen.py drivers
    "card_frame.py", "frame_crop.py", "frame_preview.py", "go_generator.py", "go_grammars.py", "go_settings.py",
    "deck_builder.py", "verb_flashcards.py", "situations.py", "gen_phrases.py", "historical.py", "qa_images.py",
    # live data
    "cards_anki.csv", "master_wordlist.csv", "card_notes.json", "study_order.csv", "audio_source.tsv",
    "wordlist_a2_pending.csv",
    # secrets (gitignored; scripts read them from the root; never share, never move)
    ".azure_key.txt", ".openai_key.txt", ".github_token", ".huggingface_token",
    # OS / editor noise that is not worth a warning
    ".DS_Store",
}
ROOT_PATTERNS = ["Lietuviu_Flashcards_v*.apkg"]      # the current release package(s); older ones -> _archive/builds/
ROOT_DIRS_IGNORED = {".git", "__pycache__", "_apkg_media", "_qa", "_cloud_media", "_cloud_out", "_transfer"}  # caches and cloud scratch
OLD_HOMES = ["images", "audio", "audio_a2", "out_deck", "out_deck_f62", "out_deck_a2", "out_deck_sent",
             "out_phrases", "out_phrases_v3", "out_phrases_a2", "images_a2", "images_sent"]
IMG_EXT = {".png", ".webp", ".jpg", ".jpeg"}
VERSION_DIRS = {"_history", "_rerolled", "_superseded"}
INDEX = os.path.join(ROOT, "INDEX.md")


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

    # --- root ---------------------------------------------------------------------------------
    for name in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, name)
        if os.path.isdir(p):
            if name in OLD_HOMES and any(True for _ in os.scandir(p)):
                report(name + "/", "a pre-2026-10-24 media folder is back; pictures belong in media/images/, audio in "
                                   "media/audio/, batch records in media/generation/<batch>/ (spec §13)")
            continue
        if name in ROOT_FILES or any(fnmatch.fnmatch(name, pat) for pat in ROOT_PATTERNS):
            continue
        if "Edit conflict" in name:
            report(name, "a Proton Drive 'Edit conflict' copy; compare with the original, then move it to _TO_DELETE/")
        else:
            report(name, "unexpected file at the root (INDEX.md says what belongs here; docs -> docs/, "
                         "superseded -> _archive/, junk -> _TO_DELETE/<reason>/)")

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
                    if name != "_history":
                        report(f"media/audio/{name}/", "only _history/ may be a folder under media/audio/")
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
