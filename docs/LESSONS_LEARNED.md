# Lessons learned

**Read this at the start of every session, and paste the "Before you start" list into every agent brief.**
It exists so that what a mistake taught us survives context compaction, new sessions and new agents.
When something costs time or quality, add an entry the same day. Append; never rewrite an old entry (correct it
with a dated note underneath). Each entry: what happened, the rule now, and where the rule is enforced
(code, spec, hook, or "by hand"). An entry enforced only "by hand" is a candidate for a check.

The image-pipeline lessons from the style work are in `docs/PLAYBOOK_flashcard_language_system.md` §4; they are
not repeated here.

## Before you start (the short list)

1. Read `INDEX.md`, then `docs/DESIGN_SPEC_CURRENT.md`, then this file.
2. Never overwrite and never delete history: new versions get new names; superseded files go to `_history/` or
   `_archive/`; only the owner deletes (`_TO_DELETE/`).
3. Stress marks are sourced, never generated or guessed, on **every** Lithuanian form a card shows.
4. Audio is never gated or trimmed by an energy threshold. Clicks are removed only with margins and a self-check;
   the raw take is always kept.
5. Anything that processes data or media is a committed script, not a one-off command or a commit message.
6. Test anything the owner will use (recorder, review pages) in a headless browser before handing it over.
7. A refused web fetch is final: never fetch the same thing another way.
8. Commit from a clone outside Proton Drive; sync Proton with fetch + `reset --hard`; push tags from the Mac.
9. Every message to the owner ends with the Review Desk link; review requests give direct links.
10. The design spec changes only through `tools/spec_release.py` (a new or changed rule = minor bump).

## Audio

- **2026-07-28 · Silence gates ate phonemes.** Three passes of head/tail gating cut word-final voiceless
  fricatives (*karves* heard as *karve*) and plosive onsets (*dukra* without its *d*). Rule: no `silenceremove`,
  no threshold trimming. Lead-in 250 ms, tail 400 ms, EBU R128 normalisation. Enforced: commit d55ec8b; the
  2026-10-28 click-removal tool must keep ≥ 99.5 % of the speech-band energy and never cut within 250 ms of speech.
- **2026-10-28 · The July processing was never committed.** Only the commit message described it, so the new
  ingest tool converted to mp3 without normalising: new takes would have shipped ~15 dB quieter (−32 vs −17 LUFS).
  Rule: every processing step is code in `tools/`, with its parameters, and new output is measured against the
  shipped material before it ships. Enforced: `tools/process_take.py` / `tools/ingest_takes.py` (2026-10-28).
- **2026-10-28 · A key click is not "under 50 ms above the floor".** In the first batch every Space press was a
  spike whose acoustic decay stayed above floor + 10 dB for 100–300 ms, and key-down and key-up often merged into
  one event; a duration rule would have called them speech (no cut) or, loosened, eaten short words. A click
  within 250 ms after the words cannot be told from a word-final release (*taĩp*). Rule: judge clicks by their
  core (frames within 15 dB of their peak) and their position (first 250 ms; ≥ 250 ms after the words); anything
  closer is kept and flagged; cuts never come within 250 ms of any non-click sound; the kept span must be
  sample-identical to the raw take around the words. Enforced: `tools/process_take.py` self-check.
- **2026-10-28 · The July takes are true-peak limited, and 63 of them were never normalised.** All 512 normalised
  human takes sit at −1.85 dBTP (median −16.7 LUFS): a limiter's signature. Linear gain alone brings the new,
  peakier takes to a median −18.8 LUFS. Separately, 63 shipped human takes (numbers, question words: 0079_trys,
  0150_kaip …) measure −36 to −48 LUFS. Rule: measure new audio against the shipped set before it ships, and
  measure the shipped set too. Enforced: `tools/process_take.py` logs loudness; the 63 are reported, not fixed.
