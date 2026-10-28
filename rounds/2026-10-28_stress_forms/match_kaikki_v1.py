import json,sys,collections,unicodedata,csv,os
K=os.path.dirname(os.path.abspath(__file__))
def strip(s):
  d=unicodedata.normalize('NFD',s); out=[]
  for ch in d:
    if ch in '̀́̃': continue
    if ch=='̇' and out and out[-1] in 'iIjJ': continue
    out.append(ch)
  return unicodedata.normalize('NFC',''.join(out))
def stressed(s): return any(c in unicodedata.normalize('NFD',s) for c in '̀́̃')
E={}
for line in open(K+'/lt.jsonl'):
  e=json.loads(line); E.setdefault(strip(e['word']).lower(),[]).append(e)
NEED={'gen_sg':{'genitive'},'fem':{'feminine','nominative','singular'},'pres3':{'present','third-person'},'past3':{'past','third-person'}}
POS={'gen_sg':{'noun','name'},'fem':{'adj','num','pron','det'},'pres3':{'verb'},'past3':{'verb'}}
def lookup(lemma,field,form,plural=False):
  cands=set(); src=[]
  for e in E.get(strip(lemma).lower(),[]):
    if e['pos'] not in POS[field]: continue
    for f in e.get('forms',[]):
      t=set(f.get('tags',[]))
      if 'error-unrecognized-form' in t and field in('pres3','past3'): pass
      need=set(NEED[field])
      if field=='gen_sg': need|={'plural' if plural else 'singular'}
      if field=='fem' and not ({'feminine','nominative','singular'}<=t or t=={'feminine'}): continue
      if field!='fem' and not need<=t: continue
      if strip(f['form']).lower()==strip(form).lower() and stressed(f['form']):
        cands.add(unicodedata.normalize('NFC',f['form']))
  return sorted(cands)
rows=[]
def run(key,lemma,field,form,gender,level,kind):
  if not form.strip() or stressed(form): return
  parts=[p.strip() for p in form.split(',')]
  outs=[];amb=False;miss=False;opts=[]
  for p in parts:
    c=lookup(lemma,field,p,'pl' in (gender or '').lower())
    if len(c)==1: outs.append(c[0])
    elif len(c)>1: amb=True; outs.append(p); opts.append(' / '.join(c))
    else: miss=True; outs.append(p)
  status='unique' if not amb and not miss else ('ambiguous' if amb and not miss else 'not_found')
  rows.append(dict(key=key,level=level,kind=kind,lemma=lemma,field=field,current=form,proposed=', '.join(outs) if status=='unique' else '',options=' | '.join(opts),status=status,source=f'https://en.wiktionary.org/wiki/{lemma} (via kaikki.org Wiktextract, Lithuanian, fetched 2026-10-28)'))
lv={r['key']:r['block'][:2] for r in csv.DictReader(open('data/study_order.csv'))}
for r in csv.DictReader(open('data/cards_anki.csv')):
  for f in ('gen_sg','pres3','past3','fem'): run(r['key'],r['lithuanian'],f,r[f],r['gender'],lv.get(r['key'],'?'),'base')
skip={r['id'] for r in csv.DictReader(open('data/merged_keys.csv'))}|{r['id'] for r in csv.DictReader(open('data/deferred_B1.csv'))}
for r in csv.DictReader(open('data/a2_wordlist.csv')):
  if r['id'] in skip or r['route']=='PHRASE': continue
  for f in ('gen_sg','pres3','past3','fem'): run(r['id'],r['lithuanian_TARGET'],f,r[f],r['gender'],lv.get(r['id'],'?'),'a2list')
out=os.path.join(K,'stress_forms_proposals.csv')
with open(out,'w',newline='',encoding='utf-8') as fh:
  w=csv.DictWriter(fh,list(rows[0])); w.writeheader(); w.writerows(rows)
c=collections.Counter((r['level'],r['field'],r['status']) for r in rows)
for k in sorted(c): print(k,c[k])
print('total',len(rows))
for r in [x for x in rows if x['status']=='ambiguous'][:8]: print(r['key'],r['field'],r['current'],'->',r['options'])
for r in [x for x in rows if x['status']=='not_found'][:12]: print('NF',r['key'],r['lemma'],r['field'],r['current'])
