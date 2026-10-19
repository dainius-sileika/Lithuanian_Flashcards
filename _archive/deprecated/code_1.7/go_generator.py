#!/usr/bin/env python3
"""
Grazhdanskaya Oborona Generator  (GO-Gen)  —  files 1.6.1
=========================================================
Reusable engine for late-Soviet civil-defense INSTRUCTIONAL WALL CHART art.

Governing principle (the north star we JUDGE against): **deadpan civic
procedure** — a technical educational wall chart, not agitprop.

1.6.1: single-glyph exception (decision Q2): glyph=True permits ONLY the one
     large letterform that IS the subject, keeps the red bars and every other
     text prohibition. Used by exactly three cards (letter/consonant/vowel).

1.6: hardening for the mass run. (a) OpenAI path now retries transient errors
     (rate limits, timeouts, 5xx) with exponential backoff — content-policy or
     auth errors still fail fast. (b) cards.csv schema carries lt_pron and
     gender so the Anki layer is fed in one pass. Prompts UNCHANGED — the
     locked 1.5.1 style renders byte-identically.

1.1: stripped the legacy supporting-label machinery from the app layer and
     from cards.csv (labels were for baked-in image text, dropped in 0.7). The
     engine keeps its optional text=True path for reuse in other projects.

1.0: styling locked. Engine unchanged from 0.9; the 1.0 change lives in the
     verb app — floating institutional main scene (context C) with an optional
     per-verb consequence inset (accent D). Nouns unchanged.

0.9 changes vs 0.8:
  - SYMBOLS: flag-only and OCCASIONAL. Intricate heraldry (Vytis, Columns of
    Gediminas, Vytis Cross, Šauliai) rendered as garble — same failure mode as
    text. Now: at most a small Lithuanian tricolor, only where it fits, and NOT
    on every card. No coats of arms or emblems.
  - light ANATOMY steer (five-finger hands, clean paws/feet) — reduces the
    extra-finger / distorted-paw rate (can't be eliminated; re-roll the rest)
  - period-correct black kirza-style work boots (black was standard issue;
    brown was the officer/long-service exception)

0.8: flat workers' caps; anatomical cutaways banned; verbs hard-capped at 2 insets.
0.7: text removed from the image; empty red bars; blue coveralls; cards.csv.

DUAL BACKEND — verbosity is inversely proportional to model competence:
  backend="openai" (default): gpt-image-1.5, quality "medium". Concept-forward.
  backend="zimage" (fallback): Z-Image-Turbo. Decomposed clause. Seeds recorded.

SETUP (keys live in YOUR environment, never in code or chat):
  OpenAI:  export OPENAI_API_KEY=sk-...   ; pip install openai
  Z-Image: export HF_TOKEN=hf_...         ; pip install gradio_client
"""
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

NO_TEXT_RULE = (
    "Render NO text, NO lettering, NO numbers, NO words, NO labels and NO "
    "captions anywhere in the image — no leader-line labels, no writing in any "
    "panel, on any flag, sign, or object, and none in the header or footer "
    "bands. Any area that would normally hold text must be left completely blank."
)
GLYPH_RULE = (
    "The ONLY lettering permitted is the one single large letter that is "
    "itself the subject of this card, drawn once as a bold display letterform. "
    "Render NO other text, lettering, numbers, words, labels or captions "
    "anywhere else in the image, and none in the header or footer bands."
)
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
                   glyph=False):
    segs = [CONCEPT_LEAD, f"Subject: {subject}."]
    if scene:
        segs.append(scene)
    segs.append(FIGURE_DRESS.get(people, FIGURE_DRESS["worker"]))
    segs.append(NO_STRAY_FIGURE)
    if insets:
        segs.append(inset_note if inset_note else INSET_RULE)
        segs.append(NO_CUTAWAY_RULE)
    if glyph:
        segs.append(GLYPH_RULE)
        segs.append(BARS_RULE)
    elif text:
        lc = _label_clause(labels, exclude)
        if lc:
            segs.append(lc)
    else:
        segs.append(NO_TEXT_RULE)
        segs.append(BARS_RULE)
    segs.append(FLAG_RULE)
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
    "clean technical textbook illustration with confident black outlines and "
    "flat matte shading, deadpan instructional calm, ordinary worker figures in "
    "plain muted blue-grey coveralls, soft flat cloth caps and black work boots, "
    "muted institutional palette of cream, blue-grey, olive, grey and brown, "
    "four-color offset print feel with faint halftone dots and aged paper "
    "texture, matte finish")
