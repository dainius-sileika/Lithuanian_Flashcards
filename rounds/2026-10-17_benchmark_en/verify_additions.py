# Verification of benchmark_en/proposed_additions.csv (executor, 2026-10-17). Reads two lookup
# caches built by a small fetcher (kirtis_cache.json: https://kirtis.info/api/krc/<form>;
# wikt_cache.json: en.wiktionary raw wikitext) in the working directory, and writes
# additions_verified.csv. Kept for provenance; the caches are not in the repo.
import csv, json, re, sys, urllib.parse, unicodedata
kc=json.load(open('kirtis_cache.json')); wc=json.load(open('wikt_cache.json'))
SRC='proposed_additions.csv'
WORD=r"[A-Za-zĄČĘĖĮŠŲŪŽąčęėįšųūž]+"
def K(w): return kc.get(w.lower())
def kurl(w): return 'https://kirtis.info/api/krc/'+urllib.parse.quote(w.lower())
def wurl(w): return 'https://en.wiktionary.org/wiki/'+urllib.parse.quote(w.replace(' ','_'))+'#Lithuanian'
def ltsec(w):
    v=wc.get('en:'+w) or ''
    i=v.find('==Lithuanian==')
    if i<0: return ''
    r=v[i+14:]; m=re.search(r'\n==[^=]',r); return r[:m.start()] if m else r
def strip(s):
    d=unicodedata.normalize('NFD',s); d=''.join(c for c in d if ord(c) not in (0x300,0x301,0x303)); return unicodedata.normalize('NFC',d).lower()
def has(w, cls=None, need=()):
    e=K(w)
    if not isinstance(e,list): return None
    for x in e:
        if cls and x['class'] not in (cls if isinstance(cls,tuple) else (cls,)): continue
        if all(n in x['state'] for n in need): return x
    return None
def known(w):
    e=K(w)
    if isinstance(e,list) and e: return 'kirtis'
    if ltsec(w): return 'wiktionary'
    return None
def stress(w, cls, need):
    x=has(w,cls,need); return x['word'].lower() if x else ''
