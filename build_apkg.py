#!/usr/bin/env python3
"""Build the importable Anki deck (Lietuviu_Flashcards.apkg) from cards_anki.csv
+ media/images/ (one picture per card key) + media/audio/ (mp3) + anki/go_theme.css.

    pip install genanki
    python3 build_apkg.py

Front = card image (question). Back = image + Lithuanian word, audio, gender,
grammatical forms (noun genitive / verb principal parts / adjective feminine),
and the English gloss. Media (webp + mp3) is bundled into the .apkg.

A2 (2026-10-11): the same build also reads the A2 list (A2_LIST, default
a2_build/a2_wordlist.csv; set A2_LIST="" to skip it). Its IMG and PHRASE rows become
picture cards of the same note type once their image exists (looked up by id in
A2_IMAGE_DIRS, since 2026-10-24 the single folder media/images/); its CLOZE and PAIR
rows become native Anki cloze notes ("Lietuvių GO Cloze") built from example_lt,
where the {braces} mark the blank — these need no image. Every note carries the lt:: tags
(tags_for below) and goes to the A1/A2 subdeck by its level.

v2.1 (2026-10-17) — standard bands. The drawn red frame of every picture varies a lot in
thickness (bottom band 4-10 % of the height), so by default the builder trims it off a
COPY of each picture (frame_crop.py; the sources are never written) and the note types
redraw the frame in CSS at one fixed width (card_frame.py + anki/frame_standard.css):
top band = section label, bottom band = "pav. N" · leader · English caption. Brygada 1918
(regular, italic, bold; 2026-10-18) ships as media (fonts/). Pictures where detection fails fall back
to a fixed-percentage crop and are listed in build_reports/frame_flags.csv.

    python3 build_apkg.py                    # --frame standard (default)
    python3 build_apkg.py --frame drawn      # the pictures' own frame, v2.0 templates

Field lists, model ids, deck ids and note GUIDs are unchanged, so v2.1 updates v2.0
notes in place; only templates, CSS and media differ.

2026-10-18 (pilot round 2): one field appended to each note type, `usage` (picture) and
`Usage` (cloze), shown on the back under the gloss as a small italic line. Model ids,
deck ids and GUIDs are unchanged; the field change is a schema change, so existing users
delete the deck and import the new package (owner: deck coherence over old study history).
"""
import argparse, genanki, csv, hashlib, html, json, os, sys
import card_frame
import frame_crop

CSS = open("anki/go_theme.css", encoding="utf-8").read()
FRONT = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
         '<span class="plate">{{number}}</span></div>{{image}}'
         '<div class="bar bottom"><span>{{category}}</span><span>?</span></div></div>')
BACK = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
        '<span class="plate">{{number}}</span></div>{{image}}'
        '<div class="answer"><div class="word">{{lithuanian}}</div>'
        '{{#pron}}<div class="pron">{{pron}}</div>{{/pron}}{{audio}}'
        '{{#gender}}<div class="gender">{{gender}}</div>{{/gender}}'
        '{{#gen_sg}}<div class="forms">{{lithuanian}} · {{gen_sg}}</div>{{/gen_sg}}'
        '{{#pres3}}<div class="forms">{{lithuanian}} · {{pres3}} · {{past3}}</div>{{/pres3}}'
        '{{#fem}}<div class="forms">{{fem}}</div>{{/fem}}'
        '<hr id="answer"><div class="gloss">{{english}}</div>{{#usage}}<div class="usage">{{usage}}</div>{{/usage}}</div>'
        '<div class="bar bottom"><span>{{category}}</span><span>{{number}}</span></div></div>')

GO_FIELDS = ['key', 'lithuanian', 'english', 'gender', 'gen_sg',
             'pres3', 'past3', 'fem', 'number', 'category', 'image', 'audio', 'pron', 'usage']
model = genanki.Model(
    1607392913, "Lietuvių GO",
    fields=[{'name': n} for n in GO_FIELDS],
    templates=[{'name': 'Card', 'qfmt': FRONT, 'afmt': BACK}], css=CSS)

# --- A2 cloze note type -----------------------------------------------------
# Native Anki cloze (model_type CLOZE): the Text field carries {{c1::...}} around the
# target form, so Anki itself blanks and reveals it. The English sentence is shown
# as a hint under the blank; the back adds the headword, stress, gender, forms and gloss.
CLOZE_CSS = CSS + """
.cloze-text { font-size: 1.6em; line-height: 1.35; margin: 1.2em 0.6em 0.4em; text-align: center; }
.cloze { font-weight: bold; text-decoration: underline; }
.hint { font-size: 0.95em; opacity: 0.75; text-align: center; margin-bottom: 0.8em; font-style: italic; }
.word-line { text-align: center; margin-top: 0.6em; }
"""
CLOZE_FRONT = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
               '<span class="plate">{{Number}}</span></div>{{Image}}'
               '<div class="cloze-text">{{cloze:Text}}</div>'
               '{{^Image}}<div class="hint">{{SentenceEN}}</div>{{/Image}}'
               '<div class="bar bottom"><span>{{Category}}</span><span>?</span></div></div>')
