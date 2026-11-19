#!/usr/bin/env python3
"""Recorte de produto com fundo de cenário: polígono aproximado + remoção, a partir da borda,
de pixels pouco saturados (fundo neutro) dentro do polígono. Depois ajusta luz/nitidez.
Uso: python3 ferramentas/recorte_poligono.py entrada.jpg saida.png "x,y x,y ..." [--sat 0.28]"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageEnhance
a=sys.argv; ent,sai=a[1],a[2]; pts=[tuple(int(v) for v in p.split(',')) for p in a[3].split()]
satmin=float(a[a.index('--sat')+1]) if '--sat' in a else 0.28
im=Image.open(ent).convert('RGB')
poly=Image.new('L',im.size,0); ImageDraw.Draw(poly).polygon(pts,fill=255); P=np.asarray(poly)>0
hsv=np.asarray(im.convert('HSV')).astype(float)/255
cand=(hsv[...,1]<satmin)&P
m=np.zeros_like(P)
# semente: pixels candidatos vizinhos de fora do polígono
out=~P; nb=out.copy(); nb[1:]|=out[:-1]; nb[:-1]|=out[1:]; nb[:,1:]|=out[:,:-1]; nb[:,:-1]|=out[:,1:]
m=cand&nb
while True:
    d=m.copy(); d[1:]|=m[:-1]; d[:-1]|=m[1:]; d[:,1:]|=m[:,:-1]; d[:,:-1]|=m[:,1:]; d&=cand
    if (d==m).all(): break
    m=d
alpha=Image.fromarray(np.where(P&~m,255,0).astype('uint8'))
alpha=alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
im=ImageOps.autocontrast(im,cutoff=0.5,preserve_tone=True)
im=ImageEnhance.Color(im).enhance(1.10); im=ImageEnhance.Contrast(im).enhance(1.05)
im=im.filter(ImageFilter.UnsharpMask(radius=2,percent=90,threshold=2))
im.putalpha(alpha); im=im.crop(alpha.getbbox()); im.save(sai); print(sai,im.size)
