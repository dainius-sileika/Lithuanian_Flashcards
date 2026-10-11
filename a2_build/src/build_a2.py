# -*- coding: utf-8 -*-
"""Builds a2_build/a2_wordlist.csv from wordlist_a2_pending.csv, a2_rebase/official_missing_triage.csv,
a2_rebase/queue_offlist.csv, sources/*, plus the decision modules in this folder.
Run from the project root:  python3 a2_build/src/build_a2.py
Needs ~/a2work/wikt_cache.json and ~/a2work/kirtis_cache.json (lookups made 2026-10-11); without them
pron/pres3/past3 for new rows stay blank and 'check' says so."""
import csv, json, os, re, sys, unicodedata
from collections import Counter, OrderedDict
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.abspath(os.path.join(HERE,'..','..'))
sys.path.insert(0,HERE)
from queue_overrides import EXCLUDE, KEEP_DUP, FIX, REROUTE_CLOZE, PHRASE_TO_CLOZE
from official_overrides import ROUTE, GLOSS, LEVEL_A1
from additions import ADD
from lettering import L as LETTER
EX={}
for m in ('examples_1','examples_2','examples_3','examples_4','examples_5','examples_6'):
    EX.update(__import__(m).EX)
EX['vogti']=EX['Vogti']
STG={}
for m in ('staging_1','staging_2','staging_3','staging_4','staging_5','staging_6'):
    STG.update(__import__(m).S)
EX['mane']=('Ar {mane} girdi?','Can you hear me?')
EX['bet kas']=('Tai gali padaryti {bet kas}.','Anyone can do that.')

def base(s):
    # strip stress marks only (grave, acute, tilde) and the dot Wiktionary adds to a stressed i; keep ė, ą, ų
    s=unicodedata.normalize('NFD',s.lower()); out=[]
    for k,c in enumerate(s):
        if c in '\u0300\u0301\u0303': continue
        if c=='\u0307' and k>0 and s[k-1]=='i': continue
        out.append(c)
    return unicodedata.normalize('NFC',''.join(out))
def norm_accent(s):
    # Wiktionary's i + U+0307 + accent → precomposed; strip ^ secondary-stress marks
    s=s.replace('^','')
    s=unicodedata.normalize('NFD',s)
    s=s.replace('i̇̀','ì').replace('i̇́','í').replace('i̇̃','ĩ')
    return unicodedata.normalize('NFC',s)
def accent_ok(acc, plain):
    return acc and base(acc)==base(plain) or (acc and base(acc).replace(' ','')==base(plain).replace(' ',''))

# ---------- sources ----------
def rd(p): return list(csv.DictReader(open(os.path.join(ROOT,p),encoding='utf-8')))
deck=rd('master_wordlist.csv'); queue=rd('wordlist_a2_pending.csv'); triage=rd('a2_rebase/official_missing_triage.csv')
offlist={r['id']:r for r in rd('a2_rebase/queue_offlist.csv')}
freq={base(r['lemma']):int(r['rank']) for r in rd('sources/lt_3000_frequency.csv')}
vu=set(base(r['entry']) for r in rd('sources/vu_a1a2_lexicon.csv'))
deck_lt=set()
for r in deck:
    for part in re.split(r'[/()]',r['lithuanian_TARGET']):
        if part.strip(): deck_lt.add(base(part.strip()))
WC=KC={}
try:
    WC=json.load(open(os.path.expanduser('~/a2work/wikt_cache.json'),encoding='utf-8'))
    KC=json.load(open(os.path.expanduser('~/a2work/kirtis_cache.json'),encoding='utf-8'))
except Exception as e:
    print('no lookup caches:',e)

# ---------- Wiktionary parsing ----------
def lt_section(wt):
    i=wt.find('==Lithuanian==')
    if i<0: return ''
    rest=wt[i+14:]; m=re.search(r'\n==[^=]',rest); return rest[:m.start()] if m else rest
def tparams(t):
    body=t[2:-2]; parts=body.split('|'); pos=[]; named={}
    for p in parts[1:]:
        if '=' in p: k,v=p.split('=',1); named[k.strip()]=v.strip()
        else: pos.append(p.strip())
    return parts[0].strip(),pos,named
