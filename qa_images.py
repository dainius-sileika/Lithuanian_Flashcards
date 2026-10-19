#!/usr/bin/env python3
"""qa_images.py — automated QA gate for generated cards.

Two rules have governed this deck from the start, and both were being checked by
eye, which is why breaches kept surfacing a batch late:

  1. NO TEXT IN THE ART. The model cannot spell Lithuanian; worse, when it does
     spell the target word correctly it hands the learner the answer and the card
     stops teaching. Any lettering beyond a card's declared `card_text` budget is
     a defect. The target word appearing is a *hard* failure.
  2. GUESSABILITY. If you didn't already know the word, the picture alone should
     get you there. An image can be text-free and still fail by being unreadable,
     off-concept, or simply weird.
  3. DECLARED TEXT CAME OUT RIGHT (2026-10-11, lettering allowed where declared).
     Every quoted string in a card's `card_text` ("2 Lt 40 ct", "NAUJOJI ROMUVA")
     must appear in the read-back exactly — diacritics and numerals included,
     case and spacing ignored. A price tag reading "2 Lt 40 et" is a defect the
     old gate waved through as "declared and permitted".

Rule 1 is mechanical. Rule 2 is a judgement call, and OCR cannot make it —
tesseract was tried first and is unusable here: the painterly, textured ground
produces pages of hallucinated words while missing a 400-pixel question mark.
So QA asks a vision model to do what a reviewer does — read the image cold,
without being told the answer, and say what it sees.

The guessability check is deliberately blind: the model is never shown the target
word before it guesses. Only afterwards is the guess compared to the gloss. A
model that was told the answer would confirm it every time.

    python3 qa_images.py out_phrases                 # QA a folder
    python3 qa_images.py out_phrases --csv qa.csv     # write a report
    python3 qa_images.py images --budget 300          # stop after 5 minutes
    python3 qa_images.py out_phrases --recheck        # ignore the cache

Results are cached in `_qa/qa_cache.json`, keyed by file content hash, so a
re-run only pays for images that actually changed. Exit code is non-zero if any
card fails, so this can gate a generation run.
"""
import base64, csv, hashlib, json, os, re, sys, time, unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from openai import OpenAI
except ImportError:
    sys.exit("pip install openai")

# Override with GO_QA_MODEL. Default switched 2026-10-10 from gpt-5-mini
# (removed 2026-12-11) to gpt-5.6-luna: vision input, not deprecated, and
# cheaper ($0.20/$1.20 vs $0.25/$2.00 per M tokens). gpt-5.4-nano was the other
# candidate but is itself deprecated for 2027-04-01.
MODEL = os.environ.get("GO_QA_MODEL", "gpt-5.6-luna")
CACHE = "_qa/qa_cache.json"
STRESS = {0x0300, 0x0301, 0x0303}

# Metadata sources, in priority order. Each maps id -> row.
SOURCES = ["a2_build/a2_wordlist.csv", "wordlist_a2_pending.csv", "master_wordlist.csv",
           "cards_anki.csv"]   # the A2 list first: its card_text is the declared lettering
# rows drawn under the engine's single-glyph exception (227 raidė): one bare
# letter IS the subject, so a lone letter in the read-back is not a leak
try:
    from deck_builder import GLYPH_ROWS
except Exception:
    GLYPH_ROWS = {227}
# spec 3.1.0 DIRECTION_RULE: QA only WARNs, and only where the rule was emitted (go_generator.direction_applies)
try:
    from deck_builder import DIRECTION_FREE_ROWS
    from go_generator import direction_applies
except Exception:
    DIRECTION_FREE_ROWS, direction_applies = set(), (lambda *a, **k: False)

