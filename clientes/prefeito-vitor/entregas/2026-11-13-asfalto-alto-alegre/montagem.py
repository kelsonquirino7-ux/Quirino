#!/usr/bin/env python3
"""Montagem do Reels "Asfalto Rumo–Alto Alegre" (Vitor Prefeito do Povo).

Fonte editável da edição: cortes, legendas pequenas, lettering, efeitos e mixagem.
Uso:  python3 montagem.py <pasta-dos-brutos-do-Drive> [saida.mp4]
  - brutos: os IMG_53xx.MOV da pasta "PAV ASFALTICA ALTO ALEGRE" (não ficam no repositório, são 580 MB)
  - midia/: clipes gerados por IA (escavadeira, asfalto-tapete), imagem do asfalto e trilha
Cores e fonte: brief do cliente (verde #0AA514, verde escuro #015927, branco; Montserrat).
"""
import math, random, subprocess, sys, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[3]
BRUTOS = Path(sys.argv[1])
SAIDA = Path(sys.argv[2]) if len(sys.argv) > 2 else AQUI / "video.mp4"
MIDIA = AQUI / "midia"
TMP = AQUI / "_tmp"; TMP.mkdir(exist_ok=True)
FONTES = RAIZ / "ferramentas" / "fontes" / "ttf"
F900 = str(FONTES / "montserrat-latin-900-normal.ttf")
F600 = str(FONTES / "montserrat-latin-600-normal.ttf")
FSERIF = str(FONTES / "playfair-display-latin-800-italic.ttf")
FB9 = str(FONTES / "barlow-condensed-latin-900-italic.ttf")
FB7 = str(FONTES / "barlow-condensed-latin-700-italic.ttf")
LOGO = RAIZ / "clientes/prefeito-vitor/identidade/logo-vitor-prefeito-do-povo.png"

W, H, FPS = 1080, 1920, 30
VERDE, ESCURO, BRANCO = (10, 165, 20), (1, 89, 39), (255, 255, 255)
VERDE_TXT = VERDE   # verde do brief; legível sobre a sombra escura e o degradê de base

def mov(n): return str(BRUTOS / f"IMG_{n}.MOV")

# ───────────── linha do tempo ─────────────
T_ESTALO = 19.04          # instante do estalo de dedos
T_ASF = 19.10             # entra a estrada asfaltada
T_VOZ5 = 21.20            # "Estrada sinalizada e asfaltada do Rumo até aqui"
T_S7 = 25.60              # fala final
T_VIN = 32.15             # vinheta
T_FIM = 35.15

# (início, fim, arquivo, ponto de entrada na fonte, velocidade, transição de entrada, zoom lento)
PLANOS = [
    (0.00, 2.10, mov(5340), 0.75, 1, "", 0.03),
    (2.10, 4.10, mov(5331), 0.30, 1, "whip", 0.10),
    (4.10, 5.30, mov(5340), 4.85, 1, "soco", 0.03),
    (5.30, 6.40, mov(5336), 1.45, 1.0, "soco", 0.05),
    (6.40, 7.75, str(MIDIA / "lama.mp4"), 0.60, 1, "whip", 0.06),
    (7.75, 8.60, mov(5329), 0.30, 1, "whip", 0.08),
    (8.60, 9.85, str(MIDIA / "escavadeira-cavando.mp4"), 1.70, 1.15, "soco", 0.06),
    (9.85, 11.05, mov(5343), 4.55, 1, "glitch", 0.03),
    (11.05, 12.60, mov(5347), 0.00, 1, "soco", 0.03),
    (12.60, 13.75, mov(5326), 1.00, 1, "whip", 0.08),
    (13.75, 15.40, str(MIDIA / "escavadeira-despejando.mp4"), 1.10, 1.15, "whip", 0.06),
    (15.40, 16.75, str(MIDIA / "escavadeira-cavando.mp4"), 3.10, 1.15, "soco", 0.08),
    (16.75, 18.70, mov(5349), 0.00, 1, "glitch", 0.04),
    (18.70, T_ASF, mov(5350), 3.20, 1, "soco", 0.25),
    (T_ASF, 24.10, str(MIDIA / "asfalto-tapete.mp4"), 0.00, 1, "", 0.0),
    (24.10, T_S7, "IMG:" + str(MIDIA / "estrada-asfaltada.png"), 0, 1, "", 0.06),
    (T_S7, T_VIN, mov(5354), 0.45, 1, "whip", 0.03),
]

# legendas pequenas (fala do Vitor)
LEGENDAS = [
    (0.19, 1.28, "Gente, olha onde eu tô:"),
    (1.34, 2.08, "no Alto Alegre."),
    (2.18, 3.07, "Essa estrada aqui é a estrada"),
    (3.07, 4.05, "que liga o Rumo ao Alto Alegre."),
    (4.12, 5.26, "Todo mundo sabe como era:"),
    (5.30, 7.05, "poeira no verão e lama no inverno,"),
    (7.05, 8.40, "onde as pessoas precisavam passar."),
    (8.78, 9.80, "Agora a máquina está na estrada"),
    (9.80, 10.98, "e o asfalto está chegando."),
    (11.05, 12.58, "São nove quilômetros de asfalto"),
    (12.58, 13.73, "que liga o Rumo ao Alto Alegre."),
    (13.75, 15.45, "Estamos na fase de terraplanagem."),
    (16.75, 17.95, "E quer ver como vai ficar?"),
    (18.05, 18.68, "Olha aí!"),
    (T_VOZ5, T_VOZ5 + 1.78, "Estrada sinalizada e asfaltada"),
    (T_VOZ5 + 1.78, T_VOZ5 + 2.75, "do Rumo até aqui."),
    (25.80, 26.86, "Compromisso é isso:"),
    (27.05, 27.78, "sair do papel"),
    (27.78, 29.88, "e chegar na estrada que você usa todo dia."),
    (30.10, 31.30, "E eu volto aqui pra mostrar."),
]

