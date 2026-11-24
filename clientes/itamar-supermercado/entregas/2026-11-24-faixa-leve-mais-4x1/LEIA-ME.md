# Faixa 4 x 1 m — Leve mais, pague menos (Itamar)
- `faixa-4x1.pdf` — arquivo para a gráfica (proporção 4:1, imprimir em 4 m x 1 m).
- `faixa-4x1.png` — 8000 x 2000 px (alternativa ao PDF).
- `faixa-4x1.html` — fonte editável; `node exportar.js` regera tudo.
- Margem de segurança de 6 cm para ilhós/bainha.
- Selo 3D gerado no Magnific (121 créditos, junto com um carrinho que saiu). Carrinho final: foto do dono, recortada no Adobe sem custo, salvos em `identidade/campanhas/` e `fotos/elementos/` para reuso.

## v2 (arte enviada pelo dono)
- `faixa-4x1-v2.pdf` / `.png` / `-preview.jpg` — arte do dono com textos menores e selo corrigido ("PAGUE MENOS").
- Fundo: `arte-v2-original-dono.jpg` com selo e textos apagados por `limpar-textos-v2.py` → `arte-v2-fundo-sem-textos.png`.
- Regerar: `node exportar.js faixa-4x1-v2`. A arte original tem 2576 px de largura (ampliada para impressão).