def wikt(word):
    sec=lt_section(WC.get('en:'+word,'') or '')
    if not sec: return None
    out={'pron':'','pos':set(),'gender':'','pres3':'','past3':'','fem':'','gen':''}
    for t in re.findall(r'\{\{lt-pr\|[^}]*\}\}',sec):
        name,pos,named=tparams(t)
        if pos:
            cand=pos[0].split('<')[0].split(',')[0]
            if accent_ok(norm_accent(cand),word): out['pron']=out['pron'] or norm_accent(cand)
    for t in re.findall(r'\{\{(?:lt-noun|lt-verb|lt-adj|lt-adv|lt-prep|head\|lt)[^}]*\}\}',sec):
        name,pos,named=tparams(t)
        h=named.get('head','') or named.get('prep','')
        if h and accent_ok(norm_accent(h),word): out['pron']=out['pron'] or norm_accent(h)
        if name=='lt-noun':
            out['pos'].add('N')
            g=named.get('g') or (pos[0] if pos and pos[0] in ('m','f','m-p','f-p') else '')
            out['gender']=out['gender'] or g
            for p in pos[1:]:
                if p and p not in ('-',) and not p.isdigit() and base(p).startswith(base(word)[:3]) and (base(p).endswith('s') or base(p).endswith('ų')) and not base(p).endswith('ai') and not base(p).endswith('iai') and not base(p).endswith('os') and not base(p).endswith('ės'):
                    out['gen']=out['gen'] or norm_accent(p)
        elif name=='lt-verb':
            out['pos'].add('V')
            if len(pos)>=2 and not out['pres3']:
                out['pres3'],out['past3']=norm_accent(pos[0]),norm_accent(pos[1])
            elif len(pos)==1 and 'head' in named and not out['pres3']:
                pass
            # pattern head=X|pres|past
            if 'head' in named and len(pos)>=2: out['pres3'],out['past3']=norm_accent(pos[0]),norm_accent(pos[1])
        elif name=='lt-adj':
            out['pos'].add('A')
            f=[p for p in pos if p and not p.isdigit()]
            if f: out['fem']=norm_accent(f[0])
        elif name=='lt-adv': out['pos'].add('ADV')
        elif name=='lt-prep': out['pos'].add('PREP')
        elif name=='head':
            if pos: out['pos'].add(pos[0])
    return out

CLASS={'N':'dktv.','A':'bdvr.','V':'vksm.','ADV':'prv.','P':'įvrd.','PRON':'įvrd.','NUM':'sktv.','PREP':'prl.','CONJ':'jng.','Q':'įvrd.','INTJ':'jst.'}
def kirtis(word,typ):
    d=KC.get(word)
    if not isinstance(d,list) or not d: return ''
    want=CLASS.get(typ,'')
    cands=[]
    for x in d:
        st=x.get('state',[]); cl=x.get('class','')
        if typ=='N' and cl=='dktv.' and 'V.' in st: cands.append(x['word'])
        elif typ=='A' and cl=='bdvr.' and 'V.' in st and 'vyr.gim.' in st: cands.append(x['word'])
        elif typ=='V' and cl=='vksm.' and ('nesngr.' in st or 'sngr.' in st) and 'asm.' not in ' '.join(st): cands.append(x['word'])
        elif typ in ('P','PRON','Q') and cl=='įvrd.' and 'V.' in st: cands.append(x['word'])
        elif typ=='NUM' and cl=='sktv.' and 'V.' in st: cands.append(x['word'])
        elif typ=='ADV' and (cl=='prv.' or (cl=='bdvr.' and 'bevrd.gim.' in st)): cands.append(x['word'])
        elif typ in ('PREP','CONJ','INTJ') and cl in ('prl.','jng.','jst.','dll.'): cands.append(x['word'])
    cands=[c[0].lower()+c[1:] for c in cands if accent_ok(c,word)]
    if cands: return cands[0]
    # permissive second pass: participles used as adjectives, case forms of pronouns, locative adverbs, 3rd-person verb forms
    for x in d:
        st=' '.join(x.get('state',[])); cl=x.get('class','')
        ok=False
        if typ=='A' and cl in ('dlv.','bdvr.') and ('V.' in st): ok=True
        elif typ in ('P','PRON','Q') and cl in ('įvrd.','sktv.'): ok=True
        elif typ=='NUM' and cl in ('sktv.','įvrd.'): ok=True
        elif typ=='ADV' and (cl=='prvks.' or 'Vt.' in st or 'bevrd.gim.' in st): ok=True
        elif typ=='V' and cl=='vksm.': ok=True
        elif typ=='N' and cl=='bdvr.' and 'V.' in st: ok=True
        elif typ in ('PREP','CONJ','INTJ','PHRASE') and ('V.' in st or cl in ('prvks.','vksm.')): ok=True
        if ok and accent_ok(x['word'],word): return x['word'][0].lower()+x['word'][1:]
    return ''