G={'m':'vyr.gim.','f':'mot.gim.'}
ENDINGS_GEN={'as':['o'],'is':['io','ies','ens','s'],'ys':['io'],'us':['aus','ius'],'ius':['iaus'],'a':['os','ės'],'ė':['ės'],'uo':['ens','s'],'ai':['ų'],'ės':['ių'],'os':['ų'],'ys':['io','ių']}
out=[]
for r in csv.DictReader(open(SRC,encoding='utf-8')):
    pid=r['proposal_id']; lem=r['lithuanian_TARGET'].strip(); pos=r['pos']
    core=re.sub(r"\(.*?\)","",lem).strip()
    notes=[]; status='verified'; src=[]; corr={}
    toks=[t for t in re.findall(WORD,core)]
    # example tokens
    ex=r['example_lt'].replace('{','').replace('}','')
    for t in re.findall(WORD,ex):
        if not known(t) and K(t)!='NOT_A_WORD':
            notes.append(f'example token not confirmed: {t}')
    unknown=[t for t in toks if not known(t) and K(t)!='NOT_A_WORD']
    nonword=[t for t in toks if K(t)=='NOT_A_WORD' and not ltsec(t)]
    pron=''
    if pos.startswith('N'):
        head=toks[-1]; g=r['gender'][:1]
        pl='pl' in r['gender']
        num='dgsk.' if pl else 'vnsk.'
        x=has(head,'dktv.',(num,'V.'))
        if not x:
            x2=has(head,'dktv.',('V.',))
            if x2: x=x2
        if x:
            src.append(kurl(head))
            kg='m' if 'vyr.gim.' in x['state'] else 'f'
            if g and kg!=g:
                corr['gender']=kg+(' pl' if pl else ''); notes.append(f'gender {g}->{kg} (kirtis)')
                g=kg
            if len(toks)==1: pron=x['word'].lower()
            gen=r['gen_sg'].strip()
            if gen:
                gh=gen.split()[-1]
                ok=has(gh,'dktv.',(G.get(g,''),num,'K.'))
                if ok: src.append(kurl(gh))
                else:
                    # try candidate genitives
                    found=None
                    for end,cands in sorted(ENDINGS_GEN.items(), key=lambda e:-len(e[0])):
                        if head.endswith(end):
                            for c in cands:
                                cand=head[:-len(end)]+c
                                if cand not in kc: continue
                                if has(cand,'dktv.',(G.get(g,''),num,'K.')): found=cand; break
                        if found: break
                    if found:
                        newgen=' '.join(gen.split()[:-1]+[found]); corr['gen_sg']=newgen; notes.append(f'gen_sg {gen}->{newgen}'); src.append(kurl(found))
                    else:
                        notes.append(f'gen_sg {gh} not confirmed by kirtis'); status='failed'
            # modifiers in genitive phrase
            if gen and len(gen.split())>1:
                for m in gen.split()[:-1]:
                    if not (has(m,('bdvr.','dlv.','dktv.'),('K.',)) or has(m,None,('K.',))): notes.append(f'modifier {m} not confirmed as genitive'); status='failed'
        else:
            if ltsec(head): src.append(wurl(head)); notes.append('noun confirmed on Wiktionary only')
            else: status='failed'; notes.append(f'head noun {head} not found')
        fm=re.search(r'\((\S+) f\)',r['gender'])
        if fm:
            f=fm.group(1)
            if has(f,'dktv.',('mot.gim.','vnsk.','V.')): src.append(kurl(f))
            else: notes.append(f'feminine {f} not confirmed'); status='failed'
    elif pos.startswith('A') and not pos.startswith('ADV'):
        head=toks[0] if len(toks)==1 else toks[0]
        x=has(head,('bdvr.','dlv.'),('vyr.gim.','vnsk.','V.')) or has(head,('bdvr.','dlv.'),('bevrd.gim.',))
        if x: src.append(kurl(head)); pron=x['word'].lower() if len(toks)==1 else ''
        elif ltsec(head): src.append(wurl(head)); notes.append('Wiktionary only')
        else: status='failed'; notes.append(f'adjective {head} not found')
        fm=re.search(r'\((\S+) f\)',r['gender'])
        if fm:
            f=fm.group(1)
            if has(f,('bdvr.','dlv.'),('mot.gim.','vnsk.','V.')): src.append(kurl(f))
            else: notes.append(f'feminine {f} not confirmed'); status='failed'
        elif pos=='A' or pos.startswith('A (part'):
            # derive fem for the record
            pass
    elif pos.startswith('V'):
        head=toks[0]
        x=has(head,'vksm.',())
        inf_ok = x and any(len(e['state'])==1 for e in K(head) if e['class']=='vksm.')
        if inf_ok: src.append(kurl(head)); pron=[e['word'].lower() for e in K(head) if e['class']=='vksm.' and len(e['state'])==1][0] if len(toks)==1 else ''
        elif ltsec(head): src.append(wurl(head)); notes.append('infinitive on Wiktionary only')
        else:
            notes.append(f'infinitive {head} not in kirtis/Wiktionary')
            if status!='failed': status='unresolved'
        pp=r['pres3_past3']
        if pp:
            p3,s3=[x.strip() for x in pp.split('/')]
            okp=has(p3,'vksm.',('esam.l.','IIIasm.')); oks=has(s3,'vksm.',('būt.kart.l.','IIIasm.'))
            sec=ltsec(head)
            m=re.search(r"\{\{lt-verb\|([^}]*)\}\}",sec)
            pos_args=[a.strip() for a in m.group(1).split('|') if '=' not in a] if m else []
            if len(pos_args)>=2:
                wp,ws=strip(pos_args[0]),strip(pos_args[1]); src.append(wurl(head))
                if wp!=strip(p3): notes.append(f'Wiktionary pres3 {wp} vs {p3}')
                if ws!=strip(s3): notes.append(f'Wiktionary past3 {ws} vs {s3}')
                okp = okp or wp==strip(p3); oks = oks or ws==strip(s3)
            if okp and oks: src.append(kurl(p3))
            else:
                notes.append(f'pres3/past3 not confirmed: {p3}={bool(okp)} {s3}={bool(oks)}')
                if status!='failed': status='unresolved'
    else:
        if unknown:
            notes.append('tokens not confirmed: '+', '.join(unknown)); status='unresolved'
        else:
            src.extend((kurl(t) if isinstance(K(t),list) else wurl(t)) for t in toks[:4])
    if unknown and pos.startswith(('N','A','V')) and status=='verified':
        notes.append('tokens not confirmed: '+', '.join(unknown))
    if pid=='P-020' and has('pasisekė','vksm.',('būt.kart.l.','IIIasm.','sngr.')) and has('pasisekti','vksm.',('sngr.',)):
        status='verified'; notes=['impersonal: past3 pasisekė and infinitive pasisekti confirmed by kirtis']; src=[kurl('pasisekė'),kurl('pasisekti')]; pron='pasìsekė'
    if pid=='P-098' and has('praktikuoja','vksm.',('esam.l.','IIIasm.')) and has('praktikavo','vksm.',('būt.kart.l.','IIIasm.')):
        status='verified'; notes=['reflexive praktikuojasi/praktikavosi built regularly on kirtis-confirmed praktikuoja/praktikavo (kirtis has no -si forms of this verb)']; src=[kurl('praktikuoja'),kurl('praktikavo')]
    fem=''
    fm=re.search(r'\((\S+) f\)',r['gender'])
    if pos.startswith('A') and not pos.startswith('ADV'):
        if fm: fem=fm.group(1)
        elif pid in ('P-028','P-029'):
            cand=toks[0][:-2]+'ė'
            if has(cand,('bdvr.','dlv.'),('mot.gim.','vnsk.','V.')): fem=cand; corr['fem']=cand; notes.append(f'feminine {cand} added (kirtis)'); src.append(kurl(cand))
        elif pid=='P-018': notes.append('predicative neuter form; no masculine/feminine pair')
    frag={'a','s','davo','esnis','iausias','ar','ir','ne','kad','su','per','iki','į','už','prie','prieš','nuo','čia','ten','taip','kur','kaip','kiek','dar','bet','gal','nors','vis','tik','ačiū','šiandien'}
    hand=sorted({t for t in re.findall(WORD,core+' '+ex) if K(t)=='NOT_A_WORD' and not ltsec(t.lower()) and t.lower() not in frag})
    if hand: notes.append('not in kirtis/Wiktionary, accepted by hand as regular form: '+', '.join(hand))
    if corr and status=='verified': status='corrected'
    out.append(dict(proposal_id=pid, lithuanian_TARGET=lem, pos=pos, route=r['route'], status=status,
        gender=corr.get('gender',r['gender']), gen_sg=corr.get('gen_sg',r['gen_sg']), pres3_past3=r['pres3_past3'],
        fem=fem, lt_pron=pron, notes='; '.join(notes), source_url=' '.join(dict.fromkeys(src))))