CLOZE_BACK = ('<div class="page"><div class="bar"><span class="plate">LIETUVIŲ KALBA</span>'
              '<span class="plate">{{Number}}</span></div>{{Image}}'
              '<div class="cloze-text">{{cloze:Text}}</div>'
              '<div class="hint">{{SentenceEN}}</div>'
              '<div class="answer word-line"><div class="word">{{Word}}</div>'
              '{{#Pron}}<div class="pron">{{Pron}}</div>{{/Pron}}{{Audio}}{{SentenceAudio}}'
              '{{#Gender}}<div class="gender">{{Gender}}</div>{{/Gender}}'
              '{{#Forms}}<div class="forms">{{Forms}}</div>{{/Forms}}'
              '<hr id="answer"><div class="gloss">{{Gloss}}</div>{{#Usage}}<div class="usage">{{Usage}}</div>{{/Usage}}</div>'
              '<div class="bar bottom"><span>{{Category}}</span><span>{{Number}}</span></div></div>')
CLOZE_FIELDS = ['Text', 'SentenceEN', 'Word', 'Pron', 'Gender', 'Forms',
                'Gloss', 'Number', 'Category', 'Audio', 'Key', 'SentenceAudio', 'Image', 'Usage']
cloze_model = genanki.Model(
    1607392914, "Lietuvių GO Cloze", model_type=genanki.Model.CLOZE,
    fields=[{'name': n} for n in CLOZE_FIELDS],
    templates=[{'name': 'Cloze', 'qfmt': CLOZE_FRONT, 'afmt': CLOZE_BACK}], css=CLOZE_CSS)

# --- frame mode (v2.1) ------------------------------------------------------------
# The module-level FRONT/BACK/CSS above are the "drawn" (v2.0) look; set_frame("standard")
# swaps the two models' templates and CSS for the standard-bands ones. Same model ids and
# FIELDS either way: only templates/CSS change, so a re-import updates notes in place.
FRAME = "standard"
# 2026-10-18 (owner, Backs and Type review: "proposed" + "thumb"): the standard frame's backs are
# the proposed design (card_frame.proposed_backs, a2_build/BACKS_AUDIT.md §2) with the picture
# as a thumbnail; --back current (or BACK_STYLE=current) keeps the previous standard back.
BACK_STYLE = os.environ.get("BACK_STYLE", "proposed")
BACK_PIC = os.environ.get("BACK_PIC", "thumb")
STD_CSS = card_frame.standard_css(CSS)
STD_CLOZE_CSS = STD_CSS + CLOZE_CSS[len(CSS):]
FRAME_FLAGS = []          # [(name, frame_crop.Detection)] collected while transcoding


def set_frame(mode, back=None):
    """Point the two models at the drawn (v2.0) or standard-bands (v2.1) templates; in the
    standard frame `back` picks the proposed back (default) or the previous one ("current")."""
    global FRAME, BACK_STYLE
    if mode not in ("standard", "drawn"):
        raise SystemExit(f"--frame: expected standard or drawn, got {mode!r}")
    if back:
        BACK_STYLE = back
    if BACK_STYLE not in ("proposed", "current"):
        raise SystemExit(f"--back: expected proposed or current, got {BACK_STYLE!r}")
    FRAME = mode
    if mode == "standard" and BACK_STYLE == "proposed":
        pb, pc = card_frame.proposed_backs(BACK_PIC)
        pcss = "\n" + card_frame.proposed_css()
        model.templates = [{'name': 'Card', 'qfmt': card_frame.FRONT, 'afmt': pb}]
        model.css = STD_CSS + pcss
        cloze_model.templates = [{'name': 'Cloze', 'qfmt': card_frame.CLOZE_FRONT, 'afmt': pc}]
        cloze_model.css = STD_CLOZE_CSS + pcss
    elif mode == "standard":
        model.templates = [{'name': 'Card', 'qfmt': card_frame.FRONT, 'afmt': card_frame.BACK}]
        model.css = STD_CSS
        cloze_model.templates = [{'name': 'Cloze', 'qfmt': card_frame.CLOZE_FRONT,
                                  'afmt': card_frame.CLOZE_BACK}]
        cloze_model.css = STD_CLOZE_CSS
    else:
        model.templates = [{'name': 'Card', 'qfmt': FRONT, 'afmt': BACK}]
        model.css = CSS
        cloze_model.templates = [{'name': 'Cloze', 'qfmt': CLOZE_FRONT, 'afmt': CLOZE_BACK}]
        cloze_model.css = CLOZE_CSS