PROMPT = """You are inspecting an illustration from a language-learning flashcard deck.
Answer ONLY about what is actually visible. Do not speculate about intent.

Return strict JSON with these keys:
  "lettering":  array of every piece of readable text/lettering in the image,
                transcribed exactly. Include single letters and words on signs,
                labels, packaging, book spines, and inside speech bubbles.
                Do NOT include punctuation-only marks here. [] if none.
  "punctuation": array of standalone punctuation glyphs shown as graphic
                elements (e.g. "?", "!"). [] if none.
  "guess":      your best guess, in English, at the single word or short phrase
                this picture is trying to teach. Guess from the picture alone.
  "confidence": "high" | "medium" | "low" — how clearly the picture points at
                one specific meaning rather than several.
  "problems":   array of short strings describing anything visually wrong:
                garbled or nonsense lettering, malformed hands or faces, duplicated
                or fused limbs, incoherent objects, elements that contradict each
                other, or anything a careful reviewer would call an error. [] if none.
  "coherence":  for a picture with two or more panels, a strip, or an inset that
                repeats the main scene: {"applies": true, "consistent": true|false,
                "note": "what differs between the repetitions, one line"} — people,
                clothes, positions (left/right, front/behind), fixtures and held
                objects must match; only gesture, expression or step may change.
                {"applies": false} when no scene is repeated (insets that show a
                different object, place or close-up do not count).
"""


# 2026-10-17 — SITUATION cards (bubble-free restaging, a2_build/RESTAGE_PROPOSAL.md
# §2(b)). Rows of situations.py get three extra checks on top of rules 1-3:
#   4. NO BUBBLE: the cold reading also lists every speech/thought bubble or symbol
#      floating in the air; any one is a hard FAIL (so is any graphic "?" or "!").
#   5. NEIGHBOUR TEST: a second, still caption-blind call is shown the card's English
#      caption shuffled among its listed confusables and asked which one the picture
#      shows; picking a confusable is a hard FAIL.
#   6. CAPTION FIT / CUE / STRAY ACT: a third call is told the caption and the
#      distinguishing cue: caption fit "no" is a FAIL; cue not visible and any stray
#      speech act (handshake, wave, raised palm, bowed head, thumb-up, pointing that
#      the phrase does not call for) are WARN — the owner judges those on the page.
# Their cache entries are keyed "<key>:<hash>:sit", so the plain cache is untouched.
# 2026-10-17 pilot round 2 (a2_build/pilot_round2/RULES.md (d)): the fit call also
# reports speakers' gaze, two-panel continuity, limb ownership and held props, each a
# hard FAIL; the base cold read gains "coherence" (every card with repeated scenes).
# Situation cache keys are now "<key>:<hash>:sit:r2" so round-1 entries are not reused.
try:
    from situations import SITUATIONS as _SIT, BY_ID as _SIT_ID
except Exception:
    _SIT, _SIT_ID = {}, {}

SIT_PROMPT = PROMPT.rstrip() + """
  "bubbles":    array describing every speech bubble, thought bubble, balloon,
                or symbol floating in the air (question marks, exclamation
                marks, hearts, stars, pictograms, motion icons) that is drawn as
                a graphic rather than as a real object in the scene. A sign
                pictogram painted on a real door or signboard is NOT a bubble.
                [] if none.
"""

NEIGHBOUR_PROMPT = """You are inspecting an illustration from a language-learning flashcard deck.
The picture illustrates the everyday situation in which ONE of these phrases is said:
{options}
Judge from the picture alone. Return strict JSON:
  "best":      the option (copied exactly) that the picture fits best,
  "runner_up": the next best option (copied exactly), or "" if none comes close,
  "margin":    "clear" | "slight" | "none" — how clearly the best beats the runner-up.
"""

