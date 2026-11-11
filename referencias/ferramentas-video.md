# Ferramentas de vídeo — as 20 do PDF

Fonte: `ferramentas-video-20-repos.pdf` (“Animação. Física. 3D. Som. Entrega.”), enviado pelo
dono em 2026-11-11. Todas são de código aberto. Coluna **Aqui** = situação no ambiente de
nuvem em que o Claude trabalha (conferido em 2026-11-11: registro npm e PyPI acessíveis,
Chromium + Playwright e FFmpeg já instalados, huggingface.co bloqueado pela rede).

| # | Ferramenta | Serve para | Aqui | Uso na Quirino |
|---|---|---|---|---|
| 01 | [Remotion](https://github.com/remotion-dev/remotion) | Vídeo programado em React | Instalável (npm). **Licença: grátis só para empresas de até 3 pessoas; conferir antes de adotar** | Alternativa ao 02; só se precisar de React |
| 02 | [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML → vídeo | Instalável (npm) | **Caminho natural**: os cards já são HTML; dá para animá-los e virar Reels |
| 03 | [Anime.js](https://github.com/juliangarnier/anime) | Linha do tempo de animação | Instalável | Coreografia das entradas (cartão, número, texto) |
| 04 | [React Spring](https://github.com/pmndrs/react-spring) | Animação de mola | Instalável | Só com React; a mola também sai do Anime.js |
| 05 | [PixiJS](https://github.com/pixijs/pixijs) | 2D acelerado por GPU | Instalável | Fundos com muitos elementos |
| 06 | [p5.js](https://github.com/processing/p5.js) | Arte generativa | Instalável | Fundos orgânicos (linhas, ondas) |
| 07 | [Paper.js](https://github.com/paperjs/paper.js) | Caminhos vetoriais | Instalável | Linhas que se desenham, conectores |
| 08 | [Matter.js](https://github.com/liabru/matter-js) | Física 2D | Instalável | Objetos caindo/empilhando |
| 09 | [Three.js](https://github.com/mrdoob/three.js) | Cenas 3D | Instalável (render por software, lento) | Objeto 3D simples girando; vidro e brilho |
| 10 | [Rapier](https://github.com/dimforge/rapier) | Colisões 3D | Instalável | Raro |
| 11 | [OGL](https://github.com/oframe/ogl) | Shaders | Instalável | Brilhos e degradês vivos de fundo |
| 12 | [tsParticles](https://github.com/tsparticles/tsparticles) | Partículas | Instalável | Poeira de luz, confete em comemoração |
| 13 | [glTF Transform](https://github.com/donmccurdy/glTF-Transform) | Otimizar modelos 3D | Instalável | Só se entrar modelo 3D |
| 14 | [GL Transitions](https://github.com/gl-transitions/gl-transitions) | Transições entre cenas | O FFmpeg já tem `xfade` com várias delas | Cortes entre trechos |
| 15 | [OBS Studio](https://github.com/obsproject/obs-studio) | Gravar tela | Não (programa de computador, para o dono usar) | Gravar tela/tutorial |
| 16 | [Chatterbox](https://github.com/resemble-ai/chatterbox) | Narração por voz | **Bloqueado** (modelo no huggingface) | Locução; hoje só via Magnific, que é pago |
| 17 | [Tone.js](https://github.com/Tonejs/Tone.js) | Efeitos sonoros sintetizados | Instalável | "Whoosh" e "pop" nas entradas, sem custo |
| 18 | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) | Transcrever áudio em legenda | **Pacote instala, modelo bloqueado** (huggingface) | Acabaria com o .srt escrito à mão |
| 19 | [OpenCut](https://github.com/OpenCut-app/OpenCut) | Editor de linha do tempo | Não (aplicativo, para o dono usar) | Edição manual |
| 20 | [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Codificar e entregar | **Já em uso** (`ferramentas/video.sh`) | Base de todo vídeo |

## O que isso destrava
1. **Cartões e gráficos animados sobre o vídeo** (as referências de `graficos-na-tela/`):
   HTML animado → quadros pelo Chromium → sobreposto com FFmpeg. Usa 02/03 + o que já existe.
2. **Cards animados** para Reels/Stories a partir dos mesmos modelos `.html` dos clientes.
3. **Efeitos sonoros** gerados sem custo (17).

## O que depende do dono
- **Transcrição automática (18) e narração (16):** precisam que o endereço `huggingface.co`
  seja liberado na rede do ambiente. Sem isso, a legenda continua vindo do texto enviado.
- **Remotion (01):** confirmar se a licença gratuita cobre a Quirino.
