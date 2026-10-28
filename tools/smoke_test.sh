#!/bin/sh
# smoke_test.sh — run every tool of this working directory once; stop at the first failure.
#
#   sh tools/smoke_test.sh              # from the root (or anywhere: it cd's to the root)
#   SMOKE_KEEP=1 sh tools/smoke_test.sh # keep the scratch folder
#
# What it proves (no paid render, no file of the working directory written except caches):
#   1. the three guards: style lock, layout (strict), inventory (check)
#   2. every live Python file compiles; every module in code/ and tools/ imports; the gen.py drivers' imports
#      resolve (parsed, not executed: they would render)
#   3. keymap resolves an old name; rename_keys --verify reports no FAIL; golden_set --status runs
#   4. build_study_order_v3 --audit on the live order; build_recorder A2 regenerated to scratch equals the live
#      recorder_A2.html and data/recording_list.csv (so the owner's sheet is current)
#   5. a smoke build (--limit 3) to scratch; verify_apkg of it against itself = 0 differences; apkg_keys_list
#   6. ingest_takes --inbox --dry-run; the Review Desk build; move_files verify of the 2026-10-24 deep tidy
# Exit 0 = green. Each step prints its own line; the first failing step stops the run with its output.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
SCRATCH=${SMOKE_SCRATCH:-"$ROOT/_qa/smoke_$(date +%Y%m%d_%H%M%S)"}
mkdir -p "$SCRATCH"
step() { printf '\n== %s\n' "$*"; }
fail() { echo "SMOKE FAIL: $*" >&2; exit 1; }

step "1a style lock";       python3 tools/style_lock.py check
step "1b layout (strict)";  python3 tools/check_layout.py --strict
step "1c inventory";        python3 tools/make_index.py --check

step "2a compile every live .py"
python3 - <<'EOF'
import py_compile, glob, sys
files = (["build_apkg.py", "build_recorder.py", "build_study_order_v3.py", "review_desk/build.py"]
         + glob.glob("code/*.py") + glob.glob("tools/*.py") + glob.glob("media/generation/*/*.py")
         + glob.glob("media/generation/*/*/*.py"))
for f in files:
    py_compile.compile(f, doraise=True)
print(f"{len(files)} files compile")
EOF
step "2b import code/ and tools/ modules"
python3 - <<'EOF'
import importlib, sys, os
sys.path[:0] = ["code", "tools", "."]
mods = ["card_frame", "frame_crop", "frame_preview", "go_generator", "go_grammars", "go_settings", "deck_builder",
        "verb_flashcards", "situations", "gen_phrases", "historical", "qa_images",
        "keymap", "style_lock", "check_layout", "golden_set", "verify_apkg", "ingest_takes", "process_take", "audio_review_page", "spec_release",
        "rename_keys", "move_files", "make_index", "build_apkg", "build_recorder"]
for m in mods:
    importlib.import_module(m)
import card_frame
for p in card_frame.font_media():
    assert os.path.exists(p), p
import deck_builder, historical, go_settings
assert deck_builder.CARD_NOTES and os.path.exists(deck_builder.WORDLIST)
assert os.path.exists(go_settings.BANK_PATH) and os.path.exists(go_settings.ASSIGN_PATH)
print(f"{len(mods)} modules import; fonts, card notes, wordlist, location bank, assignments found")
EOF
step "2c gen.py drivers: imports resolve (parsed, not run)"
python3 - <<'EOF'
import ast, glob, importlib.util, sys, os
sys.path[:0] = ["code", "tools", ".", "media/generation/out_deck_a2"]
n = 0
for f in sorted(glob.glob("media/generation/*/gen.py")) + ["media/generation/out_deck_a2/a2_adapter.py"]:
    tree = ast.parse(open(f, encoding="utf-8").read(), f)
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = [node.module.split(".")[0]]
        for name in names:
            if importlib.util.find_spec(name) is None:
                raise SystemExit(f"{f}: cannot resolve import {name}")
            n += 1
    src = open(f, encoding="utf-8").read()
    for lit in ("data/a2_wordlist.csv", "data/sentences/sentences.csv", "data/a2_staging.json", "data/sentences/staging.json"):
        if lit in src and not os.path.exists(lit):
            raise SystemExit(f"{f}: names {lit}, which does not exist")
print(f"{n} imports resolve in the drivers and the adapter")
EOF

step "3a keymap"
python3 -c "
import sys; sys.path.insert(0,'tools'); import keymap, re
k = keymap.canonical('A2-0348'); assert re.match(r'^\d{4}_[a-z]', k), k
assert 'A2-0348' in keymap.aliases(k); print('A2-0348 ->', k, '| maps:', [p.rsplit('/',1)[1] for p in keymap.maps()])"
step "3b rename_keys --verify (no FAIL; the recorder WARN is expected)"
python3 tools/rename_keys.py --verify > "$SCRATCH/rename_verify.txt" 2>&1 || true
if grep -q '^FAIL' "$SCRATCH/rename_verify.txt"; then cat "$SCRATCH/rename_verify.txt"; fail "rename_keys --verify reports FAIL"; fi
grep -c '^ok' "$SCRATCH/rename_verify.txt" | sed 's/$/ ok lines; no FAIL/'
step "3c golden_set --status"; python3 tools/golden_set.py --status > "$SCRATCH/golden_status.txt"; tail -1 "$SCRATCH/golden_status.txt"

