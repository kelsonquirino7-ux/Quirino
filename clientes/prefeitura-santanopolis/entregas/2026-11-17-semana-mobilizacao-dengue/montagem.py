#!/usr/bin/env python3
"""Montagem do Reels "Semana de Mobilização contra a Dengue" (Prefeitura de Santanópolis).

Fonte editável da edição: lista de cenas, cortes no ritmo da trilha, transições,
tratamento de cor, faixas institucionais, legenda e vinheta.

Uso: python3 montagem.py <pasta-com-os-brutos IMG_55xx.MOV> <trilha.mp3>
Brutos: pasta do Drive "AGENTES DE ENDEMIAS" + IMG_5522/5528/5529 (links avulsos). Trilha: Magnific (Lyria 3 Pro).
Duração fechada em 60 s. A trilha é emendada uma vez (fim do 1º bloco → trecho calmo da introdução)
e segue contínua até a batida final, que cai junto com a vinheta.
"""
import subprocess, sys, json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
BRUTOS = Path(sys.argv[1]); TRILHA = Path(sys.argv[2])
TMP = AQUI / "_tmp"; TMP.mkdir(exist_ok=True)

BEAT = 0.519375          # 115,5 BPM (medido na trilha)
TRILHA_INI = 21.32       # ponto da trilha no início do vídeo: o "drop" (25,32 s) cai no 1º corte
TRILHA_EMENDA = 6.5125   # depois do 1º bloco (32 batidas) a trilha volta a este ponto calmo da introdução
DURACAO = 60.0
TD = 0.24                # duração das transições
W, H = 1080, 1920

# (arquivo, entrada em s, duração em batidas ou segundos, enquadramento, transição de entrada, etiqueta)
# enquadramento: None = vertical; ("x", a, b) = recorte 9:16 de vídeo horizontal, centro indo de a até b (0–1)
FALA = ("IMG_5546", 1.55, 4.0)          # corta a 1ª tentativa (0–1,5 s) em que ela repete a fala
CENAS = [
    # Cada vídeo do Drive aparece UMA vez, inteiro (enquadramento original, sem zoom nem recorte).
    # duração: inteiro = batidas; decimal = segundos. enquadramento "H" = vídeo horizontal inteiro sobre fundo desfocado.
    # etiqueta: "LINHA 1|LINHA 2"; "+" = continua a anterior
    # — bloco 1 (drop, 32 batidas)
    ("IMG_5514", 0.3, 8, None, "zoomin",     "EQUIPES|NAS RUAS"),
    ("IMG_5527", 0.3, 8, None, "smoothleft", "MUTIRÃO|DE LIMPEZA"),
    ("IMG_5516", 0.3, 8, None, "smoothup",   "+"),
    ("IMG_5517", 0.3, 8, None, "smoothleft", "ELIMINAÇÃO|DE CRIADOUROS"),
    # — bloco 2 (introdução calma, 20 batidas)
    ("IMG_5528", 0.3, 12, None, "fade",      "VISITA ÀS|RESIDÊNCIAS"),
    ("IMG_5529", 5.6, 8, None,  "fade",      "TRATAMENTO DE|RESERVATÓRIOS"),
    # — bloco 3 (1º drop 12 batidas + respiro)
    ("IMG_5534", 0.5, 8, "H",   "zoomin",    "+"),
    ("IMG_5522", 0.4, 4, None,  "smoothup",  "RECOLHIMENTO|DE GARRAFAS"),
    ("IMG_5535", 4.3, 8.42 - 12 * 0.519375, None, "fade", "VISTORIA EM|CAIXAS-D'ÁGUA"),
    # — bloco 4 (drop final, 27 batidas + grito nas 5 últimas)
    ("IMG_5538", 0.5, 6, None,  "zoomin",     "TRATAMENTO|DE FOCOS"),
    ("IMG_5539", 1.7, 6, None,  "smoothleft", "VISTORIA|EM PNEUS"),
    ("IMG_5541", 0.3, 4, "H",   "smoothup",   "+"),
    ("IMG_5542", 3.6, 6, "H",   "smoothleft", "VISTORIA|EM QUINTAIS"),
    ("IMG_5543", 4.4, 5, None,  "smoothup",   "FERROS-VELHOS|E SUCATAS"),
]
GRITO = ("IMG_5546", 5.75, 2.6, "zoomin")  # grupo: "Todos contra a dengue!" (rotação da câmera mantida)

COR = ("eq=contrast=1.08:brightness=0.012:saturation=1.22:gamma=0.97,"
       "colorbalance=rs=0.02:bs=-0.015:rh=0.025:bh=-0.02,unsharp=5:5:0.55:5:5:0")
COR_SEM_VINHETA = COR
COR = COR + ",vignette=PI/7"


def run(cmd):
    subprocess.run(cmd, check=True)


