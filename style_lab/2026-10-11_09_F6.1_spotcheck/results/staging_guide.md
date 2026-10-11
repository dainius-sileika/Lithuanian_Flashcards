# Staging guide — writing a per-card direction so the word is obvious from the main picture

A staging line is one to four sentences inserted right after `Subject: ...` (card_notes.json → deck_builder.build_call). It is the only per-card text a writer controls; everything else (style lead, dress class, inset rules, plausibility, no-text, bands, flag, suffix) is fixed. Write it as a stage direction to an illustrator who has never seen the deck.

## The test
Cover the word. Look only at the MAIN picture. Would a learner who does not know the word say it (or its English) within two seconds? If the answer depends on an inset, the staging has failed. (Blind evidence: gatvė → "plaza", mokykla → "a house", šokti → "a couple embracing", stotis G → "harder to guess". In each case the insets knew the word and the main picture did not.)

## Principles
1. **One subject, large and central.** Name what fills the middle of the picture and say it is the subject. If a setting is attached, say what stays in the background.
2. **Show the defining feature, not the context.** A street is a roadway with traffic between kerbs, not the buildings beside it; a school is a building of identical classroom windows with children streaming in, not a nice old house; a station is a platform with a train at it, not a façade. Ask: what would be missing if this were the neighbouring word (plaza, house, hotel)? Put that thing in the centre.
3. **For actions, show the moment of maximum legibility.** Dancing = the spin or the step with feet off the floor, not the hold; singing = open mouths and songbooks; running = both feet off the ground, arms pumping; buying = goods and money crossing the counter. Static holds read as talking or hugging.
4. **Say what the insets are, concretely, and make them different from each other and from the main picture.** Three insets: a close-up detail, a second angle or moment, a result or companion object. For motion verbs only (eiti, bėgti) the engine adds the left/right strip; for every other verb write your own three insets or the engine will draw a meaningless gesture strip.
5. **Give the gaze.** Group: most at their task or each other, one or two toward the viewer. Two main figures: one toward the viewer, one at the task. Lone figure: near-frontal.
6. **Name people only as the word needs them.** Object and place cards: the people who characteristically use the thing, small and secondary. Person/role cards: the role's defining tool and setting in the frame with them.
7. **Keep the setting a servant.** A Setting line (from the bank) is appended after your staging; write the staging so the subject survives any setting: "the roadway and its traffic are the subject; the buildings of [setting] stand behind".
8. **Period and place: 1981, free Lithuania.** Zhiguli, Moskvich, Ikarus, LAZ buses, trolleybuses; panel blocks, interwar plaster houses, wooden farmsteads; tricolour only, never Soviet symbols; prices, signs and books stay wordless (NO_TEXT_RULE) unless the card is in the text pilot.
9. **Plausibility is written in, not assumed.** If a prop matters, say how it is attached and used (a sweep standing over a well-head with a bucket on the pole). If a prop does not belong, leave it out of the text entirely; naming it to forbid it primes it (the maitinti well).
10. **Animals and bodies.** Side profile for species cards; whole figure for verbs; a resting animal "curled, eyes closed, ears relaxed".

## Checklist (apply line by line)
- [ ] First sentence names the main picture and ends with "...is the subject."
- [ ] The defining feature that separates this word from its nearest neighbour is in the main picture and named.
- [ ] For a verb: the moment of maximum legibility is named (what the body is doing, where the feet/hands/mouth are).
- [ ] Two or three insets listed, each a different detail/angle/result; none repeats the main picture; none could be read as a neighbouring word.
- [ ] Non-locomotion verb: insets written explicitly (no gesture strip).
- [ ] Gaze assigned (group / pair / lone).
- [ ] People: how many, what role, dressed for setting and occasion; the dress class in deck_builder matches (worker caps / professional / civilian / formal).
- [ ] Props: every named object is complete and in use; no unneeded prop is mentioned, even negatively.
- [ ] Setting (if any) is explicitly placed behind the subject.
- [ ] 1981 Lithuania: vehicles, buildings, clothes, tricolour; nothing that needs lettering.
- [ ] Under ~80 words. Positive phrasing throughout.

## Template
"Main picture: [SUBJECT, size and placement], [defining feature 1], [defining feature 2], [the people the word needs, what they do, where they look]; [background in one clause]. [The X] is the subject. Insets: [close-up detail]; [second angle or moment]; [result or companion object]."

## Worked examples — the failures
**027_gatvė (street).** Main picture: a town street seen along its length at eye level, a two-lane asphalt roadway with a painted centre line and a zebra crossing in the foreground, kerbs and pavements on both sides, a Zhiguli and an Ikarus bus on the road, pedestrians on the pavements, three- and four-storey plastered houses with shop fronts on either side, a street lamp and a road sign on a post. The roadway and its traffic are the subject. Insets: a close-up of the kerb, pavement and a storm drain; a pedestrian crossing at the zebra; a street lamp on its post.
*Why it failed before:* the setting (a pedestrian boulevard with a fountain) replaced the roadway; no vehicles, no kerb.

