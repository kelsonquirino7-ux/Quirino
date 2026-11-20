#!/usr/bin/env python3
"""Reels Itamar · Consciência Negra — versão 4 (só o vídeo de melhor qualidade: bruto-v1.mp4).
- Remove ícones do Reels (coração, 5118, comentário) por inpainting; barra do topo e @ saem com zoom leve.
- Cenas na velocidade original; só a família (movimento suave) e o brilho final da logo ganham câmera lenta
  com interpolação de movimento. Fecha segurando a logo com aproximação suave.
- Locução (locucao-v2.mp3, voz única) encaixada frase a frase na legenda de cada cena."""
import subprocess, os, tempfile
import numpy as np, cv2
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SRC, W, H, FPS = "bruto-v1.mp4", 720, 1280, 24
TOTAL = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                           "stream=nb_read_frames", "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout)
MCI = "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none"
LUZ = "eq=brightness=0.02:contrast=1.05:saturation=1.06"
# (quadro inicial, quadro final, câmera lenta, filtro, fusão com a cena anterior em s)
CENAS = [(0,   110, 1.0, "",  0),     # senhora — "Uma história de força, coragem e resistência..."
         (300, 333, 1.0, LUZ, 0.5),   # capoeira — "Uma cultura que atravessa gerações..."
         (152, 238, 1.0, LUZ, 0.3),   # capoeira com a logo surgindo (mesma legenda)
         (364, 431, 2.0, "",  0.6),   # família — "Uma história que merece ser reconhecida..."
         (431, 451, 1.0, "",  0),     # logo se aproximando (velocidade original)
         (451, 481, 3.0, "",  0)]     # logo pousada, brilho em câmera lenta
SEGURA = 5.0                          # segundos segurando a logo no fim (aproximação suave)
# frases na gravação: (início, fim, aceleração, entrada no vídeo em s)
FRASES = [(0.03, 3.66, 1.00, 0.45),    # Uma história de força, coragem e resistência...
          (4.06, 8.69, 1.08, 4.20),    # Uma cultura que atravessa gerações...
          (9.10, 14.75, 1.12, 8.55),   # Uma história que merece ser reconhecida...
          (15.07, 18.04, 1.00, 14.25), # Porque igualdade se constrói todos os dias.
          (18.38, 23.60, 1.00, 17.40)] # Itamar Supermercado. Respeitar nossas raízes é valorizar nossa história.

# máscara dos ícones do Reels (fixos na lateral direita)
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.5", "-to", "5", "-i", SRC, "-f", "rawvideo",
                    "-pix_fmt", "gray", "-"], capture_output=True, check=True)
X0, Y0, X1, Y1 = 600, 940, 720, 1180
mn = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W).min(0)[Y0:Y1, X0:X1]
mask = cv2.dilate((mn > 150).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))

tmp = tempfile.mkdtemp()
partes = []
for i, (q0, q1, f, extra, _) in enumerate(CENAS):
    n = round((q1 - q0) * f)
    vf = f"trim=start_frame={q0}:end_frame={q1},setpts=(PTS-STARTPTS)*{f}"
    if f != 1.0:
        # lê um quadro a mais para a interpolação chegar ao fim sem repetir quadros (evita engasgo)
        q1e = min(q1 + 1, TOTAL)
        n = min(n, round((q1e - q0 - 1) * f) + 1)
        vf = f"trim=start_frame={q0}:end_frame={q1e},setpts=(PTS-STARTPTS)*{f},{MCI},setpts=N/24/TB,trim=end_frame={n}"
    if extra:
        vf += "," + extra
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-vf", vf, "-f", "rawvideo",
                               "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    saida = f"{tmp}/{i}.mkv"
    escritor = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
                                 "-s", f"{W}x{H}", "-r", "24", "-i", "-", "-c:v", "libx264", "-qp", "0",
                                 "-preset", "ultrafast", saida], stdin=subprocess.PIPE)
    ultimo_q = None
    while True:
        b = leitor.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy()
        fr[Y0:Y1, X0:X1] = cv2.inpaint(fr[Y0:Y1, X0:X1], mask, 6, cv2.INPAINT_TELEA)
        escritor.stdin.write(fr.tobytes()); ultimo_q = fr
    escritor.stdin.close(); escritor.wait(); leitor.wait()
    partes.append((saida, n / FPS))
cv2.imwrite(f"{tmp}/fim.png", ultimo_q)

# fim: segura a logo com aproximação suave (zoom feito em 4x para não tremer)
nf = round(SEGURA * FPS)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", f"{tmp}/fim.png", "-vf",
                f"scale={W*4}:{H*4}:flags=lanczos,zoompan=z='1+0.06*on/{nf}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
                f":d={nf}:s={W}x{H}:fps=24", "-frames:v", str(nf), "-c:v", "libx264", "-qp", "0",
                "-preset", "ultrafast", f"{tmp}/fim.mkv"], check=True)
partes.append((f"{tmp}/fim.mkv", SEGURA))
fusoes = [c[4] for c in CENAS[1:]] + [0]

fc, ultimo, t = [], "[0:v]", partes[0][1]
for i, d in enumerate(fusoes):
    if d:
        off = t - d
        fc.append(f"{ultimo}[{i+1}:v]xfade=transition=fade:duration={d}:offset={off:.4f}[x{i}]")
    else:
        off = t
        fc.append(f"{ultimo}[{i+1}:v]concat=n=2:v=1:a=0[x{i}]")
    ultimo, t = f"[x{i}]", off + partes[i+1][1]
    print(f"parte {i+2} começa em {off:.2f} s")
fc.append(f"{ultimo}crop=621:1104:50:75,scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,format=yuv420p[v]")
na = len(partes)
labels = []
for k, (a, b, tempo, ini) in enumerate(FRASES):
    fc.append(f"[{na}:a]atrim={a}:{b},asetpts=PTS-STARTPTS,atempo={tempo},adelay={int(ini*1000)}:all=1[a{k}]")
    labels.append(f"[a{k}]")
    print(f"frase {k+1}: {ini:.2f}–{ini+(b-a)/tempo:.2f} s")
fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad[a]")
cmd = ["ffmpeg", "-v", "error", "-y"]
for s, _ in partes: cmd += ["-i", s]
cmd += ["-i", "locucao-v2.mp3", "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
        "-t", f"{t:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-r", "24",
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "video.mp4"]
subprocess.run(cmd, check=True)
print(f"duração: {t:.2f} s")
