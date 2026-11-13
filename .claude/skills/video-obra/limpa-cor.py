import subprocess, sys, numpy as np
# Remove o miolo amarelo da ponta do rolo no clipe asfalto-tapete (uso: python3 limpa-rolo.py original.mp4 saida.mp4)
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
W, H = 1080, 1920
r = subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"], stdout=subprocess.PIPE)
w = subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","24","-i","-",
                      "-c:v","libx264","-crf","18","-pix_fmt","yuv420p",dst], stdin=subprocess.PIPE)
n = 0; tot = 0
while True:
    b = r.stdout.read(W*H*3)
    if len(b) < W*H*3: break
    a = np.frombuffer(b, np.uint8).reshape(H, W, 3).astype(np.float32)
    mx = a.max(2); mn = a.min(2); sat = (mx - mn) / (mx + 1e-6)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    amarelo = (sat > 0.55) & (mx > 120) & (R > B * 1.8) & (G > B * 1.3) & (G > R * 0.55)
    zona = np.zeros((H, W), bool); zona[700:1400, int(W * 0.62):] = True     # ponta direita do rolo
    m = amarelo & zona
    if m.sum() > 30:
        tot += 1
        mk = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
        k = (np.asarray(mk).astype(np.float32) / 255)[..., None]
        cor = np.array([44, 46, 50], np.float32)
        lum = a.mean(2, keepdims=True) / 255
        a = a * (1 - k) + (cor * (0.7 + 0.5 * lum)) * k
    w.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes()); n += 1
w.stdin.close(); w.wait(); print("quadros", n, "corrigidos", tot)
