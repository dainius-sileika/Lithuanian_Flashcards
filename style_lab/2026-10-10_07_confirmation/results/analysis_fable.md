# F5 confirmation run — scoring, arm comparison, decision

15 rounds, 44 images, blind, orig in every round. Arms: **A** = F5/F5D gpt-image-2 text-only (15 cards); **B** = A + 3 reference masters (5); **C** = Sunburst F5 (2); **L** = F5L/F5DL with the sourced Lithuanian people block (7). Two-item rounds submitted in initial order are counted as valid.

Paper tone was re-measured with a stricter estimator (`papertone2.py`: the dominant light, warm, low-chroma colour inside the bands, i.e. the paper itself rather than a mean over the scene; values in `confirm_paper_tone_strict.json`). On the first survey's images this estimator reads the winners (F3_g2, F2_g2) at L\* 86.5 / b\* 22–23 and F4dun at 82.5–85.5 / 26–27.

## 1. Pass criteria

| # | criterion | result | verdict |
|---|---|---|---|
| 1 | ≥ 11/15 arm-A cards ship-flagged; orig below arm A on ≥ 10/15 | A ship-flagged **14/15** (all but minia); A above orig **14/15** (orig won minia only) | **PASS** |
| 2 | paper on every arm-A image within the band (L\* 80–87 / b\* 20–28 by the old loose method) | loose method 3/15 in band; strict method: arm A L\* 61–83, b\* 25–31 — **0/15** inside the band the owner actually accepts (see §3). Owner: "chut chut too dark" or "too dark" on **10/15** A cards | **FAIL** |
| 3 | zero proportion/glitch comments on single-figure cards (eiti, valgyti, paltas) | **0** proportion comments anywhere in the run (21 in the first survey). eiti A: "most natural looking"; the "thick-set" → "correct natural proportions" change worked | **PASS** |
| 4 | target word identifiable on all 15 | no target-word complaints; minia's failure is gaze, not meaning ("number of people isn't bad"); miestas A "people in forefront" is a mild emphasis note | **PASS** (with the miestas note) |
| 5 | F5 and F5D each accepted on ≥ 1 card | F5D shipped 4/4 (miestas, pjauti, mokykla, turgus); F5 shipped 10/11 | **PASS** |

4/5. The one failure (paper too dark) is a wording overshoot, not a direction error: he still says "abandon the white" about orig and ranks it last in 11/15 rounds. A second problem not covered by the criteria appeared: F5's "gaze resting slightly off the viewer" made *every* figure turn ~45° the same way (visible on minia, seima, gydytojas, paltas, miestas, karas), which he flagged in 9 rounds and which sank minia.

## 2. Arm comparisons

| arm | n | ship | mean normalised Borda (rounds where it appears) | head-to-head |
|---|---|---|---|---|
| **A** (F5 text-only, g2) | 15 | **0.93** | 0.84 | beats orig 14/15; beats B 4/5; beats C 2/2 (eiti "candidate for first", paltas 2 vs 3); vs L 4–3 with two explicit ties |
| **L** (Lithuanian people block) | 7 | 0.86 | 0.71 | wins valgyti ("perfect, very Lithuanian looking"), paltas, miestas; ties gydytojas ("as good as the first") and seima ("also candidate for first"); loses vestuves (its paper was the darkest image in the run, L\* 72) and minia (both failed on gaze) |
| **B** (refs) | 5 | 0.80 | 0.55 | wins miestas ("city still the emphasis"); loses eiti ("doesn't look like a USSR citizen"), vestuves ("more posed"), paltas ("strange angle"), minia ("crowd is floating") |
| **C** (Sunburst) | 2 | 1.00 | 0.50 | 2nd on eiti ("most realistic, doesn't look Lithuanian exactly"), 3rd on paltas — but its paltas paper is "actually perfect" |
| **orig** (1.5) | 15 | 0.20 | 0.10 | last in 11/15; wins minia only (because its faces are frontal); "too bright / too white / abandon the white" ×11 |

Reading:
- **A vs L is a wash on rank and a win for L on comments.** Every unprompted "Lithuanian looking" praise is on an L card or on an A card that happened to look Lithuanian; the two "doesn't look Lithuanian/USSR" complaints are on B and C. His general note asks for more Lithuanian detail and blond/light-brown women. → the L people block becomes the default in F6.
- **Refs (B) lighten the paper and simplify the card, and that is their whole effect.** B images measure L\* 89–91 / b\* 18–26 and drew no colour complaints — useful calibration — but they lose the Soviet/Lithuanian look and the "feeling". Drop refs from production.
- **Sunburst (C) is no longer needed for proportions**, since gpt-image-2 now draws bodies correctly; keep it only as an optional fallback. Its paper is the calibration point (below).
- **F5D is settled**: 4/4 shipped, "excellent", "beautiful", "good feeling".

