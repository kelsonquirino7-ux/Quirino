#!/usr/bin/env python3
"""Reels Itamar · Consciência Negra — versão 5 (imagem só do vídeo de melhor qualidade: bruto-v1.mp4).
- Capoeira: tomadas do 1º vídeo sem logo/luzes + a tomada do pátio do 2º vídeo, com a cor levada à do 1º.
- Final com luzes girando em volta da logo: magnific/luzes-final.mp4 (Kling 2.5 no Magnific, a partir do
  último quadro do vídeo); o texto da legenda é recolado do quadro original para continuar nítido.
- Remove ícones do Reels (coração, 5118, comentário) por inpainting; barra do topo e @ saem com zoom leve.
- Cenas na velocidade original; só a família (movimento suave) e o brilho final da logo ganham câmera lenta
  com interpolação de movimento. Fecha segurando a logo com aproximação suave.
- Locução (locucao-v2.mp3, voz única) encaixada frase a frase na legenda de cada cena."""
import subprocess, os, tempfile
import numpy as np, cv2
os.chdir(os.path.dirname(os.path.abspath(__file__)))
SRC, W, H, FPS = "bruto-v1.mp4", 720, 1280, 24
def total(arq):
    return int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries",
                               "stream=nb_read_frames", "-of", "csv=p=0", arq], capture_output=True, text=True).stdout)
V2 = "bruto.mp4"   # 2º vídeo do Gemini: só a tomada da capoeira no pátio
LUZES = "magnific/luzes-final.mp4"
MCI = "minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none"
LUZ = "eq=brightness=0.02:contrast=1.05:saturation=1.06"
# (arquivo, quadro inicial, quadro final, câmera lenta, filtro, fusão com a cena anterior em s)
CENAS = [(SRC,   0,   110, 1.0, "",  0),     # senhora — "Uma história de força, coragem e resistência..."
         (SRC,   156, 178, 1.6, LUZ, 0.5),   # capoeira (antes da logo e das luzes) — "Uma cultura..."
         (SRC,   300, 356, 1.6, LUZ, 0.25),  # capoeira, mesma legenda (câmera lenta por fluxo óptico)
         (SRC,   364, 431, 2.0, "",  0.6),   # família — "Uma história que merece ser reconhecida..."
         (SRC,   431, 451, 1.0, "",  0),     # logo se aproximando (velocidade original)
         (SRC,   451, 479, 3.0, "",  0),     # logo pousada, brilho em câmera lenta
         (LUZES, 1,   121, 1.0, "",  0)]     # luzes girando em volta da logo (Magnific)
# frases na gravação: (início, fim, aceleração, entrada no vídeo em s)
FRASES = [(0.03, 3.66, 1.00, 0.45),    # Uma história de força, coragem e resistência...
          (4.06, 8.69, 1.08, 4.35),    # Uma cultura que atravessa gerações...
          (9.10, 14.75, 1.12, 9.10),   # Uma história que merece ser reconhecida...
          (15.07, 18.04, 1.00, 14.80), # Porque igualdade se constrói todos os dias.
          (18.38, 23.60, 1.00, 17.95)] # Itamar Supermercado. Respeitar nossas raízes é valorizar nossa história.

# máscara dos ícones do Reels (fixos na lateral direita)
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "0.5", "-to", "5", "-i", SRC, "-f", "rawvideo",
                    "-pix_fmt", "gray", "-"], capture_output=True, check=True)
X0, Y0, X1, Y1 = 600, 940, 720, 1180
mn = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W).min(0)[Y0:Y1, X0:X1]
mask = cv2.dilate((mn > 150).astype(np.uint8) * 255, np.ones((9, 9), np.uint8))

tmp = tempfile.mkdtemp()
partes = []
# texto da legenda final, recolado sobre o clipe das luzes (o gerador de vídeo amolece letras)
fim = cv2.imread("magnific/logo-final.png")
hsv = cv2.cvtColor(fim, cv2.COLOR_BGR2HSV)
txt = ((hsv[..., 2] > 170) & (hsv[..., 1] < 60)).astype(np.uint8) * 255
txt[:1000] = 0; txt[1140:] = 0
txt_a = cv2.GaussianBlur(cv2.dilate(txt, np.ones((5, 5), np.uint8)), (0, 0), 1.2)[..., None] / 255.0

