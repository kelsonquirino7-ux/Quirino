# Itamar · Dia da Consciência Negra (20/11) — vídeo 9:16, 30 s

## Status
- **Pronto:** `encerramento.mp4`, a cena 4 (19–30 s). Fundo preto e dourado com padrão inspirado em tecelagem africana,
  feixe de luz e o **logo original** (`identidade/logo-itamar-3d-transparente.png`). Fonte editável: `encerramento.html`.
  Renderize com `node render-video.js`.
- **Falta:** as cenas 1–3 com pessoas reais, a voz e a trilha. Usam créditos do Magnific, então aguardam aprovação do dono.
- Também prontos: `narracao.srt` (legenda dos 30 s) e `legenda.txt` (texto para o Instagram).

## Orçamento Magnific (consultado em 19/11/2026, saldo 1.611 créditos)
| Opção | Cenas 1–3 | Voz + trilha | Total |
|---|---|---|---|
| Kling 2.5 1080p (3 × 5 s, alongadas para 6/6/7 s) | 975 | ~144 | **~1.120** |
| MiniMax H3 Turbo 768p (6/6/7 s) | ~760 | ~144 | ~905 |
| Seedance 2.5 1080p multishot 19 s | ~15.000 | ~144 | ~15.140 (precisa recarregar) |

## Prompts das cenas (prontos para gerar)
Regras para todas: hiper-realista, pessoas brasileiras com expressões naturais, sem texto na tela, sem logotipos, sem estereótipos.
Look: cinema, lente anamórfica, luz de golden hour, paleta quente.

1. **0–6 s** — Close cinematográfico e lento (push-in) no rosto de uma senhora negra brasileira de uns 70 anos, com cabelos
   grisalhos naturais e olhar firme e sereno. A luz dourada do fim de tarde bate de lado no rosto, com profundidade de campo rasa.
   Sabedoria, ancestralidade e força.
2. **6–12 s** — Roda de capoeira ao ar livre no fim de tarde, em praça de cidade do interior da Bahia. Homens e mulheres negros
   jogam com movimentos autênticos, enquanto berimbau, atabaque e palmas acompanham. Rostos de alegria, orgulho e liberdade, com
   câmera em travelling lateral suave e mesma luz dourada.
3. **12–19 s** — Família negra brasileira (pai, mãe e filha de uns 7 anos) ao ar livre ao pôr do sol. A mãe abraça a filha e o pai
   sorri. A criança olha para o horizonte com esperança, com a câmera subindo suavemente (crane up). Amor, união e futuro.
4. **19–30 s** — `encerramento.mp4` (pronto).

## Áudio
- Voz: masculina brasileira, grave, firme e acolhedora. O texto está em `narracao.srt`.
- Trilha: instrumental cinematográfica com percussão afro-brasileira (atabaque, berimbau, agogô), crescendo até o logo.

## Montagem
Juntar as cenas 1–3 com transições em dissolve (0,6 s), escurecer para a cena 4, mixar voz e trilha (trilha a −18 dB sob a voz)
e queimar `narracao.srt`, se quiser legenda.
