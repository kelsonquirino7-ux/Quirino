import numpy as np, cv2
from PIL import Image, ImageEnhance
v=np.asarray(Image.open('v7.png').convert('RGB')).astype(np.float32)
p=np.asarray(Image.open('placa.png').convert('RGB')).astype(np.float32)
H,W=p.shape[:2]; k=W/1200; P=lambda x:int(x*k)
R,G,B=v[...,0],v[...,1],v[...,2]
box=np.zeros((H,W),bool); box[P(25):P(185),P(330):P(694)]=True
red=(R>150)&(G<100)&(B<100); white=(R>220)&(G>210)&(B>190)
core=((red|white)&box).astype(np.uint8)
reg=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(P(9)|1,P(9)|1)))
reg=np.maximum(reg,np.roll(reg,P(5),0))>0
reg&=box
# bg local de v7 (suave) para separar o texto: difusao a partir de fora da regiao
s=4; sm=cv2.resize(v,(W//s,H//s),interpolation=cv2.INTER_AREA)
ms=cv2.dilate(cv2.resize(reg.astype(np.uint8)*255,(W//s,H//s),interpolation=cv2.INTER_NEAREST),np.ones((3,3),np.uint8))
bgv=cv2.inpaint(np.clip(sm,0,255).astype(np.uint8),ms,10,cv2.INPAINT_TELEA).astype(np.float32)
bgv=cv2.resize(cv2.GaussianBlur(bgv,(0,0),3),(W,H),interpolation=cv2.INTER_CUBIC)
D=(v-bgv)*reg[...,None]
al=np.clip((np.abs(D).max(2)-8)/30,0,1)*reg
al=cv2.GaussianBlur(al,(0,0),0.8)
ys,xs=np.nonzero(al>0.5); print('texto atual x',xs.min()/k,xs.max()/k,'y',ys.min()/k,ys.max()/k)
# posicao alvo: centro entre cabeca e pedrinha medidos na placa
pr,pg,pb=p[...,0],p[...,1],p[...,2]
band=slice(P(40),P(165))
hair=(pr<120)&(pg<90); skin=(pr>180)&(pg>110)&(pg<190)&(pb>90)&(pr-pb>50)&(pr-pb<130)
head=np.nonzero(((hair|skin)[band,:P(330)]).sum(0)>15)[0].max()/k
mx=p.max(2);mn=p.min(2); stone=((mx-mn)<50)&(mx<215)&(mx>40)
stx=np.nonzero(stone[band,P(600):P(760)].sum(0)>10)[0].min()/k+600
print('cabeca',head,'pedra',stx)
tx0,tx1=xs.min()/k,xs.max()/k
dx=((head+stx)/2-(tx0+tx1)/2)
dy=0
print('dx',dx)
M=np.float32([[1,0,dx*k],[0,1,dy*k]])
L=cv2.warpAffine(D*al[...,None],M,(W,H)); A=cv2.warpAffine(al,M,(W,H))
# cor do texto = bg de v7 + delta, aplicada sobre a placa
Bv=cv2.warpAffine(bgv,M,(W,H))
col=Bv+L/np.maximum(A,1e-3)[...,None]
out=p*(1-A[...,None])+col*A[...,None]
o=Image.fromarray(np.clip(out,0,255).astype(np.uint8)); o.save('v8.png')
o.resize((1200,794)).save('v8-prev.jpg',quality=88)
z=o.crop([P(180),0,P(800),P(280)]).resize((1100,497)); z.save('v8-zoom.jpg'); ImageEnhance.Contrast(z).enhance(2.5).save('v8-contraste.jpg')
