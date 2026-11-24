#!/usr/bin/env python3
"""Mede, ao longo do vídeo, onde começa a cabeça da pessoa (topo do rosto com folga),
já nas coordenadas do vídeo final (vídeo inteiro centralizado em W×H).
O lettering usa isso para nunca cobrir rosto nem corpo.

Uso: python3 ferramentas/rosto.py entrada.mp4 -f 9x16 -o rosto.json
Saída: {"passo": 0.25, "topo": [y...], "rosto": [[x0,y0,x1,y1], ...]}  (null = nenhum rosto achado)
"rosto" = caixa do rosto detectado [x0, y0, x1, y1] (efeitos.py calcula a cabeça a partir dela).
"""
import argparse, json
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("-f", default="9x16"); ap.add_argument("-o", required=True)
ap.add_argument("-r", help="reenquadramento do video.sh: centro|esq|dir (pessoa a 80 %%)")
ap.add_argument("--passo", type=float, default=0.25)
a = ap.parse_args()
W, H = (1080, 1920) if a.f == "9x16" else (1920, 1080)
cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
iw, ih = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
s = min(W / iw, H / ih); oy = (H - ih * s) / 2; ox = (W - iw * s) / 2
if a.r:
    s = min(W * 0.8 / iw, H * 0.8 / ih); oy = H - ih * s; ox = 0 if a.r == "esq" else W - iw * s
    if a.r == "centro":   # igual ao video.sh: 75 %, centralizado, 70 % da sobra em cima
        s = min(W * 0.75 / iw, H * 0.75 / ih)
        oy, ox = (H - ih * s) * 0.7, (W - iw * s) / 2
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
topo, cabeca, n, prox = [], [], 0, 0.0
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
        topo.append(None); cabeca.append(None); continue
    x, y, w, h = max(rs, key=lambda r: r[2] * r[3])
    topo.append(round(oy + (y - 0.45 * h) * s))   # 0,45×altura do rosto = testa/topo da cabeça
    cabeca.append([round(ox + x * s), round(oy + y * s), round(ox + (x + w) * s), round(oy + (y + h) * s)])
json.dump({"passo": a.passo, "topo": topo, "rosto": cabeca}, open(a.o, "w"))
v = [x for x in topo if x is not None]
print(f"{a.o}: {len(topo)} amostras, topo da cabeça entre {min(v)} e {max(v)} px" if v else "nenhum rosto")
