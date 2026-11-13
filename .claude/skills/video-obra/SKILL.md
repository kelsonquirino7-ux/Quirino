---
name: video-obra
description: Edita Reels 9:16 de obra pública (asfalto, pavimentação, estrada, drenagem, máquinas) a partir dos brutos do celular do cliente, com fala sincronizada, lettering de obra, cenas de IA (máquinas trabalhando, poeira/lama, "antes e depois" como asfalto desenrolando), trilha de vitória e encerramento com a logo. Use quando o dono pedir vídeo de obra, asfalto, estrada, "antes e depois" ou "como vai ficar", ou disser "faz igual ao do asfalto do Alto Alegre".
---

# Vídeo de obra (modelo: asfalto Rumo–Alto Alegre, Vitor, 2026-11-13)

Entrega de referência: `clientes/prefeito-vitor/entregas/2026-11-13-asfalto-alto-alegre/`
(`montagem.py`, `midia/`, `legenda.txt`, `asfalto-rumo-alto-alegre-vitor.mp4`).
Modelo editável: `montagem-modelo.py` (cópia do script final) nesta pasta.

## 0. Antes de tudo
- Ler `CLAUDE.md`, o `brief.md` do cliente e `video.json`. Cores e fonte só do brief.
- Prefeitura: sem promoção pessoal. Vídeo em 1ª pessoa do político vai na pasta do político.
- Nunca inventar números ou falas: só o que o cliente disse/mandou.
- **Créditos (Magnific): perguntar SEMPRE antes, com custo e saldo** (`account_balance`, `simulate_cost`).
  Nunca passar do valor aprovado sem nova aprovação. Se uma geração for bloqueada, avisar e esperar.

## 1. Brutos e fala
- Pasta pública do Drive: listar com `https://drive.google.com/embeddedfolderview?id=<ID>`
  e baixar cada arquivo com `https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t`
  para o scratchpad (brutos não vão para o repositório).
- Folha de contato: `ffmpeg -vf "fps=3/dur,scale=240:-2,tile=3x1"` por clipe.
- Transcrição com tempos por palavra: `pip install openai-whisper` (modelo `medium`, `language="pt"`,
  `word_timestamps=True`). Corrigir nomes de lugar à mão (ex.: "Otolegre" → Alto Alegre).
- Estalo de dedos/batida: pico de amplitude no áudio do clipe.

## 2. Perguntar o roteiro passo a passo (uma vez, tudo junto)
Tabela de passos (fala → cena → efeito), custo de créditos, sentido de "BG de vitória",
encerramento (logo do cliente, sem @ se pedido). Usar AskUserQuestion.

## 3. Cenas de IA (Magnific, só com aprovação)
| Cena | Como | Custo aprox. |
|---|---|---|
| Máquina trabalhando | `video_generate` Kling 2.5, 5 s, 9:16, 1080p, `keyframes.start` = quadro real da máquina; prompt de movimento hidráulico realista | 325 |
| Estrada pronta | `images_generate` Nano Banana 2.1 com o quadro real como referência: **manter vegetação natural**, só trocar a pista e cobrir erosão com grama baixa pouco verde, terreno plano | 65 |
| Asfalto-tapete | `video_generate` Kling 2.5 com `start` = estrada de terra real e `end` = estrada pronta; rolo desenrolando e assentando | 325 |
| Lama | imagem editada (chuva, lama moderada) + vídeo com chuva leve | 65 + 325 |
| Trilha de vitória | `audio_music_generate` ElevenLabs v2, 45 s, instrumental | 900 |
- Conferir sempre com folha de quadros. Celular/mão/objetos estranhos na cena → refazer ou cortar o trecho.
- Poeira: preferir **cena real** (pessoa andando na terra) + poeira leve procedural na pisada (`poeira_pisada`).
- Defeito de cor pontual (ex.: miolo amarelo no rolo): `limpa-cor.py` troca só a cor alvo numa zona; testar
  para não estragar faixas da pista. Se piorar, voltar à versão anterior.
- Luz da máquina: manter a da geração original, salvo pedido.
- Clipes de IA em `midia/` recodificados (`crf 19`, sem áudio). Nada acima de 100 MB no git.

## 4. Montagem (`montagem-modelo.py`)
Copiar para a entrega e ajustar: `PLANOS` (linha do tempo), `LEGENDAS`, `LETTERING`, `CONTADOR`,
`SELOS`, `PISADAS`, `falas` em `mixar()`. Rodar: `python3 montagem.py <pasta-dos-brutos> video.mp4`
(`--so-audio` refaz só a mixagem).
- **Legenda pequena** embaixo (Montserrat 600, branco, **borda verde escura do cliente**).
- **Lettering de obra** (referência do dono: vídeo de obra estilo prefeitura), Barlow Condensed Itálico 900/700:
  `pilha` (pequeno branco + GRANDE verde), `selo` (placa inclinada + fita), `rotulo` (com pontilhado),
  `vazado` (contorno que preenche), contador `+9KM`. **Sempre na faixa de cima (TOPO ≈ 190 px), sem cobrir
  rosto nem cena**; selo de abertura sobre imagem aérea pode ser maior e centralizado (`esc`, `cy`).
- Transições: soco, whip, glitch; flash + tremida no estalo; zoom de impacto em palavra forte.
- Selos discretos no rodapé: "IMAGEM ILUSTRATIVA" (cenas de IA) e "PROJEÇÃO · IMAGEM ILUSTRATIVA" (obra pronta).
- Sem confete. Encerramento: logo sem efeitos, fundo branco com degradê suave e **tarja verde fina** embaixo.
- **Fala mais lenta**: `VEL = 0.90` desacelera imagem e voz juntas (setpts + atempo) → tom natural e boca
  sincronizada; trilha no andamento normal. Não descer de 0.85.

## 5. Conferir e entregar
- Folha de 14–20 quadros (`previa.jpg`) → mandar **prévia primeiro** (SendUserFile), depois o vídeo.
- Volume: `volumedetect` (média ~ -17 dB, pico < -0.3 dB). Transcrever o final para checar sincronia.
- Nome final descritivo: `<obra>-<local>-<cliente>.mp4` + `legenda.txt` (texto + 3–6 hashtags locais, sem @ se pedido).
- Commit descritivo + push no branch da sessão; resumo curto com custo de créditos gasto.