# lettering das palavras-chave: (início, fim, [linhas], centro-y, tamanho)
# lettering no estilo de inspiracoes/texto-na-tela: apoio pequeno branco + palavra-chave grande
# em serifa itálica na cor do cliente, na altura do peito, sem caixa, com sombra leve.
# (início, fim, apoio acima, destaque, apoio abaixo, centro-y)
# Lettering de obra (inspirado no vídeo de referência enviado pelo dono): condensada itálica pesada,
# caixa alta, palavra-chave grande na cor do cliente, selo inclinado com fita, rótulo com pontilhado
# e texto vazado. Cores só do brief (verde, verde escuro, branco).
#   ("pilha",   início, fim, pequeno acima, GRANDE, pequeno abaixo)
#   ("selo",    início, fim, placa, fita)
#   ("rotulo",  início, fim, texto)
#   ("vazado",  início, fim, texto)
LETTERING = [
    ("pilha", 1.36, 2.08, "OLHA ONDE EU TÔ:", "ALTO ALEGRE", ""),
    ("selo", 2.22, 4.05, "A ESTRADA", "RUMO • ALTO ALEGRE", 1.75, H / 2),
    ("pilha", 5.40, 6.36, "NO VERÃO,", "POEIRA", ""),
    ("pilha", 6.50, 7.70, "NO INVERNO,", "LAMA", ""),
    ("rotulo", 8.72, 9.82, "MÁQUINA NA ESTRADA"),
    ("selo", 9.95, 11.02, "O ASFALTO", "ESTÁ CHEGANDO"),
    ("rotulo", 13.90, 16.65, "TERRAPLANAGEM"),
    ("pilha", 17.25, 18.66, "QUER VER COMO", "VAI FICAR?", ""),
    ("pilha", T_VOZ5 + 0.45, T_S7 - 0.12, "ESTRADA", "SINALIZADA", "E ASFALTADA"),
    ("vazado", 26.05, 27.00, "COMPROMISSO"),
    ("pilha", 27.20, 27.85, "SAIR DO", "PAPEL", ""),
    ("pilha", 28.45, 29.95, "CHEGAR NA", "ESTRADA", ""),
    ("selo", 30.35, 31.95, "EU VOLTO", "PRA MOSTRAR"),
]
CONTADOR = (11.42, 12.58)   # 9 KM
SELOS = [(T_ASF + 0.25, T_S7, "PROJEÇÃO · IMAGEM ILUSTRATIVA"), (6.40, 7.75, "IMAGEM ILUSTRATIVA")]
CORTES = [(p[0], p[5]) for p in PLANOS if p[5]]

# ───────────── leitura dos planos ─────────────
class Plano:
    def __init__(s, t0, t1, src, entrada, vel, trans, zoom):
        s.t0, s.t1, s.trans, s.zoom = t0, t1, trans, zoom
        s.n = round((t1 - t0) * FPS) + 8
        s.i = 0; s.ult = None; s.img = None; s.p = None; s.tapete = None
        if src == "TAPETE":
            s.tapete = Tapete()
        elif src.startswith("IMG:"):
            s.img = np.asarray(Image.open(src[4:]).convert("RGB").resize((W, H), Image.LANCZOS))
        else:
            vf = f"setpts=PTS/{vel},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
            s.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{entrada}", "-i", src, "-vf", vf,
                                    "-frames:v", str(s.n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                   stdout=subprocess.PIPE)

    def quadro(s):
        if s.tapete is not None:
            s.i += 1; return s.tapete.quadro((s.i - 1) / FPS)
        if s.img is not None:
            return s.img
        b = s.p.stdout.read(W * H * 3)
        if len(b) == W * H * 3:
            s.ult = np.frombuffer(b, np.uint8).reshape(H, W, 3)
        return s.ult

    def fechar(s):
        if s.p: s.p.kill(); s.p.wait()

