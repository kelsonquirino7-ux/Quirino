import numpy as np, cv2
from PIL import Image, ImageDraw
base=Image.open('v9.png').convert('RGB'); W,H=base.size; k=W/1200
SS=2
mask=Image.new('L',(W*SS,H*SS),0); d=ImageDraw.Draw(mask)
# (inicio, fim, curvatura em px 1200, espessura max em px 1200)
L=[((643,207),(693,186),-3,2.6),
   ((646,229),(684,219),-2,2.1),
   ((647,250),(678,244),-1.5,1.8),
   ((646,271),(682,262),-2,2.1),
   ((643,294),(678,288),-2,2.0),
   ((641,317),(704,309),-3,2.6)]
for (x0,y0),(x1,y1),bend,wmax in L:
    t=np.linspace(0,1,80)
    mx,my=(x0+x1)/2,(y0+y1)/2
    dx,dy=x1-x0,y1-y0; n=np.hypot(dx,dy); nx,ny=-dy/n,dx/n
    cx,cy=mx+nx*bend*2,my+ny*bend*2
    X=(1-t)**2*x0+2*(1-t)*t*cx+t**2*x1; Y=(1-t)**2*y0+2*(1-t)*t*cy+t**2*y1
    w=wmax*np.sin(np.pi*t)**0.8*(0.6+0.4*(1-t))  # mais grossa perto do pe
    gx=np.gradient(X); gy=np.gradient(Y); g=np.hypot(gx,gy); px,py=-gy/g,gx/g
    left=[((X[i]+px[i]*w[i]/2)*k*SS,(Y[i]+py[i]*w[i]/2)*k*SS) for i in range(80)]
    right=[((X[i]-px[i]*w[i]/2)*k*SS,(Y[i]-py[i]*w[i]/2)*k*SS) for i in range(80)][::-1]
    d.polygon(left+right,fill=255)
m=np.asarray(mask.resize((W,H),Image.LANCZOS)).astype(np.float32)/255
glow=cv2.GaussianBlur(m,(0,0),2.2*k)
img=np.asarray(base).astype(np.float32)
a_glow=np.clip(glow*1.6,0,1)*0.45
img=img*(1-a_glow[...,None])+np.array([255,250,235])*a_glow[...,None]
a=m*0.95
img=img*(1-a[...,None])+np.array([255,255,255])*a[...,None]
o=Image.fromarray(np.clip(img,0,255).astype(np.uint8)); o.save('v10.png')
o.resize((1200,794)).save('v10-prev.jpg',quality=88)
o.crop([int(v*k) for v in (540,120,800,360)]).resize((1040,960)).save('v10-zoom.jpg')
