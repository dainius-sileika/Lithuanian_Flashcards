from __future__ import annotations
import os, sys, csv, time, shutil, argparse, hashlib, base64

# ===========================================================================
# CONCEPT-FORWARD encoding (backend="openai")
# ===========================================================================
CONCEPT_LEAD = (
    "An illustration for a Lithuanian-language learning flashcard, in the style "
    "of a late Soviet instructional wall chart / civil-defense (Grazhdanskaya "
    "Oborona) training poster, circa 1975-1985. This is an educational technical "
    "wall chart, NOT propaganda and NOT a political poster: clean technical "
    "textbook illustration (between a botanical plate and an engineering manual), "
    "realistic proportions, clean outlines, muted printing colors, deadpan "
    "instructional calm, a structured grid layout with generous white space and "
    "an aged cream-paper offset-print feel. Where people appear they are "
    "ordinary Soviet-era Lithuanian people with neutral expressions and no "
    "heroic posing, in a period late-1970s setting."
)

# --- people & dress classes (1.3): coveralls are no longer forced on everyone ---
FIGURE_DRESS = {
    "worker": (
        "Any people who appear are ordinary workers in plain muted blue-grey "
        "civil-defense coveralls, soft flat-topped cloth workers' caps (the "
        "Lenin-style flat cap) or bareheaded, and black kirza-style work boots."),
    "professional": (
        "Any people who appear are dressed for their profession and setting — a "
        "doctor or nurse in a white medical coat, a teacher in a modest 1970s "
        "jacket or dress, a uniformed officer in service uniform — and NOT in "
        "workers' coveralls."),
    "civilian": (
        "Any people who appear are ordinary Soviet-era Lithuanian civilians in "
        "plain everyday late-1970s clothes — a simple shirt, jacket, dress, or "
        "headscarf — and NOT workers' coveralls or a uniform."),
}
# guard against the model inventing a stray standing figure on object/place cards
NO_STRAY_FIGURE = ("Only include people the subject or scene actually calls for; "
                   "do not add an extra standing figure that is not needed.")

INSET_RULE = (
    "Include just 2 to 3 small supporting inset panels — external close-up "
    "details or a small civic scene of ordinary people — kept clean and "
    "uncluttered. Do not overcrowd the card."
)

# 1.7.1: the guessability gate, baked into the prompt so it holds at generation
# time instead of only at human QA. Applied whenever insets are present.
INSET_MEANING_RULE = (
    "Every inset must serve the meaning of THIS card: at best it should make the "
    "main subject easier to recognise; at the least it must stay attractive and "
    "on-theme. An inset must NEVER depict something that could be mistaken for a "
    "different, neighbouring subject, and must never compete with or pull "
    "attention away from what the card is teaching."
)

NO_CUTAWAY_RULE = (
    "Do NOT include internal anatomical cutaways or cross-sections of bodies — "
    "no organs, no digestive tracts, no bone interiors, no skin-layer diagrams, "
    "no udder or muscle interiors. Use external close-up details instead. "
    "(A simple sliced view of a fruit or plain object is fine.)"
)

ANATOMY_RULE = (
    "Render any human hands with clean, natural anatomy and exactly five "
    "fingers, and render animal paws, hooves and feet cleanly and correctly — "
    "no extra or malformed fingers or toes."
)

# 0.9: flag-only, occasional. No intricate heraldry (it garbles like text did).
FLAG_RULE = (
    "If any national emblem is shown at all, use ONLY a small Lithuanian "
    "tricolor flag (a horizontal yellow band on top, green in the middle, red "
    "on the bottom), placed small and only where it fits naturally. Do NOT "
    "include coats of arms, the Vytis knight, the Columns of Gediminas, or any "
    "other heraldic emblem or badge. Do not put a flag on every card — many "
    "cards need no emblem at all."
)

# 1.7.4: flag variants for measurement cards (metric -> EU, imperial -> US+UK).
FLAG_RULE_EU = (
    "If any flags appear, use ONLY a small Lithuanian tricolor (yellow top, "
    "green middle, red bottom) together with a small European Union flag (a ring "
    "of twelve gold stars on a blue field), side by side. No coats of arms, no "
    "other emblems.")
FLAG_RULE_IMPERIAL = (
    "If any flags appear, use ONLY a small United States flag (stars and stripes) "
    "together with a small United Kingdom Union Jack, side by side. No coats of "
    "arms, no other national flags.")
FLAG_RULES = {"eu": FLAG_RULE_EU, "imperial": FLAG_RULE_IMPERIAL}