A2_LIST = os.environ.get("A2_LIST", "a2_build/a2_wordlist.csv")
# Media layout (tidy of 2026-10-24, spec §13, INDEX.md): ONE home for the current picture of every card
# and ONE for its audio, named by card key — media/images/<key>.png|webp|jpg, media/audio/<key>.mp3 and
# <key>_s.mp3. Every other version (shadowed renders, _rerolled/, _superseded/, the 1.x WebP masters) is
# under media/images/_history/<old batch path>/ and media/audio/_history/, which the build never reads.
# Until 2026-10-24 the pictures were resolved first-hit over six batch folders (out_phrases_v3/round2,
# out_phrases_v3, out_deck_f62, out_deck_a2, out_phrases_a2, out_deck_sent, images); the winners were moved
# into media/images/ (a2_build/tidy/moves_2026-10-24.csv), so the package content did not change. The
# *_IMAGE_DIRS names stay (build_recorder.py, tools/golden_set.py read them) and still accept a
# comma-separated override, e.g. A1_IMAGE_DIRS=_cloud_media/f62 for a cloud clone without the Mac media.
IMAGE_DIR = os.environ.get("IMAGE_DIR", "media/images")
AUDIO_DIR = os.environ.get("AUDIO_DIR", "media/audio")
A1_IMAGE_DIRS = os.environ.get("A1_IMAGE_DIRS", IMAGE_DIR).split(",")
A2_IMAGE_DIRS = os.environ.get("A2_IMAGE_DIRS", IMAGE_DIR).split(",")
A2_AUDIO_DIR = os.environ.get("A2_AUDIO_DIR", AUDIO_DIR)      # A2-list and sentence audio (same folder since 2026-10-24)
# Sentence cards (picture + cloze), see a2_build/sentences/design.md
SENTENCES = os.environ.get("SENTENCES", "a2_build/sentences/sentences.csv")
SENT_IMAGE_DIRS = os.environ.get("SENT_IMAGE_DIRS", IMAGE_DIR).split(",")
# Back-of-card usage notes (pilot round 2, a2_build/pilot_round2/CONTEXT_NOTES.md; owner
# 2026-10-17: on the backs now). One line under the gloss: the register / near-synonym note,
# then the tu/jus variant as a second line. Only rows the planner verified against a read
# source (high) or marked medium go on a back, and so do the rows the owner approved
# as written ("owner-approved", 2026-10-18: the ten former "unverified" rows, whose list
# a2_build/context_notes_unverified.csv was retired once they moved into context_notes.csv).
CONTEXT_NOTES = os.environ.get("CONTEXT_NOTES", "a2_build/context_notes.csv")
USAGE_CONFIDENCE = {"high", "medium", "owner-approved"}


def load_usage(path=CONTEXT_NOTES):
    """card key -> HTML for the usage field ('' for every other card)."""
    out = {}
    if not path or not os.path.exists(path):
        return out
    for r in csv.DictReader(open(path, encoding="utf-8")):
        if (r.get("confidence") or "").strip().lower() not in USAGE_CONFIDENCE:
            continue
        line = html.escape(r["context_line"].strip(), quote=False)
        v = (r.get("variant_tu_jus") or "").strip()
        if v:
            line += "<br>" + html.escape(v, quote=False)
        out[r["key"].strip()] = line
    return out


USAGE = load_usage()
USAGE_USED = set()          # keys whose note got a usage line in this build


def usage_for(k):
    u = USAGE.get(k, "")
    if u:
        USAGE_USED.add(k)
    return u


# Study order (new-card position): study_order.csv, made by build_study_order_v3.py (2026-10-19;
# v2 of 2026-10-17 kept as history, the v1 generator is in _archive/deprecated/).
STUDY_ORDER = os.environ.get("STUDY_ORDER", "study_order.csv")

# IDENTITY — what keeps a learner's history across deck versions:
#  * note GUID = genanki.guid_for(<card key>) — the permanent key (0027_suo, 0215_kas),
#    never the row position, the picture or the text. Re-importing a new version
#    updates the note's fields in place and keeps its cards' scheduling.
#  * model ids (1607392913 picture, 1607392914 cloze) and deck ids (2059400112/3) are
#    constants; changing any of them would make Anki treat the notes as new.
#  * keys are NNNN_slug (spec §12): the number is the card's study-order position when the
#    key was minted (the rename of 2026-10-20 renamed every card once, pre-lock; history in
#    a2_build/rename/key_map_v1.csv, read through tools/keymap.py). Once A1 and A2 are signed
#    off a key is never reused or renamed; a card that changes meaning keeps its key
#    (1124_lupos teaches lūpos; its slug was taken from the headword at the rename). A row that moves
#    between note types (picture ↔ cloze) cannot be updated in place — Anki will report a
#    note-type conflict; it becomes a new card.
#  * the study order (`due`) is applied to NEW cards at import; Anki does not move
#    cards a user already has (confirmed in its importer source). The Number field is the
#    key's number (= the study position at the rename; cards added later append, so it is a
#    stable name, not a live position). Owner 2026-10-17: deck coherence
#    over old study history — the advice to an existing user is simply to delete the
#    deck and import the new package; the order is not retrofitted onto old
#    collections, and no field is added to carry it (a new field would be a schema
#    change: "conflicting" notes on import unless note types are merged, then a
#    one-way sync).
#  * 2026-10-18: the owner accepted that schema change for the usage notes (one field
#    appended per note type, CONTEXT_NOTES below); the delete-and-reimport advice covers it.

