#!/usr/bin/env python3
"""Montagem do Reels "Semana de Mobilização contra a Dengue" (Prefeitura de Santanópolis).

Fonte editável da edição: lista de cenas, cortes no ritmo da trilha, transições,
tratamento de cor, faixas institucionais, legenda e vinheta.

Uso: python3 montagem.py <pasta-com-os-brutos IMG_55xx.MOV> <trilha.mp3>
Brutos: pasta do Drive "AGENTES DE ENDEMIAS". Trilha: Magnific (Lyria 3 Pro).
"""
import subprocess, sys, json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
BRUTOS = Path(sys.argv[1]); TRILHA = Path(sys.argv[2])
TMP = AQUI / "_tmp"; TMP.mkdir(exist_ok=True)

BEAT = 0.5195            # 115,5 BPM (medido na trilha)
TRILHA_INI = 21.32       # ponto da trilha no início do vídeo: o "drop" (25,32 s) cai no 1º corte
TD = 0.24                # duração das transições
W, H = 1080, 1920

# (arquivo, entrada em s, duração em batidas ou segundos, enquadramento, transição de entrada, etiqueta)
# enquadramento: None = vertical; ("x", a, b) = recorte 9:16 de vídeo horizontal, centro indo de a até b (0–1)
FALA = ("IMG_5546", 1.55, 4.0)          # corta a 1ª tentativa (0–1,5 s) em que ela repete a fala
CENAS = [
    # etiqueta: "LINHA 1|LINHA 2"; "+" = continua a etiqueta da cena anterior
    ("IMG_5535", 4.3, 4, None,            "zoomin",     "VISTORIA EM|CAIXAS-D'ÁGUA"),
    ("IMG_5538", 1.4, 2, None,            "smoothleft", "TRATAMENTO|DE FOCOS"),
    ("IMG_5538", 4.5, 2, None,            "smoothup",   "+"),
    ("IMG_5539", 1.7, 3, None,            "smoothleft", "VISTORIA|EM PNEUS"),
    ("IMG_5541", 0.3, 2, ("x", .64, .68), "slideup",    "+"),
    ("IMG_5542", 3.6, 4, ("x", .25, .58), "smoothleft", "VISTORIA|EM QUINTAIS"),
    ("IMG_5543", 4.4, 3, None,            "smoothup",   "FERROS-VELHOS|E SUCATAS"),
    ("IMG_5543", 9.3, 2, None,            "smoothleft", "+"),
    ("IMG_5535", 8.0, 2, None,            "slideup",    None),
    ("IMG_5539", 0.0, 3, None,            "smoothright", None),
]
GRITO = ("IMG_5546", 5.75, 2.6, "zoomin")  # grupo: "Todos contra a dengue!" (rotação da câmera mantida)
VINHETA = 3.0

COR = ("eq=contrast=1.08:brightness=0.012:saturation=1.22:gamma=0.97,"
       "colorbalance=rs=0.02:bs=-0.015:rh=0.025:bh=-0.02,unsharp=5:5:0.55:5:5:0,vignette=PI/6")


def run(cmd):
    subprocess.run(cmd, check=True)


def cena(nome, ini, dur, enq, saida, zoom=0.07):
    src = BRUTOS / f"{nome}.MOV"
    f = []
    if enq:
        _, a, b = enq
        cw = 1215  # 2160*9/16
        f.append(f"crop={cw}:2160:x='(({a})+(({b})-({a}))*t/{dur})*iw-{cw}/2':y=0")
    f.append("scale=2160:3840:flags=lanczos")
    f.append(f"scale=w='trunc(2160*(1+{zoom}*t/{dur})/2)*2':h=-2:eval=frame:flags=bicubic,crop=2160:3840")
    f.append(f"scale={W}:{H}:flags=lanczos,setsar=1,fps=30,{COR},format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", f"{dur:.3f}", "-i", str(src),
         "-an", "-vf", ",".join(f), "-c:v", "libx264", "-crf", "14", "-preset", "fast", str(saida)])


# 1) linha do tempo
tempos = [0.0, FALA[2]]
for c in CENAS:
    tempos.append(tempos[-1] + c[2] * BEAT)
fim_grito = tempos[-1] + GRITO[2]
print("cortes:", [round(t, 2) for t in tempos], "fim:", round(fim_grito, 2))

pecas = [(FALA[0], FALA[1], FALA[2], None, None)]
for i, c in enumerate(CENAS):
    pecas.append((c[0], c[1], tempos[i + 2] - tempos[i + 1] + TD, c[3], c[4]))
pecas.append((GRITO[0], GRITO[1], GRITO[2] + TD, None, GRITO[3]))

arqs = []
for i, (nome, ini, dur, enq, _) in enumerate(pecas):
    out = TMP / f"c{i:02d}.mp4"
    if not out.exists(): cena(nome, ini - (TD if i else 0), dur, enq, out, zoom=0.05 if i in (0, len(pecas) - 1) else 0.08)
    arqs.append(out)

# 2) transições (xfade) — cada transição termina exatamente na batida do corte
ent = []
for a in arqs:
    ent += ["-i", str(a)]
fc, atual = [], "0:v"
for i in range(1, len(arqs)):
    trans = pecas[i][4]
    off = (tempos[i] if i < len(tempos) else tempos[-1]) - TD
    fc.append(f"[{atual}][{i}:v]xfade=transition={trans}:duration={TD}:offset={off:.3f}[x{i}]")
    atual = f"x{i}"

