# -*- coding: utf-8 -*-
"""Apply staging_a1_redo.py to card_notes.json and master_wordlist.csv (in place; both files are under git).
Also mirrors the two gloss decisions (482 storas → fat, 265 lūpa → lūpos / lips)."""
import json, csv, io, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.dirname(__file__))
from staging_a1_redo import NOTES, CARD_TEXT
p = os.path.join(ROOT, 'card_notes.json')
cn = json.load(open(p, encoding='utf-8'))
for k, v in NOTES.items():
    cn['notes'][k] = v
cn['_about'] += ' 2026-10-12: owner F6.2 review — 60 Redo cards restaged (a2_build/a1_redo/staging_a1_redo.py).'
json.dump(cn, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
p = os.path.join(ROOT, 'master_wordlist.csv')
raw = open(p, encoding='utf-8', newline='').read(); rows = list(csv.reader(io.StringIO(raw))); h = rows[0]
ci = h.index('card_text'); ni = h.index('#')
for r in rows[1:]:
    n = r[ni]
    if n.zfill(3) in CARD_TEXT:
        r[ci] = CARD_TEXT[n.zfill(3)]
    if n == '482':
        r[h.index('english')] = 'fat'
    if n == '265':
        r[h.index('lithuanian_TARGET')] = 'lūpos'; r[h.index('english')] = 'lips'; r[h.index('gender')] = 'F pl'
        r[h.index('lt_pron')] = 'lū́pos'; r[h.index('subject_phrase_EN')] = 'a pair of lips in close view, slightly parted, an arrow on the lips'
        r[h.index('notes')] = (r[h.index('notes')] + '; ' if r[h.index('notes')] else '') + 'retargeted lūpa→lūpos 2026-10-11 (plural usual); key 265_lupa unchanged'
out = io.StringIO(); csv.writer(out, lineterminator='\r\n').writerows(rows)
open(p, 'w', encoding='utf-8', newline='').write(out.getvalue())
print('applied', len(NOTES), 'notes,', len(CARD_TEXT), 'card_text')
