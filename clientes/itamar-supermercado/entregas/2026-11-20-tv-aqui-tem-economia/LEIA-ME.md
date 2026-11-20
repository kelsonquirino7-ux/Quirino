# TV — Aqui tem economia (20/11/2026)
- `tv-economia.mp4` — final: 1920x1080 (TV 65" deitada), 64 s, 30 fps, sem áudio. Feito para rodar em loop.
- `tv-economia.html` — fonte editável. Para mudar produto/preço: editar a lista `PRODUTOS` e rodar `node render-video.js`.
- Roteiro: abertura com logo + "AQUI TEM ECONOMIA" e selo discreto "quirino" nas cores oficiais, animado, no canto (4 s) → 12 produtos, 4,2 s cada → grade com os 12 (9,6 s).
- Textos e preços: copiados da arte enviada pelo dono (`fotos/referencias/encarte-aqui-tem-economia-2026-11-20.png`). Sem data de validade.
- Fotos: enviadas pelo dono, recortadas sem custo (`fotos/produtos/mercearia/`). O dono aprovou usar Mucilon 600 g, Itália 2 kg
  e Julieta 2 kg (foto). Texto do Julieta trocado para "310 g" a pedido do dono. Itália recortado de novo pelas cores da embalagem.

## Versão em pé (TV 32" vertical)
- `tv-economia-vertical.mp4` — 1080x1920, para TV/player que já toca vídeo em pé.
- `tv-economia-vertical-girado.mp4` — 1920x1080 girado 90° (anti-horário, igual ao vídeo antigo do açougue), para TV montada em pé que só toca vídeo deitado.
- Mesmo HTML, layout em pé com `?v`. Gerar: `node render-vertical.js`.
