# Vem economizar — vinheta para as TVs da loja (14/11/2026)

Avatar cai na tela, dá tchau, sai correndo pela esquerda, volta empurrando um carrinho cheio de compras,
para no centro e chama o público com a mão. Depois entram o lettering "VEM ECONOMIZAR" e a logo animada do Itamar.
Sem áudio, 16 s, 30 fps.

- `vem-economizar-tv65-4k.mp4` — TV 65" horizontal, 3840×2160.
- `vem-economizar-tv32-vertical.mp4` — TV 32" em pé: arquivo 1920×1080 com a imagem girada (igual ao vídeo do açougue).
- `vem-economizar.html` — fonte editável (fundo, sombra, queda, lettering, logo). `?fmt=h` ou `?fmt=v`.
- `render-video.js` — `node render-video.js h` e `node render-video.js v`.
- `avatar-seedance-verde.mp4` — animação do avatar gerada no Magnific (Seedance 2.5, 720p, 10 s, 4.400 créditos), fundo verde.
  Uma tentativa anterior no Kling 2.5 (650 créditos) foi descartada porque deformava o logo da camisa.

Recriar os quadros recortados (não vão para o git): `python3 recorte.py avatar-seedance-verde.mp4 avatar`.
Requer `pip install opencv-python-headless`. O recorte é próprio (não o chromakey do ffmpeg): não apaga o brócolis
e a salsa, que são verdes como o fundo; recolhe e suaviza a borda e pinta a faixa de borda com a cor do interior do avatar,
então não fica contorno verde/cinza; tapa furinhos internos e tira a sombra verde do chão.
`avatar/pes.js` guarda a posição dos pés em cada quadro (usada para a sombra no chão).

Fundo: corredor de supermercado gerado no Magnific (imagem `fundo-mercado.png`, 2×65 créditos, a 2ª trocando o hortifrúti
por gôndolas) e animado no Kling 2.5 (`fundo-mercado.mp4`, 650 créditos, câmera avançando no corredor), desfocado na composição. Quadros em `fundo/`:
`ffmpeg -i fundo-mercado.mp4 -q:v 2 fundo/%04d.jpg`.

Lettering "tela inteira" fiel à referência do dono (`referencia-lettering.jpg`): "VEM ECONOMIZAR" repetido em linhas coladas
que enchem a tela, a do meio em marrom e as outras em vermelho vivo do Itamar, fonte Titan One (SIL OFL).
Sem o @ no final.
Obs.: o avatar é 720p ampliado para 4K, então fica um pouco mais macio que o fundo e a logo.
