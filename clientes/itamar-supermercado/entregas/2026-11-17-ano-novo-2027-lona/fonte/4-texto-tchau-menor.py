import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
base=Image.open('sem-tchau-menor.png').convert('RGB'); W,H=base.size; k=W/1200
F='/home/user/Quirino/ferramentas/fontes/ttf/lilita-one-latin-400-normal.ttf'
lines=['TCHAU,','ANO VELHO!']
target_w=210*k; cx=600*k; top=58*k
fs=400
f=ImageFont.truetype(F,fs); w=max(f.getbbox(l)[2]-f.getbbox(l)[0] for l in lines)
fs=int(fs*target_w/w); f=ImageFont.truetype(F,fs)
lh=int(fs*0.98)
txt=Image.new('L',(W,H),0); d=ImageDraw.Draw(txt)
for i,l in enumerate(lines):
    bb=f.getbbox(l); lw=bb[2]-bb[0]
    d.text((cx-lw/2-bb[0], top+i*lh-bb[1]+ (0 if i==0 else 0)), l, font=f, fill=255)
t=np.array(txt).astype(np.float32)/255
stroke=int(fs*0.07)
st=cv2.dilate((t>0.5).astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*stroke+1,2*stroke+1))).astype(np.float32)
st=cv2.GaussianBlur(st,(0,0),1.2)
img=np.array(base).astype(np.float32)
def comp(img,a,color):
    return img*(1-a[...,None])+np.array(color,np.float32)*a[...,None]
# drop shadow
sh=cv2.GaussianBlur(np.roll(np.roll(st,int(fs*.06),0),int(fs*.03),1),(0,0),fs*.05)*0.45
img=comp(img,sh,(60,20,0))
# extrusion (depth) behind white stroke
depth=int(fs*0.07)
for i in range(depth,0,-2):
    a=np.roll(np.roll(st,i,0),int(i*0.4),1)
    img=comp(img,a,(150,8,4))
img=comp(img,st,(255,255,255))
# red face with vertical gradient (top lighter)
yy=np.linspace(0,1,H)[:,None]
face=np.zeros((H,W,3),np.float32)
ys,xs=np.nonzero(t>0.01); y0,y1=ys.min(),ys.max()
g=np.clip((np.arange(H)-y0)/(y1-y0),0,1)[:,None,None]
c1=np.array([255,70,50],np.float32); c2=np.array([210,18,12],np.float32)
# per-line gradient
lineg=np.zeros(H,np.float32)
for i in range(2):
    a=top+i*lh; b=a+lh*0.8; idx=np.arange(H); m=(idx>=a)&(idx<a+lh); lineg[m]=np.clip((idx[m]-a)/(b-a),0,1)
face=c1*(1-lineg[:,None,None])+c2*lineg[:,None,None]
img=img*(1-t[...,None])+face*t[...,None]
# glossy highlight on upper part of letters
hl=t*np.clip(1-lineg[:,None]*2.2,0,1)[:, :]*0.25
img=comp(img,hl,(255,255,255))
out=Image.fromarray(np.clip(img,0,255).astype(np.uint8))
out.save('v4.png')
out.resize((1200,795)).save('v4-prev.jpg',quality=88)
out.crop((int(250*k),0,int(720*k),int(230*k))).resize((1200,587)).save('v4-zoom.jpg')
print(fs, fs/k)