# Images are stored as WebP in the repo (compact). Some Anki clients/older Qt
# builds don't render WebP inside cards, so for the importable deck we transcode
# each image to JPEG (universally supported) into a temp folder. The repo set is
# untouched. Set IMG_FMT="webp" to bundle WebP directly instead.
IMG_FMT = os.environ.get("IMG_FMT", "jpg")
# Anki/AnkiWeb caps a shared deck at 250 MB. Measured on this deck, resolution
# dominates format: full-size WebP still lands ~308 MB at the projected 1365
# cards, while JPEG downscaled to 1024 px comes in at ~179 MB (+~30 MB audio)
# and keeps universal client compatibility — some Anki builds don't render WebP
# inside cards. 1024 px is still more than a card ever displays.
IMG_WIDTH = int(os.environ.get("IMG_WIDTH", "1024"))
TMP = "_apkg_media"
APKG_VERSION = os.environ.get("APKG_VERSION", "2.1")   # 2.1 = standard bands; 2.0 packages stay as they are
# APKG_LEVELS (2026-10-12): build only the listed subdecks into the package, e.g.
# APKG_LEVELS=A1 and APKG_LEVELS=A2 for two packages under AnkiWeb's 250 MB cap. Model and
# deck ids are the same constants in both, so Anki merges them under one parent deck
# "Lietuvių Flashcards"; media are filtered to what the included notes reference.
APKG_LEVELS = [l.strip() for l in os.environ.get("APKG_LEVELS", "A1,A2").split(",") if l.strip()]
APKG_OUT = os.environ.get("APKG_OUT",
                          f"Lietuviu_Flashcards_v{APKG_VERSION}_{APKG_LEVELS[0]}.apkg" if len(APKG_LEVELS) == 1
                          else f"Lietuviu_Flashcards_v{APKG_VERSION}.apkg")   # never the old file
# (IMAGE_ALIAS, the lūpa -> lūpos render stem, retired with the rename of 2026-10-20: every media
# file is named by its card key; the old render stem is an `alias` row in a2_build/rename/key_map_v1.csv.)

# --- tags (spec §12, 2026-10-20) ------------------------------------------------------------
# Four hierarchical tags per note: lt::level::A1|A2, lt::kind::picture|phrase|cloze|sentence,
# lt::pos::<part of speech> (words only) and lt::topic::<section slug>. The topic is the section
# the card's top band shows: category -> topic from a2_build/rename/topic_map_v1.csv, except that
# phrase and sentence notes show XIX/XX whatever their category (card_frame.ROUTE_SECTIONS), so
# their topic is frazes/sakiniai and the tag never disagrees with the running head.
# An unmapped category fails the build.
TOPIC_MAP = "a2_build/rename/topic_map_v1.csv"
TOPIC = {r["category"]: r["topic"] for r in csv.DictReader(open(TOPIC_MAP, encoding="utf-8"))}
POS = {"N": "noun", "V": "verb", "A": "adjective", "ADV": "adverb", "P": "pronoun", "NUM": "numeral",
       "PREP": "preposition", "CONJ": "conjunction", "Q": "question"}
KIND_TOPIC = {"phrase": "frazes", "sentence": "sakiniai"}
KIND_OF_ROUTE = {"IMG": "picture", "PHRASE": "phrase", "CLOZE": "cloze", "PAIR": "cloze"}


def tags_for(level, kind, pos_code, category):
    if kind in KIND_TOPIC:
        topic = KIND_TOPIC[kind]
    elif category in TOPIC:
        topic = TOPIC[category]
    else:
        raise SystemExit(f"tags: category {category!r} is not in {TOPIC_MAP}; map it before building")
    t = [f"lt::level::{level}", f"lt::kind::{kind}", f"lt::topic::{topic}"]
    if kind not in KIND_TOPIC and pos_code in POS:
        t.insert(2, f"lt::pos::{POS[pos_code]}")
    return t


def a1_types():
    """A1 picture rows' part of speech: master_wordlist.csv `type`, joined on its `key` column."""
    return {r["key"]: r["type"] for r in csv.DictReader(open("master_wordlist.csv", encoding="utf-8"))
            if (r.get("key") or "").strip()}

def gender_mark(g):
    """1.9 — gender as a symbol, not a letter: blue Mars for masculine, red
    Venus for feminine, with a plural tag beside where the noun is plural-only.
    Returns HTML placed straight into the gender field."""
    g = (g or "").strip()
    if not g or g == "V":
        return ""
    plural = "pl" in g.lower()
    out = []
    if g.upper().startswith("M/F") or g.upper() == "MF":
        out.append('<span class="g m">\u2642</span><span class="g f">\u2640</span>')
    elif g.upper().startswith("M"):
        out.append('<span class="g m">\u2642</span>')
    elif g.upper().startswith("F"):
        out.append('<span class="g f">\u2640</span>')
    elif g.upper().startswith("N"):
        out.append('<span class="g n">\u26b2</span>')
    if plural:
        out.append('<span class="pl">pl.</span>')
    return "".join(out)


def is_adjective(gender, fem):
    """An adjective row: gender M/F and a feminine form (2ea6462 gave every adjective with
    a gender pair both). M/F people and job nouns (mokytojas/mokytoja) have no fem."""
    return bool((fem or "").strip()) and (gender or "").strip().upper().startswith("M/F")


_STRESS = "\u0300\u0301\u0303"          # grave, acute, tilde (not ogonek/caron/dot/macron)


def _unstressed(s):
    import unicodedata
    return unicodedata.normalize("NFC", "".join(
        c for c in unicodedata.normalize("NFD", s) if c not in _STRESS))