# cor: leva a tomada do 2º vídeo à coloração da capoeira do 1º (casamento de histograma por canal Lab,
# com uma única tabela para a cena toda: sem cintilação)
def lab_px(arq, q0, q1, extra=""):
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-vf",
                        f"trim=start_frame={q0}:end_frame={q1},scale=180:320" + ("," + extra if extra else ""),
                        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True, check=True)
    fr = np.frombuffer(p.stdout, np.uint8).reshape(-1, 320, 180, 3)
    return np.concatenate([cv2.cvtColor(f, cv2.COLOR_BGR2LAB).reshape(-1, 3) for f in fr])
alvo, orig = lab_px(SRC, 300, 356, LUZ), lab_px(V2, 60, 101)
LUTS = []
for c in range(3):
    ho = np.cumsum(np.bincount(orig[:, c], minlength=256)).astype(np.float64); ho /= ho[-1]
    ha = np.cumsum(np.bincount(alvo[:, c], minlength=256)).astype(np.float64); ha /= ha[-1]
    lut = np.interp(ho, ha, np.arange(256))
    LUTS.append(cv2.GaussianBlur(lut.reshape(1, -1), (1, 9), 0).ravel().clip(0, 255).astype(np.uint8))

def dourado(fr, da, db, lift, glow):
    """Tom dourado de fim de tarde + leve névoa (mesma receita em todas as cenas filmadas)."""
    lab = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 1] += da; lab[..., 2] += db
    lab[..., 0] = lift + lab[..., 0] * (1 - lift / 255)
    x = cv2.cvtColor(lab.clip(0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR).astype(np.float32)
    if glow:
        x = 255 - (255 - x) * (1 - glow * cv2.GaussianBlur(x, (0, 0), 25) / 255)
    return x.clip(0, 255).astype(np.uint8)

def ajusta_cor(fr):
    """Tomada do 2º vídeo: casa histograma com a capoeira do 1º e completa o tom dourado/névoa dele."""
    lab = cv2.cvtColor(fr, cv2.COLOR_BGR2LAB)
    lab = cv2.merge([cv2.LUT(lab[..., c], LUTS[c]) for c in range(3)])
    return dourado(cv2.cvtColor(lab, cv2.COLOR_LAB2BGR), 5, 14, 16, 0.35)

# acabamento comum a todas as cenas filmadas (senhora, capoeira, família), para ficarem iguais;
# a logo do final não recebe, para manter as cores da marca
ACABAMENTO = (2, 5, 6, 0.12)

for i, (arq, q0, q1, f, extra, _) in enumerate(CENAS):
    n = round((q1 - q0) * f)
    vf = f"trim=start_frame={q0}:end_frame={q1},setpts=(PTS-STARTPTS)*{f}"
    if f != 1.0:
        # lê um quadro a mais para a interpolação chegar ao fim sem repetir quadros (evita engasgo)
        q1e = min(q1 + 1, total(arq))
        n = min(n, round((q1e - q0 - 1) * f) + 1)
        vf = f"trim=start_frame={q0}:end_frame={q1e},setpts=(PTS-STARTPTS)*{f},{MCI},setpts=N/24/TB,trim=end_frame={n}"
    if f != 1.0 and extra == LUZ:
        # capoeira: câmera lenta por fluxo óptico (sem blocos nem quadros repetidos)
        lento = f"{tmp}/lento{i}.mkv"
        subprocess.run(["python3", "../../../../ferramentas/camlenta.py", arq, str(q0), str(q1), str(f), lento], check=True)
        arq_l, n = lento, total(lento)
        vf = "null"
    else:
        arq_l = arq
    if extra and arq != V2:
        vf += "," + extra
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-i", arq_l, "-vf", vf, "-f", "rawvideo",
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
        if arq == V2:
            fr = ajusta_cor(fr)
        if arq == V2 or (arq == SRC and q1 <= 431):
            fr = dourado(fr, *ACABAMENTO)
        if arq == LUZES:
            fr = (fr * (1 - txt_a) + fim * txt_a).astype(np.uint8)
        escritor.stdin.write(fr.tobytes()); ultimo_q = fr
    escritor.stdin.close(); escritor.wait(); leitor.wait()
    partes.append((saida, n / FPS))
fusoes = [c[5] for c in CENAS[1:]]

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