_Z_NEGATIVE = ("no readable text, no lettering, no captions, no watermark, no "
               "coats of arms or heraldic emblems, no anatomical cutaways, no "
               "glossy oil painting, no vibrant saturated color")
DEFAULT_OVERLAYS = ["a circular zoom-in detail inset"]
MOTION_ARROW = "a single bold directional arrow showing the direction of travel"


def _prompt_zimage(subject, scene="", overlays=None, extra=""):
    if overlays is None:
        overlays = DEFAULT_OVERLAYS
    parts = [_Z_LEAD_IN.format(SUBJECT=subject)]
    if scene:
        parts.append(scene)
    if overlays:
        parts.append("with diagrammatic overlays: " + ", ".join(overlays))
    parts.append(_Z_STYLE)
    if extra:
        parts.append(extra)
    parts.append(_Z_NEGATIVE)
    return ", ".join(parts)


def build_prompt(subject, scene="", labels=None, exclude="", insets=True,
                 inset_note="", text=False, people="worker", overlays=None,
                 glyph=False,
                 extra="", backend="openai"):
    if backend == "openai":
        return _prompt_openai(subject, scene, labels, exclude, insets,
                              inset_note, text, people, extra, glyph=glyph)
    return _prompt_zimage(subject, scene, overlays, extra)


OPENAI_SIZES = {"1:1": "1024x1024", "3:4": "1024x1536", "4:3": "1536x1024"}
ZIMAGE_RES   = {"1:1": "1024x1024 ( 1:1 )", "3:4": "864x1152 ( 3:4 )"}

OPENAI_MODEL = "gpt-image-1.5"
OPENAI_QUALITY = "medium"
ZIMAGE_SPACE = "mcp-tools/Z-Image-Turbo"
ZIMAGE_STEPS = 8