def cena(nome, ini, dur, enq, saida):
    """Enquadramento original: vertical ocupa a tela inteira; horizontal entra inteiro no centro,
    com o próprio vídeo ampliado e desfocado atrás (nada é cortado)."""
    src = BRUTOS / f"{nome}.MOV"
    if enq == "H":
        vf = (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"gblur=sigma=45,eq=brightness=-0.10:saturation=0.9[bg];"
              f"[b]scale={W}:-2:flags=lanczos,{COR_SEM_VINHETA}[fg];[bg][fg]overlay=0:(H-h)/2,"
              f"setsar=1,fps=30,format=yuv420p")
    else:
        vf = f"scale={W}:{H}:flags=lanczos,setsar=1,fps=30,{COR},format=yuv420p"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ini), "-t", f"{dur:.3f}", "-i", str(src),
         "-an", "-filter_complex", vf, "-c:v", "libx264", "-crf", "14", "-preset", "fast", str(saida)])


# 1) linha do tempo
tempos = [0.0, FALA[2]]
for c in CENAS:
    tempos.append(tempos[-1] + (c[2] * BEAT if isinstance(c[2], int) else c[2]))
fim_grito = tempos[-1] + GRITO[2]
VINHETA = DURACAO - (fim_grito - 0.35)   # a vinheta completa os 60 s
print("cortes:", [round(t, 2) for t in tempos], "fim:", round(fim_grito, 2))

pecas = [(FALA[0], FALA[1], FALA[2], None, None)]
for i, c in enumerate(CENAS):
    pecas.append((c[0], c[1], tempos[i + 2] - tempos[i + 1] + TD, c[3], c[4]))
pecas.append((GRITO[0], GRITO[1], GRITO[2] + TD, None, GRITO[3]))

arqs = []
for i, (nome, ini, dur, enq, _) in enumerate(pecas):
    out = TMP / f"c{i:02d}.mp4"
    if not out.exists(): cena(nome, ini - (TD if i else 0), dur, enq, out)
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
fc.append(f"[vm][vin]xfade=transition=fadeblack:duration=0.35:offset={fim_grito - 0.35:.3f}[vb]")
# linha-cronômetro: a faixa azul avança sobre a branca e cobre tudo no último quadro
T = fim_grito - 0.35 + VINHETA
fc.append(f"color=c=0x002F67:s={W}x16:r=30:d={T:.3f}[pb]")
fc.append(f"[vb]drawbox=x=0:y={H-16}:w={W}:h=16:color=white:t=fill[vw]")
fc.append(f"[vw][pb]overlay=x='-w+w*min(1,t/({T:.3f}-1/30))':y={H-16}:eval=frame[vout]")

# 4) áudio: fala limpa + grito, trilha com "ducking" sob a fala
total = fim_grito - 0.35 + VINHETA
src = str(BRUTOS / "IMG_5546.MOV")
ent += ["-ss", str(FALA[1]), "-t", str(FALA[2]), "-i", src,
        "-ss", str(GRITO[1]), "-t", str(GRITO[2]), "-i", src,
        "-ss", str(TRILHA_INI), "-t", f"{FALA[2] + 32 * BEAT + 0.03:.3f}", "-i", str(TRILHA),  # bloco 1 (+ cruzamento)
        "-ss", str(TRILHA_EMENDA), "-i", str(TRILHA)]
voz = "highpass=f=90,afftdn=nf=-25,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=4,aresample=48000,aformat=channel_layouts=stereo"
fc.append(f"[{n+2}:a:0]{voz},volume=1.6,afade=t=in:d=0.04,afade=t=out:st={FALA[2]-0.15}:d=0.15[v1]")
fc.append(f"[{n+3}:a:0]{voz},volume=0.9,afade=t=in:d=0.08,afade=t=out:st={GRITO[2]-0.3}:d=0.3,adelay={int(tempos[-1]*1000)}|{int(tempos[-1]*1000)}[v2]")
gv = f"if(lt(t,{FALA[2]-0.25}),0.16,if(lt(t,{tempos[-1]}),0.7,if(lt(t,{fim_grito-0.2}),0.28,0.85)))"
fc.append(f"[{n+4}:a][{n+5}:a]acrossfade=d=0.03:c1=tri:c2=tri,aresample=48000,aformat=channel_layouts=stereo,apad,volume='{gv}':eval=frame,"
          f"atrim=0:{total:.3f},afade=t=out:st={total-0.8:.3f}:d=0.8[mu]")
fc.append("[mu][v1][v2]amix=inputs=3:normalize=0:duration=first,volume=0.78,alimiter=limit=0.95[aout]")

saida = AQUI / "semana-mobilizacao-contra-a-dengue.mp4"
run(["ffmpeg", "-v", "error", "-y", *ent, "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
     "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-maxrate", "10M", "-bufsize", "20M", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", str(saida)])
print("Pronto:", saida, round(total, 2), "s")
