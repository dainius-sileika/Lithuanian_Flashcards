# How to change the look

One page. Applies to anything that touches the aesthetic: a prompt lead, suffix or `*_RULE`, `FIGURE_DRESS`,
the hair wording, the image model / quality / size, a QA prompt or model, the frame CSS, band colour or
widths, fonts, section labels, card templates. If `python3 tools/style_lock.py check` would notice it,
this page applies. (Content changes — a staging line, a word, a merge — do not need it.)

| step | who | what |
|---|---|---|
| 1. Propose | planner | One written proposal: the change, why, the rule text or value before → after, which golden keys it will affect, cost. Put it on the **Review Desk** (`review_desk/items.json` → `build.py` → republish). Where the change is visual, a side-by-side page (current vs candidate) with OK/Reject per card. |
| 2. Owner approves | owner | A verdict on the Review Desk. **Nothing below happens without it.** |
| 3. Change the code | executor | Edit the constant(s). Do not touch anything the proposal did not name. `python3 tools/style_lock.py check` now fails and lists exactly the items you changed — that list must equal the proposal. |
| 4. Update the spec | planner | Edit the prose of `docs/DESIGN_SPEC_CURRENT.md` to say what the code now does (file + constant), with the owner's date. |
| 5. Release the spec | executor | `python3 tools/spec_release.py --bump <major\|minor\|patch> --note "<one line>"` — **major** = the look or card format changes, **minor** = a rule added, **patch** = wording. It bumps the header, adds the changelog line, freezes `docs/spec_history/DESIGN_SPEC_v<X.Y.Z>.md`, runs `style_lock.py update` (which refuses without the bump), commits the spec + snapshot + lock + the changed style-source files, and tags `spec-v<X.Y.Z>`. Dry-run first: add `--dry-run`. Then `git push origin HEAD --tags`. |
| 6. Golden comparison | executor → owner | Render the 28 keys of `style/golden/manifest.csv` with the new code (same prompts and settings) into a scratch folder; Review Desk page golden vs new. Owner judges the *set*. On a pass, `tools/golden_set.py --refresh` from the new renders and commit; on a fail, revert the code and release a patch that records the rejection. |
| 7. Build | executor | `build_apkg.py` refuses on drift; after step 5 it passes and stamps the package with APKG version, spec version and style hash (deck description + `reports/builds/<package>.json`). Add the row to `docs/VERSIONS.md`. |

**Rules that hold throughout**
- The lock must match the code at every commit (`tools/hooks/pre-commit`; `sh tools/install_hooks.sh` once per
  clone). `git commit --no-verify` and `GO_ALLOW_STYLE_DRIFT=1` exist for emergencies only; both leave a trace
  (the lock mismatch in history, the drift list in the build manifest and deck description).
- A frozen spec in `docs/spec_history/` is never edited; a wrong spec gets a new patch release.
- Nothing is overwritten: re-rolls to `_rerolled/`, replaced pictures to `_superseded/`, old packages keep their
  file names, old golden sets stay under their tag.
- The spec exists in three places: this repo (git + tags, pushed), the claude.ai Project (sync
  `docs/DESIGN_SPEC_CURRENT.md`, `docs/HOW_TO_CHANGE_THE_LOOK.md`, `docs/VERSIONS.md`, `style/STYLE_LOCK.json`,
  `style/golden/README.md` after each release), and `docs/spec_history/` inside the repo.
- Every ledger row written since spec 3.0.0 carries `spec_version` and `style_hash`, so any picture can be traced
  to the look that drew it; a render whose stamp is not the current lock is a candidate, not a master.
