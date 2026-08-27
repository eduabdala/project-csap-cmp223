# Diagramas com identidade INF-UFRGS

Mesma pegada do Marp: você escreve markdown, o build gera a imagem já com a
paleta do tema (`marp-ppt/inf-ufrgs.css`).

## Como usar

1. Escreva blocos ` ```mermaid ` em qualquer `.md` dentro de `diagrams/src/`.
2. Nomeie cada bloco com um comentário na linha anterior:

   ```markdown
   <!-- diagrama: metodologia-hibrida -->

   ```mermaid
   flowchart LR
       A[Entrada] --> B{Decisão}
       B --> C[Saída]
       B:::destaque
   ```
   ```

3. Rode o build:

   ```bash
   npm run diagrams          # SVG, tema claro  -> diagrams/out/*.svg
   npm run diagrams:png      # PNG @3x, tema claro
   npm run diagrams:all      # SVG + PNG, claro + escuro
   ```

Sem o comentário de nome, o arquivo vira `<nome-do-fonte>-<n>`.

## Opções do build

```bash
node diagrams/build.mjs [arquivos...] [opções]

-f, --format   svg,png            formatos de saída (default: svg)
-v, --variant  claro,escuro       variante de tema (default: claro)
-s, --scale    3                  fator de escala do PNG
    --transparent                 fundo transparente
```

Variante `escuro` gera arquivos com sufixo `-escuro` (ex: `fluxo-kem-escuro.svg`),
para usar em slides `class: lead` ou `class: dark`.

## Identidade visual

Herdada do tema dos slides: preto `#111111`, vermelho `#D32F2F`, cinzas
`#555555`/`#9E9E9E`/`#E0E0E0`, fonte Inter, cantos retos.

Três classes de ênfase, aplicadas com `:::` no nó:

| classe     | efeito                                  |
|------------|-----------------------------------------|
| `destaque` | fundo preto, borda vermelha, texto branco |
| `alerta`   | fundo vermelho, texto branco             |
| `neutro`   | fundo claro, borda tracejada             |

Ajustes ficam em `diagrams/theme/`: os `.json` controlam as variáveis do Mermaid,
os `.css` fazem os overrides finos (o renderer de `sequenceDiagram` e `pie` usa
atributos inline, então precisa de CSS).

## Usando nos slides

```markdown
![w:900](../diagrams/out/metodologia-hibrida.svg)
```

`allowLocalFiles: true` já está no `marp.config.mjs`, então o caminho relativo funciona.

## Usando no artigo (LaTeX)

```latex
\includegraphics[width=\linewidth]{../diagrams/out/metodologia-hibrida.pdf}
```

Para PDF vetorial a partir do SVG:

```bash
npx svg2pdf diagrams/out/metodologia-hibrida.svg
```

Ou use os PNG @3x, que já saem com resolução suficiente para impressão.

## Tipos suportados

Todo o Mermaid 11: `flowchart`, `sequenceDiagram`, `classDiagram`, `stateDiagram`,
`erDiagram`, `gantt`, `pie`, `xychart`, `quadrantChart`, `timeline`, `mindmap`,
`block`, `sankey`, `packet`, entre outros. Veja `diagrams/src/exemplos.md`.
