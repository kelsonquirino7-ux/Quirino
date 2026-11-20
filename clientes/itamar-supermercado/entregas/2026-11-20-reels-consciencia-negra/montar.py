#!/usr/bin/env python3
"""Reels Itamar · Consciência Negra — versão 3.
Monta cenas dos dois vídeos do Gemini (bruto-v1.mp4 = 1º, bruto.mp4 = 2º) quase sem câmera lenta,
apaga os ícones do Reels (coração, 5118, comentário) por inpainting, tira barra do topo e @ com zoom leve,
e encaixa a locução frase a frase na legenda de cada cena."""
import subprocess, os, tempfile
import numpy as np, cv2
os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 720, 1280, 24
LUZ = "eq=brightness=0.03:contrast=1.06:saturation=1.08,colorbalance=rm=0.03:bm=-0.03"   # capoeira mais iluminada
MCI = "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none"
# (arquivo, quadro inicial, quadro final, câmera lenta, filtro extra)
CENAS = [("bruto-v1.mp4",   0,  98, 1.0,  ""),    # senhora — "Uma história de força..."
         ("bruto-v1.mp4", 154, 179, 1.0,  LUZ),   # capoeira (roda sob as árvores)
         ("bruto.mp4",     60, 101, 1.0,  LUZ),   # capoeira (pátio)
         ("bruto-v1.mp4", 298, 356, 1.0,  LUZ),   # capoeira (roda sob as árvores)
         ("bruto.mp4",    110, 140, 1.5,  ""),    # família (abraço)
         ("bruto-v1.mp4", 366, 431, 1.45, ""),    # família (aberta)
         ("bruto.mp4",    152, 360, 1.0,  "")]    # logo Itamar
FUSOES = [0.35, 0.25, 0.25, 0.35, 0.3, 0.5]
# frases: (início, fim na gravação, aceleração, entrada em s)
FRASES = [(0.00, 3.52, 1.06, 0.30), (3.90, 8.52, 1.08, 3.90),
          (8.89, 14.56, 1.10, 8.22), (14.89, None, 1.06, 16.83)]

# máscara dos ícones do Reels (mesma posição nos dois vídeos), tirada da cena escura da logo
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "10.5", "-to", "15", "-i", "bruto.mp4",
                    "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True, check=True)
mn = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W).min(0)
X0, Y0, X1, Y1 = 600, 940, 720, 1180
mask = (mn[Y0:Y1, X0:X1] > 150).astype(np.uint8) * 255
mask = cv2.dilate(mask, np.ones((9, 9), np.uint8))

# o 2º vídeo do Gemini repete quadros (engasga): acha os repetidos para removê-los e interpolar
def repetidos(arq):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf", "scale=270:480", "-f", "rawvideo",
                        "-pix_fmt", "gray", "-"], capture_output=True, check=True)
    fr = np.frombuffer(p.stdout, np.uint8).reshape(-1, 480, 270).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    med = np.array([np.median(d[max(0, i-4):i+5]) for i in range(len(d))])
    return [i + 1 for i, v in enumerate(d) if v < 0.3 or v < 0.3 * med[i]]
REP = {a: repetidos(a) for a in {c[0] for c in CENAS}}

tmp = tempfile.mkdtemp()
partes = []
for i, (arq, q0, q1, f, extra) in enumerate(CENAS):
    n = round((q1 - q0) * f)
    rep = [r for r in REP[arq] if q0 <= r < q1]
    vf = f"trim=start_frame={q0}:end_frame={q1},setpts=(PTS-STARTPTS)*{f}"
    if rep:
        vf = "select='not(" + "+".join(f"eq(n,{r})" for r in rep) + ")'," + \
             f"trim=start={q0/FPS:.5f}:end={q1/FPS:.5f},setpts=(PTS-STARTPTS)*{f}"
    if f != 1.0 or rep:
        vf += f",{MCI},setpts=N/24/TB,tpad=stop=24:stop_mode=clone,trim=end_frame={n}"
    if extra:
        vf += "," + extra
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-i", arq, "-vf", vf, "-f", "rawvideo",
                               "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    saida = f"{tmp}/{i}.mkv"
    escritor = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                                 "-s", f"{W}x{H}", "-r", "24", "-i", "-", "-c:v", "libx264", "-qp", "0",
                                 "-preset", "ultrafast", saida], stdin=subprocess.PIPE)
    while True:
        b = leitor.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
        fr[Y0:Y1, X0:X1] = cv2.inpaint(fr[Y0:Y1, X0:X1], mask, 6, cv2.INPAINT_TELEA)
        escritor.stdin.write(fr.tobytes())
    escritor.stdin.close(); escritor.wait(); leitor.wait()
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                "csv=p=0", saida], capture_output=True, text=True).stdout)
    partes.append((saida, dur))

# encadeia com fusões
fc, ultimo, t = [], "[0:v]", partes[0][1]
for i, d in enumerate(FUSOES):
    off = t - d
    fc.append(f"{ultimo}[{i+1}:v]xfade=transition=fade:duration={d}:offset={off:.4f}[x{i}]")
    ultimo, t = f"[x{i}]", off + partes[i+1][1]
    print(f"cena {i+2} começa em {off:.2f} s")
# zoom leve: corta barra do topo (Reels) e rodapé (@ e enviar); mantém 9:16
fc.append(f"{ultimo}crop=621:1104:50:75,scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,format=yuv420p[v]")
na = len(partes)
af, labels = [], []
for k, (a, b, tempo, ini) in enumerate(FRASES):
    trim = f"atrim={a}:{b}" if b else f"atrim={a}"
    af.append(f"[{na}:a]{trim},asetpts=PTS-STARTPTS,atempo={tempo},adelay={int(ini*1000)}:all=1[a{k}]")
    labels.append(f"[a{k}]")
fc += af
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[a]")
cmd = ["ffmpeg", "-v", "error", "-y"]
for s, _ in partes: cmd += ["-i", s]
cmd += ["-i", "locucao-bruta.mp3", "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
        "-t", f"{t:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-r", "24",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "video.mp4"]
subprocess.run(cmd, check=True)
print(f"duração: {t:.2f} s")
