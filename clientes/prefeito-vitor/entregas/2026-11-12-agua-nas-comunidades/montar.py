#!/usr/bin/env python3
"""Monta o Reels "Água nas comunidades" (Vitor) — fonte editável da edição.

Uso (na raiz do repositório):
  python3 clientes/prefeito-vitor/entregas/2026-11-12-agua-nas-comunidades/montar.py <pasta-dos-brutos> <musica.mp3> [pasta-temp]

Brutos (pasta "ÁGUA NAS COMUNIDADES" do Drive do cliente; não ficam no repositório por tamanho):
  1.MOV 2.MOV 3.MOV 4.MOV (falas) · tubos.MOV · tubos-e-carro-pipa.MOV · cesta-basica.MOV
Antes: node cartoes.js (gera cartoes/*.png). Tempos das palavras em palavras.json (Whisper).
Saídas: video.mp4, legenda.srt e video-efeitos.ass nesta pasta.
"""
import json, subprocess, sys, re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
sys.path.insert(0, str(RAIZ / "ferramentas"))
from efeitos import Medidor, caixa_arredondada, cor_ass, ts  # noqa: E402

BRUTOS = Path(sys.argv[1]); MUSICA = Path(sys.argv[2])
TMP = Path(sys.argv[3]) if len(sys.argv) > 3 else AQUI / "tmp"
TMP.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1080, 1920, 30
q = lambda t: round(t * FPS) / FPS  # arredonda para quadro inteiro


def run(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, a)], check=True)


# ---------- 1) Roteiro de cortes -------------------------------------------------------------
# Falas: (arquivo, entrada, saída) em segundos do bruto. O áudio da fala corre inteiro;
# o vídeo troca entre Vitor (com ou sem zoom) e cenas de apoio.
FALAS = [("1", 0.45, 8.15), ("2", 0.55, 31.25), ("3", 0.00, 2.95), ("4", 0.30, 14.05)]
# Por fala: (início, fim, "v" Vitor | nome do apoio, zoom ou início no apoio)
CORTES = {
    "1": [(0.45, 3.50, "v", 1.0), (3.50, 5.20, "v", 1.14), (5.20, 8.15, "v", 1.0)],
    "2": [(0.55, 2.20, "v", 1.0), (2.20, 4.45, "tubos-e-carro-pipa", 2.6), (4.45, 7.40, "tubos-e-carro-pipa", 8.0),
          (7.40, 8.95, "v", 1.14), (8.95, 12.70, "v", 1.0), (12.70, 15.30, "tubos", 0.5), (15.30, 17.30, "v", 1.14),
          (17.30, 20.90, "v", 1.0), (20.90, 23.50, "tubos", 3.8), (23.50, 25.60, "v", 1.14),
          (25.60, 27.10, "v", 1.0), (27.10, 29.70, "tubos", 5.0), (29.70, 31.25, "v", 1.0)],
    "3": [(0.00, 2.95, "v", 1.14)],
    "4": [(0.30, 3.45, "v", 1.0), (3.45, 4.55, "v", 1.14), (4.55, 6.00, "cesta-basica", 5.8),
          (6.00, 9.60, "cesta-basica", 0.5), (9.60, 14.05, "v", 1.0)],
}
# Final: a última cena do Vitor desfoca e a logo entra por cima (as imagens de apoio ficam só durante a fala)
DUR_FINAL = 3.0

inicio = {}  # início de cada fala na linha do tempo
t = 0.0
for nome, a, z in FALAS:
    inicio[nome] = t
    t += q(z - a)
T_FINAL = t
TOTAL = T_FINAL + DUR_FINAL
G = lambda fala, local: inicio[fala] + local - dict((n, a) for n, a, _ in FALAS)[fala]  # local -> global

segs = []
for nome, _, _ in FALAS:
    for a, z, tipo, p in CORTES[nome]:
        segs.append((BRUTOS / f"{nome}.MOV", a, q(z - a), p, 1) if tipo == "v" else (BRUTOS / f"{tipo}.MOV", p, q(z - a), 1.0, 0))
segs.append((BRUTOS / "4.MOV", 14.05, DUR_FINAL, 1.0, 2))

