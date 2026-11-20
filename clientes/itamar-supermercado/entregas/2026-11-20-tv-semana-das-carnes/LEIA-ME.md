# TV — Semana das carnes / Ofertas do açougue (20/11/2026)
- `tv-carnes.mp4` — final: 1920x1080 (TV 65" deitada), 43 s, 30 fps, sem áudio. Feito para rodar em loop.
- `tv-carnes.html` — fonte editável. Para mudar produto/preço: editar a lista `PRODUTOS` e rodar `node render-video.js`.
- Roteiro: abertura (logo + SEMANA DAS CARNES + selo OFERTAS DO AÇOUGUE 3D, selo discreto "quirino") 4 s → 6 produtos, 5 s cada → grade 3x2 (9 s).
- Textos e preços: copiados da arte enviada pelo dono (`fotos/referencias/encarte-semana-das-carnes-2026-11-20.png`). Sem data.
- Fotos crescem até ocupar o espaço (object-fit), por causa da charque pequena.
- Fotos: cruz machado, bisteca e fígado já estavam em `fotos/produtos/acougue/`; charque, frango Gujão e ovos enviados pelo dono e recortados sem custo.
- Selo 3D: `identidade/selos/selo-ofertas-do-acougue-3d.png`, recortado da própria arte (resolução limitada; trocar pelo PNG original se o dono mandar).

## Versão em pé (TV 32" vertical)
- `tv-carnes-vertical.mp4` — 1080x1920, para TV/player que já toca vídeo em pé.
- `tv-carnes-vertical-girado.mp4` — 1920x1080 girado 90° (anti-horário, igual ao vídeo antigo do açougue), para TV montada em pé que só toca vídeo deitado.
- Mesmo HTML, layout em pé com `?v`. Gerar: `node render-vertical.js`.
