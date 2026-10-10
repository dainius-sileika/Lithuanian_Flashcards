import json

# ---------------------------------------------------------------- prompts
F4_lead = (
"A printed page from a 1981 Lithuanian civil-defence training album, drawn and printed like the Soviet "
"Grazhdanskaya Oborona wall charts of 1975-1985: a dark-brown brush-and-ink outline around every figure "
"and object, thin matte gouache fills with one soft shadow tone, four-colour offset lithography with a "
"faint coarse halftone, muted inks of dusty blue, olive, ochre, brick red and grey-brown on "
"pale bright cream paper. The pale cream paper itself is the background and the sky: the main subject is "
"drawn as a cut-out vignette directly on it, its ground fading to a soft edge, with wide empty "
"margins; insets are small ruled boxes on the same paper. Flat even diagram lighting. People are "
"ordinary Soviet-era Lithuanians of 1981, anonymous types: broad plain faces, "
"heavy features, closed mouths and a level direct gaze; sturdy thick-set bodies; men's hair short, combed "
"flat and side-parted, women's short and practical or under a cotton headscarf; cheap loosely cut "
"state-made clothes in brown, olive, dusty blue, grey and dull red; every movement one stiff held position."
)
F4_suffix = (
"Finish: flat muted offset print on pale bright cream paper, brush-ink outlines, plain sturdy Soviet-era "
"people, the subject floating on bare paper with wide margins."
)

F4dun_lead = (F4_lead
    .replace("on pale bright cream paper", "on dun, yellowed cream paper")
    .replace("The pale cream paper itself", "The dun paper itself"))
F4dun_suffix = F4_suffix.replace("pale bright cream paper", "dun, yellowed cream paper")

F4bleed_lead = F4_lead.replace(
    "The pale cream paper itself is the background and the sky: the main subject is drawn as a cut-out "
    "vignette directly on it, its ground fading to a soft edge, with wide empty margins; insets "
    "are small ruled boxes on the same paper.",
    "The main scene fills its whole panel edge to edge as a complete picture with its own sky, ground and "
    "background; insets are small ruled boxes beside or below it.")
F4bleed_suffix = F4_suffix.replace(
    "the subject floating on bare paper with wide margins.",
    "the main scene filling its panel edge to edge.")

F4arrow_suffix = F4_suffix + " All diagram arrows, motion lines and callout marks are drawn in solid black ink."

assert F4bleed_lead != F4_lead and F4dun_lead != F4_lead

new_prompts = {
 "F4": {"lead": F4_lead, "suffix": F4_suffix,
        "notes": "The predicted splice: F2 print-production paragraph + F3 people block, trimmed. Paper stated as PALE BRIGHT cream (all F1-F3 output came out darker/dun than 1.5). Composition stated as cut-out vignette with the paper as sky, to push Sunburst off full-bleed. Default production candidate; everything else is a one-attribute edit of it."},
 "F4dun": {"lead": F4dun_lead, "suffix": F4dun_suffix,
        "notes": "Identical to F4 except the paper words: 'dun, yellowed cream'. Isolates paper brightness."},
 "F4bleed": {"lead": F4bleed_lead, "suffix": F4bleed_suffix,
        "notes": "Identical to F4 except the composition sentence asks for a full-bleed picture panel. Isolates float vs bleed on the SAME model and prompt (gpt-image-2 obeys both, so the pair is clean there)."},
 "F4arrow": {"lead": F4_lead, "suffix": F4arrow_suffix,
        "notes": "F4 plus one suffix sentence asking for black diagram arrows/callouts. Isolates arrow colour (new models drew red arrows after the leads named brick-red ink)."},
}

KLUBAS_OVERRIDE = ("Subject: an evening dance in a house-of-culture hall: young people dancing loosely and "
                   "casually in pairs and small groups to a small amateur band on a low plywood stage, "
                   "under plain ceiling lights, on a linoleum floor.")
REFS = ["024_miestas", "041_klubas", "036_mokykla"]

# ---------------------------------------------------------------- new images
new_images = []
def add(vid, card, model, quality="medium", prompt="F4", refs=False, override=""):
    new_images.append({"vid": vid, "card": card, "model": model, "quality": quality, "prompt": prompt,
                       "references": REFS if refs else [], "subject_override": override})

G2, SUN, FLARE, V15 = "gpt-image-2", "gpt-image-2.5-sunburst", "gpt-image-2.5-flare", "gpt-image-1.5"