## 3. Paper: what "too dark" means in numbers

Strict paper L\*/b\* against his words:

| | L\* | b\* | his words |
|---|---|---|---|
| orig (all 15) | 93–96 | 9–17 | too white / too bright / abandon the white |
| B refs (5) | 89–92 | 18–26 | no colour complaint; "clean", "simple" |
| **C_066_paltas** | **82.5** | **23.6** | **"actually perfect"** |
| first-survey winners F3_g2 / F2_g2 | 86.5 | 22–23 | "bang on", "excellent colours" |
| first-survey F4dun | 82.5–85.5 | 26–27 | "yellow is good" … "a bit too yellow" |
| A_211_lova, A_050_turgus | 81.5–82.5 | 27–32 | "good colour palate"; "excellent, chut chut too dark" |
| most arm A / L | 74–81 | 28–31 | "chut chut too dark" |
| A_366_eiti, L_376_valgyti, A_137_vestuves | 61–66 | 28–29 | "too dark" (though both still ranked 1st) |

Target for F6: **L\* 83–90, b\* 20–26** (centre ≈ 86 / 23). F5's "warm yellowed dun paper" (twice, lead + suffix, with "cream" removed) overshot by ~6–8 L\* and +5 b\*. F6 uses "light aged cream paper with a soft yellow cast" and runs a one-notch-warmer twin (F6y) beside it so the next roll brackets the target instead of guessing again.

## 4. What changed vs the first survey

| | survey 1 (F1–F4) | confirmation (F5) |
|---|---|---|
| gpt-image-2 text-only ship rate | 0.51 (0.32 for F4) | **0.93** |
| orig ship rate / rounds beaten | 0.25 / 9 of 12 | 0.20 / **14 of 15** |
| proportion / glitch comments | 21 | **0** |
| "cartoony / too simple / flat" on the new arms | 17 | 0 |
| "too bright/white" | 10, all on orig/1.5 | 11, all on orig |
| "too dark" | 3 | **10** (new overshoot) |
| head position / gaze | 1 ("gaze slightly off" as a wish) | **9 rounds** (new failure, caused by my F5 wording) |
| duplicate insets | 0 | 2 (eiti strip, pjauti) + letas hare |
| "Lithuanian looking" / "doesn't look USSR" | 0 | 4 positive on A/L, 2 negative on B/C |

## 5. Settled vs open

Settled (do not re-test):
- Model gpt-image-2, quality medium, 1536×1024. Flare dropped; refs dropped; Sunburst optional fallback only.
- The 1.5 deck is not the target ("abandon the white").
- F5/F6 print vocabulary, dark-brown brush-ink outline, soft shading, black arrows (they rendered black in all A/L cards).
- Composition: F6 vignette for objects/clothing/persons/single-figure verbs; F6D full scene for places and workplace scenes.
- People: correct natural proportions (fixes g2's single-figure errors); caps on working men; moustaches sometimes; red cross on clinics via staging; the Lithuanian people block as default; women blond/light-brown, younger straight or faintly waved, older set/curled or headscarf.
- Direction of paper: yellow yes, white no.

Open (the next roll decides):
- Exact paper wording (F6 vs F6y bracket, measured against L\* 83–90 / b\* 20–26).
- Whether the gaze-distribution wording produces a natural mix (most looking at task/each other, one or two facing the viewer with eyes just past the shoulder) rather than a new uniform pose. Minia and mokytojas get two seeds each for this.
- Whether "each inset a clearly different moment" fixes duplicate frames without the model inventing off-topic insets.
- Lithuanian detail: F6 reserves a per-card staging sentence for the research agent's findings; two fresh cards (bažnyčia, namas) probe whether the model renders Lithuanian vernacular (wooden bell tower, roadside cross, carved window surrounds) from a staging line alone.
- Lead length: F6 is ~215 words, above my own ~170 guideline, because the owner's content rules grew (hair, gaze, insets, Lithuanian block). F5L at ~200 words performed well, so this is probably fine, but if the next roll shows style dilution (lighter outlines, lost halftone), the Lithuanian physiognomy sentence is the first candidate to shorten.

## 6. Decision

Adopt **F6** (`f6_candidates.json`): F5 with lighter paper, the Lithuanian people block as default, the owner's hair rules, a gaze *distribution* instead of a single off-viewer gaze, inset-variety wording, and the per-card staging fixes (minia crowd with mixed head angles, eiti alternating limbs, letas running hare, seima/vestuves/gydytojas gaze assignments, miestas scaled to a Lithuanian town). Run the next roll (`next_roll_design.json`: 14 cards × F6/F6y + 2 extra seeds + 4 Sunburst, 34 images, ≈ $1.40) with the 7 pass criteria there; on pass, commit the winning paper arm to production.
