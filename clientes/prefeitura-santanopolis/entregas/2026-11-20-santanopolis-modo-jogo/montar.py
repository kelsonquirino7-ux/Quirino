# Remove o título "Santanópolis Bahia" (preenchendo com trecho vizinho da própria imagem)
# e aplica a logo da Prefeitura. O resto da arte enviada pelo dono fica como está.
import sys
from PIL import Image, ImageDraw, ImageFilter
src, logo_path, out = sys.argv[1:4]
im = Image.open(src).convert("RGB")

def tapar(box, dx, dy, pena=16):
    # cobre a caixa inteira (opaco) e funde só a borda externa
    x0,y0,x1,y1 = box
    X0,Y0,X1,Y1 = max(0,x0-pena), max(0,y0-pena), min(im.width,x1+pena), min(im.height,y1+pena)
    patch = im.crop((X0+dx, Y0+dy, X1+dx, Y1+dy))
    m = Image.new("L", patch.size, 0)
    ImageDraw.Draw(m).rectangle([x0-X0, y0-Y0, x1-X0, y1-Y0], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(pena/2))
    m2 = Image.new("L", patch.size, 0); ImageDraw.Draw(m2).rectangle([x0-X0, y0-Y0, x1-X0, y1-Y0], fill=255)
    from PIL import ImageChops
    im.paste(patch, (X0, Y0), ImageChops.lighter(m, m2))

tapar((1380, 785, 1672, 920), -300, 0)  # "Santanópolis Bahia"

# logo da Prefeitura (versão branca) no canto inferior direito, com sombra para contraste
logo = Image.open(logo_path).convert("LA").convert("RGBA")
w = 470; logo = logo.resize((w, round(logo.height*w/logo.width)), Image.LANCZOS)
alpha = logo.split()[3]
x, y = im.width - w - 40, im.height - logo.height - 40
sombra = Image.new("RGBA", im.size, (0,0,0,0))
s = Image.new("RGBA", logo.size, (5,20,60,255)); s.putalpha(alpha)
sombra.paste(s, (x+3, y+4), s)
sombra = sombra.filter(ImageFilter.GaussianBlur(10))
base = im.convert("RGBA")
for _ in range(3): base = Image.alpha_composite(base, sombra)
base.alpha_composite(logo, (x, y))
base.convert("RGB").save(out)
print(out, base.size)
