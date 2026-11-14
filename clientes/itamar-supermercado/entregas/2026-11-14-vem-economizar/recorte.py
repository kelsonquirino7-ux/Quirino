# Recorte do avatar sobre fundo verde, preservando verduras (brócolis/salsa) que o chromakey apagava.
# Uso: python3 recorte.py avatar-seedance-verde.mp4 avatar   (gera avatar/0001.png…)
# "Verdor" = G - max(R,B): o fundo (≈10,167,66) tem ~100; o brócolis fica abaixo de ~45.
import sys, subprocess, numpy as np, os
from PIL import Image, ImageFilter
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
W, H = 1280, 720
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
n = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    n += 1
    a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verdor = g - np.maximum(r, b)
    # verduras têm B < R (verde amarelado); o fundo e a sombra no fundo têm B >= R
    verdura = b < r - 2
    alfa = np.where(verdura, np.clip((78 - verdor) / 26, 0, 1),      # verdura: só some se for verde de fundo
                             np.clip((48 - verdor) / 24, 0, 1))      # resto: some a partir de verdor 48 (sombra verde)
    al = Image.fromarray((alfa * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
    alfa = np.asarray(al).astype(np.float32) / 255
    borda = alfa < .98                                              # tira o verde só da borda (spill)
    g2 = np.where(borda, np.minimum(g, np.maximum(r, b) + 10), g)
    rgba = np.dstack([r, g2, b, alfa * 255]).clip(0, 255).astype(np.uint8)
    Image.fromarray(rgba, 'RGBA').save(f'{out}/{n:04d}.png')
print(n, 'quadros')
