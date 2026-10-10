import json, numpy as np, random
from PIL import Image
from collections import defaultdict
res=json.load(open('survey_results_owner_unblinded.json'))
des=json.load(open('survey_design.json'))
key=json.load(open('/mnt/user-data/uploads/51 Lithuanian Language & Culture/51.04 Lithuanian Flashcard Project/style_lab/2026-10-10_06_blind_survey/web_key.json'))
inv={(v['round'],v['variant']):i for i,v in key.items()}
A=des['attributes']

# observed composition overrides for new images (from viewing)
obs_comp={'F4_g2_miestas':'bleed','F4bleed_g2_miestas':'bleed','F4ref_g2_miestas':'float','F4_sun_miestas':'bleed',
 'F4_g2_gydytojas':'float','F4dun_g2_gydytojas':'float','F4_sun_gydytojas':'float','F4_15_gydytojas':'float',
 'F4_g2_eiti':'float','F4arrow_g2_eiti':'float','F4_sun_eiti':'bleed','F4arrow_sun_eiti':'bleed',
 'F4_g2_suo':'float','F4dun_g2_suo':'float','F4_g2low_suo':'float','F4_sun_suo':'float','F4_flare_suo':'float',
 'F4_sun_klubas':'bleed','F4ref_sun_klubas':'bleed','F4_g2_klubas':'bleed','F4ovr_g2_klubas':'bleed','F4ovr_sun_klubas':'bleed',
 'F4_g2_seima':'float','F4_g2b_seima':'float','F4_sun_seima':'bleed','F4_15_seima':'float',
 'F4_g2_paltas':'float','F4_sun_paltas':'float','F4dun_sun_paltas':'float','F4_flare_paltas':'float',
 'F4_g2_pjauti':'float','F4bleed_g2_pjauti':'bleed','F4_sun_pjauti':'float','F4_g2low_pjauti':'bleed',
 'F4_g2_minia':'float','F4_sun_minia':'bleed','F4ref_g2_minia':'float','F4ref_sun_minia':'bleed',
 'F4_g2_mokykla':'float','F4bleed_g2_mokykla':'bleed','F4_sun_mokykla':'bleed','F4_flare_mokykla':'float',
 'F4_g2_lova':'float','F4dun_g2_lova':'float','F4_g2low_lova':'float','F4_sun_lova':'float','F4_flare_lova':'float','F4_15_lova':'float',
 'F4_g2_vestuves':'float','F4_sun_vestuves':'float','F4_sunb_vestuves':'float','F4ref_sun_vestuves':'float','F4_15_vestuves':'float'}
# existing variants' observed composition varies by card; override for cards where they appear
obs_existing={('F3_sun',1):'bleed',('F3_sun',2):'float',('F3_sun',5):'bleed',('F3_sun',6):'bleed',('F3_sun',7):'float',('F3_sun',9):'float',('F3_sun',13):'float',
 ('F1_sun',7):'float',('sun_B',8):'bleed',('g2_A',8):'bleed',('g2_old',2):'float',('g2_old',4):'float',('sun_old',1):'bleed',('sun_old',5):'bleed',('flare_old',10):'bleed',
 ('F3_g2',1):'float',('F3_g2',2):'float',('F3_g2',3):'float',('F3_g2',5):'bleed',('F3_g2',6):'float',('F3_g2',8):'float',('F3_g2',9):'float',('F3_g2',10):'float',('F3_g2',13):'float',
 ('F2_g2',6):'float',('F1_g2',10):'float',('F1_sunlow',3):'bleed'}

def paper_tone(path):
    im=Image.open(path).convert('RGB'); w,h=im.size
    px=np.asarray(im.crop((int(w*.04),int(h*.12),int(w*.96),int(h*.88)))).reshape(-1,3).astype(float)
    r,g,b=px[:,0],px[:,1],px[:,2]
    mx=px.max(1); mn=px.min(1); sat=(mx-mn)/np.maximum(mx,1)
    paper=px[(mx>150)&(sat<0.35)]  # light low-saturation pixels = paper
    if len(paper)<100: paper=px
    # convert to Lab (approx, sRGB -> XYZ -> Lab)
    def srgb2lab(rgb):
        c=rgb/255.0; c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
        M=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
        xyz=c@M.T; xyz/=np.array([0.95047,1.0,1.08883])
        f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
        return np.stack([116*f[:,1]-16,500*(f[:,0]-f[:,1]),200*(f[:,1]-f[:,2])],1)
    lab=srgb2lab(paper); return float(np.median(lab[:,0])), float(np.median(lab[:,2]))

rows=[]
for R in res['rounds']:
    r=R['round']
    if r==12: continue
    n=len(R['ranking']); w=0.5 if r==9 else 1.0
    for e in R['ranking']:
        v=e['variant']; a=dict(A[v])
        comp=obs_comp.get(v, obs_existing.get((v,r), a['composition']))
        L,b=paper_tone(f"survey_site/img/{inv[(r,v)]}.jpg")
        rows.append(dict(round=r,card=R['card'],variant=v,rank=e['rank'],n=n,w=w,
            borda=(n-e['rank'])/(n-1),ship=int(e['ship']),comment=e['comment'],
            model=a['model'],fam=a['prompt_family'],comp=comp,refs=int(a['refs']),quality=a['quality'],
            people=a['people_block'],print_=a['print_block'],ovr=int(a.get('subject_override',False)),
            paperreq=a['paper'],L=L,bstar=b))