def adjective_forms(word, pron, fem):
    """Owner 2026-10-17: an adjective's back shows both forms, each beside its own symbol,
    "didelis ♂ · didelė ♀", in place of the bare ♂♀ pair. The masculine carries its stress
    mark from pron where the data has one (pron must be the same word, or the headword
    minus a bracketed note: "dvivietis (kambarys)" -> "dviviẽtis"); the feminine has no
    stressed form in the data and is shown plain. Returns HTML for the fem/Forms field."""
    word, pron, fem = (word or "").strip(), (pron or "").strip(), (fem or "").strip()
    bare = word.split(" (")[0].strip()
    masc = pron if pron and _unstressed(pron) in (word, bare) else word
    return (f'<span class="fp">{masc}&#8239;<span class="g m">\u2642</span></span> · '
            f'<span class="fp">{fem}&#8239;<span class="g f">\u2640</span></span>')


def _sha1(path):
    h = hashlib.sha1()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_image(k, dirs):
    """First existing <dir>/<key>.webp|png|jpg in dirs, else None."""
    for d in dirs:
        d = d.strip()
        if not d:
            continue
        for ext in ("webp", "png", "jpg"):
            p = f"{d}/{k}.{ext}"
            if os.path.exists(p):
                return p
    return None


def find_a2_image(k):
    return find_image(k, A2_IMAGE_DIRS)


def load_study_order():
    """key -> position from STUDY_ORDER (1-based); missing file -> {}."""
    if not STUDY_ORDER or not os.path.exists(STUDY_ORDER):
        return {}
    return {r["key"]: int(r["order"]) for r in csv.DictReader(open(STUDY_ORDER, encoding="utf-8"))}


def versioned_out(path):
    """Never overwrite a package: Lietuviu_Flashcards_v2.0.apkg, then _v2.0-1.apkg, -2 ..."""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path); n = 1
    while os.path.exists(f"{stem}-{n}{ext}"):
        n += 1
    return f"{stem}-{n}{ext}"


def media_image(k, src=None):
    """Transcode (and, in the standard frame, crop) one picture into the media staging
    folder TMP; returns (path, media file name). The source is only ever read."""
    src = src or find_image(k, A1_IMAGE_DIRS)
    if not src or not os.path.exists(src):
        return None, None
    ext = "webp" if IMG_FMT == "webp" else "jpg"
    std = FRAME == "standard"
    # Cropped copies get their own media name: an Anki that already holds the v2.0 file
    # under <key>.jpg would otherwise keep showing the drawn frame inside the CSS one.
    name = f"{k}_sf{frame_crop.FRAME_CROP_VERSION}.{ext}" if std else f"{k}.{ext}"
    dst = f"{TMP}/{name}"
    # The transcode cache is keyed by the SOURCE's content hash (and the
    # settings), recorded in a sidecar. Keyed by filename alone, a re-rolled
    # card silently shipped its old picture. The standard frame adds the crop
    # version and keeps the detection on the sidecar's second line (for the report).
    stamp = f"{_sha1(src)} {ext} {IMG_WIDTH}" + (f" crop{frame_crop.FRAME_CROP_VERSION}{frame_crop.override_tag(k)}" if std else "")
    side = dst + ".src"
    det = None
    cached = False
    if os.path.exists(dst) and os.path.exists(side):
        lines = open(side).read().splitlines()
        cached = bool(lines) and lines[0].strip() == stamp
        if cached and std:
            try:
                det = frame_crop.Detection.from_json(json.loads(lines[1]))
            except (IndexError, ValueError, TypeError):
                cached = False
    if not cached:
        from PIL import Image
        with Image.open(src) as im0:
            im = im0.convert("RGB")
        if std:
            det = frame_crop.detect_frame(im, k)       # at the source's own resolution
            im = frame_crop.crop_framed(im, det)       # a new image; src is untouched
        if IMG_WIDTH and im.width > IMG_WIDTH:
            im = im.resize((IMG_WIDTH, round(im.height * IMG_WIDTH / im.width)),
                           Image.LANCZOS)
        if ext == "webp":
            im.save(dst, "WEBP", quality=85, method=6)
        else:
            im.save(dst, "JPEG", quality=85, optimize=True, progressive=True)
        with open(side, "w") as fh:
            fh.write(stamp + ("\n" + json.dumps(det.to_json()) if det else ""))
    if det is not None:
        FRAME_FLAGS.append((f"{os.path.basename(os.path.dirname(src))}/{k}", det))
    return dst, name

def plate_number(key):
    """The "pav. N" in the bottom band = the key's number, for every note type (spec §12, 2026-10-20):
    0021_labas -> "21". Until spec 3.3.0 there were three sequences (A1 1-531 by wordlist row, A2 from
    1001, sentences from 4001). The Number field is display only (GUIDs come from the key)."""
    if not (len(key) > 5 and key[:4].isdigit() and key[4] == "_"):
        raise SystemExit(f"plate_number: {key!r} is not an NNNN_slug key")
    return str(int(key[:4]))


