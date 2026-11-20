# TV — Ofertas de eletro (20/11/2026)
- `tv-eletro.mp4` — final: 1920x1080 (TV 65" deitada), 46 s, 30 fps, sem áudio. Feito para rodar em loop.
- `tv-eletro.html` — fonte editável. Para mudar produto/preço: editar a lista `PRODUTOS` e rodar `node render-video.js`.
- Roteiro: abertura (logo + OFERTAS DE ELETRO + selo SUPER OFERTAS 3D, selo discreto "quirino") 4 s → 6 produtos, 5,5 s cada → grade 3x2 (9 s).
- Textos e preços: copiados da arte enviada pelo dono (`fotos/referencias/encarte-ofertas-de-eletro-2026-11-20.png`). Sem data.
- Fotos: enviadas pelo dono, recortadas sem custo (`fotos/produtos/eletro/`).
- Selo 3D: `identidade/selos/selo-super-ofertas-3d.png`, recortado do PNG de banco de imagens (Designi) enviado pelo dono.
  Tem marca-d'água fraca do banco; trocar pelo arquivo licenciado sem marca quando o dono baixar.

## Versão em pé (TV 32" vertical)
- `tv-eletro-vertical.mp4` — 1080x1920, para TV/player que já toca vídeo em pé.
- `tv-eletro-vertical-girado.mp4` — 1920x1080 girado 90° (anti-horário, igual ao vídeo antigo do açougue), para TV montada em pé que só toca vídeo deitado.
- Mesmo HTML, layout em pé com `?v`. Gerar: `node render-vertical.js`.