FIT_PROMPT = """You are inspecting an illustration from a language-learning flashcard deck.
Its English caption is: {caption}
The detail meant to make the situation unmistakable is: {cue}
{conversation_line}
Answer ONLY about what is visible. Return strict JSON:
  "fit":        "yes" | "nearly" | "no" — with the caption, does the picture show
                the moment this phrase is said?
  "cue_visible": true | false — is the detail above clearly visible?
  "stray_acts": array of gestures or symbols in the picture that belong to a
                DIFFERENT phrase and that this caption does not call for
                (a handshake, a wave, a raised palm, a bowed head, a thumb-up,
                a pointing finger, a hand on the chest). [] if none.
  "speakers":   for a picture in which someone speaks or is spoken to: an object
                {{"look_at_each_other": true|false,
                  "anyone_at_viewer": true|false,
                  "note": "who looks where, one line"}};
                null if nobody in the picture is speaking to anyone.
  "panels":     for a two-panel picture only: an object
                {{"same_people": true|false,
                  "same_positions": true|false,   (left stays left, nobody moved in front of or behind another)
                  "same_background": true|false,  (same walls, doors, windows, furniture, signs in both)
                  "props_consistent": true|false, (objects held by the same person in both, unless handed over)
                  "right_answers_left": true|false,
                  "note": "what differs, one line"}};
                null for a single scene.
  "direction":  if the MAIN figures walk, run, ride, drive or carry something from one
                place to another: which way they travel as the viewer sees it —
                "left-to-right" | "right-to-left" | "toward or away"; null if the main
                figures stand, sit or talk. Ignore background figures.
  "limbs_ok":   true | false — every arm and hand is attached to the right body
                (no hand on another person's arm, no floating or shared limb).
                If false, say which in "limbs_note".
  "limbs_note": one line, or "".
  "props_ok":   true | false — every object the caption or cue says is carried or
                held is visibly in that person's grip; no figure is merged into
                furniture, a counter or a vehicle. If false, say which in "props_note".
  "props_note": one line, or "".
"""
# 2026-10-18 hand-scan fixes: `--limbs` gives every NON-situation card the limb/prop part of the
# round-2 fit call as one extra caption-blind call (situation cards already have it), cache key
# "<key>:<hash>:limbs". limbs_ok / props_ok false are hard FAILs as on situation cards; a malformed
# hand (finger count, fused or melted fingers) is a WARN with the model's note.
LIMBS_PROMPT = """You are inspecting an illustration from a language-learning flashcard deck.
Look closely at EVERY hand and arm in the main picture and in every inset panel.
Answer ONLY about what is visible. Return strict JSON:
  "limbs_ok":   true | false — every arm and hand is attached to the right body
                (no third hand, no floating or disembodied hand, no arm crossing onto
                another person, no hand on the wrong side). If false, say which in "limbs_note".
  "limbs_note": one line, or "".
  "props_ok":   true | false — every object that someone holds is visibly in that
                person's grip (not floating beside the hand, fingers not passing through it).
                If false, say which in "props_note".
  "props_note": one line, or "".
  "hands_ok":   true | false — every clearly visible hand has natural anatomy: five
                fingers, no fused, melted or extra fingers, thumb on the correct side.
                Ignore hands too small to judge. If false, say which in "hands_note".
  "hands_note": one line, or "".
"""

CONVERSATION_LINE = ("In this picture someone speaks to someone else; the deck's rule is that "
                     "they look at each other and nobody looks at the viewer.")


def situation_row(key):
    """The situations.py entry for an image key ('0356_nieko_tokio', '0223_galvoti'), or None."""
    en = _SIT_ID.get(key)
    s = _SIT.get(en) if en else None
    if s and s.get("format") and s.get("render", "").startswith("yes"):
        return dict(s, english=en)
    return None


def _ask(client, path, text):
    b = base64.b64encode(open(path, "rb").read()).decode()
    r = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": text},
            {"type": "input_image", "image_url": f"data:image/png;base64,{b}"}]}],
    )
    txt = (r.output_text or "").strip()
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise ValueError(f"no JSON in reply: {txt[:200]}")
    return json.loads(m.group(0))


def describe_situation(client, path, srow):
    """Cold read (+ bubbles), then the caption-blind neighbour choice, then the
    caption-aware fit/cue/stray-act check. One merged dict, cached as one entry."""
    import random
    seen = _ask(client, path, SIT_PROMPT)
    cap = srow["english"]
    # a "(merge)" partner shares this very image by design — not a neighbour
    opts = [cap] + [c for c in srow.get("confusables", []) if c and c != cap and "(merge)" not in c]
    if len(opts) > 1:
        rnd = random.Random(cap)          # stable order per card
        rnd.shuffle(opts)
        nb = _ask(client, path, NEIGHBOUR_PROMPT.format(options="\n".join(f"  - {o}" for o in opts)))
        seen["neighbour"] = nb
        seen["neighbour_options"] = opts
    seen["fit"] = _ask(client, path, FIT_PROMPT.format(
        caption=cap, cue=srow.get("cue") or "(none given)",
        conversation_line=(CONVERSATION_LINE if srow.get("gaze", "conversation") == "conversation" else "")))
    return seen


