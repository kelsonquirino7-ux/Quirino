# Como pedir ao Claude (atalhos pelo celular)

Regra de ouro: **cliente + peça + dados + foto/vídeo**, numa mensagem só.
O resto (cores, fontes, modelo, legenda, hashtags, commit) o Claude já sabe.

## Apelidos de cliente
| Escreva | Cliente |
|---|---|
| `prefeitura` | Prefeitura de Santanópolis |
| `vitor` | Prefeito Vitor (pessoal/político) |
| `deni` | Deni de Vitor |
| `itamar` | Itamar Supermercado |

## Modelos prontos (copie, troque o que está em [ ])

**Card de ofertas (itamar)**
```
itamar · card ofertas · válido [data]
- [produto] [peso] R$ [preço]
- [produto] [peso] R$ [preço]
```

**Comunicado (prefeitura)**
```
prefeitura · comunicado
título: [texto curto]
texto: [o que, quando, onde]
```
(+ foto anexada, se tiver)

**Mensagem (vitor / deni)**
```
vitor · card mensagem · [data comemorativa ou tema]
frase: [texto] (ou "crie a frase")
```

**Vídeo**
```
[cliente] · vídeo [reels|youtube] · legenda: [sim/não]
texto falado: [cole o roteiro, se quiser legenda]
```
(+ vídeo anexado)

**Relatório (prefeitura)**
```
prefeitura · capa relatório · [título] · [período]
dados: [cole os números]
```

## Dicas rápidas
- **Uma mensagem, tudo junto.** Evita ida e volta.
- **Números, datas e preços sempre vêm de você.** O Claude não inventa; o que faltar sai como [PREENCHER].
- **Foto/vídeo: anexe na mesma mensagem.** Fica salva em `clientes/<cliente>/fotos/` para reuso.
- **Ajustes curtos funcionam:** "título maior", "troca a foto", "fundo mais escuro", "versão story".
- **Vários de uma vez:** "itamar · 3 cards ofertas: carnes / hortifruti / bebidas" + lista.
- **Quer só ver antes?** Escreva `rascunho` e ele não faz commit.
- **Pressa?** Comece com `urgente` — vem só o arquivo, sem explicação.