- **2026-10-28 · The recorder mixed two takes.** A fast stop → start poured the end of one take into the next
  (one shared chunk list). Rule: per-take state; no new take while one is being saved; ignore key auto-repeat;
  no navigation while recording; pause playback while recording. Reproduce every recorder bug in headless
  Chromium with a fake microphone before and after the fix. Enforced: `build_recorder.py` (commit 4832e9b).
- **2026-10-28 · Adding stress marks would have voided recorded takes.** The page compared the stored "said" text
  to the sheet text exactly. Rule: "is this take still current?" is decided on the words, blind to stress marks,
  case and punctuation, in Python and in the page alike. Enforced: `said_key()` / `saidKey()` (commit 363b5fd).
- **2026-10-28 · Re-processing from the raw master brings back what the old processing hid.** The July processing
  had cut a fixed 150 ms from the head of every take and appended 400 ms of silence (each of the 63 quiet shipped
  takes = its master from 150 ms on, r ≥ 0.998). `process_take.py` cuts only with 250 ms margins, so 22 of the 63
  re-levelled takes start earlier in the master than the old file, 7 now keep a start click the old file had cut
  (flagged), and 19 end where the raw master ends with the words still sounding (the July recorder stopped early; the
  appended silence hid it). Rule: before replacing a shipped take, prove it is the same recording (identity check)
  and tell the owner what the new file contains that the old one did not. Enforced: `tools/relevel_takes.py`
  (identity ≥ 0.99, words, logs), the review page's re-level section.
- **2026-10-28 · Two Space presses look alike.** Looking for the recorder's two-takes-in-one bug, the first 400 ms of
  one take (a Space press and silence) matched the start of another at 0.92. Rule: a copy is proven by the noise
  floor too (≥ 0.98 over the pre-roll), not by the click; whole-take containment uses 0.9. Enforced:
  `tools/check_mixed_takes.py`.
- **2026-10-19 · Takes and the deck drifted apart.** Recorded words changed on the card after recording (lūpa →
  lūpos, wrong genitives). Rule: every take stores what was said; a changed card turns its take into a re-take
  and the old take is set aside, never deleted. Enforced: `audio_source.tsv` `said` column, recorder.

## Lithuanian data

- **2026-10-28 · Only headwords had stress marks.** The spec said "stressed pron"; genitives, feminines and some
  verb forms shipped unmarked in every package until the owner noticed while recording. Rule: every Lithuanian
  form shown on a card carries a sourced mark; an unsourced one is listed for the owner. Audits check every
  displayed field, not just the headword. Enforced: spec (minor release 2026-10-28), `rounds/2026-10-28_stress_forms/`.
- **2026-10-28 · Homographs passed earlier checks.** The stress sweep found *antis* "duck" filed with the gender
  and genitive of *añtis* m "bosom" (ančio; its check said "kirtis.info confirmed"), and *kaltas* "guilty" with
  the stress of the noun *káltas* "chisel". The old checks matched the spelling, not the word. Rule: a check
  against a source matches the sense (gloss), part of speech and gender too, not just the letters.
  Enforced: `rounds/2026-10-28_stress_forms/match_kaikki_v2.py` reports headword conflicts; fixed in commit 72af6a2.
- **2026-10-20 · A parse artefact shipped on a card back** (*kosėti* showed "{{l" and "lt" as its forms).
  Rule: before a build, scan every displayed field for wiki-template residue and empty-but-expected forms.
  Enforced: by hand in the rc3 round; candidate for a build check.
- **2026-10-20 · Proofreading engines rewrite the taught word away** (*Kiek jums metų?* has no *amžius*).
  Rule: a correction that removes the cloze target is a decision (keep the word in a new sentence, retarget, or
  merge), not a paste. Enforced: `rounds/2026-10-20_proofread/` rules.
- **2026-10-19 · Reading cards used words the learner hadn't met** (37 A1 cards). Rule: after any change to the
  order or the sentences, run the dependency audit: 0 A1 cards may need an A2-only word.
  Enforced: `build_study_order_v3.py --audit`.
