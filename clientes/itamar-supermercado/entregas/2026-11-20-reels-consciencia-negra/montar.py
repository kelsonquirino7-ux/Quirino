#!/usr/bin/env python3
"""Reels Itamar · Consciência Negra: troca o áudio original por locução sincronizada à legenda.
Rampa de velocidade contínua (setpts por trecho) + interpolação de movimento (minterpolate):
cada janela de legenda é desacelerada até a frase caber, sem congelar nem duplicar quadros."""
import subprocess, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
FPS = 24
# (quadro inicial do trecho no original, fator de câmera lenta)
TRECHOS = [(0, 1.75),    # legenda 1  0,00–2,25 s
           (54, 2.0),    # fusão
           (59, 2.55),   # legenda 2  2,46–4,33 s
           (104, 2.5),   # fusão
           (107, 4.05),  # legenda 3  4,46–5,85 s
           (140, 2.0),   # fim da cena da família
           (151, 1.0)]   # logo + legenda 4, velocidade original
TOTAL_QUADROS = 361
# frases: (início e fim na gravação, aceleração, quadro do original onde a frase entra)
FRASES = [(0.00, 3.52, 1.06, 6),     # Uma história de força, coragem e resistência...
          (3.90, 8.52, 1.06, 61),    # Uma cultura que atravessa gerações...
          (8.89, 14.56, 1.10, 108),  # Uma história que merece ser reconhecida...
          (14.89, None, 1.06, 242)]  # Respeitar nossas raízes é valorizar nossa história.

def t_saida(q):  # tempo de saída (s) do quadro q do original
    t = 0.0
    for i, (ini, f) in enumerate(TRECHOS):
        fim = TRECHOS[i+1][0] if i+1 < len(TRECHOS) else 10**9
        if q <= ini: break
        t += (min(q, fim) - ini) / FPS * f
    return t

expr = "0"
inicio = 0.0
partes = []
for i, (ini, f) in enumerate(TRECHOS):
    partes.append((ini, f"({t_saida(ini):.6f}+(N-{ini})/{FPS}*{f})"))
expr = partes[-1][1]
for ini, e in reversed(partes[:-1]):
    nxt = TRECHOS[[p[0] for p in partes].index(ini)+1][0]
    expr = f"if(lt(N,{nxt}),{e},{expr})"
dur = t_saida(TOTAL_QUADROS)
MI = "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
vf = f"setpts='({expr})/TB',{MI}"

af, labels = [], []
for k, (a, b, tempo, q) in enumerate(FRASES):
    d = int(round(t_saida(q) * 1000))
    trim = f"atrim={a}:{b}" if b else f"atrim={a}"
    af.append(f"[1:a]{trim},asetpts=PTS-STARTPTS,atempo={tempo},adelay={d}:all=1[a{k}]")
    labels.append(f"[a{k}]")
    print(f"frase {k+1}: entra em {d/1000:.2f} s, dura {((b or 18.6)-a)/tempo:.2f} s")
# capoeira (quadros 54–107): movimento rápido deforma com interpolação; usa mistura de quadros
c0, c1 = round(t_saida(54)*FPS)/FPS, round(t_saida(107)*FPS)/FPS
BL = "minterpolate=fps=24:mi_mode=blend"
fc = (f"[0:v]setpts='({expr})/TB',split=2[r1][r2];[r1]{MI},split=2[m1][m2];[r2]{BL}[b];"
      f"[m1]trim=end={c0},setpts=PTS-STARTPTS[p1];[b]trim=start={c0}:end={c1},setpts=PTS-STARTPTS[p2];"
      f"[m2]trim=start={c1},setpts=PTS-STARTPTS[p3];[p1][p2][p3]concat=n=3:v=1:a=0,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5,format=yuv420p[v];") + ";".join(af) + ";" + "".join(labels) + \
     f"amix=inputs={len(labels)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[a]"
print(f"duração final: {dur:.2f} s")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "bruto.mp4", "-i", "locucao-bruta.mp3",
                "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{dur:.3f}",
                "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-r", "24",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "video.mp4"], check=True)