# R1 miestas
add("F4_g2_miestas", "024_miestas", G2)
add("F4_sun_miestas", "024_miestas", SUN)
add("F4bleed_g2_miestas", "024_miestas", G2, prompt="F4bleed")
add("F4ref_g2_miestas", "024_miestas", G2, refs=True)
# R2 gydytojas (also the repeat round)
add("F4_g2_gydytojas", "113_gydytojas", G2)
add("F4_sun_gydytojas", "113_gydytojas", SUN)
add("F4_15_gydytojas", "113_gydytojas", V15)
add("F4dun_g2_gydytojas", "113_gydytojas", G2, prompt="F4dun")
# R3 eiti
add("F4_g2_eiti", "366_eiti", G2)
add("F4arrow_g2_eiti", "366_eiti", G2, prompt="F4arrow")
add("F4_sun_eiti", "366_eiti", SUN)
add("F4arrow_sun_eiti", "366_eiti", SUN, prompt="F4arrow")
# R4 suo
add("F4_g2_suo", "001_suo", G2)
add("F4_sun_suo", "001_suo", SUN)
add("F4_flare_suo", "001_suo", FLARE)
add("F4_g2low_suo", "001_suo", G2, quality="low")
add("F4dun_g2_suo", "001_suo", G2, prompt="F4dun")
# R5 klubas
add("F4_sun_klubas", "041_klubas", SUN)
add("F4ovr_sun_klubas", "041_klubas", SUN, override=KLUBAS_OVERRIDE)
add("F4_g2_klubas", "041_klubas", G2)
add("F4ovr_g2_klubas", "041_klubas", G2, override=KLUBAS_OVERRIDE)
add("F4ref_sun_klubas", "041_klubas", SUN, refs=True)
# R6 seima (+ second seed of F4_g2 for noise)
add("F4_g2_seima", "090_seima", G2)
add("F4_g2b_seima", "090_seima", G2)
add("F4_sun_seima", "090_seima", SUN)
add("F4_15_seima", "090_seima", V15)
# R7 paltas
add("F4_g2_paltas", "066_paltas", G2)
add("F4_sun_paltas", "066_paltas", SUN)
add("F4dun_sun_paltas", "066_paltas", SUN, prompt="F4dun")
add("F4_flare_paltas", "066_paltas", FLARE)
# R8 pjauti
add("F4_g2_pjauti", "405_pjauti", G2)
add("F4_sun_pjauti", "405_pjauti", SUN)
add("F4_g2low_pjauti", "405_pjauti", G2, quality="low")
add("F4bleed_g2_pjauti", "405_pjauti", G2, prompt="F4bleed")
# R9 minia
add("F4_g2_minia", "108_minia", G2)
add("F4_sun_minia", "108_minia", SUN)
add("F4ref_g2_minia", "108_minia", G2, refs=True)
add("F4ref_sun_minia", "108_minia", SUN, refs=True)
# R10 mokykla
add("F4_g2_mokykla", "036_mokykla", G2)
add("F4bleed_g2_mokykla", "036_mokykla", G2, prompt="F4bleed")
add("F4_sun_mokykla", "036_mokykla", SUN)
add("F4_flare_mokykla", "036_mokykla", FLARE)
# R11 lova
add("F4_g2_lova", "211_lova", G2)
add("F4_sun_lova", "211_lova", SUN)
add("F4dun_g2_lova", "211_lova", G2, prompt="F4dun")
add("F4_g2low_lova", "211_lova", G2, quality="low")
add("F4_flare_lova", "211_lova", FLARE)
add("F4_15_lova", "211_lova", V15)
# R13 vestuves (+ second seed of F4_sun for noise)
add("F4_g2_vestuves", "137_vestuves", G2)
add("F4_sun_vestuves", "137_vestuves", SUN)
add("F4_sunb_vestuves", "137_vestuves", SUN)
add("F4ref_sun_vestuves", "137_vestuves", SUN, refs=True)

