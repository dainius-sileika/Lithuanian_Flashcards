#!/usr/bin/env python3
"""Style lock — the fingerprint of the GO look (F6.2), recorded in style/STYLE_LOCK.json.

Every constant that shapes the pictures and the card frame is extracted from the live code,
stored with its value and a SHA-256 per item, and folded into one overall style hash:

  prompt.*     go_generator leads, suffixes, every *_RULE text, FIGURE_DRESS, the hair wording,
               the gaze sentences, the text-exception template, five canonical prompt assemblies;
               go_grammars (spec 3.0.1): SCENE_TAIL, the category grammars (NOUN_GRAMMARS, CAT2CLASS,
               PEOPLE_CLASS, NO_INSET_CLASSES) and compose_class's output for every class and category
  engine.*     image model default, quality, size, ratio
  qa.*         qa_images model default and every QA prompt
  frame.*      anki/*.css (text), the band colour and widths parsed from frame_standard.css,
               card_frame templates and backs, SECTIONS / ROUTE_SECTIONS, frame_crop constants,
               build_apkg frame/back/media defaults
  (the modules are in code/ since 2026-10-24; an item's `source` names the file it was read from, and is not
   part of the style hash, which is computed from the item names and values only)
  font.*       the shipped font files (SHA-256 + size)

Usage
  python3 tools/style_lock.py check            # exit 1 and list the items that differ from the lock
  python3 tools/style_lock.py update           # rewrite the lock; refuses unless the spec version was bumped
  python3 tools/style_lock.py update --force   # rewrite anyway (recorded in the lock as "forced")
  python3 tools/style_lock.py show             # print the style hash and spec version
  python3 tools/style_lock.py diff             # like check, with the text around the first difference

The lock must match the code at all times: tools/hooks/pre-commit runs `check`, and build_apkg.py
refuses to build on a mismatch (GO_ALLOW_STYLE_DRIFT=1 overrides, and is written into the build
manifest). This script changes no look-defining value; it only records them.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(ROOT, "style", "STYLE_LOCK.json")
SPEC = os.path.join(ROOT, "docs", "DESIGN_SPEC_CURRENT.md")
SPEC_VERSION_RE = re.compile(r"^\*\*Spec version (\d+\.\d+\.\d+)", re.M)

# the files whose text feeds the lock (used by the hook and spec_release to stage them)
SOURCE_FILES = ["code/go_generator.py", "code/go_grammars.py", "code/qa_images.py", "code/card_frame.py", "code/frame_crop.py",
                "code/deck_builder.py", "build_apkg.py",
                "anki/go_theme.css", "anki/frame_standard.css", "anki/back_proposed.css",
                "fonts/_Brygada1918-Regular.ttf", "fonts/_Brygada1918-Italic.ttf", "fonts/_Brygada1918-Bold.ttf"]


def _sha(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def _source_default(rel, name):
    """The literal default of `NAME = os.environ.get("ENV", "default")` or `NAME = "literal"`, read
    from the source text so the lock records the code's default, not the caller's environment."""
    src = _read(rel)
    m = re.search(rf'^{name}\s*=\s*os\.environ\.get\("[A-Z_]+",\s*"([^"]*)"\)', src, re.M)
    if not m:
        m = re.search(rf'^{name}\s*=\s*"([^"]*)"', src, re.M)
    if not m:
        m = re.search(rf'^{name}\s*=\s*int\(os\.environ\.get\("[A-Z_]+",\s*"([^"]*)"\)\)', src, re.M)
    if not m:
        raise SystemExit(f"style_lock: cannot find the default of {name} in {rel}")
    return m.group(1)


def spec_version(path=SPEC) -> str:
    with open(path, encoding="utf-8") as fh:
        m = SPEC_VERSION_RE.search(fh.read())
    if not m:
        raise SystemExit(f"style_lock: no '**Spec version X.Y.Z' line in {path}")
    return m.group(1)


# ---------------------------------------------------------------------------------------
def extract() -> dict:
    """name -> {"value": str, "source": file} for every look-defining constant."""
    for d in (os.path.join(ROOT, "code"), ROOT):      # the pipeline modules live in code/ (layout of 2026-10-24, spec §13)
        if d not in sys.path:
            sys.path.insert(0, d)
    import go_generator as g
    import card_frame as cf
    import frame_crop as fc
    import qa_images as qa
    import go_grammars as gg

    items = {}

    def put(name, value, source):
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False, indent=1, sort_keys=isinstance(value, dict))
        items[name] = {"value": value, "source": source}

    # --- prompt texts -------------------------------------------------------------------
    gsrc = "code/go_generator.py"
    for name in ("CONCEPT_LEAD", "CONCEPT_LEAD_SCENE", "STYLE_SUFFIX", "STYLE_SUFFIX_SCENE"):
        put(f"prompt.{name}", getattr(g, name), gsrc)
    for name in sorted(vars(g)):
        if "_RULE" in name and isinstance(getattr(g, name), str) and not name.startswith("__"):
            put(f"prompt.{name}", getattr(g, name), gsrc)
    put("prompt.FLAG_RULES.keys", sorted(g.FLAG_RULES), gsrc)
    put("prompt.FIGURE_DRESS", g.FIGURE_DRESS, gsrc)
    put("prompt.NO_STRAY_FIGURE", g.NO_STRAY_FIGURE, gsrc)
    put("prompt.SETTING_GUARD", g.SETTING_GUARD, gsrc)
    for name in ("_HOUSE_GAZE_LEAD", "_HOUSE_GAZE_SUFFIX", "_CONVERSATION_GAZE_LEAD", "_CONVERSATION_GAZE_SUFFIX"):
        put(f"prompt.{name}", getattr(g, name), gsrc)
    # the hair wording: the sentence of the lead from "Men side-parted" to the clothing clause
    m = re.search(r"Men side-parted.*?chosen for the setting and occasion\.", g.CONCEPT_LEAD)
    put("prompt.hair_and_dress_sentence", m.group(0) if m else "<<hair sentence not found in CONCEPT_LEAD>>", gsrc)
    m = re.search(r"People are ordinary Lithuanians of 1981.*?austere and plainly handsome\.", g.CONCEPT_LEAD)
    put("prompt.people_sentence", m.group(0) if m else "<<people sentence not found in CONCEPT_LEAD>>", gsrc)
    put("prompt._exact_text_rule.template", g._exact_text_rule("{spec}", "{exclude}"), gsrc)
    put("prompt._label_clause.template", g._label_clause("{labels}", "{exclude}"), gsrc)
    # canonical assemblies: the order and choice of segments for the main card kinds
    assemblies = {
        "vignette_insets": dict(subject="{subject}", people="civilian", insets=True, composition="vignette"),
        "scene_setting": dict(subject="{subject}", people="worker", insets=True, composition="scene",
                              setting="Setting: {setting}.", staging="{staging}"),
        "no_insets": dict(subject="{subject}", people="formal", insets=False),
        "glyph": dict(subject="{subject}", glyph=True, insets=False),
        "exact_text": dict(subject="{subject}", exact_text="{text}", exclude="{word}", flag="eu"),
        "motion_strip": dict(subject="{subject}", motion_strip=True, insets=True),
        "situation_conversation_2": dict(subject="{subject}", situation=True, gaze="conversation", panels=2,
                                         insets=False, exact_text="{text}"),
        "situation_plain": dict(subject="{subject}", situation=True, insets=True, people="professional",
                                precedent="{precedent}", likeness="{likeness}"),
    }
    for name, kw in assemblies.items():
        put(f"prompt.assembly.{name}", g.build_prompt(**kw), gsrc)

    # --- category grammars (go_grammars.py; added to the lock in spec 3.0.1) -----------------
    ggsrc = "code/go_grammars.py"
    put("prompt.grammar.SCENE_TAIL", gg.SCENE_TAIL, ggsrc)
    put("prompt.grammar.NOUN_GRAMMARS", gg.NOUN_GRAMMARS, ggsrc)
    put("prompt.grammar.CAT2CLASS", gg.CAT2CLASS, ggsrc)
    put("prompt.grammar.PEOPLE_CLASS", dict(gg.PEOPLE_CLASS, _default=gg.DEFAULT_PEOPLE), ggsrc)
    put("prompt.grammar.NO_INSET_CLASSES", sorted(gg.NO_INSET_CLASSES), ggsrc)
    put("prompt.grammar.compose_class",
        {"class:" + c: list(gg.compose_class(c)) for c in sorted(gg.NOUN_GRAMMARS)}
        | {"category:" + c: list(gg.compose_noun(c)) for c in sorted(gg.CAT2CLASS)}, ggsrc)

    # --- engine --------------------------------------------------------------------------
    put("engine.OPENAI_MODEL.default", _source_default(gsrc, "OPENAI_MODEL"), gsrc)
    put("engine.OPENAI_QUALITY", g.OPENAI_QUALITY, gsrc)
    put("engine.OPENAI_SIZES", g.OPENAI_SIZES, gsrc)
    put("engine.deck_builder.RATIO", _source_default("code/deck_builder.py", "RATIO"), "code/deck_builder.py")

    # --- QA ------------------------------------------------------------------------------
    qsrc = "code/qa_images.py"
    put("qa.MODEL.default", _source_default(qsrc, "MODEL"), qsrc)
    for name in ("PROMPT", "SIT_PROMPT", "NEIGHBOUR_PROMPT", "FIT_PROMPT", "LIMBS_PROMPT", "CONVERSATION_LINE"):
        put(f"qa.{name}", getattr(qa, name), qsrc)

    # --- card frame ----------------------------------------------------------------------
    for rel in ("anki/go_theme.css", "anki/frame_standard.css", "anki/back_proposed.css"):
        put(f"frame.css.{os.path.basename(rel)}", _read(rel), rel)
    fs = _read("anki/frame_standard.css")
    for var in ("--sf-red", "--sf-ink", "--sf-cream"):
        m = re.search(rf"{var}:\s*([^;]+);", fs)
        put(f"frame.colour.{var[2:]}", m.group(1).strip() if m else "<<missing>>", "anki/frame_standard.css")

    def rule_block(selector):
        m = re.search(re.escape(selector) + r"\s*\{(.*?)\}", fs, re.S)
        return m.group(1).strip() if m else "<<missing>>"
    put("frame.band.top", rule_block(".sf-top"), "anki/frame_standard.css")
    put("frame.band.bottom", rule_block(".sf-bot"), "anki/frame_standard.css")
    put("frame.band.side", rule_block(".sf"), "anki/frame_standard.css")
    gt = _read("anki/go_theme.css")
    m = re.search(r":root\s*\{(.*?)\}", gt, re.S)
    put("frame.palette.go_theme_root", m.group(1).strip() if m else "<<missing>>", "anki/go_theme.css")

    cfsrc = "code/card_frame.py"
    put("frame.SECTIONS", cf.SECTIONS, cfsrc)
    put("frame.ROUTE_SECTIONS", cf.ROUTE_SECTIONS, cfsrc)
    put("frame.FONT_FILES", cf.FONT_FILES, cfsrc)
    put("frame.section_css", cf.section_css(), cfsrc)
    for name in ("FRONT", "BACK", "CLOZE_FRONT", "CLOZE_BACK", "FIT_JS", "PB_BOLD_JS"):
        put(f"frame.template.{name}", getattr(cf, name), cfsrc)
    pb, pc = cf.proposed_backs("thumb")
    put("frame.template.PROPOSED_BACK_thumb", pb, cfsrc)
    put("frame.template.PROPOSED_CLOZE_BACK_thumb", pc, cfsrc)
    for name in ("FRAME_CROP_VERSION", "PAD_PX", "BAND_MIN", "BAND_MAX", "SIDE_MAX", "SIDE_RUN_MAX", "FALLBACK"):
        put(f"frame.crop.{name}", getattr(fc, name), "code/frame_crop.py")
    bsrc = "build_apkg.py"
    put("frame.build.FRAME.default", _source_default(bsrc, "FRAME"), bsrc)
    put("frame.build.BACK_STYLE.default", _source_default(bsrc, "BACK_STYLE"), bsrc)
    put("frame.build.BACK_PIC.default", _source_default(bsrc, "BACK_PIC"), bsrc)
    put("frame.build.IMG_FMT.default", _source_default(bsrc, "IMG_FMT"), bsrc)
    put("frame.build.IMG_WIDTH.default", _source_default(bsrc, "IMG_WIDTH"), bsrc)
    bs = _read(bsrc)
    m = re.search(r'im\.save\(dst, "JPEG", ([^)]*)\)', bs)
    put("frame.build.jpeg_save_args", m.group(1) if m else "<<missing>>", bsrc)

    # --- fonts (binary: hash + size) -----------------------------------------------------
    for f in cf.FONT_FILES:
        rel = os.path.join(cf.FONT_DIR, f)
        with open(os.path.join(ROOT, rel), "rb") as fh:
            data = fh.read()
        put(f"font.{f}", f"sha256:{_sha(data)} bytes:{len(data)}", rel)

    return items


def fingerprint(items: dict) -> dict:
    """items with a sha256 per item and the overall style hash."""
    out = {}
    for name in sorted(items):
        it = items[name]
        out[name] = {"sha256": _sha(it["value"]), "source": it["source"], "value": it["value"]}
    overall = _sha("\n".join(f"{n}={out[n]['sha256']}" for n in sorted(out)))
    return {"style_hash": overall, "style_hash_short": overall[:12], "items": out}


def load_lock(path=LOCK):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def compare(live: dict, lock: dict):
    """-> (changed, added, removed) item names between the live fingerprint and the lock."""
    li, ki = live["items"], lock.get("items", {})
    changed = [n for n in sorted(li) if n in ki and li[n]["sha256"] != ki[n]["sha256"]]
    added = [n for n in sorted(li) if n not in ki]
    removed = [n for n in sorted(ki) if n not in li]
    return changed, added, removed


def verify():
    """-> (ok, message, live). ok is False when the lock is missing or any item differs."""
    live = fingerprint(extract())
    lock = load_lock()
    if lock is None:
        return False, f"no style lock at {os.path.relpath(LOCK, ROOT)} (run tools/style_lock.py update)", live
    changed, added, removed = compare(live, lock)
    if not (changed or added or removed):
        return True, f"style lock OK  style {live['style_hash_short']}  spec {lock.get('spec_version')}", live
    lines = [f"STYLE DRIFT: the code no longer matches style/STYLE_LOCK.json "
             f"(lock {lock['style_hash'][:12]} -> live {live['style_hash_short']})"]
    for n in changed:
        lines.append(f"  changed  {n}   ({live['items'][n]['source']})")
    for n in added:
        lines.append(f"  new      {n}   ({live['items'][n]['source']})")
    for n in removed:
        lines.append(f"  removed  {n}")
    lines.append("If the change is intended: bump the spec (tools/spec_release.py) and run "
                 "tools/style_lock.py update; see docs/HOW_TO_CHANGE_THE_LOOK.md.")
    return False, "\n".join(lines), live


def _first_diff(a: str, b: str, ctx=60):
    i = 0
    n = min(len(a), len(b))
    while i < n and a[i] == b[i]:
        i += 1
    lo = max(0, i - ctx)
    return a[lo:i + ctx].replace("\n", "⏎"), b[lo:i + ctx].replace("\n", "⏎")


def cmd_check(args, with_diff=False):
    ok, msg, live = verify()
    print(msg)
    if not ok and with_diff:
        lock = load_lock() or {"items": {}}
        for n in compare(live, lock)[0]:
            old, new = _first_diff(lock["items"][n]["value"], live["items"][n]["value"])
            print(f"\n--- {n}\n  lock: …{old}…\n  live: …{new}…")
    return 0 if ok else 1


def write_lock(live: dict, spec_ver: str, note="", forced=False, path=LOCK):
    doc = {
        "_": "GO style lock — the look-defining constants of the Lietuvių Flashcards pipeline, recorded "
             "by tools/style_lock.py. Do not edit by hand; `tools/style_lock.py update` after a spec bump.",
        "style_hash": live["style_hash"],
        "style_hash_short": live["style_hash_short"],
        "spec_version": spec_ver,
        "updated": datetime.date.today().isoformat(),
        "forced": forced,
        "note": note,
        "item_count": len(live["items"]),
        "items": live["items"],
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return doc


def cmd_update(args):
    live = fingerprint(extract())
    lock = load_lock()
    sv = spec_version()
    if lock is not None:
        changed, added, removed = compare(live, lock)
        if not (changed or added or removed) and lock.get("spec_version") == sv and not args.force:
            print(f"style lock already current (style {live['style_hash_short']}, spec {sv}); nothing to do")
            return 0
        if (changed or added or removed) and lock.get("spec_version") == sv and not args.force:
            print(f"REFUSED: the look changed ({len(changed)} changed, {len(added)} new, {len(removed)} removed "
                  f"items) but docs/DESIGN_SPEC_CURRENT.md is still spec version {sv}, the version the lock "
                  f"was made for.\nBump the spec first: python3 tools/spec_release.py --bump major|minor|patch "
                  f"--note '...' (major = look or card format, minor = a rule added, patch = wording).\n"
                  f"Then run this update again. --force overrides and is recorded in the lock.")
            for n in changed + added + removed:
                print(f"  {n}")
            return 2
    doc = write_lock(live, sv, note=args.note or "", forced=bool(args.force))
    print(f"style lock written: {os.path.relpath(LOCK, ROOT)}  style {doc['style_hash_short']}  "
          f"spec {sv}  items {doc['item_count']}" + ("  (FORCED)" if args.force else ""))
    return 0


def cmd_show(args):
    lock = load_lock()
    live = fingerprint(extract())
    print(f"live  style {live['style_hash_short']}  ({live['style_hash']})  items {len(live['items'])}")
    if lock:
        print(f"lock  style {lock['style_hash_short']}  spec {lock['spec_version']}  updated {lock['updated']}")
    print(f"spec  version {spec_version()}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    sub.add_parser("diff")
    sub.add_parser("show")
    up = sub.add_parser("update")
    up.add_argument("--force", action="store_true", help="rewrite even without a spec version bump")
    up.add_argument("--note", default="", help="one line recorded in the lock")
    a = ap.parse_args(argv)
    if a.cmd == "check":
        return cmd_check(a)
    if a.cmd == "diff":
        return cmd_check(a, with_diff=True)
    if a.cmd == "show":
        return cmd_show(a)
    return cmd_update(a)


if __name__ == "__main__":
    sys.exit(main())