# ---------- grammar rules ----------
F_IS={'pilis','pušis','avis','žąsis','kryptis','patirtis','mintis','dalis','atmintis','paslaptis','ateitis','padėtis','naktis','vagystė','sutartis','rūšis','užduotis','tapatybė','atitiktis'}
M_IES={'dantis','debesis','vagis','žvėris'}
def gen_sg(lt,gender):
    w=lt.split(' ')[-1] if ' ' not in lt else None
    if ' ' in lt: return ''
    b=lt
    if gender.endswith('pl'):
        if b.endswith('iai'): return b[:-3]+'ių'
        if b.endswith('ai'): return b[:-2]+'ų'
        if b.endswith('os') or b.endswith('ys') or b.endswith('us'): return b[:-2]+'ų'
        if b.endswith('ės'): return b[:-2]+'ių'
        return ''
    if b in M_IES or (b.endswith('is') and (b in F_IS or gender=='F')): return b[:-2]+'ies'
    if b.endswith('uo'):
        return {'mėnuo':'mėnesio','šuo':'šuns'}.get(b,b[:-2]+'ens')
    if b.endswith('tis'): return b[:-3]+'čio'
    if b.endswith('dis'): return b[:-3]+'džio'
    if b.endswith('is'): return b[:-2]+'io'
    if b.endswith('tys'): return b[:-3]+'čio'
    if b.endswith('dys'): return b[:-3]+'džio'
    if b.endswith('ys'): return b[:-2]+'io'
    if b.endswith('ius'): return b[:-3]+'iaus'
    if b.endswith('us'): return b[:-2]+'aus'
    if b.endswith('as'): return b[:-2]+'o'
    if b.endswith('a'): return b+'s'   # -a → -os
    if b.endswith('ė'): return b+'s'
    return ''
def gen_fix(g):
    return g.replace('as','os') if False else g
def guess_gender(lt):
    b=lt.split(' ')[-1]
    if base(b) in {base(x) for x in F_IS}: return 'F'
    if b.endswith(('as','is','ys','us','uo')): return 'M'
    if b.endswith(('a','ė')): return 'F'
    return ''
def fem(lt):
    b=lt
    if b.endswith('ias'): return b[:-1]
    if b.endswith('as'): return b[:-1]
    if b.endswith('us'): return b[:-2]+'i'
    if b.endswith('is'): return b[:-2]+'ė'
    if b.endswith('ęs'): return b[:-2]+'usi'
    return ''

# ---------- assemble ----------
COLS=['id','phase','phase_name','level','category','english','type','card_type','image_possible','lithuanian_TARGET','card_text','lt_pron','pron_src','ipa','gen_sg','fem','gender','subject_phrase_EN','status','dup_check','notes','source','freq_rank','route','check','example_lt','example_en','pres3','past3']
PHASES=OrderedDict([('P-A','A1 completion'),('P-B','Function words & core verbs'),('P-C','A2 topical'),('P-D','Phrases & formulas'),('P-F','Vocabulary expansion'),('P-H','Official-list pictures'),('P-I','Official-list cloze & aspect pairs'),('P-J','Frequency core additions'),('P-K','Deferred (off-list, low frequency)')])
R2C={'IMG':'image','CLOZE':'cloze','PAIR':'cloze','PHRASE':'phrase'}
out=[]; warnings=[]
def new_row(**kw):
    r={c:'' for c in COLS}; r.update(kw); return r
