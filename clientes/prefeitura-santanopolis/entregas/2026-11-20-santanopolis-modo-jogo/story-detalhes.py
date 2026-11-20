# Story 1080x1920: arte inteira no centro + dois trechos da cidade ampliados em cima e embaixo.
import sys
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
arte, original, out = sys.argv[1:4]
W, H = 1080, 1920
im = Image.open(arte).convert("RGB"); src = Image.open(original).convert("RGB")
fg = im.resize((W, round(im.height*W/im.width)), Image.LANCZOS); y = (H-fg.height)//2
bh = y  # altura de cada faixa
def zoom(box):
    c = src.crop(box).resize((W, bh), Image.LANCZOS)
    c = c.filter(ImageFilter.UnsharpMask(2, 90, 2)); return ImageEnhance.Color(c).enhance(1.08)
r = W/bh; w1 = 380; h1 = round(w1/r)
topo = zoom((560, 330, 560+w1, 330+h1))     # centro: cobertura azul e ruas
w2 = 600; h2 = round(w2/r)
base = zoom((284, 20, 284+w2, 20+h2))        # pôr do sol com um pouco da cidade
st = Image.new("RGB", (W, H)); st.paste(topo, (0, 0)); st.paste(base, (0, y+fg.height)); st.paste(fg, (0, y))
d = ImageDraw.Draw(st)
for yy in (y, y+fg.height): d.rectangle([0, yy-4, W, yy+3], fill=(255,255,255))
# cantos de "zoom" nas faixas
def cantos(y0, y1, m=40, l=60, e=7):
    for (cx, cy, sx, sy) in ((m, y0+m, 1, 1), (W-m, y0+m, -1, 1), (m, y1-m, 1, -1), (W-m, y1-m, -1, -1)):
        d.rectangle(sorted([cx, cx+sx*l])+[0,0][:0] and [min(cx,cx+sx*l), min(cy,cy+sy*e), max(cx,cx+sx*l), max(cy,cy+sy*e)], fill="white")
        d.rectangle([min(cx,cx+sx*e), min(cy,cy+sy*l), max(cx,cx+sx*e), max(cy,cy+sy*l)], fill="white")
cantos(230, y-4); cantos(y+fg.height+4, H-260)
st.save(out); print(out, st.size, h1, round(W/w1,2))
