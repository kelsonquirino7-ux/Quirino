"""Gera as vinhetas finais (HTML) de cada cliente nos formatos 9x16 e 16x9.
Uso: python3 ferramentas/vinhetas.py && node ferramentas/render.js clientes/*/modelos/vinheta-*.html"""
C = {
 'prefeitura-santanopolis': dict(bg='#002F67', logo='logo-prefeitura-branco.png', arroba='@pmssantanopolis', cor='#C7D6EC', faixa='#FFFFFF', fonte='"Exo 2"', lw=(860, 1300)),
 'prefeito-vitor':          dict(bg='linear-gradient(160deg,#FFFFFF 40%,#DDF5E0)', logo='logo-vitor-prefeito-do-povo.png', arroba='@prefeitovitor', cor='#015927', faixa='#0AA514', fonte='Montserrat', lw=(820, 1000)),
 'deni-de-vitor':           dict(bg='#FFFFFF', logo='logo-deni-de-vitor-transparente.png', arroba='@denidevitorofc', cor='#004E1C', faixa='#EB1C24', fonte='Montserrat', lw=(820, 1000)),
 'itamar-supermercado':     dict(bg='#FFD302', logo='logo-itamar-3d-transparente.png', arroba='@itamarsupermercado', cor='#FF291E', faixa='#FF291E', fonte='"Baloo 2"', lw=(880, 1100)),
}
FMT = {'9x16': (1080, 1920, 0), '16x9': (1920, 1080, 1)}
for cli, d in C.items():
    for nome, (w, h, i) in FMT.items():
        html = f'''<!doctype html><meta charset="utf-8"><meta name="tamanho" content="{w}x{h}">
<link rel="stylesheet" href="../../../ferramentas/fontes.css">
<!-- Vinheta final {nome} — gerada por ferramentas/vinhetas.py; edite lá, não aqui. -->
<style>*{{margin:0;box-sizing:border-box}}
body{{width:{w}px;height:{h}px;background:{d['bg']};display:flex;flex-direction:column;align-items:center;justify-content:center;gap:{48 if i==0 else 36}px;position:relative;overflow:hidden}}
img{{width:{d['lw'][i]}px;max-height:{int(h*0.45)}px;object-fit:contain}}
.a{{font:800 {64 if i==0 else 56}px {d['fonte']},sans-serif;color:{d['cor']};letter-spacing:.01em}}
.f{{position:absolute;left:0;right:0;bottom:0;height:{24 if i==0 else 18}px;background:{d['faixa']}}}
</style>
<img src="../identidade/{d['logo']}" alt=""><div class="a">{d['arroba']}</div><div class="f"></div>'''
        open(f'clientes/{cli}/modelos/vinheta-{nome}.html', 'w').write(html)
print('ok')
