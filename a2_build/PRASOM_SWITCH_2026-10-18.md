# Postposed prašau → prašom + infinitive (owner decision, 2026-10-18)

Owner chose "Switch to recommended form" on the Review Desk. Keys and English unchanged.

| key | was | now |
|---|---|---|
| A2-0902 | Pakartokite, prašau | Prašom pakartoti |
| A2-0903 | Užrašykite, prašau | Prašom užrašyti |
| A2-0375 | Kalbėkite lėčiau, prašau | Prašom kalbėti lėčiau |
| A2-1166 | Sėskitės, prašau | Prašom sėstis |
| A2-1674 (cloze, pakartoti) example | {Pakartokite}, prašau. | Prašom {pakartoti}. |
| A2-1713 (cloze, sėstis) example | {Sėskitės}, prašau. | Prašom {sėstis}. |

**Source check.** Kniūkšta (ed.), *Kompiuterinis lietuvių kalbos žinynas*, ch. "Kalbos etiketas" (Šviesa 2004),
read in full from http://www.xn--altiniai-4wb.info/files/kalba/KM00/Lietuvi%C5%B3_kalbos_%C5%BEinynas._Kalbos_etiketas.KM1500.pdf
(fetched 2026-10-18). §7.2 calls prašau placed after an imperative ("Pakvieskit, prašau ... perduokit, prašau") an
*atbulinis prašau*, "nepageidaujami vertiniai iš rusų kalbos"; §7.3: Lithuanians say the courtesy word first and then
the infinitive, not the imperative: "Prašom pakviesti, prašom pasakyti, prašom perduoti" (repeated in §11.4). The four
new forms follow that pattern exactly; the source does not print these four phrases verbatim. For sėstis, §7.3's
parallel advice for *Įeikite, prašau* is a plain *Prašom!*, which the usage note mentions.

**Files changed:** a2_build/a2_wordlist.csv (target, display and cloze example columns), wordlist_a2_pending.csv,
a2_build/src/additions.py, a2_build/src/examples_3.py, examples_4.py (the sources build_a2.py reads),
a2_build/id_map.csv (the new texts added with the same ids, so a rebuild keeps the keys), a2_build/restage_bubbles.csv
→ situations.py, a2_build/recording_list.csv (none of the six was recorded yet), a2_build/context_notes.csv (Lithuanian
and the usage lines rewritten for the new form; the tu/jūs imperative pair moves to the variant line),
build_study_order_v2.py SURVIVAL_PHRASES, study_order.csv rebuilt (A2-0902 moves 842 → 564; all pins intact).
**Not changed (history):** PILOT_24.md, pilot_round2/ planner files, qa/plan records, a2_rebase/ backups,
benchmark_en/gaps_phrases.csv, examples_1.py (the merged kartoti row).
The pictures are unaffected: the situation prompts use the English caption, never the Lithuanian.
