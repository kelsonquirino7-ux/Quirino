import numpy as np, cv2
from PIL import Image, ImageEnhance
im=cv2.cvtColor(cv2.imread('v8.png'),cv2.COLOR_BGR2RGB); H,W=im.shape[:2]; k=W/1200; P=lambda v:int(round(v*k))
f=im.astype(np.float32); R,G,B=f[...,0],f[...,1],f[...,2]
red=((R>180)&(G<110)&(B<100)).astype(np.uint8)
roi=np.zeros((H,W),np.uint8); roi[P(570):P(728),P(470):P(775)]=1
red&=roi
cnts,_=cv2.findContours(red,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
c=max(cnts,key=cv2.contourArea)
ell=cv2.fitEllipse(c); print('elipse',[(round(a/k,1)) for a in ell[0]],[round(a/k,1) for a in ell[1]],ell[2])
mask=np.zeros((H,W),np.uint8); cv2.ellipse(mask,ell,255,-1)
mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(P(26)|1,P(26)|1)))
a=cv2.GaussianBlur(cv2.erode(mask,np.ones((P(6),P(6)),np.uint8)).astype(np.float32)/255,(0,0),P(3))
dy=P(20); M=np.float32([[1,0,0],[0,1,dy]])
a2=cv2.warpAffine(a,M,(W,H)); t2=cv2.warpAffine(f,M,(W,H))
# preencher o crescente que fica descoberto em cima
hole=(mask>0).astype(np.uint8)*255
hole=cv2.dilate(hole,np.ones((P(4),P(4)),np.uint8))
s=2; sm=cv2.resize(im,(W//s,H//s),interpolation=cv2.INTER_AREA)
hs=cv2.dilate(cv2.resize(hole,(W//s,H//s),interpolation=cv2.INTER_NEAREST),np.ones((3,3),np.uint8))
# preenchimento suave: gradiente quadratico do anel ao redor
sm32=sm.astype(np.float32); h2,w2=hs.shape
ring=(cv2.dilate(hs,np.ones((P(14)//s,P(14)//s),np.uint8))>0)&~(hs>0)
ys,xs=np.nonzero(ring)
def FF(x,y): x=x/w2;y=y/h2; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],1)
yy,xx=np.mgrid[0:H,0:W]
Fa=FF((xx/s).ravel().astype(np.float32),(yy/s).ravel().astype(np.float32))
fill=np.zeros_like(f)
for c in range(3):
    co,*_=np.linalg.lstsq(FF(xs.astype(float),ys.astype(float)),sm32[ys,xs,c],rcond=None); fill[...,c]=(Fa@co).reshape(H,W)
ha=cv2.GaussianBlur(hole.astype(np.float32)/255,(0,0),P(3))[...,None]
base=f*(1-ha)+(fill+np.random.normal(0,1.2,f.shape).astype(np.float32))*ha
out=base*(1-a2[...,None])+t2*a2[...,None]
o=Image.fromarray(np.clip(out,0,255).astype(np.uint8)); o.save('v9.png')
o.resize((1200,794)).save('v9-prev.jpg',quality=88)
z=o.crop([P(400),P(500),P(850),P(794)]).resize((1000,653)); z.save('v9-zoom.jpg'); ImageEnhance.Contrast(z).enhance(2.5).save('v9-contraste.jpg')
