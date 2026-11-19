import sys, pypdf
from pypdf.generic import NameObject, RectangleObject, NumberObject, DictionaryObject
from PIL import Image
src, jpg, out1, out2 = sys.argv[1:5]
CM = 72/2.54
def build(w_cm, h_cm, out, newjpg=None, size=None):
    r = pypdf.PdfReader(src); w = pypdf.PdfWriter(clone_from=r)
    p = w.pages[0]; W, H = w_cm*CM, h_cm*CM
    for b in ('/MediaBox','/CropBox','/BleedBox','/TrimBox','/ArtBox'):
        p[NameObject(b)] = RectangleObject([0,0,W,H])
    from pypdf.generic import ContentStream
    cs=ContentStream(None,r); cs.set_data(f'q\n{W:.4f} 0 0 {H:.4f} 0 0 cm\n/Im0 Do\nQ\n'.encode()); p.replace_contents(cs)
    if newjpg:
        im = p['/Resources']['/XObject']['/Im0'].get_object()
        im.set_data(open(newjpg,'rb').read()) if False else None
        im._data = open(newjpg,'rb').read()
        im[NameObject('/Width')] = NumberObject(size[0]); im[NameObject('/Height')] = NumberObject(size[1])
        if '/DecodeParms' in im: del im['/DecodeParms']
    w.write(out)
# 1) 271x173 - imagem original intacta
build(271,173,out1)
# 2) 278x184 - sem redimensionar pixels: estende topo/base espelhando a borda
im = Image.open(jpg); W0,H0 = im.size
H1 = round(W0*184/278); pad = H1-H0; t = pad//2; b = pad-t
c = Image.new('CMYK',(W0,H1)); c.paste(im,(0,t))
c.paste(im.crop((0,0,W0,t)).transpose(Image.FLIP_TOP_BOTTOM),(0,0))
c.paste(im.crop((0,H0-b,W0,H0)).transpose(Image.FLIP_TOP_BOTTOM),(0,t+H0))
c.save('ext.jpg', quality=95, dpi=(1,1))
build(278,184,out2,'ext.jpg',(W0,H1))
print(W0,H0,H1,t,b)