json.dump(rows,open('survey_rows.json','w'),indent=1)
print(len(rows),'rows')

# ---- per-round table
print('\nPER ROUND')
for R in res['rounds']:
    if R['round']==12: continue
    rk=[(e['rank'],e['variant'],e['ship']) for e in R['ranking']]
    o=[e['rank'] for e in R['ranking'] if e['variant']=='orig'][0]
    print(R['round'],R['card'],'orig rank %d/%d'%(o,len(rk)),' | ',' > '.join(f"{v}{'*' if s else ''}" for _,v,s in rk))

def group(keyf,label):
    g=defaultdict(list)
    for x in rows: g[keyf(x)].append(x)
    print('\n'+label)
    for k,xs in sorted(g.items(),key=lambda kv:-np.average([x['borda'] for x in kv[1]],weights=[x['w'] for x in kv[1]])):
        bs=[x['borda'] for x in xs]; ws=[x['w'] for x in xs]
        print(f"  {str(k):28s} n={len(xs):2d}  borda={np.average(bs,weights=ws):.2f}  ship={np.mean([x['ship'] for x in xs]):.2f}  L={np.mean([x['L'] for x in xs]):.1f} b*={np.mean([x['bstar'] for x in xs]):.1f}")
group(lambda x:x['model'],'BY MODEL')
group(lambda x:x['fam'],'BY PROMPT FAMILY')
group(lambda x:(x['model'],x['fam']),'BY MODEL x FAMILY')
group(lambda x:x['comp'],'BY OBSERVED COMPOSITION')
group(lambda x:x['quality'],'BY QUALITY')
group(lambda x:x['refs'],'BY REFS')
group(lambda x:x['people'],'BY PEOPLE BLOCK')
group(lambda x:x['paperreq'],'BY PAPER REQUESTED')

# ---- paper tone vs borda
import math
L=np.array([x['L'] for x in rows]); B=np.array([x['bstar'] for x in rows]); S=np.array([x['borda'] for x in rows])
print('\nPAPER TONE: corr(borda, L)=%.2f  corr(borda, b*)=%.2f'%(np.corrcoef(S,L)[0,1],np.corrcoef(S,B)[0,1]))
for x in sorted(rows,key=lambda x:x['L']):
    pass
print('orig paper:', [(x['round'],round(x['L'],1),round(x['bstar'],1)) for x in rows if x['variant']=='orig'])
print('F4dun vs F4 pairs (L,b*):')
for pr in [(2,'F4_g2_gydytojas','F4dun_g2_gydytojas'),(4,'F4_g2_suo','F4dun_g2_suo'),(11,'F4_g2_lova','F4dun_g2_lova'),(7,'F4_sun_paltas','F4dun_sun_paltas')]:
    a=[x for x in rows if x['round']==pr[0] and x['variant']==pr[1]][0]; b=[x for x in rows if x['round']==pr[0] and x['variant']==pr[2]][0]
    print(f"  r{pr[0]} {pr[1]}: rank {a['rank']} L{a['L']:.0f} b{a['bstar']:.0f} | {pr[2]}: rank {b['rank']} L{b['L']:.0f} b{b['bstar']:.0f}")

