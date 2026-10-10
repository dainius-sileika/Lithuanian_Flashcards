import json, numpy as np
from PIL import Image
def srgb2lab(rgb):
    c=rgb/255.0; c=np.where(c<=0.04045,c/12.92,((c+0.055)/1.055)**2.4)
    M=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
    xyz=c@M.T; xyz/=np.array([0.95047,1.0,1.08883])
    f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
    return np.stack([116*f[:,1]-16,500*(f[:,0]-f[:,1]),200*(f[:,1]-f[:,2])],1)
def paper(path):
    """Strict paper estimate: the dominant light, low-chroma colour = mode of L in 1-unit bins among low-chroma pixels, upper part of distribution."""
    im=Image.open(path).convert('RGB'); w,h=im.size
    px=np.asarray(im.crop((int(w*.03),int(h*.10),int(w*.97),int(h*.90)))).reshape(-1,3).astype(float)
    lab=srgb2lab(px[::3])
    chroma=np.hypot(lab[:,1],lab[:,2])
    m=(lab[:,0]>60)&(chroma<32)&(lab[:,2]>0)   # light, warm, low chroma
    sel=lab[m]
    if len(sel)<200: return None
    hist,edges=np.histogram(sel[:,0],bins=np.arange(60,101,1))
    # paper = most populated bin among the upper half of the mass
    peak=np.argmax(hist); Lp=edges[peak]+0.5
    near=sel[np.abs(sel[:,0]-Lp)<2]
    return round(float(Lp),1), round(float(np.median(near[:,2])),1), round(float(m.mean()),2)
if __name__=='__main__':
    k=json.load(open('confirm_web_key.json')); out={}
    for i,v in k.items():
        out[f"{v['variant']}@{v['card']}" if v['variant']=='orig' else v['variant']]=paper(f'confirm_site/img/{i}.jpg')
    json.dump(out,open('confirm_paper_tone_strict.json','w'),indent=1)
    for kk,vv in sorted(out.items(), key=lambda kv:(kv[1] or (0,0,0))[0]): print(kk,vv)
