# Amplia os quadros recortados do avatar 2x (Lanczos, com alfa pré-multiplicado para não criar halo) e aplica nitidez.
# Uso: python3 nitidez.py avatar     (roda depois de recorte.py; sobrescreve os PNG)
import sys, glob, cv2, numpy as np
for f in sorted(glob.glob(sys.argv[1] + '/*.png')):
    a = cv2.imread(f, cv2.IMREAD_UNCHANGED).astype(np.float32)
    al = a[..., 3:4] / 255.
    pm = a[..., :3] * al
    h, w = a.shape[:2]
    pm2 = cv2.resize(pm, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4)
    al2 = cv2.resize(al, (w * 2, h * 2), interpolation=cv2.INTER_LANCZOS4).clip(0, 1)[..., None]
    rgb = pm2 / np.maximum(al2, 1e-3)
    borr = cv2.GaussianBlur(rgb, (0, 0), 1.6)
    rgb = rgb + 0.8 * (rgb - borr)                       # máscara de nitidez
    out = np.dstack([rgb.clip(0, 255), al2[..., 0] * 255]).astype(np.uint8)
    cv2.imwrite(f, out, [cv2.IMWRITE_PNG_COMPRESSION, 1])
print('ok')
