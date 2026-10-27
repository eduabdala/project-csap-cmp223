# CMP223 — Avaliação de Desempenho de Criptografia Pós-Quântica em Sistemas Embarcados

Trabalho final da disciplina **CMP223 — Análise de Desempenho de Sistemas
Computacionais** (INF/UFRGS). O projeto avalia a aplicabilidade de algoritmos de
criptografia pós-quântica (PQC) em sistemas embarcados restritos, usando como
SUT a placa Arduino Nano Every (microcontrolador ATmega4809, megaAVR 0-series).

Métricas analisadas: consumo energético por operação (keygen/encap/decap), uso
de stack, tempo de execução, tamanho dos binários e margem operacional do
sistema.

## Estrutura do repositório

| Diretório / arquivo | Conteúdo |
|---------------------|----------|
| `src/`              | Código-fonte: firmware, ports PQC, instrumentação e análise |
| `artigo/`           | Artigo em LaTeX (`artigo/main.tex`) |
| `slides/`           | Apresentações em [Marp](https://marp.app/) (proposta, parcial, final) |
| `diagrams/`         | Diagramas Mermaid com identidade INF-UFRGS (fonte e build) |
| `docs/`             | Documentação: planejamento (`plan.md`), roadmap, guia de execução (`running-guide.md`), referências e decisões |
| `.github/workflows/`| CI: build dos slides (PDF) e do artigo (LaTeX) |

## Como gerar os entregáveis

Pré-requisitos: Node.js 20+ e, para o artigo, uma distribuição LaTeX
(`latexmk`).

```bash
npm ci                 # instala as dependências (Marp, Mermaid CLI)

npm run pdf            # slides  -> dist/slides/*.pdf
npm run pptx           # slides  -> dist/slides/*.pptx
npm run html           # slides  -> dist/slides/*.html
npm run watch          # slides em PDF com rebuild automático

npm run diagrams       # diagramas SVG (tema claro)  -> diagrams/out/
npm run diagrams:png   # diagramas PNG @3x
npm run diagrams:all   # SVG + PNG, temas claro e escuro
```

Artigo:

```bash
cd artigo && latexmk -pdf main.tex
```

## Integração contínua

O workflow em `.github/workflows/build.yml` gera os PDFs dos slides a cada push
na `main`, compila o artigo quando existir `artigo/*.tex`, e publica um release
com todos os entregáveis ao criar uma tag `v*`.

## Autor

Eduardo Silva Abdala — INF/UFRGS, 2026.
