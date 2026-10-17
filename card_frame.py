#!/usr/bin/env python3
"""The "standard bands" card frame: note-type templates, CSS and section labels.

build_apkg.py --frame standard (the default) uses this module; --frame drawn keeps the
pictures' own drawn frame and the old templates. The look is anki/frame_standard.css
(appended to anki/go_theme.css); the pictures are cropped by frame_crop.py.

Nothing here changes a note type's FIELDS (that would break updating in place on
re-import): the section label is worked out in CSS from the note's existing Category
field and its tags, via attribute selectors generated from SECTIONS below.

SECTIONS is the one place to edit the running heads. Each entry: numeral, English label
(shown in small caps), and the Category values (A1 cards_anki.csv / A2 a2_wordlist.csv /
sentences) it covers. ROUTE_SECTIONS overrides by note tag: every PHRASE-route note is a
phrase whatever its category, every sentence card (tag SENT) a sentence. A category
missing from SECTIONS is shown as it is (build_apkg prints a warning listing them).
"""
import os

SECTIONS = [
    ("I", "people", ["People", "Nationalities", "Languages"]),
    ("II", "animals", ["Animal"]),
    ("III", "places", ["Location", "Travel"]),
    ("IV", "transport", ["Transportation"]),
    ("V", "home", ["Home", "Electronics", "Technology"]),
    ("VI", "food", ["Food", "Beverages"]),
    ("VII", "clothing", ["Clothing"]),
    ("VIII", "body & health", ["Body", "Health"]),
    ("IX", "nature", ["Nature"]),
    ("X", "work & school", ["Job", "Jobs", "Work & school", "Work & culture"]),
    ("XI", "society", ["Society", "Money & admin", "Shopping", "Art"]),
    ("XII", "colours & materials", ["Color", "Materials"]),
    ("XIII", "numbers & time", ["Numbers", "Math", "Time"]),
    ("XIV", "actions", ["Verbs", "Modal & core verbs"]),
    ("XV", "qualities", ["Adjectives"]),
    ("XVI", "things & ideas", ["Nouns", "Abstract", "Misc"]),
    ("XVII", "feelings & opinions", ["Feelings", "Opinion & discourse"]),
    ("XVIII", "small words", ["Pronouns", "Question words", "Prepositions", "Conjunctions", "Adverbs"]),
    ("XIX", "phrases", ["Phrases", "Greetings", "Politeness", "Basics", "Getting by", "Formulas",
                        "Transactions", "Core patterns", "Extended patterns"]),
    ("XX", "sentences", ["Sakiniai"]),
]
ROUTE_SECTIONS = {"PHRASE": "XIX", "SENT": "XX"}     # note tag -> numeral

FONT_FILES = ["_PTSerif-Regular.ttf", "_PTSerif-Italic.ttf", "_PTSerif-Bold.ttf",
              "_OldStandardTT-Regular.ttf"]
FONT_DIR = "fonts"

# TODO(owner decision): the deck has three plate numberings -- A1 "1".."531", A2 "0001"
# (from the A2-xxxx key) and sentences "S 0001" -- shown as "pav. N" in the bottom band.
# Unifying them is out of scope for the frame change and awaits the owner's decision
# (see a2_build/BACKS_AUDIT.md item 10). The Number fields are used as they are.


def _css_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def section_of(category, tags=()):
    """(numeral, label) for a note, or None if unmapped; mirrors the generated CSS."""
    by_num = {n: (n, lab) for n, lab, _ in SECTIONS}
    for t in tags:
        if t in ROUTE_SECTIONS:
            return by_num[ROUTE_SECTIONS[t]]
    for n, lab, cats in SECTIONS:
        if category in cats:
            return (n, lab)
    return None


def section_css():
    """Attribute-selector rules that print 'Section N ·' and the label in the top band."""
    out = ["/* --- section labels, generated from card_frame.SECTIONS --- */"]
    by_num = {n: lab for n, lab, _ in SECTIONS}
    for n, lab, cats in SECTIONS:
        for c in cats:
            sel = f'.sf-sec[data-cat={_css_str(c)}]'
            out.append(f'{sel}::before{{content:{_css_str(f"Section {n} ·")}}}'
                       f'{sel}::after{{content:{_css_str(lab)}}}')
    for tag, n in ROUTE_SECTIONS.items():
        sel = f'.sf[data-tags~={_css_str(tag)}] .sf-sec'
        out.append(f'{sel}::before{{content:{_css_str(f"Section {n} ·")}}}'
                   f'{sel}::after{{content:{_css_str(by_num[n])}}}')
    return "\n".join(out) + "\n"


def standard_css(base_css):
    here = os.path.dirname(os.path.abspath(__file__))
    frame = open(os.path.join(here, "anki", "frame_standard.css"), encoding="utf-8").read()
    return base_css + "\n" + frame + "\n" + section_css()


def font_media():
    here = os.path.dirname(os.path.abspath(__file__))
    return [os.path.join(here, FONT_DIR, f) for f in FONT_FILES]


