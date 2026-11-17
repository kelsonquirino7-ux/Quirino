import numpy as np, cv2
from PIL import Image
src='/home/user/Quirino/clientes/itamar-supermercado/entregas/2026-11-17-ano-novo-2027-lona/v2-lona-itamar-2027.jpg'
im=np.array(Image.open(src).convert('RGB')).astype(np.float32); H,W=im.shape[:2]; k=W/1200
s=8; sm=cv2.resize(im,(W//s,H//s),interpolation=cv2.INTER_AREA); h,w=sm.shape[:2]; ks=k/s
def rect(x0,y0,x1,y1):
    m=np.zeros((h,w),bool); m[int(y0*ks):int(y1*ks),int(x0*ks):int(x1*ks)]=True; return m
hole=rect(255,0,703,200)
# protect rock/debris/glove at right & fist below
mx=sm.max(2);mn=sm.min(2)
obj=(((mx-mn)<70)&(mx<215))|((mx>235)&(mn>215))  # gray stones, white glove
obj&=rect(698,0,800,260)
obj=cv2.dilate(obj.astype(np.uint8),np.ones((5,5),np.uint8))>0
hole&=~obj
ring=rect(180,0,800,260)&~rect(255,0,703,200)
r,g,b=sm[...,0],sm[...,1],sm[...,2]
bg=(r>180)&(g>110)&(b<140)&(r-b>90)   # golden background only
ring&=bg&~rect(0,0,250,400)  # skip head side partially
ys,xs=np.nonzero(ring)
def feats(x,y):
    x=x/w;y=y/h; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],1)
A=feats(xs.astype(float),ys.astype(float))
yy,xx=np.mgrid[0:H,0:W]
F=feats((xx/s).ravel().astype(np.float32),(yy/s).ravel().astype(np.float32))
fill=np.zeros_like(im)
for c in range(3):
    coef,*_=np.linalg.lstsq(A,sm[ys,xs,c],rcond=None); fill[...,c]=(F@coef).reshape(H,W)
fill+=np.random.normal(0,1.6,im.shape).astype(np.float32)
mask=cv2.resize(hole.astype(np.float32),(W,H),interpolation=cv2.INTER_NEAREST)
mask=cv2.GaussianBlur(mask,(0,0),5*k)
# keep objects crisp
objF=cv2.resize(obj.astype(np.float32),(W,H))
mask*= (1-np.clip(objF,0,1))
out=im*(1-mask[...,None])+fill*mask[...,None]
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save('sem-tchau.png')
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).crop((1400,0,5600,1800)).resize((1200,514)).save('sem-tchau-zoom.jpg')
