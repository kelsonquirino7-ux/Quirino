#!/usr/bin/env python3
"""Câmera lenta por fluxo óptico (DIS, OpenCV) — interpola quadros intermediários sem blocos.
Uso: python3 ferramentas/camlenta.py entrada.mp4 q0 q1 fator saida.mkv
Lê os quadros q0..q1-1 (24 fps) e grava round((q1-q0)*fator) quadros a 24 fps, sem perdas."""
import sys, subprocess, numpy as np, cv2
src, q0, q1, fator, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
p = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"trim=start_frame={q0}:end_frame={q1 + 1},setpts=PTS-STARTPTS",
                    "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True)
W, H = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                "stream=width,height", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.split(","))
fr = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)
dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
gx, gy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
cache = {}
def flows(i):
    if i not in cache:
        a, b = (cv2.cvtColor(fr[j], cv2.COLOR_BGR2GRAY) for j in (i, i + 1))
        cache[i] = (dis.calc(a, b, None), dis.calc(b, a, None))
    return cache[i]
n = round((q1 - q0) * fator)
w = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                      "-r", "24", "-i", "-", "-c:v", "libx264", "-qp", "0", "-preset", "ultrafast", out], stdin=subprocess.PIPE)
for k in range(n):
    pos = k / fator
    i, t = int(pos), pos - int(pos)
    i = min(i, len(fr) - 1)
    if t < 1e-3 or i + 1 >= len(fr):
        img = fr[i]
    else:
        f01, f10 = flows(i)
        ft0 = -(1 - t) * t * f01 + t * t * f10
        ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10
        w0 = cv2.remap(fr[i], gx + ft0[..., 0], gy + ft0[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        w1 = cv2.remap(fr[i + 1], gx + ft1[..., 0], gy + ft1[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        img = ((1 - t) * w0.astype(np.float32) + t * w1.astype(np.float32)).clip(0, 255).astype(np.uint8)
    w.stdin.write(img.tobytes())
w.stdin.close(); w.wait()
