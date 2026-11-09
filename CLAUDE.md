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
- Ao terminar uma entrega: commit descritivo, push no branch de trabalho e resumo curto
  com link/preview para o celular.
- Não abrir PR sem pedido explícito.
