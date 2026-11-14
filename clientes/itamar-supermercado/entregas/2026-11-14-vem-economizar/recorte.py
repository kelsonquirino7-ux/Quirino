# Recorte do avatar sobre fundo verde, sem contorno e preservando verduras (brócolis/salsa).
# Uso: python3 recorte.py avatar-seedance-verde.mp4 avatar   (gera avatar/0001.png…)  · requer opencv-python-headless
# 1) "Verdor" = G - max(R,B): o fundo (≈10,167,66) tem ~100; verduras (B < R) ficam abaixo de ~45.
# 2) A borda é recolhida ~2 px e suavizada (sem degrau serrilhado).
# 3) Descontaminação: os pixels da faixa de borda recebem a cor do interior do avatar (convolução normalizada),
#    então não sobra o verde/cinza do fundo que formava o contorno.
import sys, subprocess, os
import numpy as np, cv2
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
W, H = 1280, 720
K = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
n = 0
while True:
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3: break
    n += 1
    a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    verdor = g - np.maximum(r, b)
    verdura = b < r - 2
    alfa0 = np.where(verdura, np.clip((78 - verdor) / 26, 0, 1), np.clip((48 - verdor) / 24, 0, 1)).astype(np.float32)
    # máscara sólida e borda recolhida
    solido = (alfa0 > .99).astype(np.uint8)
    solido = cv2.morphologyEx(solido, cv2.MORPH_OPEN, K(1))
    # fecha furos pequenos internos (pontos claros do brócolis, reflexos), sem tocar vãos grandes (braço e corpo)
    nlab, lab, st, _ = cv2.connectedComponentsWithStats(1 - solido, connectivity=4)
    for i in range(1, nlab):
        x, y, w, h, area = st[i]
        if area < 2500 and x > 0 and y > 0 and x + w < W and y + h < H:
            m = lab == i
            if np.percentile(verdor[m], 75) < 60:         # só tapa se não for fundo verde visto por um vão (carrinho, pernas)
                solido[m] = 1
    alfa = cv2.erode(solido, K(2)).astype(np.float32)
    alfa = cv2.GaussianBlur(alfa, (0, 0), 1.1)
    # cor da borda puxada do interior
    interior = cv2.erode(solido, K(4)).astype(np.float32)
    num = cv2.GaussianBlur(a * interior[..., None], (0, 0), 3.5)
    den = cv2.GaussianBlur(interior, (0, 0), 3.5)[..., None]
    cor_int = num / np.maximum(den, 1e-4)
    usa = (interior < 1)[..., None] & (den > .02)
    rgb = np.where(usa, cor_int, a)
    rgba = np.dstack([rgb, alfa * 255]).clip(0, 255).astype(np.uint8)
    cv2.imwrite(f'{out}/{n:04d}.png', cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
print(n, 'quadros')
