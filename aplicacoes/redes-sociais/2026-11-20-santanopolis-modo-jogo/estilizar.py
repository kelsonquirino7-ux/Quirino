# Transforma a foto em visual de "jogo de mundo aberto" (sem custo, só PIL).
import sys
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB").resize((1920,1080), Image.LANCZOS)
# 1) suaviza texturas (aspecto pintado) mantendo bordas
p = im.filter(ImageFilter.ModeFilter(5)).filter(ImageFilter.MedianFilter(5))
# 2) cores saturadas e contraste
p = ImageEnhance.Color(p).enhance(1.65); p = ImageEnhance.Contrast(p).enhance(1.18)
# 3) posterização leve
p = ImageOps.posterize(p, 5)
# 4) contornos escuros (traço de ilustração)
g = ImageOps.grayscale(im).filter(ImageFilter.GaussianBlur(1.2))
e = g.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v < 22 else max(0, 255-(v-22)*4))
p = ImageChops.multiply(p, Image.merge("RGB",(e,e,e)))
# 5) gradação de "fim de tarde" suave: brilho quente no horizonte, sombras azuladas
w,h = p.size
sky = Image.new("RGB",(w,h),(255,150,90))
mask = Image.linear_gradient("L").resize((w,h)).point(lambda v: int(max(0,110-v*0.7)))
p = Image.composite(sky, p, mask)
r,g2,b = p.split()
b = b.point(lambda v: min(255,int(v*0.9+30)))   # sombras levemente azuis
r = r.point(lambda v: min(255,int(v*1.04)))
p = Image.merge("RGB",(r,g2,b))
p = ImageEnhance.Color(p).enhance(1.15); p = ImageEnhance.Sharpness(p).enhance(1.6)
p.save(out, quality=92)
