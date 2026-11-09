#!/usr/bin/env python3
"""Gera um arquivo .ass com efeitos estilo Reels nas cores do cliente.

  - Legenda animada: o texto do .srt aparece em blocos de poucas palavras, em
    maiúsculas, com a palavra "da vez" dentro de uma caixa na cor do cliente.
    O tempo de cada palavra é dividido pelo tamanho dela (não há leitura de áudio).
  - Textos de destaque: frases grandes em caixa colorida, com animação de entrada.
    Arquivo de texto, uma por linha:  0:03-0:06 OBRA ENTREGUE
    (aceita segundos, M:SS ou M:SS.d; linhas com # são ignoradas)

Uso: python3 ferramentas/efeitos.py -c <cliente> -f 9x16|16x9 [-l legenda.srt] [-d destaques.txt] -o saida.ass
As cores e a fonte vêm de clientes/<cliente>/video.json.
"""
import argparse, json, re, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import ImageFont

RAIZ = Path(__file__).resolve().parent.parent
FONTES = RAIZ / "ferramentas" / "fontes" / "ttf"


def cor_ass(hexa, alfa="00"):
    h = hexa.lstrip("#")
    return f"&H{alfa}{h[4:6]}{h[2:4]}{h[0:2]}".upper()


def seg(txt):
    """'1:02.5' / '62.5' / '00:01:02,500' -> segundos"""
    p = txt.strip().replace(",", ".").split(":")
    s = 0.0
    for x in p:
        s = s * 60 + float(x)
    return s


