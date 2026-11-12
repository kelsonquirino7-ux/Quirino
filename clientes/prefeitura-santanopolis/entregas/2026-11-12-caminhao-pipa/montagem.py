#!/usr/bin/env python3
"""Corte do vídeo do caminhão-pipa, sincronizado na batida da trilha (90 bpm).
Uso: python3 montagem.py <pasta com takes 1080x1920 (3409.mp4...)> <saida.mp4>
Cada linha: take, início no bruto (s), duração em batidas, velocidade, zoom (+ aproxima, - afasta)."""
import subprocess, sys
B = 2 / 3  # uma batida a 90 bpm
CORTES = [
    ("3428", 0.3, 4, 1.0, 0.07),   # seca: árvores sem folha ao pôr do sol
    ("3419", 1.0, 4, 1.0, 0.08),   # balde vazio
    ("3409", 2.6, 6, 1.25, 0.0),   # caminhão chegando pela estrada
    ("3410", 0.8, 3, 1.0, 0.05),   # passando pela cerca
    ("3417", 0.6, 3, 1.0, 0.0),    # lateral do caminhão
    ("3411", 3.0, 4, 1.0, 0.04),   # motorista desce
    ("3413", 1.0, 4, 1.0, 0.06),   # mãos na mangueira
    ("3414", 1.6, 4, 1.0, 0.06),   # registro abrindo
    ("3416", 0.2, 5, 1.0, -0.10),  # ÁGUA (virada da música)
    ("3422", 0.3, 4, 1.0, 0.06),   # água caindo na cisterna
    ("3426", 5.6, 6, 1.0, 0.05),   # balde cheio subindo
    ("3420", 1.3, 3, 1.0, 0.0),    # cachorro
    ("3425", 0.0, 7, 1.0, 0.0),    # depoimento (áudio original)
    ("3427", 0.0, 5, 1.0, 0.06),   # aceno
]
pasta, saida = sys.argv[1], sys.argv[2]
ent, f, t = [], "", 0.0
for i, (take, ini, bat, vel, zoom) in enumerate(CORTES):
    d = bat * B
    ent += ["-ss", str(ini), "-t", str(d * vel + 0.5), "-i", f"{pasta}/{take}.mp4"]
    z = (f"1+{zoom}*t/{d}" if zoom >= 0 else f"1+{-zoom}*(1-t/{d})")
    c = f"[{i}:v]setpts=(PTS-STARTPTS)/{vel},fps=30,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={round(d * 30)},setpts=PTS-STARTPTS,"
    if zoom:
        c += f"scale=w='2*trunc(540*({z}))':h=-2:eval=frame:flags=bicubic,crop=1080:1920,"
    c += "eq=contrast=1.06:saturation=0.90:gamma=0.98,vignette=PI/5.5,setsar=1,format=yuv420p"
    if i == 0:
        c += ",fade=t=in:st=0:d=0.6"
    if take == "3416":
        c += ",fade=t=in:st=0:d=0.3:color=white"   # clarão na virada
    f += c + f"[v{i}];"
    print(f"{t:6.2f}-{t + d:6.2f}  {take}")
    t += d
f += "".join(f"[v{i}]" for i in range(len(CORTES))) + f"concat=n={len(CORTES)}:v=1:a=0[v]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex", f, "-map", "[v]", "-an",
                "-c:v", "libx264", "-preset", "medium", "-crf", "15", saida], check=True)
print("total", round(t, 2))