def cloze_text(example_lt):
    """'Aš {esu} mokytojas.' -> 'Aš {{c1::esu}} mokytojas.' (first braces only; later
    braces become c2, c3 so a sentence may blank two forms)."""
    out, n, i = [], 0, 0
    while True:
        a = example_lt.find("{", i)
        if a < 0:
            out.append(example_lt[i:]); break
        b = example_lt.find("}", a)
        if b < 0:
            out.append(example_lt[i:]); break
        n += 1
        out.append(example_lt[i:a] + "{{c%d::%s}}" % (n, example_lt[a + 1:b]))
        i = b + 1
    return "".join(out), n


def a2_forms(r):
    w = r["lithuanian_TARGET"]
    if is_adjective(r.get("gender", ""), r.get("fem", "")):
        return adjective_forms(w, r.get("lt_pron", ""), r["fem"])
    if r.get("gen_sg"):
        return f"{w} · {r['gen_sg']}"
    if r.get("pres3"):
        return f"{w} · {r['pres3']} · {r.get('past3', '')}"
    if r.get("fem"):
        return f"{w} · {r['fem']}"
    return ""


def add_a2_notes(DECKS, media, order=None):
    """Add the A2 list to the decks. Picture rows (IMG, PHRASE) need an image in
    A2_IMAGE_DIRS and use the GO model; CLOZE/PAIR rows need example_lt and use the
    cloze model. Returns counts. Skipped silently: no list, rows without image/sentence."""
    counts = {"image": 0, "cloze": 0, "skipped_no_image": 0, "skipped_no_sentence": 0}
    if not A2_LIST or not os.path.exists(A2_LIST):
        return counts
    os.makedirs(TMP, exist_ok=True)
    order = order or {}
    for r in csv.DictReader(open(A2_LIST, encoding="utf-8")):
        k = r["id"]; route = r.get("route", "")
        due = order.get(k, 0)
        level = (r.get("level") or "A2").strip() or "A2"
        target = DECKS.get(level, DECKS["A2"])
        tags = tags_for(level, KIND_OF_ROUTE.get(route, route.lower()), r.get("type", ""), r.get("category", ""))
        aud = f"{A2_AUDIO_DIR}/{k}.mp3"
        audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
        adj = is_adjective(r.get("gender", ""), r.get("fem", ""))
        # adjectives: no separate symbol pair; the symbols sit in the forms line
        gmark = "" if adj else gender_mark(r.get("gender", ""))
        if route in ("IMG", "PHRASE"):
            src = find_a2_image(k)
            if not src:
                counts["skipped_no_image"] += 1; continue
            img_path, img_name = media_image(k, src)
            target.add_note(genanki.Note(
                model=model, tags=tags, guid=genanki.guid_for(k), due=due,
                fields=[k, r["lithuanian_TARGET"], r["english"], gmark,
                        r.get("gen_sg", ""), r.get("pres3", ""), r.get("past3", ""),
                        adjective_forms(r["lithuanian_TARGET"], r.get("lt_pron", ""), r["fem"])
                        if adj else r.get("fem", ""),
                        plate_number(k), r.get("category", ""),
                        f'<img class="art" src="{img_name}">', audf, r.get("lt_pron", ""),
                        usage_for(k)]))
            media.append(img_path); counts["image"] += 1
        elif route in ("CLOZE", "PAIR"):
            text, n = cloze_text(r.get("example_lt", ""))
            if not n:
                counts["skipped_no_sentence"] += 1; continue
            saud = f"{A2_AUDIO_DIR}/{k}_s.mp3"          # the recorded example sentence
            saudf = f"[sound:{k}_s.mp3]" if os.path.exists(saud) else ""
            target.add_note(genanki.Note(
                model=cloze_model, tags=tags, guid=genanki.guid_for(k), due=due,
                fields=[text, r.get("example_en", ""), r["lithuanian_TARGET"], r.get("lt_pron", ""),
                        gmark, a2_forms(r), r["english"],
                        plate_number(k), r.get("category", ""), audf, k, saudf, "", usage_for(k)]))
            counts["cloze"] += 1
            if saudf:
                media.append(saud)
        else:
            continue
        if audf:
            media.append(aud)
    return counts


def add_sentence_notes(DECKS, media, order=None):
    """Picture + cloze sentence cards from SENTENCES (design: a2_build/sentences/design.md).
    Front: picture + Lithuanian sentence with the blank, no English; back adds the English.
    A sentence without a picture is still built (as a plain cloze with the English hint)."""
    counts = {"sentence": 0, "sentence_with_image": 0}
    if not SENTENCES or not os.path.exists(SENTENCES):
        return counts
    os.makedirs(TMP, exist_ok=True)
    order = order or {}
    for r in csv.DictReader(open(SENTENCES, encoding="utf-8")):
        k = r["id"]
        text, n = cloze_text(r["lt"])
        if not n:
            continue
        level = (r.get("level") or "A2").strip() or "A2"
        target = DECKS.get(level, DECKS["A2"])
        src = find_image(k, SENT_IMAGE_DIRS)
        img = ""
        if src:
            img_path, img_name = media_image(k, src)
            img = f'<img class="art" src="{img_name}">'; media.append(img_path)
            counts["sentence_with_image"] += 1
        aud = f"{A2_AUDIO_DIR}/{k}.mp3"
        audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
        if audf:
            media.append(aud)
        target.add_note(genanki.Note(
            model=cloze_model, tags=tags_for(level, "sentence", "", "Sakiniai"), guid=genanki.guid_for(k), due=order.get(k, 0),
            fields=[text, r["en"], "", "", "", "", r.get("grammar_point", ""),
                    plate_number(k), "Sakiniai", "", k, audf, img, usage_for(k)]))
        counts["sentence"] += 1
    return counts


