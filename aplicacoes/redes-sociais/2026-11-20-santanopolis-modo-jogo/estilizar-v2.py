# Versão 2: visual "render de jogo" ensolarado — céu azul limpo, cores vivas e nítidas. Sem créditos.
import sys, random
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops
src, out = sys.argv[1], sys.argv[2]
W, H, TOP = 1920, 1200, 150
foto = Image.open(src).convert("RGB").resize((W, 1080), Image.LANCZOS)
# limpa ruído e dá acabamento "render": suaviza + realça
f = foto.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.SMOOTH_MORE)
f = ImageEnhance.Color(f).enhance(1.5); f = ImageEnhance.Contrast(f).enhance(1.12)
f = ImageEnhance.Brightness(f).enhance(1.05)
f = f.filter(ImageFilter.UnsharpMask(radius=2.5, percent=140, threshold=2))
# tom mais frio e limpo (luz de meio-dia)
r,g,b = f.split()
r = r.point(lambda v: int(v*0.97)); b = b.point(lambda v: min(255, int(v*1.06+6)))
f = Image.merge("RGB", (r,g,b))
# céu azul degradê
ceu = Image.new("RGB", (W, H)); d = ImageDraw.Draw(ceu)
for y in range(H):
    t = min(1, y/420)
    c = tuple(int(a+(bb-a)*t) for a,bb in zip((30,95,215),(150,200,245)))
    d.line([(0,y),(W,y)], fill=c)
# nuvens suaves
nuv = Image.new("L", (W, H), 0); dn = ImageDraw.Draw(nuv); random.seed(7)
for _ in range(14):
    x, y = random.randint(-100, W), random.randint(30, 230)
    for _ in range(6):
        rx, ry = random.randint(60,150), random.randint(18,40)
        ox, oy = x+random.randint(-120,120), y+random.randint(-15,15)
        dn.ellipse([ox-rx, oy-ry, ox+rx, oy+ry], fill=random.randint(90,170))
nuv = nuv.filter(ImageFilter.GaussianBlur(22))
ceu = Image.composite(Image.new("RGB",(W,H),(255,255,255)), ceu, nuv)
# junta: foto embaixo, céu no lugar da faixa de horizonte enevoada
img = ceu.copy()
mask = Image.new("L", (W, 1080), 255); dm = ImageDraw.Draw(mask)
for y in range(0, 140):
    dm.line([(0,y),(W,y)], fill=int(255*max(0,(y-40)/100)))
img.paste(f, (0, H-1080), mask)
# leve névoa azul na distância + vinheta
haze = Image.new("L", (W, H), 0); dh = ImageDraw.Draw(haze)
for y in range(H):
    dh.line([(0,y),(W,y)], fill=int(70*max(0, 1-abs(y-(TOP+40))/220)))
img = Image.composite(Image.new("RGB",(W,H),(175,210,245)), img, haze)
img.save(out, quality=93)
