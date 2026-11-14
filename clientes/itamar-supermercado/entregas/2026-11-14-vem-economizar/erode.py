import sys, glob
from PIL import Image, ImageFilter
for f in sorted(glob.glob(sys.argv[1] + '/*.png')):
    im = Image.open(f).convert('RGBA'); r, g, b, a = im.split()
    a = a.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    Image.merge('RGBA', (r, g, b, a)).save(f, optimize=False)