step "4a build_study_order_v3 --audit (live order)"
python3 build_study_order_v3.py --audit data/study_order.csv > "$SCRATCH/order_audit.txt" 2>&1 || { tail -20 "$SCRATCH/order_audit.txt"; fail "study order audit"; }
tail -2 "$SCRATCH/order_audit.txt"
step "4b build_recorder A2 to scratch == live sheet"
RECORDER_OUT="$SCRATCH/recorder_A2.html" RECORDING_LIST_OUT="$SCRATCH/recording_list.csv" python3 build_recorder.py A2 > "$SCRATCH/recorder.txt" 2>&1 || { cat "$SCRATCH/recorder.txt"; fail "build_recorder"; }
head -1 "$SCRATCH/recorder.txt"
grep -q 'const SHEET_ID = "A2_afb2ebe2"' "$SCRATCH/recorder_A2.html" || fail "the regenerated sheet does not carry SHEET_ID A2_afb2ebe2 (IndexedDB lt_recorder_A2_afb2ebe2)"
grep -q 'function migrateKeys' "$SCRATCH/recorder_A2.html" || fail "the regenerated sheet has no migrateKeys (old take keys would be lost)"
echo "IndexedDB lt_recorder_A2_afb2ebe2 and migrateKeys present in the regenerated sheet"
if [ -n "$(ls media/images 2>/dev/null | grep -c '\.png$' | grep -v '^0$')" ]; then
  # the Mac (pictures present): the live sheet and list must be exactly what a regeneration writes
  if ! cmp -s "$SCRATCH/recording_list.csv" data/recording_list.csv; then fail "data/recording_list.csv is not what build_recorder.py A2 writes now (regenerate it)"; fi
  if ! cmp -s "$SCRATCH/recorder_A2.html" recorder_A2.html; then
    diff "$SCRATCH/recorder_A2.html" recorder_A2.html | head -5
    fail "recorder_A2.html is not what build_recorder.py A2 writes now (python3 build_recorder.py A2)"
  fi
  echo "recorder and recording list: identical to a fresh regeneration"
else
  echo "(no pictures in this clone: the sheet lists only the cards the build finds here; equality with the live sheet is checked on the Mac)"
fi

step "5a smoke build (--limit 3) to scratch"
APKG_VERSION=0.0 APKG_LEVELS=A1 APKG_OUT="$SCRATCH/smoke.apkg" REPORT_DIR="$SCRATCH/reports" python3 build_apkg.py --limit 3 > "$SCRATCH/build.txt" 2>&1 || { tail -30 "$SCRATCH/build.txt"; fail "smoke build"; }
tail -3 "$SCRATCH/build.txt"
test -f "$SCRATCH/smoke.apkg" || fail "no package written"
step "5b verify_apkg (the smoke package against itself)"
python3 tools/verify_apkg.py "$SCRATCH/smoke.apkg" --against "$SCRATCH/smoke.apkg" --key-map data/key_maps/key_map_v1.csv > "$SCRATCH/verify.json" 2>&1 || true
python3 - "$SCRATCH/verify.json" <<'EOF'
import json, sys
t = open(sys.argv[1], encoding="utf-8").read()
d = json.loads(t[t.index("{"):])      # the exit status also reflects the smoke package's missing pictures; the report is what counts
c = d["checks"]
assert c["fields_modulo_rename"]["n_field_diffs"] == 0, c["fields_modulo_rename"]
g = c["guids"]
assert g["n_changed_unexpectedly"] == 0 and g["n_only_new"] == 0 and g["n_only_old"] == 0, g
imp = d.get("import_test", {})
print(f"verify_apkg ran: {d['notes']} notes, 0 field differences, GUIDs unchanged, Anki import "
      f"{'ok' if imp.get('notes') == d['notes'] else 'not run'}; fail list {d['fail']} "
      "(a smoke package without pictures fails the picture check by design)")
EOF
step "5c apkg_keys_list"
python3 tools/apkg_keys_list.py "$SCRATCH/smoke.apkg" data/audio_source.tsv "$SCRATCH/smoke_keys.tsv" > /dev/null
wc -l < "$SCRATCH/smoke_keys.tsv" | sed 's/$/ lines in the per-card list/'

step "6a ingest_takes --inbox --dry-run"; python3 tools/ingest_takes.py --inbox --dry-run | tail -3
step "6b review_desk build"
( cd review_desk && python3 build.py > "$SCRATCH/review_desk.txt" 2>&1 ) || { cat "$SCRATCH/review_desk.txt"; fail "review_desk/build.py"; }
test -s review_desk/review_desk.html && echo "review_desk/review_desk.html written ($(wc -c < review_desk/review_desk.html) bytes; gitignored)"
step "6c move_files verify (deep tidy plan)"
if [ -d media/images/_history/out_deck_f62 ] && [ -n "$(ls media/images 2>/dev/null | head -1)" ]; then
  python3 tools/move_files.py verify rounds/2026-10-24_deep_tidy/moves.csv > "$SCRATCH/moves_verify.txt" || { grep -v '^EDITED' "$SCRATCH/moves_verify.txt" | tail -20; fail "move_files verify"; }
else
  python3 tools/move_files.py verify rounds/2026-10-24_deep_tidy/moves.csv --tracked-only > "$SCRATCH/moves_verify.txt" || { grep -v '^EDITED' "$SCRATCH/moves_verify.txt" | tail -20; fail "move_files verify (tracked only)"; }
fi
tail -1 "$SCRATCH/moves_verify.txt"

[ -n "$SMOKE_KEEP" ] || rm -rf "$SCRATCH"
printf '\nSMOKE TEST GREEN\n'
