#!/usr/bin/env python3
"""Gera um arquivo .ass com efeitos estilo Reels nas cores do cliente.

  - Legenda animada: o texto do .srt aparece em blocos de poucas palavras, em
    maiúsculas, com a palavra "da vez" dentro de uma caixa na cor do cliente.
    O tempo de cada palavra é dividido pelo tamanho dela (não há leitura de áudio).
  - Textos de destaque: frases grandes em caixa colorida, com animação de entrada.
    Arquivo de texto, uma por linha:  0:03-0:06 OBRA ENTREGUE
    (aceita segundos, M:SS ou M:SS.d; linhas com # são ignoradas)

Uso: python3 ferramentas/efeitos.py -c <cliente> -f 9x16|16x9 [-l legenda.srt] [-b] [-d destaques.txt] [-e lettering.txt] -o saida.ass
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


def legenda_animada(cues, cfg, W, H, vertical, medir, S, baixo=False):
    caixa, tcaixa = cor_ass(cfg["caixa"]), cor_ass(cfg["texto_caixa"])
    maxw = W * (0.80 if vertical else 0.70)
    maxp = 3 if vertical else 5
    cy = H * (0.68 if vertical else 0.84)
    if baixo:  # borda inferior, acima da barra de botões do Reels
        cy = H * (0.83 if vertical else 0.90)
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


def mistura(c1, c2, f):
    a = [int(c1.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)]
    b = [int(c2.lstrip("#")[k:k + 2], 16) for k in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * f):02X}" for x, y in zip(a, b))


def geometria(rosto, a, z, W, H, zooms):
    """Caixa da cabeça (união no intervalo a..z, já com zoom): (x0, topo, x1, queixo) ou None."""
    if not rosto or not rosto.get("rosto"):
        return None
    passo, caixas = rosto["passo"], rosto["rosto"]
    xs0, ys0, xs1, ys1 = [], [], [], []
    t = a - 0.3
    while t <= z + 0.3:
        k = int(round(t / passo))
        for c in caixas[max(0, k - 2):k + 3]:
            if c is None:
                continue
            x0, y0, x1, y1 = c
            w, h = x1 - x0, y1 - y0
            f = 1.0
            for T in zooms:
                f += 0.18 * min(max((t - T) / 0.15, 0), 1) * min(max((T + 0.95 - t) / 0.3, 0), 1)
            tx = lambda v: W / 2 + (v - W / 2) * f
            ty = lambda v: H / 2 + (v - H / 2) * f
            xs0.append(tx(x0 - 0.02 * w)); xs1.append(tx(x1 + 0.02 * w))
            ys0.append(ty(y0 - 0.45 * h)); ys1.append(ty(y1 + 0.08 * h))
        t += passo
    if not xs0:
        return None
    return min(xs0), min(ys0), max(xs1), min(ys1)


CAP, DESC = 0.496, 0.19      # proporções da Anton: altura das maiúsculas e descida (fs = altura da caixa)


def hexagono(w, h):
    k = w * 0.25
    return f"m {k:.0f} 0 l {w - k:.0f} 0 l {w:.0f} {h / 2:.0f} l {w - k:.0f} {h:.0f} l {k:.0f} {h:.0f} l 0 {h / 2:.0f}"


def montar_manchete(txt, med):
    """Monta a composição em unidades (palavra grande = 100). Devolve lista de peças:
    dict(tipo='texto'|'caixa'|'hex', ...). Formatos (separados por |):
      TOPO|*GRANDE*|BAIXO      pequena em cima à esquerda, grande, pequena embaixo à direita
      *+60*|MILHÕES|EM INVESTIMENTOS   "+" branco, número grande, palavra ao lado e linha embaixo
      SELO:O|TRABALHO|CHEGOU   selo em caixas (emblema, caixa clara, caixa escura)"""
    W = lambda t, fs: med(t) * fs / 100
    pecas = []
    def texto(t, fs, x, base, papel, ordem):
        pecas.append(dict(tipo="texto", t=t, fs=fs, x=x, base=base, papel=papel, ordem=ordem, w=W(t, fs)))
    if txt.startswith("SELO:"):
        emb, c1, c2 = (txt[5:].split("|") + ["", ""])[:3]
        fs1, fs2, pad = 100, 62, 14
        w1 = W(c1, fs1) + 2 * pad + 30
        h1 = CAP * fs1 + 2 * pad + 6
        eh = h1 * 0.78
        pecas.append(dict(tipo="caixa", x=eh * 0.55, y=-h1, w=w1, h=h1, papel="caixa1", ordem=0))
        texto(c1, fs1, eh * 0.55 + pad + 22, -pad - 3, "caixa1_txt", 0)
        pecas.append(dict(tipo="hex", x=0, y=-h1 * 0.5 - eh * 0.25, w=eh * 0.95, h=eh, papel="emblema", ordem=1))
        texto(emb, fs2 * 0.9, eh * 0.95 / 2 - W(emb, fs2 * 0.9) / 2, -h1 * 0.5 - eh * 0.25 + eh / 2 + CAP * fs2 * 0.9 / 2, "emblema_txt", 1)
        w2 = W(c2, fs2) + 2 * pad + 20
        h2 = CAP * fs2 + 2 * pad + 4
        x2 = eh * 0.55 + w1 - w2 + w1 * 0.08
        pecas.append(dict(tipo="caixa", x=x2, y=-6, w=w2, h=h2, papel="caixa2", ordem=2))
        texto(c2, fs2, x2 + pad + 10, -6 + h2 - pad - 2, "caixa2_txt", 2)
        return pecas
    campos = (txt.split("|") + ["", ""])[:3]
    if campos[0].startswith("*"):          # *+60*|MILHÕES|EM INVESTIMENTOS
        grande, topo, baixo = campos
    else:
        topo, grande, baixo = campos
    grande = grande.strip("*")
    if campos[0].startswith("*"):
        num = grande.lstrip("+")
        fp = 62
        xb = 0
        if grande.startswith("+"):
            texto("+", fp, 0, -CAP * 100 / 2 + CAP * fp / 2, "branco", 1)
            xb = W("+", fp) + 4
        texto(num, 100, xb, 0, "grande", 0)
        wb = W(num, 100)
        if topo:
            texto(topo, 50, xb + wb + 8, -CAP * 100 + CAP * 50, "branco", 1)
        if baixo:
            texto(baixo, 32, xb + wb * 0.25, 7 + CAP * 32, "branco", 2)
        return pecas
    texto(grande, 100, 0, 0, "grande", 0)
    wb = W(grande, 100)
    if topo:
        texto(topo, 42, 2, -CAP * 100 - 5, "branco", 1)
    if baixo:
        fb = 36
        texto(baixo, fb, wb - W(baixo, fb), 7 + CAP * fb, "branco", 2)
    return pecas


def caixa_pecas(pecas):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for p in pecas:
        if p["tipo"] == "texto":
            xs0.append(p["x"]); xs1.append(p["x"] + p["w"] + 0.14 * CAP * p["fs"])
            ys0.append(p["base"] - CAP * p["fs"] * 1.25); ys1.append(p["base"] + 2)
        else:
            xs0.append(p["x"]); xs1.append(p["x"] + p["w"]); ys0.append(p["y"]); ys1.append(p["y"] + p["h"])
    return min(xs0), min(ys0), max(xs1), max(ys1)


def lettering(arquivo, cfg, W, H, vertical, rosto=None, zooms=()):
    r"""Lettering fiel à referência "manchete de obra" (ver montar_manchete para os formatos).
    Bloco no canto superior esquerdo, levemente girado, peças entrando em sequência com
    borrão de movimento e saindo em varredura. Nunca cobre rosto nem corpo (rosto.json)."""
    med = Medidor(FONTES / cfg.get("arquivo_lettering", "anton-latin-400-normal.ttf"), 100)
    claro = mistura(cfg.get("lettering_destaque", cfg["caixa"]), "#FFFFFF", 0.30)
    vivo = cfg.get("lettering_destaque", cfg["caixa"])
    escuro_hex = cfg.get("lettering_borda", cfg["caixa"])
    escuro = cor_ass(escuro_hex)
    M = W * 0.05
    ytop = H * 0.03
    ROT = 4                                  # graus, sobe para a direita
    ev = []
    for n, linha in enumerate(Path(arquivo).read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        m = re.match(r"^([\d:.,]+)\s*-\s*([\d:.,]+)\s+(.+)$", linha)
        if not m:
            sys.exit(f"lettering linha {n} fora do formato '0:03-0:06 TEXTO': {linha}")
        a, z = seg(m[1]), seg(m[2])
        pecas = montar_manchete(m[3].strip().upper().replace("SELO:", "SELO:"), med)
        bx0, by0, bx1, by1 = caixa_pecas(pecas)
        bw, bh = bx1 - bx0, by1 - by0
        cab = geometria(rosto, a, z, W, H, zooms) or (W * 0.3, H * 0.3, W * 0.7, H * 0.55)
        hx0, htop, hx1, queixo = cab
        hw = hx1 - hx0
        proibido = [(hx0 - M * 0.6, htop - M * 0.6, hx1 + M * 0.6, queixo + M * 0.3),
                    (hx0 - hw * 0.75, queixo, hx1 + hw * 0.75, H),
                    (W * 0.70, 0, W, H * 0.085)]        # logo do canto (video.sh -m)
        folga_rot = 0.07                     # crescimento da caixa pelo giro
        def cabe(sx, X, Y):
            x0, y0 = X, Y
            x1, y1 = X + bw * sx * (1 + folga_rot), Y + bh * sx * (1 + folga_rot) + bw * sx * 0.07
            if x1 > W - M or y1 > H * 0.62:
                return False
            return all(x1 < r0 or x0 > r1 or y1 < s0 or y0 > s1 for r0, s0, r1, s1 in proibido)
        melhor = None
        for k in range(30):
            Y = ytop + k * H * 0.015
            lo, hi, ok = 0.3, 4.0, None
            for _ in range(18):
                mid = (lo + hi) / 2
                if cabe(mid, M, Y):
                    ok, lo = mid, mid
                else:
                    hi = mid
            if ok and (melhor is None or ok > melhor[0] * 1.04):
                melhor = (ok, Y)
        if not melhor:
            sys.exit(f"lettering linha {n}: sem espaço livre fora da pessoa: {linha}")
        sx, Y = melhor
        sx = min(sx, 4.2 if vertical else 3.0)
        X0 = M - bx0 * sx
        Y0 = Y - by0 * sx + bw * sx * 0.07          # compensa o giro (lado esquerdo desce)
        org = rf"\org({M:.0f},{Y0:.0f})\frz{ROT}"
        dur = (z - a) * 1000
        SAI = 180
        # sombra suave atrás do bloco
        pad = 40 * sx
        ev.append((0, a, z, "Caixa", rf"{{\an7\pos({M - pad:.0f},{Y - pad * 0.6:.0f}){org}\bord0\shad0\1c&H000000&\1a&H90&\blur{35 * sx:.0f}\fad(200,150)\p1}}"
                                     + caixa_arredondada(bw * sx + 2 * pad, bh * sx + 2 * pad, pad)))
        for p in sorted(pecas, key=lambda q: q["ordem"]):
            atraso = p["ordem"] * 110
            entra = (rf"\alpha&HFF&\t({atraso},{atraso + 1},\alpha&H00&)" if atraso else "")
            def mov(x, y):
                d = 160 * sx
                return (rf"\move({x - d:.0f},{y:.0f},{x:.0f},{y:.0f},{atraso},{atraso + 200})"
                        rf"\blur12\t({atraso},{atraso + 200},\blur0)\fscx135\t({atraso},{atraso + 200},\fscx100)"
                        rf"\t({dur - SAI:.0f},{dur:.0f},\blur16\fscx150\alpha&HFF&)")
            if p["tipo"] in ("caixa", "hex"):
                x, y = X0 + p["x"] * sx, Y0 + p["y"] * sx
                w, h = p["w"] * sx, p["h"] * sx
                forma = hexagono(w, h) if p["tipo"] == "hex" else caixa_arredondada(w, h, 10 * sx)
                if p["papel"] == "caixa1":
                    cor, borda = "&HFFFFFF&", escuro
                elif p["papel"] == "caixa2":
                    cor, borda = escuro, "&HFFFFFF&"
                else:
                    cor, borda = cor_ass(vivo), "&HFFFFFF&"
                ev.append((3, a, z, "Caixa", rf"{{\an7{mov(x, y)}{org}{entra}\fax-0.10\1c{cor}\3c{borda}\bord{5 * sx:.0f}\shad{6 * sx:.0f}\4c&H000000&\4a&H70&\p1}}{forma}"))
                continue
            fs = p["fs"] * sx
            pe = Y0 + (p["base"] + DESC * p["fs"]) * sx
            x = X0 + p["x"] * sx
            base_txt = rf"\an1{mov(x, pe)}{org}{entra}\fax-0.14\fs{fs:.0f}"
            if p["papel"] == "grande":
                topo_l = Y0 + (p["base"] - CAP * p["fs"] * 1.3) * sx
                fim_l = Y0 + p["base"] * sx
                nb = 6
                for b in range(nb):
                    ya = 0 if b == 0 else topo_l + (fim_l - topo_l) * b / nb
                    yb = H if b == nb - 1 else topo_l + (fim_l - topo_l) * (b + 1) / nb
                    cor = cor_ass(mistura(claro, vivo, b / (nb - 1)))
                    ev.append((5, a, z, "Lettering", rf"{{{base_txt}\clip(0,{ya:.0f},{W},{yb:.0f})\1c{cor}\bord0\shad{fs * 0.035:.0f}\4c{escuro}\4a&H40&}}{p['t']}"))
            elif p["papel"] == "caixa1_txt":
                ev.append((4, a, z, "Lettering", rf"{{{base_txt}\1c{escuro}\bord0\shad0}}{p['t']}"))
            elif p["papel"] == "emblema_txt":
                ev.append((4, a, z, "Lettering", rf"{{{base_txt}\1c&HFFFFFF&\bord{fs * 0.04:.0f}\3c{escuro}\shad0}}{p['t']}"))
            else:   # branco
                ev.append((4, a, z, "Lettering", rf"{{{base_txt}\1c&HFFFFFF&\bord{fs * 0.025:.0f}\3c{escuro}\3a&H60&\shad{fs * 0.05:.0f}\4c&H000000&\4a&H50&}}{p['t']}"))
    return ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", required=True)
    ap.add_argument("-f", default="9x16")
    ap.add_argument("-l")
    ap.add_argument("-d")
    ap.add_argument("-e", help="arquivo de lettering (palavra-chave entre *asteriscos*)")
    ap.add_argument("--rosto", help="rosto.json de ferramentas/rosto.py (lettering não cobre a pessoa)")
    ap.add_argument("--zoom", default="", help="instantes do zoom de impacto, ex.: 2.5,8")
    ap.add_argument("-b", action="store_true", help="legenda na borda inferior")
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
        ev += legenda_animada(ler_srt(a.l), cfg, W, H, vertical, medir, S, a.b)
    if a.d:
        ev += destaques(a.d, W, H, vertical)
    if a.e:
        ev += lettering(a.e, cfg, W, H, vertical,
                       json.loads(Path(a.rosto).read_text()) if a.rosto else None,
                       [float(t) for t in a.zoom.split(",") if t])
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
Style: Lettering,{cfg.get('fonte_lettering', 'Anton')},100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H70000000,0,0,0,0,100,100,0,0,1,4,5,5,40,40,0,1
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