def ts(s):
    s = max(0.0, s)
    cs = int(round(s * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ler_srt(caminho):
    blocos = re.split(r"\n\s*\n", Path(caminho).read_text(encoding="utf-8-sig").replace("\r", ""))
    cues = []
    for b in blocos:
        linhas = [l for l in b.strip().split("\n") if l.strip()]
        for i, l in enumerate(linhas):
            if "-->" in l:
                a, z = l.split("-->")
                texto = " ".join(linhas[i + 1:])
                texto = re.sub(r"<[^>]+>|\{[^}]*\}", "", texto).strip()
                if texto:
                    cues.append((seg(a), seg(z.split()[0]), texto))
                break
    return cues


class Medidor:
    """Mede larguras de texto do mesmo jeito que o libass desenha (tamanho = altura da linha)."""

    def __init__(self, arquivo, tamanho):
        t = TTFont(arquivo)
        o = t["OS/2"]
        px = tamanho * t["head"].unitsPerEm / (o.usWinAscent + o.usWinDescent)
        self.f = ImageFont.truetype(str(arquivo), size=max(1, round(px * 4)))

    def __call__(self, txt):
        return self.f.getlength(txt) / 4


def caixa_arredondada(w, h, r):
    r = min(r, h / 2, w / 2)
    k = r * 0.45
    return (f"m {r:.0f} 0 l {w - r:.0f} 0 b {w - k:.0f} 0 {w:.0f} {k:.0f} {w:.0f} {r:.0f} "
            f"l {w:.0f} {h - r:.0f} b {w:.0f} {h - k:.0f} {w - k:.0f} {h:.0f} {w - r:.0f} {h:.0f} "
            f"l {r:.0f} {h:.0f} b {k:.0f} {h:.0f} 0 {h - k:.0f} 0 {h - r:.0f} "
            f"l 0 {r:.0f} b 0 {k:.0f} {k:.0f} 0 {r:.0f} 0")


def legenda_animada(cues, cfg, W, H, vertical, medir, S):
    caixa, tcaixa = cor_ass(cfg["caixa"]), cor_ass(cfg["texto_caixa"])
    maxw = W * (0.80 if vertical else 0.70)
    maxp = 3 if vertical else 5
    cy = H * (0.68 if vertical else 0.84)
    esp = medir(" ") * 2  # espaço duplo ("\h ") para respirar entre as palavras
    ev = []
    for ini, fim, texto in cues:
        palavras = texto.upper().split()
        # agrupa em blocos curtos que cabem numa linha
        blocos, atual = [], []
        for p in palavras:
            teste = atual + [p]
            if atual and (len(teste) > maxp or medir(" ".join(teste)) > maxw):
                blocos.append(atual)
                atual = [p]
            else:
                atual = teste
        if atual:
            blocos.append(atual)
        # tempo proporcional ao número de letras
        peso = lambda p: len(p) + 2
        total = sum(peso(p) for p in palavras)
        t = ini
        for bloco in blocos:
            larg = [medir(p) for p in bloco]
            linha = sum(larg) + esp * (len(bloco) - 1)
            x = W / 2 - linha / 2
            centros = []
            for lw in larg:
                centros.append(x + lw / 2)
                x += lw + esp
            for i, p in enumerate(bloco):
                d = (fim - ini) * peso(p) / total
                a, z = t, t + d
                t = z
                entrada = r"\fscx88\fscy88\t(0,90,\fscx100\fscy100)" if i == 0 else ""
                bw, bh = larg[i] + S * 0.36, S * 1.02
                ev.append((1, a, z, "Caixa",
                           rf"{{\an5\pos({centros[i]:.0f},{cy:.0f})\bord0\shad0\1c{caixa}"
                           rf"\fscx80\fscy80\t(0,80,\fscx100\fscy100)\p1}}{caixa_arredondada(bw, bh, S * 0.2)}"))
                partes = [(rf"{{\1c{tcaixa}\3a&HFF&\4a&HFF&}}{w}{{\1c&HFFFFFF&\3a&H00&\4a&H80&}}" if j == i else w)
                          for j, w in enumerate(bloco)]
                ev.append((2, a, z, "Legenda", rf"{{\an5\pos({W / 2:.0f},{cy:.0f}){entrada}}}" + r"\h ".join(partes)))
    return ev


def destaques(arquivo, W, H, vertical):
    ev = []
    for n, linha in enumerate(Path(arquivo).read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        m = re.match(r"^([\d:.,]+)\s*-\s*([\d:.,]+)\s+(.+)$", linha)
        if not m:
            sys.exit(f"destaques linha {n} fora do formato '0:03-0:06 TEXTO': {linha}")
        a, z, txt = seg(m[1]), seg(m[2]), m[3].strip().upper()
        y = H * (0.20 if vertical else 0.18)
        anim = r"\fscx55\fscy55\t(0,160,\fscx108\fscy108)\t(160,240,\fscx100\fscy100)\fad(0,180)"
        ev.append((3, a, z, "Destaque", rf"{{\an5\pos({W / 2:.0f},{y:.0f}){anim}}}{txt}"))
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", required=True)
    ap.add_argument("-f", default="9x16")
    ap.add_argument("-l")
    ap.add_argument("-d")
    ap.add_argument("-o", required=True)
    a = ap.parse_args()
    cfg = json.loads((RAIZ / "clientes" / a.c / "video.json").read_text(encoding="utf-8"))
    vertical = a.f == "9x16"
    W, H = (1080, 1920) if vertical else (1920, 1080)
    S = 82 if vertical else 66          # legenda
    SD = 104 if vertical else 88        # destaque
    medir = Medidor(FONTES / cfg["arquivo_fonte"], S)
    fonte = cfg["fonte"]
    caixa, tcaixa = cor_ass(cfg["caixa"]), cor_ass(cfg["texto_caixa"])
    ev = []
    if a.l:
        ev += legenda_animada(ler_srt(a.l), cfg, W, H, vertical, medir, S)
    if a.d:
        ev += destaques(a.d, W, H, vertical)
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Legenda,{fonte},{S},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,{S * 0.09:.0f},{S * 0.05:.0f},5,60,60,0,1
Style: Caixa,{fonte},{S},{caixa},{caixa},{caixa},{caixa},0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Destaque,{fonte},{SD},{tcaixa},{tcaixa},{caixa},&H60000000,0,0,0,0,100,100,0,0,3,{SD * 0.28:.0f},0,5,90,90,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev.sort(key=lambda e: (e[1], e[0]))
    corpo = "".join(f"Dialogue: {l},{ts(i)},{ts(f)},{s},,0,0,0,,{t}\n" for l, i, f, s, t in ev)
    Path(a.o).write_text(cab + corpo, encoding="utf-8")
    print(f"{a.o}: {len(ev)} eventos")


if __name__ == "__main__":
    main()