# ---- direct one-attribute contrasts
print('\nDIRECT CONTRASTS (rank a vs rank b; lower is better)')
pairs=[('composition float vs bleed (g2,F4)',[(1,'F4_g2_miestas','F4bleed_g2_miestas'),(8,'F4_g2_pjauti','F4bleed_g2_pjauti'),(10,'F4_g2_mokykla','F4bleed_g2_mokykla')]),
 ('paper bright vs dun',[(2,'F4_g2_gydytojas','F4dun_g2_gydytojas'),(4,'F4_g2_suo','F4dun_g2_suo'),(11,'F4_g2_lova','F4dun_g2_lova'),(7,'F4_sun_paltas','F4dun_sun_paltas')]),
 ('arrows default vs black',[(3,'F4_g2_eiti','F4arrow_g2_eiti'),(3,'F4_sun_eiti','F4arrow_sun_eiti')]),
 ('quality medium vs low (g2)',[(4,'F4_g2_suo','F4_g2low_suo'),(8,'F4_g2_pjauti','F4_g2low_pjauti'),(11,'F4_g2_lova','F4_g2low_lova')]),
 ('text vs refs',[(1,'F4_g2_miestas','F4ref_g2_miestas'),(5,'F4_sun_klubas','F4ref_sun_klubas'),(9,'F4_g2_minia','F4ref_g2_minia'),(9,'F4_sun_minia','F4ref_sun_minia'),(13,'F4_sun_vestuves','F4ref_sun_vestuves')]),
 ('klubas plain vs override',[(5,'F4_g2_klubas','F4ovr_g2_klubas'),(5,'F4_sun_klubas','F4ovr_sun_klubas')]),
 ('F4 g2 vs F4 sun (same card)',[(1,'F4_g2_miestas','F4_sun_miestas'),(2,'F4_g2_gydytojas','F4_sun_gydytojas'),(3,'F4_g2_eiti','F4_sun_eiti'),(4,'F4_g2_suo','F4_sun_suo'),(5,'F4_g2_klubas','F4_sun_klubas'),(6,'F4_g2_seima','F4_sun_seima'),(7,'F4_g2_paltas','F4_sun_paltas'),(8,'F4_g2_pjauti','F4_sun_pjauti'),(9,'F4_g2_minia','F4_sun_minia'),(10,'F4_g2_mokykla','F4_sun_mokykla'),(11,'F4_g2_lova','F4_sun_lova'),(13,'F4_g2_vestuves','F4_sun_vestuves')]),
 ('F3 g2 vs F3 sun (same card)',[(1,'F3_g2','F3_sun'),(2,'F3_g2','F3_sun'),(6,'F3_g2','F3_sun'),(9,'F3_g2','F3_sun'),(13,'F3_g2','F3_sun')]),
 ('F3_g2 vs F4_g2 (same card)',[(1,'F3_g2','F4_g2_miestas'),(2,'F3_g2','F4_g2_gydytojas'),(3,'F3_g2','F4_g2_eiti'),(6,'F3_g2','F4_g2_seima'),(8,'F3_g2','F4_g2_pjauti'),(9,'F3_g2','F4_g2_minia'),(10,'F3_g2','F4_g2_mokykla'),(13,'F3_g2','F4_g2_vestuves')]),
 ('orig vs F4 on 1.5',[(2,'orig','F4_15_gydytojas'),(6,'orig','F4_15_seima'),(11,'orig','F4_15_lova'),(13,'orig','F4_15_vestuves')]),
 ('F4_15 vs F4_g2',[(2,'F4_15_gydytojas','F4_g2_gydytojas'),(6,'F4_15_seima','F4_g2_seima'),(11,'F4_15_lova','F4_g2_lova'),(13,'F4_15_vestuves','F4_g2_vestuves')]),
 ('flare F4 vs g2 F4',[(4,'F4_flare_suo','F4_g2_suo'),(7,'F4_flare_paltas','F4_g2_paltas'),(10,'F4_flare_mokykla','F4_g2_mokykla'),(11,'F4_flare_lova','F4_g2_lova')]),
 ('seed pairs',[(6,'F4_g2_seima','F4_g2b_seima'),(13,'F4_sun_vestuves','F4_sunb_vestuves')]),
]
def rk(r,v): return [x for x in rows if x['round']==r and x['variant']==v][0]
for label,ps in pairs:
    out=[]; wins=0
    for r,a,b in ps:
        ra,rb=rk(r,a)['rank'],rk(r,b)['rank']; out.append(f"r{r}:{ra}v{rb}"); wins+= (ra<rb)
    print(f"  {label:34s} a-wins {wins}/{len(ps)}  ", ' '.join(out))

# ---- regression with round fixed effects, bootstrap over rounds
feat=lambda x:[x['model']=='gpt-image-2',x['model']=='gpt-image-2.5-sunburst',x['model']=='gpt-image-2.5-flare',
               x['people']=='F3', x['print_']=='F2', x['comp']=='bleed', x['refs'], x['quality']=='low',
               x['fam'] in ('shipped',), (x['L']-80)/5, x['bstar']/10]
names=['g2','sunburst','flare','peopleF3','printF2','bleed','refs','low','shippedprompt','paperL(/5)','paperB*(/10)']
X=np.array([feat(x) for x in rows],float); y=np.array([x['borda'] for x in rows]); w=np.array([x['w'] for x in rows])
rounds=sorted(set(x['round'] for x in rows)); R=np.array([[x['round']==r for r in rounds] for x in rows],float)
def fit(idx):
    Xi=np.hstack([X[idx],R[idx]]); yi=y[idx]; wi=w[idx]
    lam=np.diag([0.5]*X.shape[1]+[1e-3]*R.shape[1])
    W=np.diag(wi); beta=np.linalg.solve(Xi.T@W@Xi+lam, Xi.T@W@yi); return beta[:X.shape[1]]
b0=fit(np.arange(len(rows)))
random.seed(1); bs=[]
for _ in range(400):
    rs=[random.choice(rounds) for _ in rounds]; idx=np.concatenate([np.where(np.array([x['round']==r for x in rows]))[0] for r in rs]); bs.append(fit(idx))
bs=np.array(bs)
print('\nREGRESSION (normalised Borda, round fixed effects, ridge 0.5; bootstrap over rounds, 400 reps)')
for i,nm in enumerate(names):
    lo,hi=np.percentile(bs[:,i],[5,95]); print(f"  {nm:14s} {b0[i]:+.2f}  [{lo:+.2f},{hi:+.2f}]")
