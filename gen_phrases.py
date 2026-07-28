# -*- coding: utf-8 -*-
"""gen_phrases.py — generation driver for the question / phrase / sentence cards.

These cards are the first in the deck to carry speech bubbles, and the bubble is
what broke the no-text rule that had held for 520 cards. Two lessons are baked in
here:

  1. NEVER PUT A CONDITION IN A PROMPT. The first version asked for a question
     mark "only if the phrase is a question". The model ignored the condition and
     drew one on all nine non-question cards — *Cheers!*, *Welcome!*, *Of course*
     all ended up interrogative. Python decides; the prompt only ever states.

  2. A TEXT EXCEPTION SUSPENDS THE NO-TEXT RULE. Passing any `exact_text` swaps
     out the strong NO_TEXT_RULE, which is why the Lithuanian target started
     appearing in bubbles. Cards that need no lettering now pass exact_text=""
     so the proven rule governs them, and `exclude` names the target as forbidden
     on every card either way.

    python3 gen_phrases.py [count] [budget_seconds]
"""
import csv, os, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from go_generator import GOGenerator
from go_grammars import NOUN_GRAMMARS, SCENE_TAIL
import deck_builder as db
from bubbles import UTTER, EXCH

OUT = "out_phrases"
os.makedirs(OUT, exist_ok=True)

# The only lettering ever permitted on these cards: a lone question mark, on
# cards that really are questions. Stated unconditionally or not at all.
QMARK = ('one single bold question mark "?" drawn as a graphic symbol inside '
         'the speech bubble, and nothing else whatsoever.')


# Decided from the data, never delegated to the model. Defined in qa_images so
# the generator and the QA gate share one definition of "question".
from qa_images import is_question


def main():
    rows = [r for r in csv.DictReader(open("wordlist_a2_pending.csv", encoding="utf-8"))
            if r["status"] == "pending" and r["level"] == "A1"
            and (r["category"] == "Question words" or r["phase"] == "P-G")]

    gen = GOGenerator(backend="openai", ratio="4:3")
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    BUD = float(sys.argv[2]) if len(sys.argv) > 2 else 38
    t0 = time.time()

    jobs = []
    for r in rows:
        key, en = r["id"], r["english"]
        if os.path.exists(f"{OUT}/{key}.png"):
            continue
        if len(jobs) >= N:
            break

        q = is_question(r)
        if r["category"] == "Question words":
            bub = db.QUESTION_BUBBLE.get(db.QUESTION_BY_GLOSS.get(en, ""), "")
            if not bub:
                continue
            scene = (NOUN_GRAMMARS["question"]["main"]
                     + " The pictogram inside the bubble is " + bub + "." + SCENE_TAIL)
            subj = f"the question word {en.upper()}"
        elif en in EXCH:
            setting, left, right = EXCH[en]
            scene = (NOUN_GRAMMARS["exchange"]["main"] + f" The setting is {setting}. "
                     f"The LEFT panel's bubble contains {left}. The RIGHT panel shows "
                     f"{right}." + SCENE_TAIL)
            subj = f"the phrase '{en}'"
        elif en in UTTER:
            setting, bub = UTTER[en]
            scene = (NOUN_GRAMMARS["utterance"]["main"] + f" The setting is {setting}. "
                     f"Inside the bubble, and nowhere else, place {bub}." + SCENE_TAIL)
            subj = f"the phrase '{en}'"
        else:
            continue

        jobs.append((key, en, subj, scene, q,
                     r.get("lithuanian_TARGET", "").strip(" .!?")))

    # Generation is ~16 s a card and entirely network-bound, so run a pool —
    # serial batches could not fit enough cards inside the sandbox time limit.
    def run(job):
        key, en, subj, scene, q, target = job
        gen.generate(subject=subj, scene=scene, insets=False, text=False,
                     people="civilian", exact_text=(QMARK if q else ""),
                     exclude=target, out_dir=OUT, filename=f"{key}.png")
        return key, en, q

    done = 0
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(run, j): j for j in jobs}
        for fut in as_completed(futs):
            key, en = futs[fut][0], futs[fut][1]
            try:
                _, _, q = fut.result()
                done += 1
                print(f"  {key} {en[:34]:36} {'question' if q else 'statement'}")
            except Exception as e:
                print(f"  {key}: FAIL {str(e)[:70]}")
            if time.time() - t0 > BUD:
                print("  budget reached — rerun to continue")
                break

    total = len([f for f in os.listdir(OUT) if f.endswith('.png')])
    print(f"generated {done} | total {total}/{len(rows)}")


if __name__ == "__main__":
    main()