partes = []
for i, (src, a, d, zoom, tipo) in enumerate(segs):
    out = TMP / f"seg{i:02d}.mp4"
    partes.append(out)
    if out.exists():
        continue
    vf = (f"scale={round(W * zoom / 2) * 2}:-2,crop={W}:{H}:(iw-{W})/2:(ih-{H})*0.30,fps={FPS},setsar=1,format=yuv420p")
    if tipo == 2:  # fundo do final: mesma cena em câmera lenta, desfocando e escurecendo
        vf = ("setpts=1.85*PTS," + vf + ",split[s][t];[t]gblur=sigma=24,eq=brightness=-0.09,format=yuva420p,"
              "fade=t=in:st=0:d=0.5:alpha=1[u];[s][u]overlay,format=yuv420p")
    run("-ss", f"{a:.3f}", "-i", src, "-an", "-vf", vf, "-frames:v", round(d * FPS),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", out)
(TMP / "lista.txt").write_text("".join(f"file '{p}'\n" for p in partes))
run("-f", "concat", "-safe", "0", "-i", TMP / "lista.txt", "-c", "copy", TMP / "base.mp4")

# ---------- 2) Áudio: voz normalizada + trilha baixa, subindo no final -------------------------
ent, f = [], ""
for i, (nome, a, z) in enumerate(FALAS):
    ent += ["-i", BRUTOS / f"{nome}.MOV"]
    f += (f"[{i}:a:0]atrim={a}:{a + q(z - a):.4f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,"
          f"afade=t=in:d=0.04,afade=t=out:st={q(z - a) - 0.05:.3f}:d=0.05[f{i}];")
n = len(FALAS)
f += "".join(f"[f{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,highpass=f=80,loudnorm=I=-15:TP=-1.5:LRA=9,apad=pad_dur={DUR_FINAL}[voz];"
ent += ["-i", MUSICA, "-i", MUSICA]
sobe = T_FINAL - 0.4
f += (f"[{n}:a][{n + 1}:a]acrossfade=d=1.5:c1=tri:c2=tri,aresample=48000,aformat=channel_layouts=stereo,atrim=0:{TOTAL:.3f},"
      f"volume='0.11+0.45*clip((t-{sobe:.2f})/0.8,0,1)':eval=frame,afade=t=in:d=0.6,afade=t=out:st={TOTAL - 1.1:.2f}:d=1.1[mus];"
      f"[voz][mus]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.79,atrim=0:{TOTAL:.3f}[a]")
run(*ent, "-filter_complex", f, "-map", "[a]", "-c:a", "pcm_s16le", TMP / "audio.wav")

# ---------- 3) Legenda palavra a palavra (tempos do Whisper) ----------------------------------
cfg = json.loads((RAIZ / "clientes/prefeito-vitor/video.json").read_text(encoding="utf-8"))
palavras = []  # (início global, fim global, texto, quebra depois?)
for nome, ws in json.loads((AQUI / "palavras.json").read_text(encoding="utf-8")).items():
    for a, z, w in ws:
        palavras.append([G(nome, a), G(nome, z), w, bool(re.search(r"[.,?!:]$", w))])
S, CY = 80, H * 0.56
medir = Medidor(RAIZ / "ferramentas/fontes/ttf" / cfg["arquivo_fonte"], S)
caixa, tcaixa = cor_ass(cfg["caixa"]), cor_ass(cfg["texto_caixa"])
blocos, atual = [], []
for i, p in enumerate(palavras):
    atual.append(p)
    prox = palavras[i + 1] if i + 1 < len(palavras) else None
    txt = " ".join(re.sub(r"[.,?!:]", "", x[2]).upper() for x in atual + ([prox] if prox else []))
    if not prox or p[3] or prox[0] - p[1] > 0.4 or len(atual) >= 3 or medir(txt) > W * 0.80:
        blocos.append(atual); atual = []
ev, srt = [], []
esp = medir(" ") * 2
for b, bloco in enumerate(blocos):
    tx = [re.sub(r"[.,!:]", "", x[2]).upper() for x in bloco]
    larg = [medir(x) for x in tx]
    x = W / 2 - (sum(larg) + esp * (len(tx) - 1)) / 2
    cent = []
    for lw in larg:
        cent.append(x + lw / 2); x += lw + esp
    limite = blocos[b + 1][0][0] if b + 1 < len(blocos) else T_FINAL
    fim_bloco = min(bloco[-1][1] + 0.35, limite)
    srt.append((bloco[0][0], fim_bloco, " ".join(x[2] for x in bloco)))
    for i, p in enumerate(bloco):
        a = p[0]
        z = bloco[i + 1][0] if i + 1 < len(bloco) else fim_bloco
        entrada = r"\fscx88\fscy88\t(0,90,\fscx100\fscy100)" if i == 0 else ""
        bw, bh = larg[i] + S * 0.36, S * 1.02
        ev.append((1, a, z, "Caixa", rf"{{\an5\pos({cent[i]:.0f},{CY:.0f})\bord0\shad0\1c{caixa}"
                   rf"\fscx80\fscy80\t(0,80,\fscx100\fscy100)\p1}}{caixa_arredondada(bw, bh, S * 0.2)}"))
        partes_txt = [(rf"{{\1c{tcaixa}\3a&HFF&\4a&HFF&}}{w}{{\1c&HFFFFFF&\3a&H00&\4a&H80&}}" if j == i else w)
                      for j, w in enumerate(tx)]
        ev.append((2, a, z, "Legenda", rf"{{\an5\pos({W / 2:.0f},{CY:.0f}){entrada}}}" + r"\h ".join(partes_txt)))
cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,{cfg['fonte']},{S},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{S * 0.09:.0f},{S * 0.05:.0f},5,60,60,0,1
Style: Caixa,{cfg['fonte']},{S},{caixa},{caixa},{caixa},{caixa},0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ASS = AQUI / "video-efeitos.ass"
ASS.write_text(cab + "".join(f"Dialogue: {l},{ts(i)},{ts(z)},{s},,0,0,0,,{x}\n" for l, i, z, s, x in sorted(ev, key=lambda e: (e[1], e[0]))), encoding="utf-8")
st = lambda s: f"{int(s // 3600):02d}:{int(s // 60 % 60):02d}:{int(s % 60):02d},{int(round(s % 1 * 1000)) % 1000:03d}"
(AQUI / "legenda.srt").write_text("".join(f"{i}\n{st(a)} --> {st(z)}\n{x}\n\n" for i, (a, z, x) in enumerate(srt, 1)), encoding="utf-8")

# ---------- 4) Cartões animados, marca-d'água, legenda e logo final ---------------------------
BAIXO, MEIO = H * 0.735, H * 0.34  # centro dos cartões sobre o Vitor / sobre cena de apoio
m = lambda ini, *ts: [round(x - ini, 3) for x in ts]  # momentos da fala relativos ao início do cartão
# (cartão, início, fim, centro y ou None = tela cheia, marcas)
CART = [
    ("titulo", 0.25, 3.30, BAIXO, []),
    ("pipa", G("2", 2.25), G("2", 4.42), MEIO, []),
    ("lista", G("2", 8.90), G("2", 12.68), BAIXO, m(8.90, 9.12, 9.40, 10.14, 11.12, 11.82)),
    ("segunda", G("2", 19.60), G("2", 23.45), BAIXO, []),
    ("rota", G("2", 26.20), G("2", 31.22), BAIXO, m(26.20, 26.48, 27.62, 29.84)),
    ("cestas", G("4", 6.05), G("4", 9.55), MEIO, []),
    ("final", T_FINAL + 0.10, TOTAL, None, []),
]
QUADROS = TMP / "quadros"
(TMP / "tempos.json").write_text(json.dumps({n: {"dur": round(z - a, 3), "marcas": mk} for n, a, z, _, mk in CART}))
subprocess.run(["node", str(AQUI / "cartoes.js"), str(TMP / "tempos.json"), str(QUADROS)], check=True)
from PIL import Image  # noqa: E402
ent = ["-i", TMP / "base.mp4", "-i", TMP / "audio.wav", "-i", AQUI / "cartoes/marca.png"]
f = f"[2:v]format=rgba,colorchannelmixer=aa=0.92[mk];[0:v][mk]overlay={W - 338 + 14}:54:enable='lt(t,{T_FINAL + 0.2:.3f})'[v0];"
ult, k = "v0", 3
for nome, a, z, cy, _ in CART:
    if nome == "final":  # legenda entra por baixo da logo final
        f += f"[{ult}]ass='{ASS}':fontsdir='{RAIZ / 'ferramentas/fontes/ttf'}'[vl];"; ult = "vl"
    w, h = Image.open(QUADROS / nome / "0000.png").size
    ent += ["-framerate", FPS, "-i", QUADROS / nome / "%04d.png"]
    x, y = ((W - w) // 2, round(cy - h / 2)) if cy else (0, 0)
    f += (f"[{k}:v]format=rgba,setpts=PTS+{a:.3f}/TB[c{k}];"
          f"[{ult}][c{k}]overlay={x}:{y}:eof_action=repeat:enable='between(t,{a:.3f},{z:.3f})'[v{k}];")
    ult = f"v{k}"; k += 1
f += f"[{ult}]format=yuv420p[v]"
run(*ent, "-filter_complex", f, "-map", "[v]", "-map", "1:a", "-t", f"{TOTAL:.3f}",
    "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-r", FPS, "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart", AQUI / "video.mp4")
print(f"Pronto: {AQUI / 'video.mp4'} ({TOTAL:.1f}s)")