NO_TEXT_RULE = (
    "Render NO text, NO lettering, NO numbers, NO words, NO labels and NO "
    "captions anywhere in the image — no leader-line labels, no writing in any "
    "panel, on any flag, sign, or object, and none in the header or footer "
    "bands. Any area that would normally hold text must be left completely blank. "
    "This applies with full force inside speech bubbles and thought balloons: a "
    "bubble may contain a drawn picture or symbol, but never a written word, "
    "letter, or punctuation mark in any language."
)
GLYPH_RULE = (
    "The ONLY lettering permitted is the one single large letter that is "
    "itself the subject of this card, drawn once as a bold display letterform. "
    "Render NO other text, lettering, numbers, words, labels or captions "
    "anywhere else in the image, and none in the header or footer bands."
)
def _exact_text_rule(spec, exclude=""):
    """1.7.7 text exception. A few cards are unteachable without a little
    lettering (unit marks on a ruler, ABC/123 on a blackboard, a price, a
    masthead, the vowel set). This permits EXACTLY the specified lettering and
    nothing else — the no-text rule still governs the rest of the card.

    1.9.0: the spec must be UNCONDITIONAL. Phrasing like "a question mark only
    if the phrase is a question" was silently ignored by the model, which drew
    the mark on all nine non-question cards. The caller decides; the prompt only
    ever states what to draw. The exclusion clause is also carried here — it
    previously reached the labelled branch only, so cards using a text exception
    had nothing stopping the target word from being written into the art."""
    segs = ["TEXT EXCEPTION for this card: the only lettering permitted "
            f"anywhere in the image is {spec} Draw it cleanly and correctly "
            "spelled in the muted period print style, large enough to read. "
            "Render NO other text, lettering, numbers, words, labels or "
            "captions anywhere else in the image — no leader-line labels, no "
            "writing on any other object, sign or flag — and none in the "
            "header or footer bands."]
    if exclude:
        segs.append(f"Absolutely never write the word \"{exclude}\", any part "
                    "of it, its translation, or any other Lithuanian or English "
                    "word anywhere in the image. Speech bubbles must stay free "
                    "of words in every language.")
    return " ".join(segs)


BARS_RULE = (
    "Frame the card with a plain solid dark-red horizontal band across the very "
    "top and another across the very bottom, plus a thin dark-red border around "
    "the whole card. These bands are blank design elements and must contain no "
    "text whatsoever. Keep ALL illustration content — every figure, object, and "
    "inset panel — fully inside the inner frame; nothing may overlap, touch, or "
    "extend across the red header or footer bands."
)


def _label_clause(labels, exclude=""):
    segs = []
    if labels:
        words = labels if isinstance(labels, str) else ", ".join(labels)
        segs.append("Annotate with thin leader lines labeling ONLY these "
                    f"supporting Lithuanian words, spelled exactly as given, and "
                    f"NO other text at all: {words}.")
    if exclude:
        segs.append(f"Never write the target word \"{exclude}\" or its "
                    "translation anywhere.")
    return " ".join(segs)


def _prompt_openai(subject, scene="", labels=None, exclude="", insets=True,
                   inset_note="", text=False, people="worker", extra="",
                   glyph=False, flag="lt", exact_text=""):
    segs = [CONCEPT_LEAD, f"Subject: {subject}."]
    if scene:
        segs.append(scene)
    segs.append(FIGURE_DRESS.get(people, FIGURE_DRESS["worker"]))
    segs.append(NO_STRAY_FIGURE)
    if insets:
        segs.append(inset_note if inset_note else INSET_RULE)
        segs.append(INSET_MEANING_RULE)
        segs.append(NO_CUTAWAY_RULE)
    if glyph:
        segs.append(GLYPH_RULE)
        segs.append(BARS_RULE)
    elif exact_text:
        segs.append(_exact_text_rule(exact_text, exclude))
        segs.append(BARS_RULE)
    elif text:
        lc = _label_clause(labels, exclude)
        if lc:
            segs.append(lc)
    else:
        # Wordless cards deliberately do NOT name the target word: naming a
        # forbidden thing primes it, and NO_TEXT_RULE already bans all lettering.
        # `exclude` therefore only reaches the branches that permit some text.
        segs.append(NO_TEXT_RULE)
        segs.append(BARS_RULE)
    segs.append(FLAG_RULES.get(flag, FLAG_RULE))
    segs.append(ANATOMY_RULE)
    if extra:
        segs.append(extra)
    return " ".join(segs)


# ===========================================================================
# DECOMPOSED encoding (backend="zimage") — text-incapable fallback
# ===========================================================================
_Z_LEAD_IN = ("1970s Soviet civil defense grazhdanskaya oborona instructional "
              "wall chart illustration of {SUBJECT}")
_Z_STYLE = (
