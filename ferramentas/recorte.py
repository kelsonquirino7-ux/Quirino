#!/usr/bin/env python3
"""Recorte gratuito de produto em fundo claro + ajuste de luz/nitidez (PIL + numpy).
Uso: python3 ferramentas/recorte.py entrada.jpg saida.png x0,y0,x1,y1 [--tol 22] [--retangulo]
- crop: caixa em volta do produto (tira ícones/UI da captura de tela).
- fundo: tudo que for quase branco e ligado à borda da caixa vira transparente.
- --retangulo: em vez de fundo, usa a caixa toda com cantos arredondados (fundos com cenário)."""
import sys, numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw

def conectado(cand):
    m = np.zeros_like(cand); m[0,:]=cand[0,:]; m[-1,:]=cand[-1,:]; m[:,0]=cand[:,0]; m[:,-1]=cand[:,-1]
    while True:
        d = m.copy()
        d[1:,:]|=m[:-1,:]; d[:-1,:]|=m[1:,:]; d[:,1:]|=m[:,:-1]; d[:,:-1]|=m[:,1:]
        d &= cand
        if (d==m).all(): return m
        m = d

def main():
    a=sys.argv; ent,sai=a[1],a[2]; box=tuple(int(v) for v in a[3].split(','))
    tol=int(a[a.index('--tol')+1]) if '--tol' in a else 22
    im=Image.open(ent).convert('RGB').crop(box)
    # luz e nitidez
    im=ImageOps.autocontrast(im,cutoff=0.5,preserve_tone=True)
    im=ImageEnhance.Color(im).enhance(1.10)
    im=ImageEnhance.Contrast(im).enhance(1.05)
    im=im.filter(ImageFilter.UnsharpMask(radius=2,percent=90,threshold=2))
    if '--retangulo' in a:
        alpha=Image.new('L',im.size,0); ImageDraw.Draw(alpha).rounded_rectangle([0,0,im.width-1,im.height-1],radius=28,fill=255)
    else:
        arr=np.asarray(im).astype(int)
        mn=arr.min(2); mx=arr.max(2)
        cand=(mn>255-tol-8)&((mx-mn)<tol)
        fundo=conectado(cand)
        alpha=Image.fromarray(np.where(fundo,0,255).astype('uint8'))
        alpha=alpha.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1))
    im.putalpha(alpha)
    bb=alpha.point(lambda v:255 if v>20 else 0).getbbox(); im=im.crop(bb)
    im.save(sai)
    print(sai, im.size)
main()