def finish(r):
    plain=r['lithuanian_TARGET']; key=re.sub(r'\s*\(.*\)','',plain).strip()
    let=LETTER.get(plain) or LETTER.get(key)
    if let:
        ct,rt,nt=let
        r['card_text']=ct
        if rt and rt!=r['route']:
            r['route']=rt; r['notes']=(r['notes']+'; ' if r['notes'] else '')+f'route → {rt} (lettering allowed 2026-10-11: {nt})'
            if rt=='IMG': r['image_possible']=''
        r['notes']=(r['notes']+'; ' if r['notes'] else '')+'card_text: declared Lithuanian lettering (owner 2026-10-11)'
    if plain=='euras' and r['route']=='IMG':
        r['route']='CLOZE'; r['notes']=(r['notes']+'; ' if r['notes'] else '')+'route → CLOZE: prices are in litai (owner 2026-10-11); litas gets the coin card'
    r['card_type']=R2C[r['route']]
    r['image_possible']={'IMG':'yes'}.get(r['route'],'no') if r['image_possible'] not in ('weak',) else 'weak'
    r['phase_name']=PHASES[r['phase']]
    r['status']=r['status'] or 'pending'
    fr=freq.get(base(key)); r['freq_rank']=r['freq_rank'] or (fr if fr else '')
    checks=[r['check']] if r['check'] else []
    # pron
    if not r['lt_pron'] and ' ' not in key and r['type'] not in ('PHRASE','SENTENCE'):
        w=wikt(key) or wikt(key.lower()); k=kirtis(key,r['type']) or kirtis(key.lower(),r['type'])
        if w and w['pron']:
            r['lt_pron']=w['pron']; r['pron_src']='en.wiktionary'
            if k and base(k)==base(w['pron']) and norm_accent(k).lower()!=w['pron'].lower(): checks.append(f'stress: Wiktionary {w["pron"]} vs kirtis.info {k} — DISAGREE, verify')
            elif k: checks.append('stress: Wiktionary = kirtis.info')
            else: checks.append('stress: Wiktionary only')
        elif k:
            r['lt_pron']=norm_accent(k); r['pron_src']='kirtis.info (engine)'; checks.append('stress: kirtis.info only (rule engine) — verify')
        else:
            checks.append('stress: NOT FOUND (Wiktionary, kirtis.info) — needs DLKŽ lookup')
        if w:
            if r['type']=='V' and w['pres3'] and not r['pres3']:
                r['pres3'],r['past3']=w['pres3'],w['past3']; checks.append('principal parts: Wiktionary')
            if r['type']=='N' and w['gender'] and not r['gender']:
                r['gender']={'m':'M','f':'F','m-p':'M pl','f-p':'F pl'}.get(w['gender'],w['gender']); checks.append('gender: Wiktionary')
            if r['type']=='A' and w['fem'] and not r['fem'] and accent_ok(w['fem'],fem(key)): r['fem']=base(w['fem']) if False else re.sub(r'[̀́̃]','',unicodedata.normalize('NFD',w['fem'])); r['fem']=unicodedata.normalize('NFC',r['fem'])
        if r['type']=='V' and not r['pres3']: checks.append('principal parts: NOT FOUND — verb_flashcards.py / DLKŽ')
    elif not r['lt_pron'] and ' ' in key and r['type'] not in ('PHRASE','SENTENCE'):
        parts=[]; ok=True
        for p in key.split(' '):
            w=wikt(p); k=kirtis(p,'N') or kirtis(p,'A') or kirtis(p,'V') or kirtis(p,'ADV') or kirtis(p,'P') or kirtis(p,'PREP')
            if not k and isinstance(KC.get(p),list) and KC[p]:
                k=next((x['word'] for x in KC[p] if accent_ok(x['word'],p)),'')
            a=(w['pron'] if w and w['pron'] else '') or (norm_accent(k) if k else '')
            if not a: ok=False; break
            parts.append(a)
        parts=[(a[0].lower()+a[1:]) if p0[0].islower() else a for a,p0 in zip(parts,key.split(' '))]
        if ok: r['lt_pron']=' '.join(parts); r['pron_src']='per word (Wiktionary/kirtis.info)'; checks.append('stress: assembled per word — verify phrase stress')
        else: checks.append('stress: multiword, not all parts found')
    if r['lt_pron'] and not accent_ok(r['lt_pron'],key): warnings.append(f"{r['id']} pron/target mismatch: {r['lt_pron']} vs {key}")
    # grammar
    if r['type']=='N':
        if not r['gender']: r['gender']=guess_gender(key); checks.append('gender: by ending (rule)')
        if not r['gen_sg']:
            g=gen_sg(key,r['gender'])
            if g: r['gen_sg']=g; checks.append('gen_sg: rule-derived')
    if r['type']=='A' and not r['fem'] and ' ' not in key:
        r['fem']=fem(key); checks.append('fem: rule')
    # example
    if r['route'] in ('CLOZE','PAIR','PHRASE'):
        ex=EX.get(plain) or EX.get(key) or EX.get(key.lower())
        if ex: r['example_lt'],r['example_en']=ex
        elif r['route']!='PHRASE': warnings.append(f"{r['id']} no example for {plain}")
        if r['route']=='PHRASE' and not ex: r['example_lt'],r['example_en']=plain,r['english']
    r['check']='; '.join(c for c in checks if c)
    return r

def main():
  pass
