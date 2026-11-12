#!/usr/bin/env python3
"""Gera video-efeitos.ass: lettering estilo cinema (linha fina + palavra forte, sombra suave, sem contorno)
e a legenda da fala. Uso: python3 lettering.py  (edite a lista TEXTOS e rode de novo)."""
# início, fim, linha pequena, linha grande
TEXTOS = [
    (2.95, 5.25, "QUANDO A", "ÁGUA FALTA"),
    (5.65, 7.25, "TODOS", "SOFREM"),
    (7.75, 10.6, "MAS JAMAIS SOLTAREMOS", "A MÃO"),
    (10.9, 13.25, "DO NOSSO", "POVO"),
    (13.65, 15.9, "VAMOS LEVAR", "ÁGUA"),
    (16.3, 18.55, "PARA TODOS", "QUE PRECISAM"),
    (27.75, 31.2, "ÁGUA É DIREITO", "DE TODOS"),
]
FALA = [(31.5, 33.65, "O caminhão já chegou"), (33.65, 35.9, "e tá botando água\\Npara todo mundo")]
Y_FALA = 1530

def t(x):
    cs = round(x * 100); return f"0:{cs // 6000:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"

def linha(a, z, txt, y, est, sp, sobe=26, atraso=0.0):
    """Texto que entra subindo de leve, em fade, com o espaçamento fechando; sombra suave por baixo."""
    a += atraso; d = int((z - a) * 1000)
    mov = rf"\an5\move(540,{y + sobe},540,{y},0,520)\fad(380,320)\fsp{sp[0]}\t(0,{d},\fsp{sp[1]})"
    s = f"Dialogue: 0,{t(a)},{t(z)},{est},,0,0,0,,{{{mov}\\1c&H000000&\\3c&H000000&\\1a&H38&\\3a&H38&\\bord7\\blur12}}{txt}\n"
    s += f"Dialogue: 1,{t(a)},{t(z)},{est},,0,0,0,,{{{mov}\\bord0\\shad0\\blur6\\t(0,450,\\blur0.4)}}{txt}\n"
    return s

def traco(a, z, y, larg=300):
    return (f"Dialogue: 1,{t(a)},{t(z)},Traco,,0,0,0,,{{\\an5\\pos(540,{y})\\fad(250,300)\\fscx0\\t(0,550,\\fscx100)"
            f"\\bord0\\shad0\\p1}}m 0 0 l {larg} 0 l {larg} 3 l 0 3{{\\p0}}\n")

ev = linha(0.6, 2.7, "SANTANÓPOLIS", 1125, "Grande", (22, 9))
ev += traco(1.0, 2.7, 1203, 360)
ev += linha(0.6, 2.7, "12 DE NOVEMBRO DE 2026", 1268, "Pequena", (8, 5), atraso=0.4)
for a, z, p, g in TEXTOS:
    ev += linha(a, z, p, 1096, "Pequena", (10, 6))
    ev += traco(a + 0.2, z, 1154, 120)
    ev += linha(a, z, g, 1236, "Grande", (12, 3), atraso=0.22)
for a, z, txt in FALA:
    ev += f"Dialogue: 0,{t(a)},{t(z)},Fala,,0,0,0,,{{\\an5\\pos(540,{Y_FALA})\\fad(120,120)\\1c&H000000&\\3c&H000000&\\1a&H30&\\3a&H30&\\bord7\\blur12}}{txt}\n"
    ev += f"Dialogue: 2,{t(a)},{t(z)},Fala,,0,0,0,,{{\\an5\\pos(540,{Y_FALA})\\fad(120,120)\\bord0\\shad0}}{txt}\n"
cab = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Grande,Exo 2 ExtraBold,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,30,30,0,1
Style: Pequena,Exo 2,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,6,0,1,0,0,5,30,30,0,1
Style: Traco,Exo 2 Medium,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Fala,Inter SemiBold,62,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(__file__.rsplit("/", 1)[0] + "/video-efeitos.ass", "w", encoding="utf-8").write(cab + ev)