class Tapete:
    """Asfalto desenrolando como tapete (feito aqui, sem IA): um rolo escuro corre pela estrada de
    terra real, do primeiro plano até o horizonte, e deixa a estrada pronta (midia/estrada-asfaltada.png)."""
    YH = 1128                      # fim visível da pista (horizonte da estrada)
    def __init__(s):
        s.terra = np.asarray(Image.open(MIDIA / "estrada-terra-original.jpg").convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32)
        s.pronta = np.asarray(Image.open(MIDIA / "estrada-asfaltada.png").convert("RGB").resize((W, H), Image.LANCZOS)).astype(np.float32)
        rng = np.random.default_rng(5)
        s.poeira = [(rng.uniform(-1, 1), rng.uniform(0.6, 1.4), rng.uniform(0, 6.3)) for _ in range(26)]
    def frente(s, t):              # posição y da frente do rolo
        p = ease_out(min(1, max(0, (t - 0.15) / 2.6)) ) if t > 0.15 else 0
        return s.YH + (H + 260 - s.YH) * (1 - p) ** 2.2, p
    def xr(s, y):
        return float(np.interp(y, [s.YH, s.YH + 30, 1575, 1920], [W, 700, 900, 1060]))
    def quadro(s, t):
        y, p = s.frente(t)
        esc = max(0.0, (y - s.YH) / (H - s.YH))           # escala de perspectiva
        th = 14 + 300 * esc                               # espessura do rolo
        yi = int(min(H, max(0, y)))
        out = s.terra.copy()
        # tudo abaixo da base do rolo já é estrada pronta (com transição curta)
        borda = int(6 + 30 * esc)
        if yi < H:
            out[yi:] = s.pronta[yi:]
            y0 = max(0, yi - borda)
            if yi > y0:
                k = np.linspace(0, 1, yi - y0)[:, None, None]
                out[y0:yi] = s.terra[y0:yi] * (1 - k) + s.pronta[y0:yi] * k
        # no fim, o resto da paisagem (acostamento, talude) assenta na versão pronta
        f = min(1, max(0, (t - 2.7) / 0.6))
        if f > 0: out = out * (1 - f) + s.pronta * f
        im = Image.fromarray(out.clip(0, 255).astype(np.uint8))
        if p < 1 and yi > s.YH - 5:
            d = ImageDraw.Draw(im, "RGBA")
            x0, x1 = -40, s.xr(y) + 30 * esc
            top = y - th
            # sombra
            d.rectangle((x0, y - th * 0.15, x1, y + th * 0.12), fill=(0, 0, 0, 90))
            # corpo do rolo: faixas com sombreamento de cilindro
            n = max(6, int(th / 3))
            for i in range(n):
                a = i / n; yy = top + a * th
                c = 18 + 70 * max(0, 1 - abs(a - 0.28) / 0.28) ** 1.5 + 12 * a
                d.rectangle((x0, yy, x1, yy + th / n + 1), fill=(int(c), int(c), int(c + 3), 255))
            # tampa do rolo (espiral) na ponta direita
            r = th / 2; cx, cy = x1, top + r
            d.ellipse((cx - r * 0.42, cy - r, cx + r * 0.42, cy + r), fill=(28, 28, 30, 255), outline=(70, 70, 72, 255), width=max(1, int(r * 0.05)))
            for k in (0.7, 0.45, 0.22):
                d.ellipse((cx - r * 0.42 * k, cy - r * k, cx + r * 0.42 * k, cy + r * k), outline=(55, 55, 58, 255), width=max(1, int(r * 0.03)))
            # poeira leve levantada nas pontas e atrás do rolo
            for u, v, ph in s.poeira:
                px = (x1 if u > 0 else 40 + 200 * esc) + u * 60 * esc
                py = y - th * 0.1 - abs(math.sin(ph + t * 3)) * th * 0.6 * v
                rr = (18 + 60 * esc) * v
                d.ellipse((px - rr, py - rr * 0.6, px + rr, py + rr * 0.6), fill=(205, 180, 150, int(28 * min(1, 2 * (1 - p)))))
        return np.asarray(im)