# ---- 1. queue rows ----
seen_lt=set(deck_lt)
for q in queue:
    qid=q['id']
    if qid in EXCLUDE: continue
    if q['status']=='review-duplicate' and qid not in KEEP_DUP: continue
    r=new_row(**{c:q.get(c,'') for c in q if c in COLS})
    r['source']='queue'
    fx=FIX.get(qid,{})
    notes=[q['notes']] if q['notes'] else []
    if qid in KEEP_DUP: notes.append('kept despite dup flag: '+KEEP_DUP[qid]); r['status']='pending'
    for k,v in fx.items():
        if k=='notes_add': notes.append(v)
        elif k=='check': r['check']=v
        else: r[k]=v
    route={'image':'IMG','sentence':'CLOZE','phrase':'PHRASE'}.get(q['card_type'],'CLOZE')
    if q['type']=='SENTENCE': route='PHRASE'
    if fx.get('route'): route=fx['route']
    if qid in REROUTE_CLOZE and route=='IMG':
        route='CLOZE'; notes.append('re-routed IMG→CLOZE: '+REROUTE_CLOZE[qid])
    if qid in PHRASE_TO_CLOZE and route=='PHRASE':
        route='CLOZE'; notes.append('re-routed PHRASE→CLOZE: '+PHRASE_TO_CLOZE[qid])
    r['route']=route
    # weekday/month card_text: numerals only (no English on the card)
    if q['category']=='Time' and ('calendar' in q['card_text']):
        import re as _re
        days=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        months=['January','February','March','April','May','June','July','August','September','October','November','December']
        if q['english'] in days: r['card_text']=f'the numeral "{days.index(q["english"])+1}" in the marked column of a seven-column week strip'
        elif q['english'] in months: r['card_text']=f'the numeral "{months.index(q["english"])+1}" on the calendar header'
        r['image_possible']=''; notes.append('card_text changed from the English day/month name (would letter English on the card) to the numeral;  with lettering allowed the week strip carries the abbreviations Pr…Sk — CLOZE alternative if it still misreads: '+('{%sį} einu į darbą.'%q['lithuanian_TARGET'].capitalize()[:-2] if q['english'] in days else 'Mano gimtadienis – {%s}.'%q['lithuanian_TARGET']) )
    # DEFER → P-K
    sug=offlist.get(qid,{}).get('suggestion','')
    if sug.startswith('DEFER'): r['phase']='P-K'; notes.append('DEFER per a2_rebase/queue_offlist.csv (off-list, not top-3,000)')
    elif q['phase']=='P-G': r['phase']='P-D'
    elif q['phase'] in PHASES: r['phase']=q['phase']
    else: r['phase']='P-F'
    if route=='CLOZE' and r['phase']=='P-A' and q['category'] in ('Time','People','Society'): pass
    r['notes']='; '.join(n for n in notes if n)
    r['dup_check']=q['dup_check']
    out.append(finish(r)); seen_lt.add(base(re.sub(r'\s*\(.*\)','',r['lithuanian_TARGET'])))

# ---- 2. official-list rows ----
POS2T={'N':'N','V':'V','A':'A','ADV':'ADV','PRON':'P','PREP':'PREP','CONJ':'CONJ','NUM':'NUM','INTJ':'PHRASE','PHRASE':'PHRASE','PREP/ADV':'PREP'}
FUNC={'P','PREP','CONJ','ADV','NUM','Q'}
nid=985
def nextid():
    global nid; s=f'A2-{nid:04d}'; nid+=1; return s