# ---------------------------------------------------------------- rounds
rounds = [
 {"round": 1, "card": "024_miestas", "repeat_of": None,
  "variants": ["orig", "F3_g2", "F3_sun", "F4_g2_miestas", "F4_sun_miestas", "F4bleed_g2_miestas", "F4ref_g2_miestas", "sun_old"],
  "discriminates": "float vs bleed on the same model+prompt (F4_g2 vs F4bleed_g2); refs (F4ref_g2 vs F4_g2); splice vs F3; sun_old is the known-'Western' anchor."},
 {"round": 2, "card": "113_gydytojas", "repeat_of": None,
  "variants": ["orig", "F3_g2", "F3_sun", "F4_g2_gydytojas", "F4_sun_gydytojas", "F4_15_gydytojas", "g2_old", "F4dun_g2_gydytojas"],
  "discriminates": "model vs prompt (orig vs F4_15 vs F4_g2); paper (F4_g2 vs F4dun_g2); people block (g2_old vs F3_g2). Faces card."},
 {"round": 3, "card": "366_eiti", "repeat_of": None,
  "variants": ["orig", "F3_g2", "F4_g2_eiti", "F4arrow_g2_eiti", "F4_sun_eiti", "F4arrow_sun_eiti", "F1_sunlow"],
  "discriminates": "arrow colour (F4 vs F4arrow on both models); low quality; verb card with a single figure."},
 {"round": 4, "card": "001_suo", "repeat_of": None,
  "variants": ["orig", "g2_old", "F4_g2_suo", "F4_sun_suo", "F4_flare_suo", "F4_g2low_suo", "F4dun_g2_suo"],
  "discriminates": "finish alone, no people: model (g2/sun/flare), paper, quality. If orig still wins here the preference is about rendering/paper, not people."},
 {"round": 5, "card": "041_klubas", "repeat_of": None,
  "variants": ["orig", "F3_sun", "F4_sun_klubas", "F4ovr_sun_klubas", "F4_g2_klubas", "F4ovr_g2_klubas", "F4ref_sun_klubas", "sun_old"],
  "discriminates": "the Western stress test: subject override (ovr vs plain, both models); refs on Sunburst; model."},
 {"round": 6, "card": "090_seima", "repeat_of": None,
  "variants": ["orig", "F3_g2", "F3_sun", "F4_g2_seima", "F4_g2b_seima", "F4_sun_seima", "F4_15_seima", "F2_g2"],
  "discriminates": "people block (F2_g2 generic people vs F3_g2); seed noise (F4_g2 vs F4_g2b, identical settings); model vs prompt (F4_15)."},
 {"round": 7, "card": "066_paltas", "repeat_of": None,
  "variants": ["orig", "F1_sun", "F3_sun", "F4_g2_paltas", "F4_sun_paltas", "F4dun_sun_paltas", "F4_flare_paltas"],
  "discriminates": "clothing card: paper on Sunburst (F4_sun vs F4dun_sun); flare; F1 vs F3 vs F4 on Sunburst."},
 {"round": 8, "card": "405_pjauti", "repeat_of": None,
  "variants": ["orig", "g2_A", "sun_B", "F3_g2", "F4_g2_pjauti", "F4_sun_pjauti", "F4_g2low_pjauti", "F4bleed_g2_pjauti"],
  "discriminates": "worker verb: float vs bleed (F4_g2 vs F4bleed_g2); quality (F4_g2 vs F4_g2low); the 'flat and austere' g2_A and the refs-only sun_B as anchors."},
 {"round": 9, "card": "108_minia", "repeat_of": None,
  "variants": ["orig", "F3_g2", "F3_sun", "F4_g2_minia", "F4_sun_minia", "F4ref_g2_minia", "F4ref_sun_minia"],
  "discriminates": "crowd of faces: refs vs text-only on both models; F3 vs F4."},
 {"round": 10, "card": "036_mokykla", "repeat_of": None,
  "variants": ["orig", "flare_old", "F1_g2", "F3_g2", "F4_g2_mokykla", "F4bleed_g2_mokykla", "F4_sun_mokykla", "F4_flare_mokykla"],
  "discriminates": "place card: float vs bleed (F4_g2 vs F4bleed_g2); flare old vs flare F4; F1 vs F3 vs F4 on g2."},
 {"round": 11, "card": "211_lova", "repeat_of": None,
  "variants": ["orig", "F4_g2_lova", "F4_sun_lova", "F4dun_g2_lova", "F4_g2low_lova", "F4_flare_lova", "F4_15_lova"],
  "discriminates": "pure object card, nobody present: model vs prompt on finish alone (orig vs F4_15 vs F4_g2); paper; quality; flare."},
 {"round": 12, "card": "113_gydytojas", "repeat_of": 2,
  "variants": ["orig", "F3_g2", "F3_sun", "F4_g2_gydytojas", "F4_sun_gydytojas", "F4_15_gydytojas", "g2_old", "F4dun_g2_gydytojas"],
  "discriminates": "REPEAT of round 2, same images, reshuffled letters and grid positions: test-retest consistency (Kendall tau vs round 2)."},
 {"round": 13, "card": "137_vestuves", "repeat_of": None,
  "variants": ["orig", "F3_g2", "F3_sun", "F4_g2_vestuves", "F4_sun_vestuves", "F4_sunb_vestuves", "F4ref_sun_vestuves", "F4_15_vestuves"],
  "discriminates": "people action card: seed noise on Sunburst (F4_sun vs F4_sunb); refs on Sunburst; model vs prompt (F4_15)."},
]
# fix: vestuves needs F4_15 too
add("F4_15_vestuves", "137_vestuves", V15)

