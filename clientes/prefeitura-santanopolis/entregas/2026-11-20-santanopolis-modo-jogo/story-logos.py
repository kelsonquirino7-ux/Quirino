# Story 1080x1920: faixa de cima (centro ampliado) com a logo do jogo, arte no meio sem as logos,
# faixa de baixo (pôr do sol + cidade) com a logo da Prefeitura.
import sys, colorsys
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageChops, ImageOps
original, logo_pref, out = sys.argv[1:4]
src = Image.open(original).convert("RGB"); W, H = 1080, 1920

# --- arte do meio sem logos -------------------------------------------------
arte = src.copy()
def tapar(img, box, dx, pena=16):
    x0,y0,x1,y1 = box
    X0,Y0,X1,Y1 = max(0,x0-pena), max(0,y0-pena), min(img.width,x1+pena), min(img.height,y1+pena)
    patch = src.crop((X0+dx, Y0, X1+dx, Y1))
    m = Image.new("L", patch.size, 0); ImageDraw.Draw(m).rectangle([x0-X0,y0-Y0,x1-X0,y1-Y0], fill=255)
    img.paste(patch, (X0, Y0), ImageChops.lighter(m.filter(ImageFilter.GaussianBlur(pena/2)), m))
tapar(arte, (1380, 785, 1672, 920), -300)               # título "Santanópolis Bahia"
# logo do jogo: espelha o lado direito do sol (x=338) para o lado esquerdo — o brilho fica simétrico
SOL = 338; caixa = (0, 0, 306, 222)
esp = ImageOps.mirror(src.crop((2*SOL-caixa[2], caixa[1], 2*SOL-caixa[0], caixa[3])))
m = Image.new("L", esp.size, 255); d = ImageDraw.Draw(m)
for i in range(18): d.line([(esp.width-1-i, 0), (esp.width-1-i, esp.height)], fill=int(255*i/18))
for i in range(18): d.line([(0, esp.height-1-i), (esp.width, esp.height-1-i)], fill=int(255*i/18))
arte.paste(esp, caixa[:2], ImageChops.darker(m, Image.new("L", m.size, 255)))

# --- logo do jogo recortada da arte enviada (fundo removido por cor) ---------
def recorte_hud(box):
    c = src.crop(box); a = Image.new("L", c.size, 0); px = c.load(); pa = a.load()
    for y in range(c.height):
        for x in range(c.width):
            r,g,b = [v/255 for v in px[x,y]]; h,s,v = colorsys.rgb_to_hsv(r,g,b); h *= 360
            keep = (s < 0.18 and v > 0.85) or v < 0.16 or (s < 0.3 and v < 0.45) or (240 <= h <= 330 and s > 0.35)
            pa[x,y] = 255 if keep else 0
    a = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    c = c.convert("RGBA"); c.putalpha(a); return c
jogo = recorte_hud((36, 14, 282, 206))

# --- montagem ---------------------------------------------------------------
fg = arte.resize((W, round(arte.height*W/arte.width)), Image.LANCZOS); y = (H-fg.height)//2; bh = y
r = W/bh
def zoom(box):
    c = src.crop(box).resize((W, bh), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 90, 2))
    return ImageEnhance.Color(c).enhance(1.08)
w1 = 380; topo = zoom((560, 330, 560+w1, 330+round(w1/r)))
w2 = 600; base = zoom((284, 20, 284+w2, 20+round(w2/r)))
st = Image.new("RGBA", (W, H)); st.paste(topo, (0,0)); st.paste(base, (0, y+fg.height)); st.paste(fg, (0, y))

def sombra(img, pos, cor=(5,20,60), raio=12, vezes=3):
    global st
    s = Image.new("RGBA", img.size, cor+(255,)); s.putalpha(img.split()[3])
    lay = Image.new("RGBA", (W,H), (0,0,0,0)); lay.paste(s, (pos[0]+3, pos[1]+5), s)
    lay = lay.filter(ImageFilter.GaussianBlur(raio))
    for _ in range(vezes): st = Image.alpha_composite(st, lay)

# logo do jogo: pequena, canto superior esquerdo da faixa de cima (como na arte original)
lj = 260; jogo = jogo.resize((lj, round(jogo.height*lj/jogo.width)), Image.LANCZOS)
pj = (50, 250)
sombra(jogo, pj, (0,0,0), 14, 2); st.alpha_composite(jogo, pj)
# logo da Prefeitura: pequena, canto inferior direito da faixa de baixo (como na arte original)
lp = 400; pref = Image.open(logo_pref).convert("LA").convert("RGBA")
pref = pref.resize((lp, round(pref.height*lp/pref.width)), Image.LANCZOS)
pp = (W-50-lp, 1660-pref.height)
sombra(pref, pp); st.alpha_composite(pref, pp)

d = ImageDraw.Draw(st)
for yy in (y, y+fg.height): d.rectangle([0, yy-4, W, yy+3], fill=(255,255,255))
st.convert("RGB").save(out); print(out, st.size)
