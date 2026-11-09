# Quirino — Identidade Visual

Repositório da **Quirino**, produtora de vídeos, relatórios e cards (artes para redes sociais)
para governos e empresas de Santanópolis (BA) e região. Contém a identidade visual da Quirino
e as pastas de cada cliente. O dono trabalha principalmente
pelo celular, então o Claude deve agir com autonomia: decidir, executar, commitar e
reportar de forma curta, em português.

## Fonte da verdade
- `brief/brief.md` — quem é a marca, público, valores, tom. **Leia antes de qualquer criação.**
  Se algo essencial estiver vazio, pergunte uma única vez e siga com a melhor suposição.
- `cores/paleta.md` — paleta oficial (HEX, RGB, CMYK, uso). Cores saem só daqui.
- `tipografia/tipografia.md` — fontes oficiais e hierarquia.
- `logo/` — `fontes/` (SVG editável) e `exportados/` (PNG/SVG/PDF finais).
- `aplicacoes/` — mockups e peças (cartão, redes sociais, papelaria, fachada...).
- `referencias/` — moodboard e referências enviadas pelo dono.
- `aplicacoes/video/` — vinhetas finais (16:9, 9:16, 1:1), marca-d'água e crédito "PRODUÇÃO quirino".
- `clientes/<cliente>/` — `brief.md`, `identidade/` (arquivos do cliente) e `entregas/`.

## Logo aprovado
Conceito **A · Pixel** (`logo/fontes/A-*`). B e C estão em `logo/descartados/` e não devem ser usados.

## Trabalho para clientes
- Peças de cliente usam a identidade **do cliente**; leia `clientes/<cliente>/brief.md` antes.
  Se faltar logo/brasão oficial, peça o arquivo; não redesenhe marca de cliente.
- A Quirino entra só como assinatura discreta, se o brief permitir.
- Prefeitura: seguir as regras de comunicação pública do brief (CF art. 37 §1º, sem promoção
  pessoal). Conteúdo pessoal/político fica nas pastas do político, nunca na da Prefeitura.
- Nunca inventar números, obras, datas ou falas para relatórios e cards: usar só dados
  enviados pelo cliente e marcar o que falta com [PREENCHER].
- Entregas em `clientes/<cliente>/entregas/AAAA-MM-DD-nome/` com fonte editável + exportados.

## Como produzir um card
1. Copie `clientes/<cliente>/modelos/<modelo>.html` para a pasta da entrega (ajuste os caminhos `../` relativos).
2. Troque os textos entre colchetes e as fotos (`background-image` em `.foto`).
3. Renderize: `node ferramentas/render.js caminho/arquivo.html` → gera o `.png` ao lado.
4. Confira o PNG, faça commit e mande a imagem para o celular.
Fontes locais (licença OFL) em `ferramentas/fontes/`, declaradas em `ferramentas/fontes.css`.

## Regras
- Logo sempre em SVG vetorial como fonte; exportar PNG em 512, 1024 e 2048 px,
  versões colorida, preta, branca e símbolo isolado.
- Toda cor de texto precisa passar contraste WCAG AA (4.5:1).
- Fontes apenas gratuitas para uso comercial (Google Fonts ou licença SIL OFL).
- Ferramentas: conectores Canva e Magnific (geração de imagem, vetorização,
  mockups) e Artifacts para o manual da marca em página web.
- Não criar nada que imite marca de terceiros.
- Ao terminar uma entrega: commit descritivo, push e resumo curto
  com link/preview para o celular.
- Não abrir PR sem pedido explícito.

## Como finalizar um vídeo
`bash ferramentas/video.sh -c <cliente> -i bruto.mp4 -o clientes/<cliente>/entregas/AAAA-MM-DD-nome/video.mp4 [-f 9x16|16x9] [-l legenda.srt [-a]] [-d destaques.txt] [-z 2.5,8] [-m] [-q]`
- Ajusta para Reels (9x16, padrão) ou YouTube (16x9) com fundo desfocado, sem cortar o vídeo.
- `-l` queima legenda .srt (o Claude escreve o .srt a partir do texto/roteiro enviado pelo dono;
  não há transcrição automática de áudio neste ambiente).
- `-a` legenda animada estilo Reels (blocos curtos em maiúsculas, palavra da vez em caixa na cor do cliente).
  Padrão para Reels quando houver legenda.
- `-d` textos de destaque grandes e animados; arquivo com uma linha por texto: `0:03-0:06 OBRA ENTREGUE`.
- `-z` zoom de impacto nos segundos indicados (ex.: `-z 2.5,8`), para frases fortes ou viradas.
- Cores e fonte dos efeitos: `clientes/<cliente>/video.json` (tiradas do brief, contraste AA conferido).
  O `.ass` gerado fica ao lado do vídeo como fonte editável.
- `-m` logo do cliente no canto · `-q` crédito "PRODUÇÃO quirino" nos 4 s iniciais (só se o brief permitir).
- Vinheta final de 3 s com logo e @ do cliente (`-v 0` desliga). Vinhetas: `python3 ferramentas/vinhetas.py`.
- Depois de gerar, extrair 2 quadros com ffmpeg, conferir e mandar o vídeo pelo SendUserFile.

## Fotos
`clientes/<cliente>/fotos/` — ver `LEIA-ME.md` de cada cliente. Toda foto que o dono mandar no chat
deve ser salva ali com nome descritivo e commitada, para reuso.

## Fluxo pelo celular (padrão para todo pedido)
1. Identificar cliente e peça. Faltou dado essencial (data, preço, local)? Perguntar UMA vez, tudo junto.
2. Produzir a partir do modelo do cliente; conferir a imagem renderizada.
3. Salvar em `clientes/<cliente>/entregas/AAAA-MM-DD-nome/`: fonte (.html/.srt), final (.png/.mp4)
   e `legenda.txt` com a legenda pronta para o Instagram (texto + @ do cliente + 3–6 hashtags locais).
4. Commit + push, e enviar o arquivo final e a legenda no chat (SendUserFile) para o dono postar.
5. Trabalhar direto no branch padrão (`main`) quando não houver branch definido para a sessão.
