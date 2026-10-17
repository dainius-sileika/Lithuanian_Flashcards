# Hand-glitch scan brief

You are checking illustrations for an Anki flashcard deck. They are painted in a Soviet civil-defence manual style: a main vignette, often with small inset panels and a red frame. An AI image model made them, and it sometimes botches hands. Your job is to find the cards where that shows.

## Process
For each image path in your batch file, open it with the Read tool and look closely at EVERY hand in the picture, in the main scene and in every inset. Check for:
- **Wrong finger count:** extra or missing fingers. Count them where a hand is clearly visible.
- **Malformed fingers:** fused, melted, too long or too many joints, a thumb on the wrong side, or a mitten-like blob where fingers should be.
- **Wrong attachment:** a hand or arm attached to the wrong person, a disembodied hand, a third hand or arm, or a left/right hand mirrored impossibly.
- **Bad grips:** an object floating near a hand rather than held, fingers passing through an object, or a grip that is anatomically impossible.
- Secondary, but report it if obvious: a badly deformed face, an extra or missing limb, or a body merged into furniture.

## Calibration
- Judge at the size you see. Ignore a hand too small or too far away to judge, and don't invent problems.
- A hand partly hidden behind an object is fine.
- Stylised simplification is fine. A glitch is something a careful viewer would notice as wrong.

## Output
Append one line per image to your output CSV (path given in your task) as you go, so that nothing is lost if you are cut off. Columns:

`key,verdict,where,issue`

- **verdict:** `ok`, `minor` (noticeable on close look), or `glitch` (obvious on a phone).
- **where:** `main`, `inset1`, `inset2`, `inset3` (top to bottom, then left to right), or `-`.
- **issue:** a short description, or empty when ok. Quote the field if it contains a comma.
- **key:** the file name without `.jpg`.

Write a header line first. Work through the whole batch, then reply with a summary only: the number of images checked, and the counts of ok, minor and glitch.
