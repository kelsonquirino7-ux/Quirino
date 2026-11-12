#!/usr/bin/env python3
"""Corte do vídeo do caminhão-pipa, sincronizado na batida da trilha (90 bpm), com transições suaves.
Uso: python3 montagem.py <pasta com takes 1080x1920 (3409.mp4...)> <saida.mp4>
Cada linha: take, início no bruto (s), duração em batidas, velocidade, zoom (+ aproxima, - afasta),
transição de SAÍDA para o próximo take (nome do xfade do ffmpeg, duração em s). "corte" = corte seco."""
import subprocess, sys
B = 2 / 3  # uma batida a 90 bpm
CORTES = [
    ("3428", 0.0, 4, 1.0, 0.07, ("fade", 0.6)),        # sol: Santanópolis, data
    ("3419", 1.0, 4, 1.0, 0.08, ("fade", 0.5)),        # balde vazio: quando a água falta
    ("3420", 1.3, 3, 1.0, 0.0, ("fadeblack", 0.5)),    # cachorro: todos sofrem
    ("3409", 2.6, 5, 1.5, 0.0, ("fade", 0.35)),        # caminhão chegando: mas jamais soltaremos a mão
    ("3410", 0.8, 2, 1.0, 0.05, ("fade", 0.35)),       # passando pela cerca: do nosso povo
    ("3417", 0.8, 2, 1.0, 0.0, ("fade", 0.35)),        # lateral do caminhão
    ("3411", 3.0, 4, 1.0, 0.04, ("fade", 0.4)),        # motorista desce: vamos levar água
    ("3413", 1.0, 4, 1.0, 0.06, ("fade", 0.4)),        # mangueira: para todos que precisam
    ("3414", 1.6, 4, 1.0, 0.06, ("corte", 0)),         # registro abrindo -> corte seco + clarão na virada
    ("3416", 0.2, 5, 1.0, -0.10, ("fade", 0.5)),       # água (virada da música)
    ("3422", 0.3, 4, 1.0, 0.06, ("fade", 0.5)),        # água caindo na cisterna
    ("3426", 5.2, 6, 1.0, 0.05, ("fade", 0.4)),        # balde cheio: água é direito de todos
    ("3425", 0.0, 7, 1.0, 0.0, ("fade", 0.35)),        # depoimento (áudio original + legenda)
    ("3427", 0.0, 5, 1.0, 0.06, ("fade", 0.5)),        # aceno (a sobra serve para fundir com a vinheta)
]
pasta, saida = sys.argv[1], sys.argv[2]
ent, f, t = [], "", 0.0
for i, (take, ini, bat, vel, zoom, (tr, T)) in enumerate(CORTES):
    d = bat * B
    dd = d + T                      # sobra para a fusão com o próximo take
    ent += ["-ss", str(ini), "-t", str(dd * vel + 0.5), "-i", f"{pasta}/{take}.mp4"]
    z = (f"1+{zoom}*t/{dd}" if zoom >= 0 else f"1+{-zoom}*(1-t/{dd})")
    c = f"[{i}:v]setpts=(PTS-STARTPTS)/{vel},fps=30,tpad=stop_mode=clone:stop_duration=1,trim=end_frame={round(dd * 30)},setpts=PTS-STARTPTS,"
    if zoom:
        c += f"scale=w='2*trunc(540*({z}))':h=-2:eval=frame:flags=bicubic,crop=1080:1920,"
    c += "eq=contrast=1.06:saturation=0.90:gamma=0.98,vignette=PI/5.5,setsar=1,format=yuv420p,settb=AVTB"
    if i == 0:
        c += ",fade=t=in:st=0:d=0.8"
    if take == "3416":
        c += ",fade=t=in:st=0:d=0.3:color=white"   # clarão na virada
    f += c + f"[v{i}];"
    print(f"{t:6.2f}-{t + d:6.2f}  {take}  -> {tr} {T}")
    t += d
ant, t = "v0", 0.0
for i in range(1, len(CORTES)):
    t += CORTES[i - 1][2] * B
    tr, T = CORTES[i - 1][5]
    if tr == "corte":
        f += f"[{ant}]trim=end_frame={round(t * 30)},setpts=PTS-STARTPTS[c{i}];[v{i}]setpts=PTS-STARTPTS[d{i}];[c{i}][d{i}]concat=n=2:v=1:a=0,fps=30,settb=AVTB[x{i}];"
    else:
        f += f"[{ant}][v{i}]xfade=transition={tr}:duration={T}:offset={t:.4f}[x{i}];"
    ant = f"x{i}"
subprocess.run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex", f.rstrip(";"), "-map", f"[{ant}]", "-an",
                "-c:v", "libx264", "-preset", "medium", "-crf", "15", saida], check=True)
print("total", round(t + CORTES[-1][2] * B, 2), "+ sobra", CORTES[-1][5][1])
