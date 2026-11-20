# Story 1080x1920 com a arte horizontal inteira no centro e fundo desfocado da própria arte.
import sys
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
src, out = sys.argv[1:3]
im = Image.open(src).convert("RGB"); W, H = 1080, 1920
esc = H / im.height
bg = im.resize((round(im.width*esc), H), Image.LANCZOS)
l = (bg.width - W)//2; bg = bg.crop((l, 0, l+W, H)).filter(ImageFilter.GaussianBlur(40))
bg = ImageEnhance.Brightness(bg).enhance(0.75)
fg = im.resize((W, round(im.height*W/im.width)), Image.LANCZOS)
y = (H - fg.height)//2
sh = Image.new("L", (W, H), 0); ImageDraw.Draw(sh).rectangle([0, y-6, W, y+fg.height+16], fill=170)
bg.paste((10,10,30), (0,0), sh.filter(ImageFilter.GaussianBlur(24)))
bg.paste(fg, (0, y)); bg.save(out); print(out, bg.size, fg.size)
