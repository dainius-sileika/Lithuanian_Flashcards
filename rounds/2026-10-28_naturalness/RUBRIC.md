# Naturalness review, 2026-10-28: rubric

**Owner (verbatim):** "Since these cards are more than for me, i.e., what the user learns proliferates the more
users use this deck, it's essential that we nail down the best and most natural, and correct, Lithuanian, instead
of just the technically correct form. I'm OK to re-record for the greater good." and "A full naturalness review by
Fable is the right spirit … the text must be natural more than just correct."

**Packets:** `packet_A.csv` (A1, 504 rows), `packet_B.csv` (A2 rows 1–430), `packet_C.csv` (A2 rows 431–751).
Every Lithuanian sentence and phrase in the deck, in study order. `sentence` keeps the cloze braces `{…}`
around the taught word; `recorded` says whether the owner has already recorded it (a change turns it into a
re-take; the owner accepts that).

## The question for every row
Would a native speaker naturally say exactly this, in this situation, to this person? Not "is it grammatical".

Check:
1. **Register and setting.** Who speaks to whom? Requests to strangers and in service encounters → polite
   forms (*norėčiau*, *ar galėčiau / ar galėtumėte*, *Ar …?* questions); *jūs* to strangers, *tu* to family and
   friends. Plain present for one's own wishes and plans, and on cards whose point is the present form.
2. **Word order and information structure.** Natural Lithuanian order (topic first, new information last), not
   English order.
3. **Calques.** English or Russian patterns in Lithuanian words ("turiu peršalimą", "daryti nuotrauką"…).
4. **Collocations and idiom.** The verb or adjective a native uses with this noun; fixed expressions.
5. **Case and aspect choices** that are grammatical but not what people say (perfective vs imperfective in
   context, genitive of negation, partitive genitive).
6. **The English line** must match the Lithuanian's meaning and register.
7. **Phrases (no braces):** is this the phrase people actually use for this function? Is the card's English
   gloss the right one?

## Constraints
- Keep the card's **taught word** (the braced form's lemma) unless keeping it forces an unnatural sentence; then
  flag "retarget/merge" for the lead instead of silently changing it.
- **A1 rows** may use only words taught by an earlier A1 card (or the target): check new words against
  `data/study_order.csv` + the deck's headwords, with the lemma logic of `build_study_order_v3.py`.
- Short and plain; one clear situation per sentence. No stress marks in sentences.
- Most rows will be fine: say "keep" quickly; spend the effort where something is off.

## Evidence
Use WebSearch (and WebFetch on returned pages where allowed) for anything not obvious: Lithuanian course
materials, vlkk.lt *kalbos patarimai*, Lietuvių kalbos institutas, real Lithuanian texts (news, shop and service
sites), corpus counts where available. Cite direct URLs; mark "unverified" what you could not read. A refused
fetch is final.

## Output per packet (`review_X.csv`)
`key, verdict (keep | change | owner), current, proposed (braces on the taught word), proposed_english,
reason (category 1–7 + one line), evidence (URL or "native-speaker judgement: …"), a1_dependency_ok,
recorded, confidence (high/medium/low)`; plus `review_X.md` with a short summary and every "owner" row explained.
Rows the separate politeness review covers (requests and approaches to strangers) may simply be marked
"see politeness" if you agree with what it is likely to propose; flag disagreements.