staged=[]
for t in triage:
    e=t['entry'].strip(); rt0=t['route']
    rt,reason=ROUTE.get(e,(rt0,''))
    if rt not in ('IMG','CLOZE','PHRASE','PAIR'): continue
    key=e if e!='Vogti' else 'vogti'
    if base(key) in seen_lt: continue
    typ=POS2T.get(t['pos'],'N')
    if rt=='PHRASE': typ='PHRASE' if typ in ('PHRASE','ADV','A','V','N') and (' ' in key or t['pos'] in ('INTJ','PHRASE')) else typ
    NOT_A1={'seimas','savivaldybė','ministras','ministras pirmininkas','meras','direktorius','teisėjas','bauda','partija','kandidatas','deklaracija','deklaruoti','konkursas','pensija','specialistas','procentai','suma','balsuoti','dalyvauti','reikalas','akcija','sąlygos','prašymas','pristatyti','kokybė','kiekis','varžybos','vykti','padėtis','pavadinimas','sugebėti','pažymėjimas','tam tikras','bendras','uostas','dujos','elektra','futbolas','krepšinis','vartotojas','rodyti','parodyti','manyti','valdžia'}
    level='A1' if (key in LEVEL_A1 or (t['freq_rank'] and int(t['freq_rank'])<=1000 and key not in NOT_A1)) else 'A2'
    gloss=GLOSS.get(e,t['english'])
    notes=[t['note']] if t['note'] else []
    if reason: notes.append((f'route {rt0}→{rt}: ' if rt!=rt0 else 'staging hint: ')+reason)
    cat={'N':'Nouns','V':'Verbs','A':'Adjectives','ADV':'Adverbs','P':'Pronouns','PREP':'Prepositions','CONJ':'Conjunctions','NUM':'Numbers','PHRASE':'Phrases','Q':'Question words'}.get(typ,'Misc')
    if ' kalba' in key: cat='Languages'
    if rt=='PHRASE': phase='P-D'
    elif rt=='IMG': phase='P-H'
    elif typ in FUNC: phase='P-B'
    else: phase='P-I'
    r=new_row(id=None,phase=phase,level=level,category=cat,english=gloss,type=typ,lithuanian_TARGET=key,route=rt,source='official',freq_rank=t['freq_rank'],notes='; '.join(notes),dup_check=t['overlap'])
    staged.append(r); seen_lt.add(base(key))

# ---- 3. additions ----
for lt,en,typ,rt,level,cat,src,fr,note in ADD:
    key=re.sub(r'\s*\(.*\)','',lt).strip()
    if base(key) in seen_lt and '(' not in lt: continue
    if rt=='PHRASE': phase='P-D'
    elif typ in FUNC or typ=='Q': phase='P-B'
    elif typ=='P': phase='P-B'
    elif rt=='IMG' and level=='A1' and cat in ('Time','Numbers'): phase='P-A'
    else: phase='P-J'
    r=new_row(id=None,phase=phase,level=level,category=cat,english=en,type=typ,lithuanian_TARGET=lt,route=rt,source=src,freq_rank=fr or '',notes=note)
    staged.append(r); seen_lt.add(base(key))

# order staged rows by phase then category then target, assign ids
order={p:i for i,p in enumerate(PHASES)}
staged.sort(key=lambda r:(order[r['phase']],r['category'],base(r['lithuanian_TARGET'])))
for r in staged:
    r['id']=nextid(); out.append(finish(r))

# staging: subject phrases into the CSV, staging lines into a2_staging.json
stg_notes={}; no_subject=[]
for r in out:
    if r['route']!='IMG': continue
    key=r['lithuanian_TARGET']; k2=re.sub(r'\s*\(.*\)','',key).strip()
    sp=STG.get(key) or STG.get(k2)
    if sp:
        if sp[0]: r['subject_phrase_EN']=sp[0]
        if sp[1]: stg_notes[r['id']]=sp[1]
    if not r['subject_phrase_EN']: no_subject.append(f"{r['id']} {key}")
json.dump({'_about':'Per-card staging lines for the A2 IMG rows (Fable, 2026-10-11), keyed by a2_wordlist.csv id; same format as card_notes.json, inserted after the Subject sentence by deck_builder.build_call. Written to staging_guide.md: the main picture alone carries the word; insets support; positive phrasing; 1981 free Lithuania.',
           'notes':stg_notes},open(os.path.join(ROOT,'a2_build','a2_staging.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('staging lines',len(stg_notes),'IMG rows without subject phrase',len(no_subject))
open(os.path.join(ROOT,'a2_build','build_warnings.txt'),'a',encoding='utf-8').write('\nIMG rows without subject phrase:\n'+'\n'.join(no_subject))
# final order: by phase, keep queue order inside
out.sort(key=lambda r:(order[r['phase']], r['id']))
with open(os.path.join(ROOT,'a2_build','a2_wordlist.csv'),'w',encoding='utf-8',newline='') as f:
    w=csv.DictWriter(f,fieldnames=COLS); w.writeheader(); w.writerows(out)
print('rows',len(out))
print('by route',Counter(r['route'] for r in out))
print('by phase',Counter(r['phase'] for r in out))
print('by level',Counter(r['level'] for r in out))
print('by source',Counter(r['source'] for r in out))
print('pron blank (single word, non-phrase):',sum(1 for r in out if not r['lt_pron'] and r['type'] not in('PHRASE','SENTENCE')))
print('warnings',len(warnings))
open(os.path.join(ROOT,'a2_build','build_warnings.txt'),'w',encoding='utf-8').write('\n'.join(warnings))