**036_mokykla (school).** Main picture: a two-storey school building seen from the front, long rows of large identical classroom windows, a flagpole with the tricolour and a wide entrance with steps, a stream of children with satchels and white collars going up the steps, a teacher holding the door, a bell on a bracket beside it, the paved schoolyard and a football goal to one side. The school building with its children is the subject. Insets: a classroom with a teacher at a chalkboard bearing only a simple diagram and pupils at desks; children playing in the schoolyard; a satchel, slate and pencil case.
*Why it failed before:* a handsome wooden manor from the settings bank, a few children; it read as a house.

**408_šokti (to dance).** Main picture: a couple in full motion on a wooden dance floor, the woman spun out at arm's length with her skirt flaring, both feet of the man mid-step, a small band with accordion and drum on the stage behind, seated onlookers at tables along the wall, musical notes in the air. The spinning couple is the subject. Insets: three phases of one dance step, left to right: step together, the woman turning under the man's raised arm, the pair apart at arm's length; a close-up of the dancers' feet mid-step; the accordion player.
*Why it failed before:* a static close hold reads as embracing.

**411_dainuoti (to sing).** Main picture: a small village choir of six singing with open mouths from songbooks, standing in a row on a low outdoor stage, a conductor seen from behind, musical notes drawn in the air above them. Open mouths and songbooks make the action clear. Insets: a close-up of one singer's face with the mouth open in song and notes in the air; hands holding an open songbook; the choir seen from the side with the accordion player. These insets replace any motion strip.
*Why it failed before:* the engine's default strip drew conductor hand gestures.

**030_stotis (station).** Main picture: a railway platform with a green passenger train standing at it, carriage doors open, passengers with suitcases boarding and alighting, the station building with its clock and canopy along the platform, rails running out of frame. The train at the platform is the subject. Insets: the station clock; a ticket window with a queue; a bench with a waiting family.

## Worked examples — by category
**Places (parkas, turgus, paplūdimys).** The activity that only happens there, in the middle: market = stalls heaped with produce and scales, buyers and sellers across them; beach = sand, water's edge, bathers and towels. Buildings and sky behind.
**Buildings (ligoninė, bažnyčia, stotis).** Front elevation with the one feature that names it (red cross and ambulance; tower and cross; platform and train) AND the people who use it entering or leaving. Insets: the interior scene, the identifying detail, the people's typical object.
**Abstract verbs (galvoti, laukti, mokytis).** One person, whole figure, in the posture that names the verb, with the object of the verb visible: thinking = chin on hand over a chessboard; waiting = looking down the road at a bus stop with a watch raised; learning = at a desk with an open book and notebook, pencil moving. Insets: the face close-up, the object, the before/after.
**Activities (virti, skalbti, žvejoti).** Hands and tool at the moment of action, result visible: pot boiling with steam, washboard and suds, rod bent with a fish on the line.
**People / roles (gydytojas, kunigas, pardavėja).** The person large, in role dress, holding the role's defining tool, in the role's place; at most one assistant figure. Two-figure rule for gaze.
**Objects (laikrodis, telefonas, batai).** The object alone, large, flat-laid or three-quarter, on the paper; insets = a detail, the object in use by a hand or a small figure, a second type of the same object. Variation inside insets (three clocks at three times, both shoes and a sole).
**Animals.** Side profile standing, whole animal; insets = head close-up, foot/hoof/paw, the animal with the person who keeps it.
**Adjectives / opposites (lėtas, karštas, didelis).** A pair in one picture with the target one marked by the black arrow: slow = tortoise with the arrow, hare running in an inset; big = the big one with the arrow beside a small one. The contrast object must be unmistakably the opposite (an awake running hare, not a sleeping one).
**Clothing.** Garment flat-laid, large, central; one wearer standing near-frontal, dressed for the garment's season; detail insets of collar, fastening, pocket.

## House constraints the staging must respect
- No lettering anywhere (NO_TEXT_RULE) unless the card is in the text pilot; blackboards carry diagrams, signs are blank shapes.
- Dress classes: worker (blue-grey jacket, flat cap, kirza boots), professional (white coat + red cross / teacher with pupils / smock / service uniform), civilian (for setting and weather), formal (Sunday best: church, weddings, theatre, social dance). Choose the class in deck_builder; the staging must not contradict it.
- Motion strips only for eiti/bėgti (engine adds left/right phases); all other verbs get written insets.
- Settings bank: real Lithuanian places on roughly 2/3 of scene-capable cards; the staging names what stays behind.
- Plausibility: every named prop attached and in use; sleeping animals visibly alive; furniture on the floor; doorways clear; machines scaled to people.
- Flag: small tricolour only, only where it fits; many cards none.
- Gaze: group distribution / pair rule / lone near-frontal.