def judge_limbs(lm):
    fails, warns = [], []
    if lm.get("limbs_ok") is False:
        fails.append(f"LIMBS: {lm.get('limbs_note') or 'a limb is on the wrong body'}")
    if lm.get("props_ok") is False:
        fails.append(f"PROPS: {lm.get('props_note') or 'a held object is not in the grip'}")
    if lm.get("hands_ok") is False:
        warns.append(f"HANDS: {lm.get('hands_note') or 'a malformed hand'}")
    return fails, warns


def judge_situation(seen, row, srow):
    """Rules 1-3 as for any card (minus the '?' and guessability rules, which belonged
    to the bubble grammar), plus rules 4-6 above."""
    r2 = dict(row); r2["category"] = ""; r2["type"] = ""; r2["flags"] = ""
    r2["english"] = r2.get("english") or srow["english"]
    s2 = dict(seen); s2["punctuation"] = []; s2["confidence"] = "high"; s2["guess"] = ""
    fails, warns = judge(s2, r2)
    warns = [w for w in warns if not w.startswith("question card shows no")]
    for b in seen.get("bubbles") or []:
        fails.append(f"BUBBLE/FLOATING SYMBOL: {b}")
    for p in seen.get("punctuation") or []:
        if p.strip():
            fails.append(f"floating punctuation {p!r}")
    nb = seen.get("neighbour") or {}
    best = (nb.get("best") or "").strip()
    if (best and best != srow["english"] and best in (srow.get("confusables") or [])
            and "(merge)" not in best):
        # a clear win for a neighbour is a hard fail; a slight one (near-synonyms such as
        # Thank you / Thank you very much) is left to the owner's neighbour toggle
        msg = f"NEIGHBOUR TEST: reads as {best!r} (margin {nb.get('margin', '?')})"
        (fails if (nb.get("margin") or "") == "clear" else warns).append(msg)
    elif best == srow["english"] and (nb.get("margin") or "") == "none":
        warns.append(f"neighbour test: no margin over {nb.get('runner_up')!r}")
    fit = seen.get("fit") or {}
    if (fit.get("fit") or "").lower() == "no":
        fails.append("caption fit: no")
    elif (fit.get("fit") or "").lower() == "nearly":
        warns.append("caption fit: nearly")
    if fit.get("cue_visible") is False:
        warns.append(f"cue not visible: {srow.get('cue')}")
    for a in fit.get("stray_acts") or []:
        warns.append(f"stray act: {a}")
    # 2026-10-17 pilot round 2 — the four owner-flagged defect classes. Each was a
    # re-roll in the owner's hands, so each is a hard FAIL here, not a WARN; the vision
    # model's own uncertainty is carried in the note.
    conv = srow.get("gaze", "conversation") == "conversation"
    sp = fit.get("speakers")
    if conv:
        if not sp:
            warns.append("gaze: model saw nobody speaking on a conversation card")
        elif sp.get("anyone_at_viewer") is True:
            fails.append(f"GAZE: a speaker looks at the viewer ({sp.get('note', '')})")
        elif sp.get("look_at_each_other") is False:
            fails.append(f"GAZE: speakers do not look at each other ({sp.get('note', '')})")
    pn = fit.get("panels") or {}
    if srow.get("format") == "situation_2":
        if not pn:
            warns.append("panels: model did not report on the two panels")
        else:
            bad = [k for k in ("same_people", "same_positions", "same_background", "props_consistent")
                   if pn.get(k) is False]
            if bad:
                fails.append(f"CONTINUITY: {', '.join(bad)} ({pn.get('note', '')})")
            if pn.get("right_answers_left") is False:
                warns.append(f"two panels: right does not answer left ({pn.get('note', '')})")
    if fit.get("limbs_ok") is False:
        fails.append(f"LIMBS: {fit.get('limbs_note') or 'a limb is on the wrong body'}")
    if fit.get("props_ok") is False:
        fails.append(f"PROPS: {fit.get('props_note') or 'a carried object is not held / figure merged into furniture'}")
    if ((fit.get("direction") or "").lower() == "right-to-left"
            and not any(i in DIRECTION_FREE_ROWS for i in srow.get("ids") or [])
            and direction_applies(srow.get("scene", ""), panels=2 if srow.get("format") == "situation_2" else 1)):
        warns.append("direction: the main moving figures head right-to-left (DIRECTION_RULE, spec 3.1.0)")
    return fails, warns