# ───────────── efeitos de imagem ─────────────
def ease_out(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
def elastico(x):
    x = min(1, max(0, x))
    return 1 + 2.2 * (x - 1) ** 3 + 1.2 * (x - 1) ** 2   # passa de 1 e assenta

def zoom(im, z, dx=0, dy=0):
    if abs(z - 1) < 1e-3 and not dx and not dy: return im
    w, h = W / z, H / z
    x0 = (W - w) / 2 + dx; y0 = (H - h) / 2 + dy
    x0 = min(max(0, x0), W - w); y0 = min(max(0, y0), H - h)
    return im.transform((W, H), Image.EXTENT, (x0, y0, x0 + w, y0 + h), Image.BILINEAR)

def borrao_h(im, f):
    if f <= 0: return im
    k = max(2, int(W / (1 + f * 40)))
    return im.resize((k, H), Image.BOX).resize((W, H), Image.BILINEAR)

def desloca(im, dx):
    a = np.asarray(im); return Image.fromarray(np.roll(a, int(dx), axis=1))

def rgb_split(im, d):
    a = np.asarray(im).copy(); d = int(d)
    if d: a[..., 0] = np.roll(a[..., 0], d, axis=1); a[..., 2] = np.roll(a[..., 2], -d, axis=1)
    return Image.fromarray(a)

def clarao(im, a, cor=(255, 255, 255)):
    return im if a <= 0 else Image.blend(im, Image.new("RGB", (W, H), cor), min(1, a))

# ───────────── textos ─────────────
def fonte(arq, tam): return ImageFont.truetype(arq, tam)

def caixa_texto(txt, tam, fundo, cor, pad=(34, 14), raio=18):
    f = fonte(F900, tam)
    x0, y0, x1, y1 = f.getbbox(txt)
    w, h = x1 - x0 + 2 * pad[0], tam + 2 * pad[1]
    im = Image.new("RGBA", (w + 24, h + 24), (0, 0, 0, 0))
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((12, 20, 12 + w, 20 + h), raio, fill=(0, 0, 0, 120))
    im = Image.alpha_composite(im, sombra.filter(ImageFilter.GaussianBlur(8)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 8, 12 + w, 8 + h), raio, fill=fundo + (255,))
    d.text((12 + w / 2, 8 + h / 2 + tam * 0.02), txt, font=f, fill=cor + (255,), anchor="mm")
    return im

def _texto_sombra(txt, f, cor):
    w = int(f.getlength(txt)) + 60; asc, desc = f.getmetrics(); h = asc + desc + 50
    som = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(som).text((w / 2, 25 + asc), txt, font=f, fill=(0, 0, 0, 255), anchor="ms",
                             stroke_width=max(3, f.size // 14), stroke_fill=(0, 0, 0, 255))
    im = Image.alpha_composite(som.filter(ImageFilter.GaussianBlur(max(6, f.size // 9))), som.filter(ImageFilter.GaussianBlur(3)))
    im.putalpha(im.getchannel("A").point(lambda v: int(v * 0.85)))
    ImageDraw.Draw(im).text((w / 2, 25 + asc), txt, font=f, fill=cor + (255,), anchor="ms")
    return im

def _sombra(im, raio=10, alfa=150, dx=6, dy=8):
    """Sombra suave atrás de um RGBA (para ler sobre qualquer fundo)."""
    a = im.getchannel("A").point(lambda v: v * alfa // 255)
    sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
    sh.paste(Image.new("RGBA", im.size, (0, 0, 0, 255)), (30 + dx, 30 + dy), a)
    sh = sh.filter(ImageFilter.GaussianBlur(raio)); sh.alpha_composite(im, (30, 30))
    return sh

def _txt(txt, f, cor, contorno=0, cor_cont=None):
    asc, desc = f.getmetrics(); w = int(f.getlength(txt)) + 30 + 2 * contorno
    im = Image.new("RGBA", (w, asc + desc + 2 * contorno + 10), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((15 + contorno, 5 + contorno), txt, font=f, fill=cor, stroke_width=contorno,
                            stroke_fill=cor_cont if cor_cont else cor)
    return im.crop(im.getbbox())

def _pilha(peq, grande, peq2):
    fg = fonte(FB9, 150)
    while fg.getlength(grande) > 880: fg = fonte(FB9, fg.size - 8)
    fp = fonte(FB7, 50)
    return dict(tipo="pilha", p=_sombra(_txt(peq, fp, BRANCO + (255,))) if peq else None,
                g=_sombra(_txt(grande, fg, VERDE + (255,), 4, ESCURO + (255,)), 12, 170),
                p2=_sombra(_txt(peq2, fp, BRANCO + (255,))) if peq2 else None)

def _selo(placa, fita, esc=1.0, cy=None):
    fpl = fonte(FB9, int(108 * esc)); ff = fonte(FB9, int(60 * esc))
    t = _txt(placa, fpl, ESCURO + (255,)); w, h = t.width + 64, t.height + 46
    pl = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(pl)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=ESCURO + (255,))
    d.rounded_rectangle((12, 12, w - 13, h - 13), 18, fill=BRANCO + (255,))
    pl.alpha_composite(t, ((w - t.width) // 2, (h - t.height) // 2))
    tf = _txt(fita, ff, BRANCO + (255,)); fw, fh = tf.width + 60, tf.height + 30
    fi = Image.new("RGBA", (fw, fh), (0, 0, 0, 0)); d = ImageDraw.Draw(fi)
    d.polygon([(22, 0), (fw, 0), (fw - 22, fh), (0, fh)], fill=VERDE + (255,))
    d.polygon([(fw - 30, fh), (fw - 22, fh), (fw - 4, fh + 0), (fw - 30, fh)], fill=ESCURO + (255,))
    fi.alpha_composite(tf, ((fw - tf.width) // 2, (fh - tf.height) // 2))
    return dict(tipo="selo", pl=_sombra(pl, 14, 160), fi=_sombra(fi, 12, 150), cy=cy, esc=esc)

def _rotulo(txt):
    f = fonte(FB9, 84)
    return dict(tipo="rotulo", t=_sombra(_txt(txt, f, BRANCO + (255,), 3, ESCURO + (255,)), 10, 160))

def _vazado(txt):
    f = fonte(FB9, 150)
    while f.getlength(txt) > 900: f = fonte(FB9, f.size - 8)
    return dict(tipo="vazado", o=_txt(txt, f, (0, 0, 0, 0), 6, BRANCO + (255,)),
                c=_sombra(_txt(txt, f, VERDE + (255,), 6, ESCURO + (255,)), 12, 170))

def bloco_lettering(item):
    tipo, a, b, *arg = item
    return a, b, {"pilha": _pilha, "selo": _selo, "rotulo": _rotulo, "vazado": _vazado}[tipo](*arg)

def _borrao(im, k):
    """Borrão de movimento horizontal (entrada em chicote)."""
    if k < 0.05: return im
    n = max(2, int(im.width / (1 + 40 * k)))
    return im.resize((n, im.height), Image.BOX).resize(im.size, Image.BILINEAR)

def _corta_x(im, frac):
    frac = min(1, max(0, frac)); w = max(1, int(im.width * frac))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.paste(im.crop((0, 0, w, im.height)), (0, 0)); return out

TOPO = 190   # linha de base do lettering: faixa de cima da tela, acima do rosto

def desenha_lettering(base, L, k, fora):
    X0 = 60
    if L["tipo"] == "pilha":
        y = TOPO
        if L["p"] is not None:
            e = ease_out(k / 0.22)
            cola(base, _corta_x(L["p"], e), X0 + L["p"].width / 2, y - L["p"].height / 2 + 20, alfa=fora)
        kg = k - 0.08; e = ease_out(kg / 0.3)
        if kg > 0:
            g = _borrao(L["g"], 1 - e)
            dx = -380 * (1 - e) + 18 * math.sin(min(1, kg / 0.45) * math.pi) * (1 - min(1, kg / 0.45))
            cola(base, g, X0 + g.width / 2 + dx, y + g.height / 2 - 25, escala=1 + 0.06 * (1 - elastico(kg / 0.4)), alfa=min(1, kg / 0.08) * fora)
        if L["p2"] is not None and k > 0.3:
            e2 = ease_out((k - 0.3) / 0.22)
            cola(base, L["p2"], X0 + 30 + L["p2"].width / 2 + 60 * (1 - e2), y + L["g"].height - 30 + L["p2"].height / 2, alfa=e2 * fora)
    elif L["tipo"] == "selo":
        cx, cy = W / 2, (L["cy"] or TOPO + 40)
        e = elastico(k / 0.32); ang = -4 - 10 * (1 - min(1, k / 0.3))
        pl = L["pl"].rotate(ang, Image.BICUBIC, expand=True)
        cola(base, pl, cx - (20 if L["esc"] == 1 else 0), cy, escala=max(0.05, e), alfa=min(1, k / 0.06) * fora)
        if k > 0.18:
            fi = _corta_x(L["fi"], ease_out((k - 0.18) / 0.25)).rotate(-4, Image.BICUBIC, expand=True)
            cola(base, fi, cx + (60 if L["esc"] == 1 else 0), cy + pl.height * 0.42, alfa=fora)
    elif L["tipo"] == "rotulo":
        y = TOPO + 40; e = ease_out(k / 0.25); t = L["t"]
        cola(base, _borrao(t, 1 - e), X0 + t.width / 2 - 300 * (1 - e), y, alfa=min(1, k / 0.06) * fora)
        d = ImageDraw.Draw(base); n = int(min(1, max(0, (k - 0.2) / 0.5)) * 14)
        for i in range(n):
            x = X0 + t.width - 10 + i * 22; r = 5
            d.ellipse((x - r, y + 22 - r, x + r, y + 22 + r), fill=VERDE)
    elif L["tipo"] == "vazado":
        cx, cy = W / 2, TOPO + 60; e = ease_out(k / 0.35)
        cola(base, L["o"], cx, cy, escala=1.25 - 0.25 * e, alfa=min(1, k / 0.1) * fora)
        if k > 0.3:
            cola(base, _corta_x(L["c"], ease_out((k - 0.3) / 0.35)), cx, cy, alfa=fora)

def cola(base, rgba, cx, cy, escala=1.0, alfa=1.0):
    if alfa <= 0.01: return
    if abs(escala - 1) > 1e-3:
        rgba = rgba.resize((max(1, int(rgba.width * escala)), max(1, int(rgba.height * escala))), Image.BILINEAR)
    if alfa < 1:
        rgba = rgba.copy(); rgba.putalpha(rgba.getchannel("A").point(lambda v: int(v * alfa)))
    base.paste(rgba, (int(cx - rgba.width / 2), int(cy - rgba.height / 2)), rgba)

def legenda_img(txt):
    f = fonte(F600, 42); linhas = [txt]
    if f.getlength(txt) > 880:
        p = txt.split(); m = len(p) // 2
        cand = min(range(1, len(p)), key=lambda k: abs(f.getlength(" ".join(p[:k])) - f.getlength(" ".join(p[k:]))))
        linhas = [" ".join(p[:cand]), " ".join(p[cand:])]
    im = Image.new("RGBA", (W, 60 * len(linhas) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(linhas):
        d.text((W / 2, 38 + 58 * i), l, font=f, fill=BRANCO + (255,), anchor="mm",
               stroke_width=5, stroke_fill=(0, 0, 0, 255))
    return im

LET = [bloco_lettering(i) for i in LETTERING]
LEG = [(a, b, legenda_img(t)) for a, b, t in LEGENDAS]
KM_SUB = _sombra(_txt("DE ASFALTO", fonte(FB7, 54), BRANCO + (255,)))
KM_NUM = {n: _sombra(_txt(f"+{n}KM", fonte(FB9, 180), VERDE + (255,), 4, ESCURO + (255,)), 12, 170) for n in range(1, 10)}
# degradê escuro suave na base (como nas referências) para o texto ler sobre qualquer imagem
_y = np.arange(H)
_g = np.clip((_y - H * 0.62) / (H * 0.38), 0, 1) ** 1.3 * 140 + np.clip(1 - _y / (H * 0.30), 0, 1) ** 1.6 * 120
BASE_ESCURA = Image.fromarray(np.dstack([np.zeros((H, W, 3), np.uint8),
                                         np.broadcast_to(_g[:, None], (H, W)).astype(np.uint8)]), "RGBA")
def selo_img(t):
    f = fonte(F600, 26)
    w = int(f.getlength(t)) + 36
    im = Image.new("RGBA", (w, 50), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, 49), 10, fill=(0, 0, 0, 170))
    d.text((w / 2, 25), t, font=f, fill=BRANCO + (255,), anchor="mm")
    return im
SELO_IMGS = [(a, b, selo_img(t)) for a, b, t in SELOS]

# confete (fundo animado de vitória)
random.seed(7)
CONF = [dict(x=random.uniform(0, W), v=random.uniform(500, 1100), d=random.uniform(0, 1.2),
             s=random.uniform(14, 30), f=random.uniform(2, 7), ph=random.uniform(0, 6.3),
             c=random.choice([VERDE, ESCURO, BRANCO, VERDE])) for _ in range(150)]
def confete(d, t, cores=None):
    for c in CONF:
        tt = t - c["d"]
        if tt < 0: continue
        y = -40 + c["v"] * tt + 120 * tt * tt
        if y > H + 40: continue
        x = c["x"] + 60 * math.sin(c["ph"] + tt * 2.5)
        a = c["ph"] + tt * c["f"]; s = c["s"]; hh = s * (0.35 + 0.65 * abs(math.cos(a * 1.3)))
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in
               [(-s / 2, -hh / 2), (s / 2, -hh / 2), (s / 2, hh / 2), (-s / 2, hh / 2)]]
        cor = c["c"] if not cores else cores[int(c["s"]) % len(cores)]
        d.polygon(pts, fill=cor)

def raios(t, cor_a, cor_b, n=14, centro=(W / 2, H * 0.47)):
    im = Image.new("RGB", (W // 2, H // 2), cor_a); d = ImageDraw.Draw(im)
    cx, cy = centro[0] / 2, centro[1] / 2; R = 1400
    for i in range(n):
        a0 = t * 0.35 + i * 2 * math.pi / n; a1 = a0 + math.pi / n
        d.polygon([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                   (cx + R * math.cos(a1), cy + R * math.sin(a1))], fill=cor_b)
    return im.resize((W, H), Image.BILINEAR)

LOGO_IMG = Image.open(LOGO).convert("RGBA")
LOGO_IMG = LOGO_IMG.resize((860, int(860 * LOGO_IMG.height / LOGO_IMG.width)), Image.LANCZOS)

def _fundo_vinheta():
    g = np.linspace(0, 1, H)[:, None, None]
    a = np.array([255, 255, 255]) * (1 - g) + np.array([232, 240, 233]) * g      # branco -> cinza-esverdeado bem claro
    im = Image.fromarray(np.broadcast_to(a, (H, W, 3)).astype(np.uint8).copy())
    d = ImageDraw.Draw(im)
    d.rectangle((0, H - 64, W, H), fill=ESCURO); d.rectangle((0, H - 72, W, H - 64), fill=VERDE)
    im.paste(LOGO_IMG, ((W - LOGO_IMG.width) // 2, int(H * 0.45 - LOGO_IMG.height / 2)), LOGO_IMG)
    return im
VINHETA = _fundo_vinheta()

def vinheta(t):
    """Encerramento limpo: fundo branco com degradê suave, faixa verde embaixo e logo, sem @ e sem efeitos."""
    return VINHETA.copy()

# poeira leve levantada a cada pisada (cena do Vitor andando na terra, IMG_5336)
PISADAS = [(5.36, 330, 930), (5.84, 690, 890), (6.30, 430, 850)]   # (instante, x, y do pé)
def _textura_poeira(seed):
    rng = np.random.default_rng(seed); w, h = 520, 300
    a = np.zeros((h, w), np.float32); yy, xx = np.mgrid[0:h, 0:w]
    for _ in range(40):
        cx, cy = rng.normal(w / 2, w / 7), rng.normal(h * 0.62, h / 8); r = rng.uniform(25, 70)
        a += np.exp(-(((xx - cx) ** 2) + ((yy - cy) * 1.4) ** 2) / (2 * r * r)) * rng.uniform(0.3, 1)
    ruido = np.asarray(Image.fromarray((rng.random((h // 8, w // 8)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)) / 255
    a = np.clip(a / a.max() * (0.55 + 0.45 * ruido), 0, 1)
    rgba = np.dstack([np.full((h, w), 214), np.full((h, w), 190), np.full((h, w), 158), a * 255]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA").filter(ImageFilter.GaussianBlur(6))
POEIRA_TEX = [_textura_poeira(i) for i in range(3)]
def poeira_pisada(im, t):
    for i, (tp, x, y) in enumerate(PISADAS):
        k = (t - tp) / 0.9
        if 0 <= k < 1:
            e = ease_out(k / 0.5)
            alfa = 0.42 * min(1, k / 0.12) * (1 - k) ** 1.3
            cola(im, POEIRA_TEX[i], x + 30 * k, y - 60 * e, escala=0.55 + 0.75 * e, alfa=alfa)

# ───────────── composição quadro a quadro ─────────────
def render():
    total = round(T_FIM * FPS)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "21",
                            "-pix_fmt", "yuv420p", str(TMP / "video.mp4")], stdin=subprocess.PIPE)
    planos = [Plano(*p) for p in PLANOS]
    ip = 0; ant = None
    for n in range(total):
        t = n / FPS
        if t >= T_VIN - 1e-6:
            tv = t - T_VIN
            im = vinheta(tv)
            if tv < 0.4 and ant is not None:      # fusão simples
                im = Image.blend(ant, im, tv / 0.4)
            enc.stdin.write(im.tobytes()); continue
        while ip + 1 < len(planos) and t >= planos[ip + 1].t0 - 1e-6:
            planos[ip].fechar(); ip += 1
        pl = planos[ip]
        im = Image.fromarray(pl.quadro())
        dt = t - pl.t0; dur = pl.t1 - pl.t0
        z = 1 + pl.zoom * dt / dur; dx = dy = 0
        # transições de entrada
        if pl.trans == "soco" and dt < 0.25:
            z *= 1 + 0.20 * (1 - ease_out(dt / 0.25))
        if pl.trans == "whip" and dt < 0.2:
            k = 1 - ease_out(dt / 0.2); im = desloca(borrao_h(im, k), k * W * 0.6)
        if pl.trans == "glitch" and dt < 0.2:
            k = 1 - dt / 0.2; im = rgb_split(im, 28 * k); dx = 30 * k * math.sin(n * 2.1)
        # saída em whip quando o próximo plano entra em whip
        if ip + 1 < len(planos) and planos[ip + 1].trans == "whip" and pl.t1 - t < 0.1:
            k = 1 - (pl.t1 - t) / 0.1; im = desloca(borrao_h(im, k), -k * W * 0.5)
        # estalo: aproxima, treme e estoura em branco
        if 18.70 <= t < T_ASF:
            z *= 1 + 0.5 * ((t - 18.70) / 0.4) ** 3
        if T_ASF <= t < T_ASF + 0.5:
            k = 1 - (t - T_ASF) / 0.5
            dx, dy = 26 * k * math.sin(n * 1.9), 26 * k * math.cos(n * 2.7); z *= 1 + 0.06 * k
        # zoom de impacto em palavras fortes
        for tz in (1.4, 11.45, 26.05):
            if tz <= t < tz + 0.9:
                z *= 1 + 0.10 * ease_out((t - tz) / 0.12) * min(1, (tz + 0.9 - t) / 0.3)
        im = zoom(im, z, dx, dy)
        if T_ESTALO - 0.02 <= t < T_ASF + 0.25:
            im = clarao(im, 1.0 if t < T_ASF + 0.03 else 1 - (t - T_ASF - 0.03) / 0.22)
        for tc, tr in CORTES:                       # piscada leve nos cortes "soco"
            if tr == "soco" and tc <= t < tc + 0.1 and tc != 18.70:
                im = clarao(im, 0.28 * (1 - (t - tc) / 0.1))
        poeira_pisada(im, t)
        im.paste(BASE_ESCURA, (0, 0), BASE_ESCURA)
        d = ImageDraw.Draw(im)
        # confete de vitória quando a estrada fica pronta
        # (sem confete: pedido do dono)
        # selo
        for a, b, simg in SELO_IMGS:
            if a <= t < b:
                cola(im, simg, 40 + simg.width / 2, H - 120, alfa=min(1, (t - a) / 0.3))
        # contador +9KM
        a, b = CONTADOR
        if a <= t < b:
            k = t - a; num = min(9, 1 + int(k / 0.045)); fora = min(1, (b - t) / 0.12); g = KM_NUM[num]
            cola(im, g, 60 + g.width / 2, TOPO + g.height / 2 - 40, escala=1 + 0.08 * (1 - elastico(k / 0.35)), alfa=min(1, k / 0.08) * fora)
            if k > 0.25:
                e = ease_out((k - 0.25) / 0.25)
                cola(im, KM_SUB, 90 + KM_SUB.width / 2 + 60 * (1 - e), TOPO + g.height - 20, alfa=e * fora)
        # lettering
        for a, b, L in LET:
            if a <= t < b:
                desenha_lettering(im, L, t - a, min(1, (b - t) / 0.15))
        # legenda pequena
        for a, b, img in LEG:
            if a <= t < b:
                cola(im, img, W / 2, 1530, alfa=min(1, (t - a) / 0.06))
        ant = im
        enc.stdin.write(im.tobytes())
        if n % 150 == 0: print(f"quadro {n}/{total}", flush=True)
    for p in planos: p.fechar()
    enc.stdin.close(); enc.wait()

# ───────────── áudio ─────────────
def sfx():
    """Efeitos sonoros sintetizados (whoosh nos cortes, subida + impacto no estalo)."""
    sr = 48000; a = np.zeros(int(T_FIM * sr)); rng = np.random.default_rng(3)
    def soma(t0, s):
        i = int(t0 * sr); s = s[: max(0, len(a) - i)]; a[i:i + len(s)] += s
    def whoosh(dur, g):
        n = int(dur * sr); r = rng.standard_normal(n)
        k = np.linspace(0, 1, n); env = np.sin(math.pi * k) ** 2
        f = np.cumsum(r) ; f -= np.convolve(f, np.ones(400) / 400, "same")      # passa-faixa tosco
        f /= np.abs(f).max() + 1e-9
        return f * env * g
    for tc, tr in CORTES:
        if tr in ("whip", "soco") and tc != 18.70:
            soma(tc - 0.12, whoosh(0.3, 0.16 if tr == "whip" else 0.10))
    n = int(0.9 * sr); k = np.linspace(0, 1, n)                                   # subida antes do estalo
    soma(T_ESTALO - 0.9, np.sin(2 * math.pi * np.cumsum(200 + 1400 * k ** 2) / sr) * k ** 2 * 0.10 + whoosh(0.9, 0.12) * k)
    n = int(1.6 * sr); k = np.arange(n) / sr                                      # impacto
    soma(T_ASF - 0.02, np.sin(2 * math.pi * (95 * k - 28 * k * k)) * np.exp(-k * 3.2) * 0.75
         + rng.standard_normal(n) * np.exp(-k * 9) * 0.22)
    soma(T_ASF, whoosh(2.2, 0.14))                                                # tapete desenrolando
    soma(T_VIN - 0.1, whoosh(0.45, 0.16))
    a = np.clip(a, -1, 1)
    with wave.open(str(TMP / "sfx.wav"), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype(np.int16).tobytes())

def ganho(arq, ss, dur, alvo=-20.0):
    r = subprocess.run(["ffmpeg", "-ss", str(ss), "-t", str(dur), "-i", arq, "-vn", "-af", "highpass=f=90,volumedetect",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = float(r.split("mean_volume:")[1].split("dB")[0])
    return min(16.0, alvo - m)

def mixar():
    falas = [  # (arquivo, entrada, duração, instante na linha do tempo)
        (mov(5340), 0.75, 5.30, 0.00), (mov(5343), 0.00, 5.75, 5.30), (mov(5347), 0.00, 4.50, 11.05),
        (mov(5349), 0.00, 1.95, 16.75), (mov(5350), 3.40, 0.50, 18.90), (mov(5352), 0.00, 2.85, T_VOZ5),
        (mov(5354), 0.45, 6.30, T_S7),
    ]
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(TMP / "video.mp4")]; fc = []; nomes = []
    for i, (arq, ss, dur, t0) in enumerate(falas):
        cmd += ["-ss", str(ss), "-t", str(dur), "-i", arq]
        g = ganho(arq, ss, dur) if i != 4 else 6.0
        fc.append(f"[{i + 1}:a]aresample=48000,highpass=f=90,afftdn=nr=8,volume={g:.1f}dB,"
                  f"afade=t=in:d=0.04,afade=t=out:st={dur - 0.06}:d=0.06,adelay={int(t0 * 1000)}:all=1[f{i}]")
        nomes.append(f"[f{i}]")
    nm = len(falas) + 1
    cmd += ["-i", str(MIDIA / "trilha-vitoria.mp3"), "-i", str(TMP / "sfx.wav")]
    # trilha: baixa sob a fala, sobe nas viradas (máquinas, asfalto e encerramento)
    pts = [(0, .30), (.25, .11), (15.3, .11), (15.6, .34), (16.6, .34), (16.8, .11), (18.6, .11), (T_ASF, .50),
           (T_VOZ5 - .1, .50), (T_VOZ5 + .2, .15), (T_VOZ5 + 2.8, .15), (T_VOZ5 + 3.1, .42), (T_S7 - .1, .42),
           (T_S7 + .2, .11), (31.2, .11), (T_VIN, .46), (T_FIM - .9, .46), (T_FIM, 0)]
    expr = "0"
    for (t0, v0), (t1, v1) in reversed(list(zip(pts, pts[1:]))):
        expr = f"if(lt(t,{t1}),{v0}+({v1}-{v0})*(t-{t0})/{t1 - t0},{expr})"
    fc.append(f"[{nm}:a]aresample=48000,atrim=0:{T_FIM},volume='{expr}':eval=frame[mus]")
    fc.append(f"[{nm + 1}:a]aresample=48000,volume=0.9[sfx]")
    fc.append(f"{''.join(nomes)}amix=inputs={len(falas)}:normalize=0,acompressor=threshold=-18dB:ratio=3:attack=5:release=120:makeup=2[voz]")
    fc.append(f"[voz][mus][sfx]amix=inputs=3:normalize=0,alimiter=limit=0.89,apad,atrim=0:{T_FIM}[a]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ac", "2", "-movflags", "+faststart", str(SAIDA)]
    subprocess.run(cmd, check=True)

def srt():
    def ts(s): ms = round(s * 1000); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    (AQUI / "legenda.srt").write_text("\n".join(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n" for i, (a, b, t) in enumerate(LEGENDAS, 1)), encoding="utf-8")

if __name__ == "__main__":
    srt()
    if "--so-audio" not in sys.argv: render()
    sfx(); mixar()
    print("Pronto:", SAIDA)
