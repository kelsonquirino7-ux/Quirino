#!/usr/bin/env python3
"""Mede, ao longo do vídeo, onde começa a cabeça da pessoa (topo do rosto com folga),
já nas coordenadas do vídeo final (vídeo inteiro centralizado em W×H).
O lettering usa isso para nunca cobrir rosto nem corpo.

Uso: python3 ferramentas/rosto.py entrada.mp4 -f 9x16 -o rosto.json
Saída: {"passo": 0.25, "topo": [y0, y1, ...]}  (null = nenhum rosto achado)
"""
import argparse, json
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("-f", default="9x16"); ap.add_argument("-o", required=True)
ap.add_argument("--passo", type=float, default=0.25)
a = ap.parse_args()
W, H = (1080, 1920) if a.f == "9x16" else (1920, 1080)
cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
iw, ih = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
s = min(W / iw, H / ih); oy = (H - ih * s) / 2
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
topo, n, prox = [], 0, 0.0
while True:
    ok, fr = cap.read()
    if not ok:
        break
    t = n / fps; n += 1
    if t + 1e-6 < prox:
        continue
    prox += a.passo
    cinza = cv2.equalizeHist(cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY))
    rs = cas.detectMultiScale(cinza, 1.1, 5, minSize=(int(iw * 0.12),) * 2)
    if len(rs) == 0:
        topo.append(None); continue
    x, y, w, h = max(rs, key=lambda r: r[2] * r[3])
    topo.append(round(oy + (y - 0.45 * h) * s))   # 0,45×altura do rosto = testa/topo da cabeça
json.dump({"passo": a.passo, "topo": topo}, open(a.o, "w"))
v = [x for x in topo if x is not None]
print(f"{a.o}: {len(topo)} amostras, topo da cabeça entre {min(v)} e {max(v)} px" if v else "nenhum rosto")
