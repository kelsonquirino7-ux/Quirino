import numpy as np
from PIL import Image, ImageDraw, ImageFilter
im=Image.open('base.png').convert('RGB'); W,H=im.size
mask=Image.new('L',(W,H),0); d=ImageDraw.Draw(mask)
d.polygon([(60,60),(1100,60),(1100,470),(835,470),(835,940),(60,940)],fill=255)   # selo antigo
d.polygon([(2330,130),(3275,130),(3275,575),(3205,575),(3205,905),(2330,905)],fill=255)                                           # textos da direita
def fill(img,m,f):
    small=img.resize((W//f,H//f),Image.BOX); ms=np.array(m.resize((W//f,H//f),Image.BOX))>0
    a=np.array(small).astype(float); known=~ms
    a[ms]=0; w=known.astype(float)
    acc=a*w[...,None]; 
    for i in range(400):
        acc2=(np.roll(acc,1,0)+np.roll(acc,-1,0)+np.roll(acc,1,1)+np.roll(acc,-1,1))/4
        w2=(np.roll(w,1,0)+np.roll(w,-1,0)+np.roll(w,1,1)+np.roll(w,-1,1))/4
        acc=np.where(known[...,None],a*1.0,acc2); w=np.where(known,1.0,w2)
    out=np.where(known[...,None],a,acc/np.maximum(w,1e-6)[...,None])
    return Image.fromarray(out.clip(0,255).astype('uint8')).resize((W,H),Image.BICUBIC).filter(ImageFilter.GaussianBlur(f))
f=fill(im,mask,8)
# granulado leve para não ficar liso demais
n=(np.random.default_rng(1).normal(0,3,(H,W,1))).repeat(3,2)
f=Image.fromarray((np.array(f).astype(float)+n).clip(0,255).astype('uint8'))
soft=mask.filter(ImageFilter.GaussianBlur(10))
Image.composite(f,im,soft).save('base-limpa.png')
Image.composite(f,im,soft).resize((2000,500)).save('chk.jpg')
