#!/usr/bin/env python3
# Remove a logo Itamar da cena da capoeira (sem créditos): recompõe o fundo atrás da logo
# com os quadros de antes de ela surgir, alinhados ao movimento da câmera. Rodar dentro de magnific/.
import cv2, numpy as np, subprocess, sys
W,H=720,1280
p=subprocess.run(["ffmpeg","-v","error","-i","capoeira-com-logo.mp4","-f","rawvideo","-pix_fmt","bgr24","-"],capture_output=True)
fr=np.frombuffer(p.stdout,np.uint8).reshape(-1,H,W,3)

def logomask(f):
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    yel=cv2.inRange(hsv,(18,120,140),(35,255,255))
    red=cv2.inRange(hsv,(0,150,120),(8,255,255))|cv2.inRange(hsv,(170,150,120),(180,255,255))
    m=(yel|red); m[650:]=0
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    out=np.zeros_like(m)
    for i in range(1,n):
        if st[i,4]>800: out[lab==i]=255
    return out
for i in []:
    m=logomask(fr[i]); print(i,(m>0).sum(), cv2.boundingRect(m))
plate=np.median(fr[2:14],axis=0).astype(np.uint8)
pg=cv2.cvtColor(plate,cv2.COLOR_BGR2GRAY).astype(np.float32)
ref_mask=np.zeros((H,W),np.uint8); ref_mask[60:620]=255; ref_mask[240:540,90:640]=0
out=[]
for i,f in enumerate(fr):
    m=logomask(f)
    if (m>0).sum()<1500: out.append(f); continue
    # usa só o maior bloco (a logo) + vizinhança
    n,lab,st,_=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); m=(lab==k).astype(np.uint8)*255
    hull=cv2.convexHull(cv2.findNonZero(m)); mm=np.zeros_like(m); cv2.fillConvexPoly(mm,hull,255)
    mm=cv2.dilate(mm,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(61,41))); mm[520:]=0
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY).astype(np.float32)
    warp=np.eye(2,3,dtype=np.float32)
    try:
        _,warp=cv2.findTransformECC(pg,g,warp,cv2.MOTION_AFFINE,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,60,1e-5),ref_mask,5)
    except cv2.error: pass
    pw=cv2.warpAffine(plate,warp,(W,H),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP)
    # casa brilho do patch com o quadro atual (anel ao redor)
    a=cv2.GaussianBlur(mm.astype(np.float32)/255,(0,0),12)[...,None]
    out.append((f*(1-a)+pw*a).astype(np.uint8))
import os
w=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s","720x1280","-r","24","-i","-","-c:v","libx264","-crf","12","-pix_fmt","yuv420p","capoeira-sem-logo-local.mp4"],stdin=subprocess.PIPE)
for o in out: w.stdin.write(o.tobytes())
w.stdin.close(); w.wait()