# Caption fit: shrink a long English caption to fit one line (down to 72 % of its size),
# else let it wrap to two smaller lines (.sf-wrap, clamped to two). Re-runs once the embedded
# fonts have loaded and on resize. Without JS the caption ends in an ellipsis.
FIT_JS = """<script>
(function () {
  function px(v) { v = parseFloat(v); return isNaN(v) ? 0 : v; }
  function fit() {
    var els = document.querySelectorAll('.sf-en');
    for (var i = 0; i < els.length; i++) {
      var e = els[i], band = e.parentNode;
      e.classList.remove('sf-wrap'); e.style.fontSize = '';
      var cs = getComputedStyle(band), gap = px(cs.columnGap);
      // room for the caption: the band minus its padding, the plate number, the
      // leader at its minimum width and the gaps
      var avail = band.clientWidth - px(cs.paddingLeft) - px(cs.paddingRight);
      for (var j = 0; j < band.children.length; j++) {
        var c = band.children[j];
        if (c === e) continue;
        avail -= gap + (c.className.indexOf('sf-lead') >= 0 ? px(getComputedStyle(c).minWidth)
                                                            : c.getBoundingClientRect().width);
      }
      // the caption's natural one-line width (fractional, unlike scrollWidth)
      e.style.flex = 'none'; e.style.maxWidth = 'none';
      var w = e.getBoundingClientRect().width;
      e.style.flex = ''; e.style.maxWidth = '';
      if (!w || w <= avail - 1) continue;
      var s = px(getComputedStyle(e).fontSize), ns = s * (avail - 2) / w;
      if (ns >= s * 0.72) e.style.fontSize = ns + 'px';
      else e.classList.add('sf-wrap');
    }
  }
  window.__sfFit = fit;
  if (!window.__sfFitBound) {
    window.__sfFitBound = true;
    window.addEventListener('resize', function () { window.__sfFit && window.__sfFit(); });
  }
  fit();
  setTimeout(fit, 60);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
})();
</script>"""


def _frame(cat, num, cap, pic):
    return ('<div class="sf" data-tags="{{Tags}}">'
            f'<div class="sf-top"><span class="sf-sec" data-cat="{{{{text:{cat}}}}}"></span></div>'
            f'{pic}'
            f'<div class="sf-bot"><span class="sf-pav">pav. {{{{{num}}}}}</span>'
            f'<span class="sf-lead"></span><span class="sf-en">{{{{{cap}}}}}</span></div>'
            '</div>')


# --- picture note ("Lietuvių GO"): A1/A2 pictures and A2 phrases ----------------------
_PIC_FRAME = _frame("category", "number", "english", '<div class="sf-pic">{{image}}</div>')
FRONT = f'<div class="sf-card">{_PIC_FRAME}</div>{FIT_JS}'
BACK = (f'<div class="sf-card">{_PIC_FRAME}'
        '<div class="answer"><div class="word">{{lithuanian}}</div>'
        '{{#pron}}<div class="pron">{{pron}}</div>{{/pron}}{{audio}}'
        '{{#gender}}<div class="gender">{{gender}}</div>{{/gender}}'
        '{{#gen_sg}}<div class="forms">{{lithuanian}} · {{gen_sg}}</div>{{/gen_sg}}'
        '{{#pres3}}<div class="forms">{{lithuanian}} · {{pres3}} · {{past3}}</div>{{/pres3}}'
        '{{#fem}}<div class="forms">{{lithuanian}} · {{fem}}</div>{{/fem}}'
        '<hr id="answer"><div class="gloss">{{english}}</div></div>'
        f'</div>{FIT_JS}')

# --- cloze note ("Lietuvių GO Cloze"): A2 cloze/pair rows and sentence cards ----------
# With a picture (sentence cards) the sentence sits under the frame; without one it sits
# on a paper panel inside the frame. The caption is the target word's English gloss
# (hidden on sentence cards by CSS, whose Gloss field holds the grammar point).
_CLOZE_PIC = ('{{#Image}}<div class="sf-pic">{{Image}}</div>{{/Image}}'
              '{{^Image}}<div class="sf-panel"><div class="cloze-text">{{cloze:Text}}</div>'
              '<div class="hint">{{SentenceEN}}</div></div>{{/Image}}')
_CLOZE_FRAME = _frame("Category", "Number", "Gloss", _CLOZE_PIC)
CLOZE_FRONT = (f'<div class="sf-card">{_CLOZE_FRAME}'
               '{{#Image}}<div class="cloze-text">{{cloze:Text}}</div>{{/Image}}'
               f'</div>{FIT_JS}')
CLOZE_BACK = (f'<div class="sf-card">{_CLOZE_FRAME}'
              '{{#Image}}<div class="cloze-text">{{cloze:Text}}</div>'
              '<div class="hint">{{SentenceEN}}</div>{{/Image}}'
              '<div class="answer word-line"><div class="word">{{Word}}</div>'
              '{{#Pron}}<div class="pron">{{Pron}}</div>{{/Pron}}{{Audio}}{{SentenceAudio}}'
              '{{#Gender}}<div class="gender">{{Gender}}</div>{{/Gender}}'
              '{{#Forms}}<div class="forms">{{Forms}}</div>{{/Forms}}'
              '<hr id="answer"><div class="gloss">{{Gloss}}</div></div>'
              f'</div>{FIT_JS}')


def unmapped(categories_with_tags):
    """[(category, tags)] -> sorted categories that no section covers."""
    return sorted({c for c, t in categories_with_tags if c and section_of(c, t) is None})


if __name__ == "__main__":
    print(section_css())
