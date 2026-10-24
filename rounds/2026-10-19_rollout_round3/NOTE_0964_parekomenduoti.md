# A2-0964 — "Ar galite ką nors rekomenduoti?" or "…parekomenduoti?" (owner: "check, I think it's 'parekomenduoti'")

**Verdict: change to `Ar galite ką nors parekomenduoti?` (pron: Ar̃ gãlite ką̃ nórs parekomendúoti?). Confidence: medium.**
Both forms are standard; the prefixed one is the aspectually natural one after *galite* for a single act, and it is the
owner's own instinct. The one-line alternative that is more frequent in everyday speech is `Ar galite ką nors pasiūlyti?`
— worth an `english_alt`/usage mention, not a replacement, because the card's English is "recommend".

## What was checked (2026-10-19)

| source | finding | URL |
|---|---|---|
| LKŽ s.v. rekomenduoti | lists **parekomendúoti** as a standard derivative: "parekomendúoti tr. duoti rekomendaciją, pakalbėti apie ką nors teigiamai: Ražnauskienė prižadėjusi parekomenduoti ją kažkokiai savo pažįstamai" — so the prefixed verb is dictionary Lithuanian, not a colloquialism | http://lkz.lt/?zodis=rekomenduoti&lns=-1&les=-1 (article read via http://lkz.lt/Zodzio_straipsniui.asp?txtZodis=rekomenduoti&zHom=0) |
| Tatoeba (lit), exact-lemma search | `=rekomenduoti`: 2 sentences, both with *galite* ("Ar jūs galite kažką rekomenduoti?", "Kokį vyną Jūs man galite rekomenduoti?"); `=parekomenduoti`: 3, all with *gali/galite* ("Ar jūs galite parekomenduoti gerą viešbutį?", "Ar tu gali man parekomenduoti gerą advokatą?", "Aš galiu parekomenduoti gerą viešbutį"); `=pasiūlyti`: 21 ("Ar jūs galite kažką pasiūlyti?", "Ką jūs galite mums pasiūlyti?"…) — both of our forms occur in exactly this frame; neither dominates; *pasiūlyti* is the common everyday verb | https://tatoeba.org/en/api_v0/search?from=lit&query=%3Dparekomenduoti · https://tatoeba.org/en/api_v0/search?from=lit&query=%3Drekomenduoti · https://tatoeba.org/en/api_v0/search?from=lit&query=%3Dpasi%C5%ABlyti |
| OpenSubtitles LT lemma list (project file) | rekomenduoti rank 3790 (138), parekomenduoti rank 19182 (14), pasiūlyti rank 901 (768), siūlyti 694 (1031). Lemma counts pool every form (rekomenduoju, nerekomenduočiau…), so they say "the unprefixed verb is the frequent lemma", not "the unprefixed infinitive is what follows *galite*" | `a2_build/study_order/opensubtitles_lt_lemmas.csv` |
| the deck's own request phrases | every "Ar galite/Prašom + infinitive" card uses the prefixed perfective: *pakartoti* (0902/0374), *padėti* (0383/0950), *parodyti*, *pasakyti*, *pasiūlyti* (2007). *rekomenduoti* would be the only bare imperfective in the set; the owner's ear is picking up that mismatch | `a2_build/a2_wordlist.csv` |
| VLKK consultation bank | **not checked** — vlkk.lt returns 403 to this environment (Cloudflare). If the owner wants a ruling, search "rekomenduoti" at https://www.vlkk.lt/konsultacijos | — |
| DLKŽ / BŽ (ekalba.lt) | **not checked** — the site is a JS app with no reachable text endpoint from here | — |

## Why parekomenduoti

With *galėti* + infinitive for a one-off request Lithuanian prefers the perfective (prefixed) verb; the bare
*rekomenduoti* is heard — especially from speakers treating the international verb as unprefixable — and is attested
(Tatoeba), but *parekomenduoti* matches the aspect of every neighbouring phrase in the deck and is the form LKŽ records
for "give someone a recommendation". The counter-hypothesis (bare *rekomenduoti* is the only standard form) is not
supported by any source read: LKŽ lists the prefixed verb without comment, and the corpus examples use both.

## Data change (for the executor, with the merges batch)

- `a2_wordlist.csv` A2-0964: `lithuanian_TARGET` and `example_lt` → `Ar galite ką nors parekomenduoti?`; `lt_pron` →
  `Ar̃ gãlite ką̃ nórs parekomendúoti?` (ar̃ — en.wiktionary; gãlite, ką̃ — kirtis; nórs — LKŽ http://lkz.lt/?zodis=nors&lns=-1&les=-1 ; parekomendúoti — LKŽ);
  `notes` += `owner 2026-10-19: perfective; LKŽ parekomenduoti`; `english_alt` += `Ar galite ką nors pasiūlyti? (everyday variant)`.
- `restage_bubbles.csv` / `situations.py`: no change to the staging (menu handed back open); the caption is not drawn.
- A2-2012 *Ką rekomenduotumėte?* stays (owner: overlap kept); its conditional is fine unprefixed or prefixed — leave.
- Audio: none recorded yet for 0964, so nothing to re-record.