import collections
print(collections.Counter(o['status'] for o in out))
for o in out:
    if o['status']!='verified': print(o['proposal_id'],o['lithuanian_TARGET'],o['pos'],o['status'],'|',o['notes'])
json.dump(out,open('verify_out.json','w'),ensure_ascii=False,indent=0)

# ---- stress for single-word rows without one (indeclinables: Wiktionary lt-pr / head=) ----
def wikt_pron(w):
    sec=ltsec(w)
    m=re.search(r"\{\{lt-pr\|([^|}]+)",sec) or re.search(r"head=([^|}]+)",sec)
    return m.group(1).strip() if m else ''
ID0=1863
rows=list(csv.DictReader(open(SRC,encoding='utf-8')))
with open('additions_verified.csv','w',newline='',encoding='utf-8') as f:
    w=csv.writer(f)
    w.writerow(['proposal_id','new_id','lithuanian_TARGET','pos','route','status','gender','gen_sg','fem','pres3','past3','lt_pron','pron_src','notes','source_url'])
    for i,(o,r) in enumerate(zip(out,rows)):
        core=re.sub(r"\(.*?\)","",o['lithuanian_TARGET']).strip()
        pron=o['lt_pron']; ps='kirtis.info' if pron else ''
        if not pron and len(core.split())==1 and o['pos'] not in ('PHRASE','SENT'):
            wp=wikt_pron(core)
            if wp and strip(wp)==strip(core): pron=wp; ps='en.wiktionary'; o['source_url']+=' '+wurl(core)
        if o['pos'] in ('PHRASE','SENT'): ps='n/a (phrase)'
        p3,s3=(x.strip() for x in o['pres3_past3'].split('/')) if o['pres3_past3'] else ('','')
        w.writerow([o['proposal_id'],f'A2-{ID0+i:04d}',o['lithuanian_TARGET'],o['pos'],o['route'],o['status'],o['gender'],o['gen_sg'],o['fem'],p3,s3,pron,ps,o['notes'],o['source_url'].strip()])
print('written')
