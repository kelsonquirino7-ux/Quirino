import numpy as np, cv2, sys
from PIL import Image, ImageDraw
SC=float(sys.argv[1]) if len(sys.argv)>1 else 0.82
im=np.array(Image.open('sem-tchau.png').convert('RGB')).astype(np.float32); H,W=im.shape[:2]; k=W/1200
def poly(pts,w=W,h=H,kk=k):
    m=Image.new('L',(w,h),0); ImageDraw.Draw(m).polygon([(x*kk,y*kk) for x,y in pts],fill=255); return np.array(m)>0
P=[(345,470),(400,402),(462,362),(820,360),(880,392),(948,408),(948,613),(318,613),(318,560),(342,515)]
s=8; sm=cv2.resize(im,(W//s,H//s),interpolation=cv2.INTER_AREA); h,w=sm.shape[:2]; ks=k/s
holeS=poly(P,w,h,ks)
r,g,b=sm[...,0],sm[...,1],sm[...,2]
mx=sm.max(2);mn=sm.min(2)
bg=(r>170)&(g>100)&(b<150)&(r-b>80)&~((r-g>110))
ring=poly([(400,330),(880,325),(990,390),(1000,660),(280,660),(260,560),(380,420)],w,h,ks)&~holeS&bg
ys,xs=np.nonzero(ring)
def feats(x,y): x=x/w;y=y/h; return np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],1)
A=feats(xs.astype(float),ys.astype(float))
yy,xx=np.mgrid[0:H,0:W]
F=feats((xx/s).ravel().astype(np.float32),(yy/s).ravel().astype(np.float32))
fill=np.zeros_like(im)
for c in range(3):
    coef,*_=np.linalg.lstsq(A,sm[ys,xs,c],rcond=None); fill[...,c]=(F@coef).reshape(H,W)
R,G,B=im[...,0],im[...,1],im[...,2]
blue=(B>G+5)&(B>R-30)
gray=((im.max(2)-im.min(2))<60)&(im.max(2)<210)
lim=np.zeros((H,W),bool); lim[:, :int(365*k)]=True
protect=cv2.dilate(((blue&lim)).astype(np.uint8),np.ones((int(3*k),int(3*k)),np.uint8))>0
hole=poly(P)&~protect
holeF=cv2.GaussianBlur(cv2.erode(hole.astype(np.uint8),np.ones((int(7*k),int(7*k)),np.uint8)).astype(np.float32),(0,0),3*k)
D=(im-fill)*hole[...,None]
Dm=np.abs(D).max(2)
al=np.clip((Dm-35)/45,0,1)
al=cv2.dilate(al,np.ones((int(2*k),int(2*k)),np.uint8))
core=poly([(462,366),(814,366),(830,366),(880,392),(946,400),(946,612),(320,612),(320,566),(352,470),(405,440),(462,440)])
al=cv2.GaussianBlur(al*core,(0,0),1.0*k)*hole
w=(1-al)*hole
sig=12*k
G=cv2.GaussianBlur(D*w[...,None],(0,0),sig)/np.maximum(cv2.GaussianBlur(w,(0,0),sig),1e-3)[...,None]
G*=hole[...,None]
cx,cy=622*k,500*k
M=np.float32([[SC,0,cx*(1-SC)],[0,SC,cy*(1-SC)]])
L=cv2.warpAffine(D*al[...,None],M,(W,H),flags=cv2.INTER_AREA)
A=cv2.warpAffine(al,M,(W,H),flags=cv2.INTER_AREA)
noise=np.random.normal(0,1.5,im.shape).astype(np.float32)
base=fill+G+noise
new=base*(1-A[...,None])+(fill+G)*0+ (base*(1-A[...,None]) if False else 0)
# composite letters: letter color = fill(old pos) + D ; approximate with fill + L/A
col=fill+ L/np.maximum(A,1e-3)[...,None]
new=base*(1-A[...,None])+col*A[...,None]
out=im*(1-holeF[...,None])+new*holeF[...,None]
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).save('sem-tchau-menor.png')
Image.fromarray(np.clip(out,0,255).astype(np.uint8)).resize((1200,795)).save('menor-prev.jpg',quality=88)