class GOGenerator:
    def __init__(self, backend="openai", ratio="4:3", quality=OPENAI_QUALITY,
                 steps=ZIMAGE_STEPS, verbose=True):
        self.backend = backend
        self.ratio = ratio
        self.quality = quality
        self.steps = steps
        self.verbose = verbose
        if backend == "openai":
            from openai import OpenAI
            if not os.environ.get("OPENAI_API_KEY") and verbose:
                print("WARNING: no OPENAI_API_KEY in environment. See SETUP.")
            self._client = OpenAI()
            self.size = OPENAI_SIZES.get(ratio, "1536x1024")
        elif backend == "zimage":
            from gradio_client import Client
            token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            if token:
                import inspect
                params = inspect.signature(Client.__init__).parameters
                kw = "token" if "token" in params else "hf_token"
                self._client = Client(ZIMAGE_SPACE, **{kw: token})
            else:
                if verbose:
                    print("WARNING: no HF_TOKEN — anonymous quota throttles fast.")
                self._client = Client(ZIMAGE_SPACE)
            self.size = ZIMAGE_RES.get(ratio, "864x1152 ( 3:4 )")
        else:
            raise ValueError(f"unknown backend: {backend}")

    def _gen_openai(self, prompt, dest, tries=5, wait=20):
        """Retry transient failures (rate limit / timeout / 5xx) with
        exponential backoff; anything else (auth, content policy) fails fast."""
        for i in range(tries):
            try:
                resp = self._client.images.generate(
                    model=OPENAI_MODEL, prompt=prompt, size=self.size,
                    quality=self.quality, n=1)
                with open(dest, "wb") as fh:
                    fh.write(base64.b64decode(resp.data[0].b64_json))
                return None
            except Exception as e:
                name = type(e).__name__
                transient = (any(k in name for k in
                                 ("RateLimit", "Timeout", "APIConnection",
                                  "InternalServer", "APIStatus"))
                             or any(c in str(e) for c in ("429", "500", "502",
                                                          "503", "504")))
                if transient and i < tries - 1:
                    delay = wait * (2 ** i)
                    if self.verbose:
                        print(f"   transient {name}, retrying in {delay}s "
                              f"({i+1}/{tries})")
                    time.sleep(delay)
                else:
                    raise

    def _gen_zimage(self, prompt, dest, tries=6, wait=45):
        from gradio_client.exceptions import AppError
        for i in range(tries):
            try:
                result, seed_msg = self._client.predict(
                    prompt=prompt, resolution=self.size, steps=self.steps,
                    random_seed=True, api_name="/generate")
                shutil.copy(result, dest)
                return "".join(c for c in str(seed_msg) if c.isdigit())
            except AppError as e:
                if "quota" in str(e).lower() and i < tries - 1:
                    if self.verbose:
                        print(f"   quota hit, waiting {wait}s ({i+1}/{tries})")
                    time.sleep(wait)
                else:
                    raise
        raise RuntimeError("retries exhausted")

    def generate(self, subject, scene="", labels=None, exclude="", insets=True,
                 inset_note="", text=False, people="worker", overlays=None,
                 glyph=False,
                 extra="", out_dir=".", filename=None):
        prompt = build_prompt(subject, scene=scene, labels=labels,
                              exclude=exclude, insets=insets, inset_note=inset_note,
                              text=text, people=people, overlays=overlays,
                              glyph=glyph, extra=extra, backend=self.backend)
        os.makedirs(out_dir, exist_ok=True)
        if filename is None:
            filename = "go_" + hashlib.md5(subject.encode()).hexdigest()[:8] + ".png"
        dest = os.path.join(out_dir, filename)
        seed = (self._gen_openai(prompt, dest) if self.backend == "openai"
                else self._gen_zimage(prompt, dest))
        if self.verbose:
            print(f"OK  {filename}  seed={seed or 'n/a'}")
        return dest, seed, prompt

    @staticmethod
    def open_ledger(path):
        new = not os.path.exists(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        f = open(path, "a", newline="")
        w = csv.writer(f)
        if new:
            w.writerow(["key", "subject", "seed", "backend", "size", "file", "prompt"])
        return f, w

    @staticmethod
    def open_cards(path):
        new = not os.path.exists(path)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        f = open(path, "a", newline="")
        w = csv.writer(f)
        if new:
            w.writerow(["key", "lithuanian", "english", "lt_pron", "gender",
                        "number", "category", "image_file"])
        return f, w


def _cli():
    p = argparse.ArgumentParser(description="Grazhdanskaya Oborona Generator")
    p.add_argument("subject")
    p.add_argument("--backend", default="openai", choices=["openai", "zimage"])
    p.add_argument("--scene", default="")
    p.add_argument("--ratio", default="4:3")
    p.add_argument("--text", action="store_true", help="bake text (default off)")
    p.add_argument("--out", default="./go_out")
    a = p.parse_args()
    gen = GOGenerator(backend=a.backend, ratio=a.ratio)
    dest, seed, prompt = gen.generate(a.subject, scene=a.scene, text=a.text,
                                      out_dir=a.out)
    f, w = GOGenerator.open_ledger(os.path.join(a.out, "ledger.csv"))
    w.writerow(["cli", a.subject, seed, a.backend, gen.size,
                os.path.basename(dest), prompt]); f.close()
    print(f"\nsaved -> {dest}")


if __name__ == "__main__":
    _cli()