REPORT_DIR = os.environ.get("REPORT_DIR", "build_reports")

# --- deck <-> spec <-> style linkage (spec 3.0.0, 2026-10-19; docs/DESIGN_SPEC_CURRENT.md §11) ----
# A build refuses to run when the code has drifted from style/STYLE_LOCK.json, so no package can
# ship an unrecorded look. GO_ALLOW_STYLE_DRIFT=1 overrides, and the drift is written into the
# build manifest (build_reports/builds/<package>.json) and the deck description.
_TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
import style_lock  # noqa: E402
import check_layout  # noqa: E402   (spec §13: warn, never block, when the working directory drifts from INDEX.md)


def git_commit():
    """Short commit of the working tree, '+dirty' when it has uncommitted changes; '' outside git."""
    import subprocess
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True,
                             check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True).stdout.strip()
        return sha + ("+dirty" if dirty else "")
    except Exception:
        return ""


def style_gate():
    """Run the style-lock check. Returns the stamp dict; exits on drift unless GO_ALLOW_STYLE_DRIFT=1."""
    ok, msg, live = style_lock.verify()
    lock = style_lock.load_lock() or {}
    drift = []
    if not ok:
        print(msg)
        if os.environ.get("GO_ALLOW_STYLE_DRIFT") != "1":
            raise SystemExit("build_apkg: refused — the code does not match style/STYLE_LOCK.json. "
                             "Release the spec and update the lock (docs/HOW_TO_CHANGE_THE_LOOK.md), "
                             "or set GO_ALLOW_STYLE_DRIFT=1 to build anyway (logged in the manifest).")
        changed, added, removed = style_lock.compare(live, lock) if lock else ([], list(live["items"]), [])
        drift = changed + added + removed
        print(f"WARNING: GO_ALLOW_STYLE_DRIFT=1 — building with {len(drift)} drifted style item(s); "
              f"this is recorded in the manifest and the deck description")
    import datetime
    return {
        "apkg_version": APKG_VERSION,
        "spec_version": style_lock.spec_version(),
        "style_hash": live["style_hash"],
        "style_hash_short": live["style_hash_short"],
        "style_lock_hash": lock.get("style_hash", ""),
        "style_drift": drift,
        "git_commit": git_commit(),
        "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
    }


def deck_description(stamp):
    d = (f"Lietuvių Flashcards v{stamp['apkg_version']} · design spec {stamp['spec_version']} · "
         f"style {stamp['style_hash_short']} · built {stamp['date'][:10]}"
         + (f" · {stamp['git_commit']}" if stamp["git_commit"] else ""))
    if stamp["style_drift"]:
        d += f" · STYLE DRIFT ALLOWED ({len(stamp['style_drift'])} items)"
    return d


def media_hash(files):
    """sha256 over the sorted media names and their content hashes (the package's picture/audio identity)."""
    h = hashlib.sha256()
    for p in sorted(set(files), key=os.path.basename):
        h.update(os.path.basename(p).encode("utf-8") + b"\0" + _sha1(p).encode() + b"\n")
    return h.hexdigest()


def write_manifest(out, stamp, counts, media, extra):
    os.makedirs(f"{REPORT_DIR}/builds", exist_ok=True)
    stem = os.path.splitext(os.path.basename(out))[0].replace("Lietuviu_Flashcards_", "")
    path = f"{REPORT_DIR}/builds/{stem}.json"
    doc = dict(stamp)
    doc.update({
        "package": os.path.basename(out),
        "package_sha256": hashlib.sha256(open(out, "rb").read()).hexdigest() if os.path.exists(out) else "",
        "levels": APKG_LEVELS, "frame": FRAME, "back": BACK_STYLE, "back_pic": BACK_PIC,
        "counts": counts, "media_files": len(media), "media_hash": media_hash(media),
        "description": deck_description(stamp),
    })
    doc.update(extra)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return path