# ---------------------------------------------------------------- attributes
def attr(model, fam, comp, paper, refs=False, quality="medium", people="none", print_="none", override=False, note=""):
    d = {"model": model, "prompt_family": fam, "composition": comp, "paper": paper, "refs": refs,
         "quality": quality, "people_block": people, "print_block": print_, "subject_override": override}
    if note: d["note"] = note
    return d

attributes = {
 "orig":      attr("gpt-image-1.5", "shipped", "float", "bright-cream", note="control; appears in every round"),
 "g2_old":    attr(G2, "shipped", "bleed", "default"),
 "sun_old":   attr(SUN, "shipped", "bleed", "default"),
 "flare_old": attr(FLARE, "shipped", "bleed", "default"),
 "g2_A":      attr(G2, "A", "bleed", "default", people="A-dress", print_="A-flat"),
 "g2_B":      attr(G2, "shipped+refs", "bleed", "default", refs=True),
 "sun_A":     attr(SUN, "A", "bleed", "default", people="A-dress", print_="A-flat"),
 "sun_B":     attr(SUN, "shipped+refs", "bleed", "default", refs=True),
 "F1_g2":     attr(G2, "F1", "float", "dun-observed"),
 "F2_g2":     attr(G2, "F2", "float", "dun-observed", print_="F2"),
 "F3_g2":     attr(G2, "F3", "float", "dun-observed", people="F3"),
 "F1_sun":    attr(SUN, "F1", "bleed", "dun-observed"),
 "F2_sun":    attr(SUN, "F2", "bleed", "dun-observed", print_="F2"),
 "F3_sun":    attr(SUN, "F3", "bleed", "dun-observed", people="F3"),
 "F1_sunlow": attr(SUN, "F1", "bleed", "dun-observed", quality="low"),
}
for im in new_images:
    fam = im["prompt"]
    comp = "expected-bleed" if fam == "F4bleed" else ("expected-float" if im["model"] in (G2, V15) else "expected-float?")
    paper = "dun-requested" if fam == "F4dun" else "bright-requested"
    attributes[im["vid"]] = attr(im["model"], fam, comp, paper, refs=bool(im["references"]), quality=im["quality"],
                                 people="F3", print_="F2", override=bool(im["subject_override"]))