def plain(s):
    """Lowercase, strip stress marks — so 'kodėl' and 'kodė́l' compare equal."""
    s = (s or "").replace("i̇", "i")
    d = unicodedata.normalize("NFD", s)
    d = "".join(c for c in d if ord(c) not in STRESS)
    return unicodedata.normalize("NFC", d).lower().strip()


def compact(s):
    """plain() with all whitespace removed, so 'A E I O U' read back as five
    separate letters, or '2 + 3 = 5' read back as '2+3=5', still compare equal.
    Dashes and the minus sign fold to '-' ("1901–1979", "−10°")."""
    return re.sub(r"[\u2010-\u2015\u2212]", "-", re.sub(r"\s+", "", plain(s)))


def declared_strings(card_text):
    """The exact strings a card's `card_text` puts in double quotes."""
    return [q for q in re.findall(r'"([^"]+)"', card_text or "") if q.strip()]


def words_of(s):
    return [w for w in re.split(r"[^\wĀ-ſ]+", plain(s)) if len(w) >= 3]


def file_hash(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def card_id(r):
    """One id per card across all three sources, the card key (spec §12, 2026-10-20): A2 list rows
    by `id`, cards_anki and master_wordlist by `key` (master gained the column at the rename).
    Master rows without a card (superseded colours, category-multi) get 'ff<#>', which joins
    nothing. No numeric-prefix fallback: '0151_...' is study position 151, not wordlist row 151."""
    if (r.get("id") or "").strip():
        return r["id"].strip()
    if (r.get("key") or "").strip():
        return r["key"].strip()
    if (r.get("#") or "").strip():
        return f"ff{int(r['#'])}"
    return ""


def load_meta():
    """Merge every source into one row per card. Earlier sources win per
    field, but an empty field never hides a filled one — so `card_text` from
    master_wordlist reaches the text-exception cards even though cards_anki
    has no such column. (Before 2026-10-10 master_wordlist, keyed `#`, was
    never indexed at all, and the exception cards failed QA as text leaks.)"""
    meta = {}
    for src in SOURCES:
        if not os.path.exists(src):
            continue
        for r in csv.DictReader(open(src, encoding="utf-8")):
            cid = card_id(r)
            if not cid:
                continue
            row = meta.setdefault(cid, {})
            for k, v in r.items():
                if k and (v or "").strip() and not (row.get(k) or "").strip():
                    row[k] = v
    return meta


def describe(client, path):
    """Ask the vision model what it sees. Returns the parsed dict."""
    b = base64.b64encode(open(path, "rb").read()).decode()
    r = client.responses.create(
        model=MODEL,
        input=[{"role": "user", "content": [
            {"type": "input_text", "text": PROMPT},
            {"type": "input_image", "image_url": f"data:image/png;base64,{b}"}]}],
    )
    txt = (r.output_text or "").strip()
    m = re.search(r"\{.*\}", txt, re.S)
    if not m:
        raise ValueError(f"no JSON in reply: {txt[:200]}")
    return json.loads(m.group(0))


def is_question(row):
    """Canonical test — imported by gen_phrases.py so the generator and the QA
    gate cannot drift apart. They did once: full sentences like 'Kas tai?' are
    questions by their punctuation but sit outside the 'Question words' category,
    so the generator drew the mark correctly and QA then failed the card for it."""
    if row.get("category") == "Question words":
        return True
    if "question" in (row.get("flags") or "") or (row.get("type") or "").upper() == "Q":
        return True
    return ((row.get("lithuanian_TARGET") or "").strip().endswith("?")
            or (row.get("english") or "").strip().endswith("?"))


def judge(seen, row):
    """Turn a vision reading + the card's metadata into pass/fail findings."""
    target = row.get("lithuanian_TARGET") or row.get("lithuanian") or row.get("word") or ""
    gloss = row.get("english") or row.get("english_gloss") or row.get("gloss") or ""
    allowed = row.get("card_text") or ""
    is_q = is_question(row)

    fails, warns = [], []
    try:
        is_glyph = int(row.get("#") or row.get("ff_no") or 0) in GLYPH_ROWS
    except ValueError:
        is_glyph = False
    allow_words = set(words_of(allowed)) | {plain(x) for x in re.split(r"[,;/]", allowed) if x.strip()}
    tgt_words = set(words_of(target))

    for piece in seen.get("lettering", []) or []:
        p = plain(piece)
        if not p:
            continue
        # Bare numerals are illustration, not answer-leakage — clock faces,
        # prices, and rulers all carry them and none of them spell a word.
        if re.fullmatch(r"[\d\s.,:%+=-]+", p):
            continue
        if is_glyph and len(p) == 1 and p.isalpha():
            continue   # the glyph card's own letter (main picture + insets)
        pw = set(words_of(piece)) or {p}
        if pw & tgt_words:
            fails.append(f"TARGET WORD IN ART: {piece!r}")
        elif allowed and (p in allow_words or pw <= allow_words):
            pass  # declared and permitted
        elif allowed and (p in plain(allowed) or compact(p) in compact(allowed)):
            pass
        else:
            fails.append(f"undeclared text: {piece!r}")

    # Rule 3: every declared quoted string must have come out exactly. The
    # read-back is compared whitespace-free and in order; if the model listed
    # the pieces out of order, each whitespace-separated token must still be
    # present ("100" and "cm" for '"100" with "cm"').
    if allowed:
        readback = compact(" ".join(seen.get("lettering", []) or []))
        for want in declared_strings(allowed):
            cw = compact(want)
            if cw in readback:
                continue
            toks = [compact(t) for t in want.split() if compact(t)]
            if toks and all(t in readback for t in toks):
                continue
            fails.append(f"declared text garbled/missing: {want!r} (read back: "
                         f"{' | '.join(seen.get('lettering') or []) or 'nothing'})")

    puncts = [p for p in (seen.get("punctuation") or []) if p.strip()]
    has_q = any("?" in p for p in puncts)
    if has_q and not is_q:
        fails.append("stray '?' — this card is not a question")
    if is_q and not has_q:
        warns.append("question card shows no '?'")

    # Guessability gate — blind guess vs. the actual gloss.
    #
    # Exempt for question words: their grammar is one deliberately uniform
    # enquiry scene where only a small bubble pictogram changes, so a cold
    # reading returns the props ("wrench", "cup") and never "how" or "what kind
    # of". The card teaches through the cloze sentence on the back, not the
    # picture, so scoring it on guessability would flag the design as a bug.
    if not is_q:
        # crude singular fold, so "vowels" matches "vowel"
        fold = lambda ws: {w[:-1] if w.endswith("s") and len(w) > 3 else w for w in ws}
        guess, gw = seen.get("guess", ""), fold(words_of(seen.get("guess", "")))
        glw = fold(words_of(gloss))
        if gloss and gw and glw and not (gw & glw):
            warns.append(f"guessed {guess!r}, card teaches {gloss!r}")
        if (seen.get("confidence") or "").lower() == "low":
            warns.append("picture points at no single meaning (low confidence)")

    coh = seen.get("coherence") or {}
    if coh.get("applies") and coh.get("consistent") is False:
        fails.append(f"CONTINUITY: {coh.get('note') or 'repeated scene differs between panels/insets'}")
    for p in seen.get("problems", []) or []:
        warns.append(str(p))

    return fails, warns


def main():
    args = sys.argv[1:]
    folder = next((a for a in args if not a.startswith("--")), "out_phrases")
    out_csv = args[args.index("--csv") + 1] if "--csv" in args else None
    budget = float(args[args.index("--budget") + 1]) if "--budget" in args else 1e9
    recheck = "--recheck" in args
    limbs = "--limbs" in args

    if not os.getenv("OPENAI_API_KEY") and os.path.exists(".openai_key.txt"):
        os.environ["OPENAI_API_KEY"] = open(".openai_key.txt").read().strip()
    client = OpenAI()

    os.makedirs("_qa", exist_ok=True)
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) and not recheck else {}
    cache = {k: v for k, v in cache.items() if "error" not in v}  # legacy entries
    meta = load_meta()

    files = sorted(f for f in os.listdir(folder)
                   if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg")))
    todo = []
    for f in files:
        path = os.path.join(folder, f)
        key = os.path.splitext(f)[0]
        ck = f"{key}:{file_hash(path)}" + (":sit:r2" if situation_row(key) else "")
        if limbs and not situation_row(key):
            lk = f"{key}:{file_hash(path)}:limbs"
            if lk not in cache:
                todo.append((key, path, lk))
        if ck in cache:
            continue
        todo.append((key, path, ck))

    print(f"{len(files)} images | {len(files)-len(todo)} cached | {len(todo)} to inspect")
    t0 = time.time()
    done = 0
    errors = {}
    def save_cache():
        # Proton Drive can refuse a write with EDEADLK while it syncs; the
        # cache is the run's only record, so retry rather than lose it
        for i in range(6):
            try:
                json.dump(cache, open(CACHE, "w"), ensure_ascii=False, indent=1)
                return
            except OSError:
                time.sleep(2 * (i + 1))

    hard_stop = False
    if todo:
        ex = ThreadPoolExecutor(max_workers=int(os.environ.get("QA_WORKERS", "8")))
        futs = {(ex.submit(_ask, client, p, LIMBS_PROMPT) if ck.endswith(":limbs")
                 else ex.submit(describe_situation, client, p, situation_row(k)) if situation_row(k)
                 else ex.submit(describe, client, p)): (k, ck) for k, p, ck in todo}
        for fut in as_completed(futs):
            k, ck = futs[fut]
            try:
                cache[ck] = fut.result()
            except Exception as e:
                # errors are reported but never cached, so a transient API
                # failure is retried on the next run instead of sticking
                errors[ck] = {"error": str(e)[:200]}
            done += 1
            if done % 10 == 0:
                save_cache()          # a killed run keeps what it paid for
            if time.time() - t0 > budget:
                print(f"  budget reached — {done}/{len(todo)} inspected; rerun to continue")
                # do not wait for the in-flight requests: the budget is a hard
                # stop (a 180 s shell cap killed runs that waited on 40 futures)
                ex.shutdown(wait=False, cancel_futures=True)
                hard_stop = True
                break
        else:
            ex.shutdown(wait=True)
        save_cache()

    rows, nfail, nwarn = [], 0, 0
    for f in files:
        key = os.path.splitext(f)[0]
        srow = situation_row(key)
        ck = f"{key}:{file_hash(os.path.join(folder, f))}" + (":sit:r2" if srow else "")
        seen = cache.get(ck) or errors.get(ck)
        if not seen:
            continue
        row = meta.get(key) or {}
        if seen.get("error"):
            fails, warns = [f"QA error: {seen['error']}"], []
        elif srow:
            fails, warns = judge_situation(seen, row, srow)
        else:
            fails, warns = judge(seen, row)
        if limbs and not srow and not seen.get("error"):
            lk = f"{key}:{file_hash(os.path.join(folder, f))}:limbs"
            lm = cache.get(lk) or {}
            if not lm:
                warns.append("limbs check missing (rerun): " + str((errors.get(lk) or {}).get("error", ""))[:120])
            else:
                lf, lw = judge_limbs(lm); fails += lf; warns += lw
        status = "FAIL" if fails else ("WARN" if warns else "PASS")
        nfail += bool(fails)
        nwarn += bool(warns and not fails)
        word = row.get("lithuanian_TARGET") or row.get("lithuanian") or ""
        rows.append({"key": key, "word": word, "status": status,
                     "fails": " | ".join(fails), "warnings": " | ".join(warns),
                     "guess": seen.get("guess", ""),
                     "lettering": " | ".join(seen.get("lettering") or []),
                     "neighbour": ((seen.get("neighbour") or {}).get("best", "") if srow else ""),
                     "fit": ((seen.get("fit") or {}).get("fit", "") if srow else "")})
        if status != "PASS":
            print(f"  {status}  {key:12} {word[:22]:24} {' | '.join(fails + warns)[:80]}")

    print(f"\n{len(rows)} checked · {nfail} FAIL · {nwarn} WARN · {len(rows)-nfail-nwarn} PASS")
    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["key", "word", "status", "fails",
                                               "warnings", "guess", "lettering",
                                               "neighbour", "fit"])
            w.writeheader()
            w.writerows(rows)
        print(f"report -> {out_csv}")
    if hard_stop:
        sys.stdout.flush()
        os._exit(1 if nfail else 0)   # skip the interpreter's thread join
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