def main(frame="standard", back=None, limit=0):
    """limit > 0: a smoke build of only the first `limit` A1 rows that have a picture (A2 and
    sentences still read their lists); for testing the stamp and manifest path without the media."""
    stamp = style_gate()
    for line in sum(check_layout.check(strict=False), []):
        print("layout:", line)
    set_frame(frame, back)
    FRAME_FLAGS.clear()
    os.makedirs(TMP, exist_ok=True)
    # 1.7.9 — one deck, split into CEFR subdecks. Studying the parent studies
    # everything; clicking A1 or A2 studies just that level. Cards also carry an
    # A1/A2 tag so custom filtered decks stay possible.
    DECKS = {
        "A1": genanki.Deck(2059400112, "Lietuvių Flashcards::A1", description=deck_description(stamp)),
        "A2": genanki.Deck(2059400113, "Lietuvių Flashcards::A2", description=deck_description(stamp)),
    }
    deck = DECKS["A1"]   # default for rows with no level set
    media = []
    order = load_study_order()
    skipped = []
    n_a1 = 0
    a1_pos = a1_types()
    for r in csv.DictReader(open("cards_anki.csv", encoding="utf-8")):
        k = r['key']; aud = f"{AUDIO_DIR}/{k}.mp3"
        if limit and n_a1 >= limit:
            break
        img_path, img_name = media_image(k)
        if not img_path:
            skipped.append(k); continue
        n_a1 += 1
        audf = f"[sound:{k}.mp3]" if os.path.exists(aud) else ""
        level = (r.get("level") or "A1").strip() or "A1"
        target = DECKS.get(level, DECKS["A1"])
        # adjectives (incl. the colours): "raudónas ♂ · raudona ♀" in the forms line,
        # no separate symbol pair; nouns, M/F job nouns and verbs as before
        adj = is_adjective(r['gender'], r['fem'])
        gmark = "" if adj else gender_mark(r['gender'])
        fem = adjective_forms(r['lithuanian'], r.get('pron', ''), r['fem']) if adj else r['fem']
        target.add_note(genanki.Note(
            model=model,
            tags=tags_for(level, "picture", a1_pos.get(k, ""), r['category']),
            # STABLE identity: guid derived from the card key, never random, so
            # re-importing an updated deck updates cards in place (keeps study
            # history / scheduling) instead of creating duplicates.
            guid=genanki.guid_for(k), due=order.get(k, 0),
            fields=[k, r['lithuanian'], r['english'], gmark, r['gen_sg'],
                    r['pres3'], r['past3'], fem, plate_number(k), r['category'],
                    f'<img class="art" src="{img_name}">', audf, r.get('pron', ''), usage_for(k)]))
        media.append(img_path)
        if os.path.exists(aud):
            media.append(aud)

    a2_counts = add_a2_notes(DECKS, media, order)
    s_counts = add_sentence_notes(DECKS, media, order)

    unknown = [l for l in APKG_LEVELS if l not in DECKS]
    if unknown:
        raise SystemExit(f"APKG_LEVELS: unknown level(s) {unknown}; known: {list(DECKS)}")
    built = {lv: d for lv, d in DECKS.items() if lv in APKG_LEVELS}
    if len(built) < len(DECKS):
        import re
        used = set()
        for d in built.values():
            for n in d.notes:
                for f in n.fields:
                    used.update(re.findall(r'src="([^"]+)"', f))
                    used.update(re.findall(r'\[sound:([^\]]+)\]', f))
        media = [m for m in media if os.path.basename(m) in used]
    if FRAME == "standard":
        # the fonts are referenced only from the CSS (leading underscore: Anki keeps them)
        media += [f for f in card_frame.font_media() if f not in media]
        n_flag = frame_crop.write_reports(FRAME_FLAGS, REPORT_DIR)
        cats = [(n.fields[9], n.tags) for d in built.values() for n in d.notes if n.model is model] + \
               [(n.fields[8], n.tags) for d in built.values() for n in d.notes if n.model is cloze_model]
        missing = card_frame.unmapped(cats)
        print(f"standard frame: {len(FRAME_FLAGS)} pictures cropped, {n_flag} flagged "
              f"(fixed-percentage fallback) -> {REPORT_DIR}/frame_flags.csv")
        if missing:
            print(f"  categories without a section in card_frame.SECTIONS (shown as is): {missing}")
    out = versioned_out(APKG_OUT)
    pkg = genanki.Package(list(built.values())); pkg.media_files = media
    pkg.write_to_file(out)
    counts = {lv: len(d.notes) for lv, d in built.items()}
    print(f"built {out} — {len(media)} media files | subdecks: {counts} | "
          f"A1 rows without image: {len(skipped)} | A2 list: {a2_counts} | sentences: {s_counts} | "
          f"study order: {len(order)} positions | usage notes: {len(USAGE_USED)} of {len(USAGE)}")
    manifest = write_manifest(out, stamp, counts, media, {
        "a1_rows_without_image": len(skipped), "a2": a2_counts, "sentences": s_counts,
        "study_order_positions": len(order), "usage_notes": len(USAGE_USED),
        "frame_flagged": n_flag if FRAME == "standard" else None, "smoke_limit": limit or None,
    })
    print(f"manifest {manifest} | spec {stamp['spec_version']} | style {stamp['style_hash_short']} | "
          f"{stamp['git_commit']}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Build the Lietuvių Flashcards .apkg")
    ap.add_argument("--frame", choices=["standard", "drawn"], default="standard",
                    help="standard: trim the drawn frame off copies of the pictures and redraw "
                         "it in CSS at one fixed width (default, v2.1); drawn: the pictures' "
                         "own frame and the v2.0 templates")
    ap.add_argument("--back", choices=["proposed", "current"], default=None,
                    help="standard frame only: proposed = the redesigned back with a thumbnail (default, "
                         "owner 2026-10-18); current = the previous standard back")
    ap.add_argument("--limit", type=int, default=0,
                    help="smoke build: only the first N A1 picture rows (tests the stamp/manifest path)")
    a = ap.parse_args()
    main(a.frame, a.back, a.limit)