# 3) legenda (fala + grito) embaixo, etiquetas das cenas, faixas
srt = AQUI / "legenda.srt"
g0 = tempos[-1] + (5.9 - GRITO[1])
srt.write_text(
    "1\n00:00:00,050 --> 00:00:02,950\nEstamos na semana de mobilização contra o mosquito da dengue\n\n"
    f"2\n00:00:{g0:06.3f} --> 00:00:{g0 + 1.75:06.3f}\nTodos contra a dengue!\n".replace(".", ","),
    encoding="utf-8")
ass = AQUI / "efeitos.ass"
run(["python3", str(RAIZ / "ferramentas/efeitos.py"), "-c", "prefeitura-santanopolis", "-f", "9x16",
     "-l", str(srt), "-o", str(ass)])
txt = ass.read_text(encoding="utf-8").replace(",1306)", ",1650)")  # legenda embaixo, acima da linha branca
# lettering das cenas: barra branca + chapéu "AGENTES DE ENDEMIAS" + título em 2 linhas, alinhado à esquerda
txt = txt.replace("[Events]",
    "Style: Chapeu,Inter SemiBold,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,6,0,1,0,2,7,0,0,0,1\n"
    "Style: Titulo,Exo 2 ExtraBold,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,0,3,7,0,0,0,1\n\n[Events]")
def ts(s): return f"0:00:{s:05.2f}"
blocos = []
for i, c in enumerate(CENAS):
    if c[5] == "+":
        blocos[-1][2] = tempos[i + 2]
    elif c[5]:
        blocos.append([c[5], tempos[i + 1], tempos[i + 2]])
X, Y = 96, 1395
for rot, a, z in blocos:
    a, z = a + 0.12, z - 0.12
    l1, l2 = rot.split("|")
    out = int((z - a) * 1000) - 200
    txt += (f"Dialogue: 4,{ts(a)},{ts(z)},Titulo,,0,0,0,,{{\\an7\\bord0\\shad0\\1c&HFFFFFF&\\fscy0"
            f"\\pos({X - 34},{Y})\\t(0,260,\\fscy100)\\t({out},{out + 200},\\fscy0)\\p1}}m 0 0 l 10 0 l 10 262 l 0 262{{\\p0}}\n")
    txt += (f"Dialogue: 5,{ts(a)},{ts(z)},Chapeu,,0,0,0,,{{\\an7\\move({X - 20},{Y},{X},{Y},80,380)"
            f"\\fad(220,180)}}AGENTES DE ENDEMIAS\n")
    txt += (f"Dialogue: 5,{ts(a)},{ts(z)},Titulo,,0,0,0,,{{\\an7\\move({X},{Y + 74},{X},{Y + 44},120,420)"
            f"\\fad(260,180)\\blur0.6}}{l1}\\N{l2}\n")
ass.write_text(txt, encoding="utf-8")
fontes = RAIZ / "ferramentas/fontes/ttf"
n = len(arqs)
ent += ["-loop", "1", "-i", str(AQUI / "faixas.png"), "-loop", "1", "-t", str(VINHETA), "-i", str(AQUI / "vinheta.png")]
fc.append(f"[{atual}][{n}:v]overlay=0:0:shortest=1,ass='{ass}':fontsdir='{fontes}',format=yuv420p,settb=1/30[vm]")
fc.append(f"[{n+1}:v]scale={W}:{H},setsar=1,fps=30,format=yuv420p,settb=1/30[vin]")
fc.append(f"[vm][vin]xfade=transition=fadeblack:duration=0.35:offset={fim_grito - 0.35:.3f}[vout]")

# 4) áudio: fala limpa + grito, trilha com "ducking" sob a fala
total = fim_grito - 0.35 + VINHETA
src = str(BRUTOS / "IMG_5546.MOV")
ent += ["-ss", str(FALA[1]), "-t", str(FALA[2]), "-i", src,
        "-ss", str(GRITO[1]), "-t", str(GRITO[2]), "-i", src,
        "-ss", str(TRILHA_INI), "-i", str(TRILHA)]
voz = "highpass=f=90,afftdn=nf=-25,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=4,aresample=48000,aformat=channel_layouts=stereo"
fc.append(f"[{n+2}:a:0]{voz},volume=1.6,afade=t=in:d=0.04,afade=t=out:st={FALA[2]-0.15}:d=0.15[v1]")
fc.append(f"[{n+3}:a:0]{voz},volume=0.9,afade=t=in:d=0.08,afade=t=out:st={GRITO[2]-0.3}:d=0.3,adelay={int(tempos[-1]*1000)}|{int(tempos[-1]*1000)}[v2]")
gv = f"if(lt(t,{FALA[2]-0.25}),0.16,if(lt(t,{tempos[-1]}),0.7,if(lt(t,{fim_grito-0.2}),0.28,0.85)))"
fc.append(f"[{n+4}:a]aresample=48000,aformat=channel_layouts=stereo,volume='{gv}':eval=frame,"
          f"atrim=0:{total:.3f},afade=t=out:st={total-0.8:.3f}:d=0.8[mu]")
fc.append("[mu][v1][v2]amix=inputs=3:normalize=0:duration=first,volume=0.78,alimiter=limit=0.95[aout]")

saida = AQUI / "semana-mobilizacao-contra-a-dengue.mp4"
run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
     "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", str(saida)])
print("Pronto:", saida, round(total, 2), "s")