analysis_plan = """\
PRESENTATION (to protect the blind)
- Re-encode every image, including orig, through the same resize+JPEG pipeline and crop to identical pixel size so compression, sharpness or border width cannot identify the model. Shuffle grid POSITIONS as well as letters each round (do not keep orig at a fixed cell). Never show the card name together with model names. Send the repeat round (12) without flagging it as a repeat.
- Ask for: (a) a full strict ranking of the letters, best to worst; (b) an asterisk on every variant he would accept for production as-is (gives an absolute threshold that a relative ranking lacks); (c) optional one-word notes. Do not prompt him with attribute words (paper, faces, flat); let the notes be his own vocabulary and code them afterwards.
- Order rounds 1-13 as listed: high-information favourites first, the pure-object rounds (4, 11) in the middle so finish-only judgements are made while fresh but after calibration, repeat at 12, one people round at 13 so the repeat is not last.

SCORING
1. Per round: Borda score per variant, normalised to [0,1] by round size (rounds have 7 or 8 variants). Report orig's normalised rank in every round: if orig is top in >=10 of 13 rounds, the result is 'nothing yet matches 1.5' and the question becomes which attributes bring variants closest; if orig is beaten in several rounds, those rounds say what beats it.
2. Pooled model: Plackett-Luce (or Bradley-Terry on all implied pairwise comparisons within rounds) over all ~65 distinct variants, fitted with mild L2 regularisation. Then regress the fitted item strengths on the attribute columns in `attributes` (model one-hot, people_block, print_block, composition, paper, refs, quality, subject_override) with ridge regression; report coefficients with bootstrap CIs by resampling rounds. The design pairs each attribute at least twice on the same model and card (paper: rounds 2,4,7,11; composition: 1,8,10; refs: 1,5,9,13; quality: 3,4,8,11; arrows: 3; override: 5; flare: 4,7,10,11; 1.5+F4: 2,6,11,13), so the within-round pairwise contrasts are the primary evidence and the regression is the summary.
3. Direct contrasts (report alongside the regression, they are cleaner): for each one-attribute pair in the same round, sign and rank gap. E.g. F4_g2 vs F4bleed_g2 (3 rounds), F4_g2 vs F4dun_g2 (3 rounds), F4_sun vs F4dun_sun (1), F4 vs F4arrow (2 in round 3), F4_g2 vs F4_g2low (3), plain vs override (2 in round 5), text vs refs (6 pairs).
4. Model-vs-prompt: orig vs F4_15 vs F4_g2 in rounds 2, 6, 11, 13. If F4_15 ~ orig > F4_g2: the 1.5 look is the model, and the production question is purely 'which new model gets closest'. If F4_15 > orig: the F4 text improves even 1.5 and the attributes it carries are the preference. If orig > F4_15: something in the SHIPPED prompt (not the model) is loved; diff the shipped lead against F4 phrase by phrase.
5. Reliability: Kendall tau between rounds 2 and 12 (same images). tau >= 0.6: trust individual rounds. tau 0.3-0.6: trust pooled effects only. tau < 0.3: his preference at this granularity is noise; fall back to the asterisk threshold and the top-2 per round only. Seed noise: rank gap between F4_g2_seima/F4_g2b_seima and F4_sun_vestuves/F4_sunb_vestuves; any attribute effect smaller than this gap is not real.
6. Notes vs rankings: code his one-word notes into the same attribute set and compare to the regression. Where his stated reasons and his revealed weights disagree (e.g. he says 'paper' but the rankings move with people), report the disagreement explicitly; that is the 'hard to determine intellectually' finding he asked for.
7. People vs no-people: compare attribute effects in people rounds (2, 5, 6, 9, 13) against object rounds (4, 11). If model/paper effects persist in object rounds, the preference is about rendering; if they vanish, it is about people and the production lead only needs the people block.

DECISION RULE
Pick the production configuration as the attribute combination with the highest predicted strength that also has >= 50% asterisk rate in its appearances; if that is not F4 on one model, splice the winning attribute values into F4 and run one confirmation set of 15 cards before committing the remaining ~1,000.
"""

out = {"new_prompts": new_prompts, "new_images": new_images, "rounds": rounds, "attributes": attributes,
       "analysis_plan": analysis_plan}
path = "/tmp/claude-0/-home-claude/d7674abf-8089-5641-8362-8f132083a14b/scratchpad/survey_design.json"
json.dump(out, open(path, "w"), ensure_ascii=False, indent=2)

# checks
vids = {im["vid"] for im in new_images}
assert len(vids) == len(new_images), "duplicate vid"
existing = set(attributes) - vids
for r in rounds:
    assert "orig" in r["variants"]
    assert 5 <= len(r["variants"]) <= 8, r
    for v in r["variants"]:
        assert v in vids or v in existing, (r["round"], v)
        if v in vids:
            assert next(i for i in new_images if i["vid"] == v)["card"] == r["card"], (r["round"], v)
from collections import Counter
c = Counter(im["model"] for im in new_images)
cost = c[G2]*0.044 + c[SUN]*0.0135 + c[FLARE]*0.03 + c[V15]*0.07
print("new images:", len(new_images), dict(c), "est cost ~$%.2f" % cost)
print("F4 lead words:", len(F4_lead.split()), "suffix:", len(F4_suffix.split()))
import re
for k,v in new_prompts.items():
    print(k, "negations:", re.findall(r"\b(no|not|never)\b", v["lead"]+" "+v["suffix"]))
print("rounds:", len(rounds), "sizes:", [len(r["variants"]) for r in rounds])
print("written", path)
