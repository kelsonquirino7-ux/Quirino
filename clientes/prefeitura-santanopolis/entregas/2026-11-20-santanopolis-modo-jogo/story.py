# Story 1080x1920 a partir da arte enviada: recorte vertical da cena + elementos de HUD reposicionados
# (recortados da própria arte, com fundo removido por cor) + logo da Prefeitura.
import sys, colorsys
from PIL import Image, ImageFilter, ImageEnhance
src, logo_path, out = sys.argv[1:4]
im = Image.open(src).convert("RGB")
W, H = 1080, 1920
# fundo: fatia vertical centrada na avenida e no ginásio
x0 = 470; fatia = im.crop((x0, 0, x0 + round(im.height*W/H), im.height))
bg = fatia.resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))

def recorte_hud(box):
    """Mantém só branco, preto, roxo/magenta e verde do HUD; remove céu laranja/rosa."""
    c = im.crop(box); a = Image.new("L", c.size, 0); px = c.load(); pa = a.load()
    for y in range(c.height):
        for x in range(c.width):
            r,g,b = [v/255 for v in px[x,y]]; h,s,v = colorsys.rgb_to_hsv(r,g,b); h*=360
            keep = (s < 0.18 and v > 0.85) or v < 0.16 or (s < 0.3 and v < 0.45) or (240 <= h <= 330 and s > 0.35) or (90 <= h <= 160 and s > 0.4)
            pa[x,y] = 255 if keep else 0
    a = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.6))
    c = c.convert("RGBA"); c.putalpha(a); return c

def colar(img, pos, larg):
    img = img.resize((larg, round(img.height*larg/img.width)), Image.LANCZOS)
    bg_rgba.alpha_composite(img, pos); return img.size

bg_rgba = bg.convert("RGBA")
SEG_TOPO, SEG_BASE = 250, 1650           # área segura do story
colar(recorte_hud((36, 14, 282, 206)), (50, SEG_TOPO), 400)
colar(recorte_hud((1440, 20, 1648, 108)), (W-50-340, SEG_TOPO+20), 340)
mapa = im.crop((30, 722, 293, 910)).convert("RGBA")
mw, mh = colar(mapa, (50, SEG_BASE-0-round(188*380/263)), 380)
# logo da Prefeitura (branca) à direita do minimapa, com sombra
logo = Image.open(logo_path).convert("LA").convert("RGBA"); lw = W-50-(50+mw+40)
logo = logo.resize((lw, round(logo.height*lw/logo.width)), Image.LANCZOS)
lx, ly = W-50-lw, SEG_BASE - logo.height - 20
s = Image.new("RGBA", logo.size, (5,20,60,255)); s.putalpha(logo.split()[3])
sh = Image.new("RGBA", (W,H), (0,0,0,0)); sh.paste(s, (lx+3, ly+4), s); sh = sh.filter(ImageFilter.GaussianBlur(10))
for _ in range(3): bg_rgba = Image.alpha_composite(bg_rgba, sh)
bg_rgba.alpha_composite(logo, (lx, ly))
bg_rgba.convert("RGB").save(out); print(out, bg_rgba.size)
