# Versão 3: igual à v2, mas mantém a resolução original da foto (2576x1449). Sem créditos.
import sys, random
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops
src, out = sys.argv[1], sys.argv[2]
src_im = Image.open(src); W, H = src_im.size; FH = H; TOP = 190; S = W/2000
foto = Image.open(src).convert("RGB").resize((W, FH), Image.LANCZOS)
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
    t = min(1, y/(540*S))
    c = tuple(int(a+(bb-a)*t) for a,bb in zip((30,95,215),(150,200,245)))
    d.line([(0,y),(W,y)], fill=c)
# nuvens suaves
nuv = Image.new("L", (W, H), 0); dn = ImageDraw.Draw(nuv); random.seed(7)
for _ in range(14):
    x, y = random.randint(-100, W), random.randint(30, int(290*S))
    for _ in range(6):
        rx, ry = int(random.randint(60,150)*S), int(random.randint(18,40)*S)
        ox, oy = x+random.randint(-120,120), y+random.randint(-15,15)
        dn.ellipse([ox-rx, oy-ry, ox+rx, oy+ry], fill=random.randint(90,170))
nuv = nuv.filter(ImageFilter.GaussianBlur(28))
ceu = Image.composite(Image.new("RGB",(W,H),(255,255,255)), ceu, nuv)
# junta: foto embaixo, céu no lugar da faixa de horizonte enevoada
img = ceu.copy()
mask = Image.new("L", (W, FH), 255); dm = ImageDraw.Draw(mask)
for y in range(0, int(180*S)):
    dm.line([(0,y),(W,y)], fill=int(255*max(0,(y-50*S)/(130*S))))
img.paste(f, (0, int(155*S)), mask)
# leve névoa azul na distância + vinheta
haze = Image.new("L", (W, H), 0); dh = ImageDraw.Draw(haze)
for y in range(H):
    dh.line([(0,y),(W,y)], fill=int(70*max(0, 1-abs(y-(TOP+50))/280)))
img = Image.composite(Image.new("RGB",(W,H),(175,210,245)), img, haze)
img.save(out, quality=95)
