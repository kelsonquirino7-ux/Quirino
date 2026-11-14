# Vem economizar — vinheta para as TVs da loja (14/11/2026)

Avatar cai na tela, dá tchau, sai correndo pela esquerda, volta empurrando um carrinho cheio de compras,
para no centro e chama o público com a mão. Depois entram o lettering "VEM ECONOMIZAR" e a logo animada do Itamar.
Sem áudio, 15,5 s, 30 fps.

- `vem-economizar-tv65-4k.mp4` — TV 65" horizontal, 3840×2160.
- `vem-economizar-tv32-vertical.mp4` — TV 32" em pé: arquivo 1920×1080 com a imagem girada (igual ao vídeo do açougue).
- `vem-economizar.html` — fonte editável (fundo, sombra, queda, lettering, logo). `?fmt=h` ou `?fmt=v`.
- `render-video.js` — `node render-video.js h` e `node render-video.js v`.
- `avatar-seedance-verde.mp4` — animação do avatar gerada no Magnific (Seedance 2.5, 720p, 10 s, 4.400 créditos), fundo verde.
  Uma tentativa anterior no Kling 2.5 (650 créditos) foi descartada porque deformava o logo da camisa.

Recriar os quadros recortados (não vão para o git):
```
ffmpeg -i avatar-seedance-verde.mp4 -vf "chromakey=0x0BA640:0.13:0.06,despill=type=green:mix=0.6:expand=0.1,format=rgba" avatar/%04d.png
```
`avatar/pes.js` guarda a posição dos pés em cada quadro (usada para a sombra no chão).

Lettering: estilo provisório (letras quicando) até o dono mandar a referência do link do YouTube.
Obs.: o avatar é 720p ampliado para 4K, então fica um pouco mais macio que o fundo e a logo.
