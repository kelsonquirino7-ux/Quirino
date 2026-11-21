# Empresa X Confraternização — Itamar Supermercado (21/11/2026)
- `empresa-x-confraternizacao.mp4` — final 1080×1920, 30 fps, H.264, 64,1 s (60,5 s da filmagem original + 3,6 s de encerramento com o logo).
- `grafismos.html` — fonte editável dos grafismos (título em arco, selo do X, transições, confete, encerramento).
- `render.js` — renderiza os grafismos quadro a quadro: `node render.js /pasta/quadros` (teste: `--quadro 3.0 teste.png`).
- `montar.sh` — junta tudo: `bash montar.sh bruto.mp4 /pasta/quadros`.
- `trilha-magnific-animada.mp3` — trilha mais agitada (2ª versão, Magnific, 80 créditos aprovados pelo dono), em loop. A 1ª trilha (também 80 créditos) foi descartada.
- Vídeo bruto (não versionado, 85 MB): Google Drive, arquivo 14-vEI2uxvYaEU30kFTSYrzYLIpvj8TQI.

Decisões
- O título "Empresa X Confra" vinha gravado no bruto; a nova tarja 3D em arco cobre esse texto, com "EMPRESA X CONFRA": X no centro e cada palavra centralizada na sua metade (pedido do dono: "Confra" no lugar de "Confraternização").
- Cores só do logo: amarelo #FFD302, vermelho #FF291E e o vermelho-sombra do próprio logo #BF0101 (amarelo sobre #BF0101 = 4,5:1).
  Marrom #280E01 não usado (quase preto; o pedido proíbe preto). Sem "@" no vídeo (só na legenda do post).
- Trecho 11,27–15,47 s tinha barras pretas laterais no original: preenchidas com o próprio quadro desfocado (sem cortar a cena).
- Áudio original era uma música (sem fala); substituído pela trilha + efeitos sonoros sintetizados.
- A filmagem original terminava com 6 quadros pretos (60,47–60,67 s): cortados; o encerramento começa ali.
- Zoom suave de 4,5% nos cortes (ancorado no topo, para a faixa continuar cobrindo o texto antigo) e transição em faixas diagonais em 11,3 · 23,7 · 36,4 · 49,1 s e no final.
- v2 (pedido do dono): moldura fina vermelha com filete amarelo; logo do Itamar fixo embaixo o vídeo todo, que no final sobe girando em 3D
  (espessura feita com cópias escurecidas atrás do logo; o logo da frente fica intacto); chuva de confete em tela cheia no encerramento;
  selo amarelo atrás do logo retirado.
- v3 (pedidos do dono): texto "EMPRESA X CONFRA" em maiúsculas na fonte Comfortaa Bold (OFL, em `ferramentas/fontes/`), a mais próxima do
  "itamar" do logo; tarja ampliada 1,25× para cima e de ponta a ponta da tela (a borda de baixo segue cobrindo o texto antigo);
  confete caindo do arco só na 2ª parte de cada pessoa (roupa de festa) — trechos listados em `CONFRA` no grafismos.html.