- **2026-10-20 · Regenerating the order moved a pair apart** (*Kelinta valanda?* 331 → 1,069). Rule: pin pairs
  (`PIN_AFTER`), and diff positions after every regeneration before accepting it.

## Pictures

- **2026-10-19 · Masked patching of pictures failed** (owner: "this patching of images isn't working"). Rule: fixes
  are whole re-rolls unless the owner asks for an edit; the old picture goes to `_rerolled/` first.
- **2026-10-19 · A leading QA question passed a wrong picture** (round 5 asked "is the second the man
  leaving?"; the picture showed him arriving). Rule: QA questions are blind ("what is in panel 2?") and run
  against a control picture that has the defect.
- **2026-10-17 · Preview images were squashed on review pages.** Rule: every image on a page is
  `width:100%; height:auto`.

## Keys, versions, releases

- **2026-10-19/20 · Card IDs.** Never encode level or anything else that can change in a key; keys lock only once
  A1 and A2 are signed off; every rename keeps an old → new map forever (`data/key_maps/`).
- **2026-10-19 · A new rule went out as a patch** (3.0.1). Rule: new or changed rule = minor; wording/paths =
  patch; recorded as an erratum in 3.1.0. Enforced: `tools/spec_release.py`, by hand judgement.
- **2026-10-19 · Description placeholders.** Counts in public text come from the build manifest of the package
  that ships, recounted after every rebuild.
- **2026-10-19 · Release candidates.** A rebuilt package never overwrites the previous one: it becomes
  `_archive/builds/…_rcN.apkg` with its manifests renamed.

## Infrastructure

- **Recurring · Proton Drive corrupts `.git`.** It rolls back refs and files, makes "Edit conflict" copies, once
  renamed `.git/index` to `index 2`. Rule: commit from `~/work/repo` or the cloud clone; sync Proton with
  `git config core.logAllRefUpdates false`, fetch, `reset --hard FETCH_HEAD`; move conflict copies to
  `.git/_sync_conflicts/`; re-check 30–60 s later. git there needs the owner's delete permission per session.
- **Recurring · The cloud proxy refuses tag pushes** (403). Push tags from the Mac.
- **2026-10-20 · A container restart killed a running executor mid-task.** Rule: long jobs work in committed
  stages; before relaunching, check what landed (git log, file states on the Mac) and resume from there.
- **2026-10-20 · A refused WebFetch was worked around with curl.** Not acceptable. Rule: a refused or unanswered
  fetch is reported; the owner can paste the URL. Bulk sources the shells can reach (e.g. the kaikki.org
  Wiktionary dump) are fine.
- **2026-10-24 · Six picture folders searched first-hit-wins.** Nobody could tell which picture a card used.
  Rule: one home per medium (`media/images/<key>`, `media/audio/<key>`); `INDEX.md` + generated `FILES.md`;
  the pre-commit hook fails on an undescribed file. Enforced: `tools/check_layout.py`, `tools/make_index.py`.
- **2026-10-24 · Sub-agents cannot write to the claude.ai Project.** The lead copies INDEX, FILES, the spec,
  VERSIONS, STYLE_LOCK and this file after each change.

## Working with the owner

- **2026-10-28 · Choosing the agent (owner).** "Be judicious when you call a subagent: if Opus or another agent is good
  enough to do a job, use it; Fable should be for the hardest or most necessary work." Rule: execution, data
  plumbing, builds, audio processing, tidies with a clear plan → Opus (or a cheaper model); Fable only for hard
  judgement (aesthetic and image-prompt design, Lithuanian decisions sources can't settle, plans with real risk)
  or when the owner asks for it by name.
- One Review Desk for everything he must see or decide; every message ends with its link; settled items and
  settled reference documents leave the desk (a stale "card backs" document made a settled question look open).
- He is a native speaker: Lithuanian judgement calls that sources can't settle go to him as a short list, with
  the alternatives and the reason.
- He records on the Mac in Chrome; never change the recorder's IndexedDB name or its take keys without the
  migration code.
