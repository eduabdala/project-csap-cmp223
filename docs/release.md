# Release: repositório de experimento (plug and play)

Este repositório é o **laboratório**: aqui o experimento é desenvolvido,
validado e ajustado. O resultado entregável vai para um **segundo repositório**,
curado e reprodutível, que não é editado à mão.

## Modelo

```
project-csap-cmp223 (este, laboratório)  ──export.py──▶  cmp223-pqc-avr (release)
  tudo: rascunhos, specs, simulações,                   só o que é auditável e
  pastas vazias, scripts antigos                         roda num clone limpo
```

- **Fluxo em uma direção só.** Mudanças são feitas aqui e exportadas. Commit
  direto no repo de release fica proibido; se precisar corrigir algo, corrige
  aqui e exporta de novo.
- **Mesma estrutura de pastas** (`src/`, `data/experiments/`, `artigo/`,
  `slides/`). Nenhum caminho é reescrito, então o que roda aqui roda lá.
- **Rastreável.** Cada export grava um `PROVENANCE` com o commit de origem, e
  cada entrega (parcial, final) vira uma tag no repo de release.
- **Pronto de fato.** O CI do repo de release parte de um clone limpo e precisa
  reexecutar o caderno e compilar artigo e slides. Se falhar, o export não vale.

Alternativas descartadas:
- **Submódulo:** inverte a dependência e obriga a desenvolver dentro dele.
- **`git subtree split`:** só funciona com o conteúdo numa única pasta; aqui
  ele está espalhado.
- **Cópia manual:** desalinha os dois repos na segunda atualização.

## O que entra

O manifesto (`release/manifest.txt`) é a fonte da verdade. Conteúdo previsto:

| Caminho | Observação |
| :--- | :--- |
| `src/firmware/atmega4809/`, `src/firmware/common/` | firmware do SUT |
| `src/firmware/rp2040/` | só se for usado nos resultados; hoje não é |
| `src/scripts/trigger.py`, `src/scripts/vendor-pqc.sh` | coleta e fontes PQC |
| `src/analysis/design.py`, `config.yaml` | projeto experimental (DOE) |
| `src/analysis/run_experiment.py`, `catalog.py`, `parse.py`, `plot_histogram.py` | execução, proveniência, integrador de energia |
| `src/analysis/analise.ipynb`, `requirements-notebook.txt` | análise (programação literal) |
| `data/experiments/<pastas bench>/`, `catalog.csv` | **só** as pastas com `source = bench` no `catalog.csv` |
| `artigo/` (`main.tex`, `acmart.cls` v2.14, `.bst`, `.bib`, `figures/`, `tables/`) | relatório (template ACM) |
| `slides/01-proposta.md`, `02-parcial.md`, `03-final.md`, temas, `logo_inf.png` | apresentações |
| `docs/Requisitos_projeto.pdf`, `docs/references.md` | referência |
| `flake.nix`, `flake.lock`, `package.json`, `package-lock.json`, `marp.config.mjs` | ambiente |
| `.github/workflows/` | CI do release |
| `README.md` | escrito para o release (ver abaixo) |

## O que fica só aqui

- `.kiro/`, `.kyanite/`, `.vscode/`
- `docs/draft.md`, `docs/plan.md`, `docs/roadmap.md`, `docs/experiment-0.md`
- `slides/00-teste.md`, `slides/apresentação.md`, `slides/layout-test.css`
- `diagrams/src/exemplos.md`
- Scripts antigos ou em esqueleto: `experiment_zero.py`, `experiment_one.py`,
  `pipeline.py`, `process_partial_experiment.py`, `Snakefile`, `collect.py`,
  `aggregate.py`, `figures.py`, `plot_la.py`
- Pastas de experimento `sim`, `empty` e `bench_legacy`

O `Snakefile` e o `collect.py` só entram no release quando deixarem de ser
esqueleto. O fluxo que funciona hoje é
`run_experiment.py` → `catalog.py` → `analise.ipynb`.

## Pendências antes do primeiro export

| # | Pendência | Onde | Situação |
| :--- | :--- | :--- | :--- |
| 1 | Hash do pyDOE3 zerado (`sha256-000…`): `nix develop` falha | `flake.nix` | a fazer |
| 2 | Faltam jupyter, statsmodels, seaborn no ambiente Nix | `flake.nix` | a fazer |
| 3 | Fontes PQC sem versão fixa: o padrão é `main`/`master` | `vendor-pqc.sh` | a fazer |
| 4 | Experimentos não gravam o commit do firmware | `run_experiment.py` | a fazer |
| 5 | Ordem aleatória do `schedule.json` não é aplicada na bancada | `run_experiment.py` | documentado como limitação |
| 6 | README do release (reproduzir do zero ao PDF) | `release/README.md` | a fazer |
| 7 | Versão do toolchain AVR (avr-gcc, binutils, DFP) desconhecida; o firmware não recompila igual fora da máquina do autor | `flake.nix`, `run_experiment.py` | **bloqueante**, ver `docs/analise-lacunas.md` §1.7 |

Para o item 3, os commits em uso hoje (lidos de `src/firmware/pqc/*/VENDOR.txt`):

| Fonte | Commit |
| :--- | :--- |
| CTRU-Light-and-PQC-on-AVR (Kyber-512 e CTRU-Light) | `fb07b9573fcdb0f4f662ad6594191fc09597907a` |
| micro-ecc (ECDH) | `541b3a78026420a3e369c4c9281c396b5e531113` |

Esses valores viram o padrão de `CHES_REF` e `UECC_REF` no `vendor-pqc.sh`.

## Rastreabilidade

- **`PROVENANCE`** (na raiz do release), gerado a cada export:
  commit de origem, branch, data, se havia mudanças não commitadas (o export
  recusa rodar com a árvore suja) e a lista de pastas de experimento incluídas.
- **Por experimento:** a partir da pendência 4, `schedule.json` e `report.md`
  passam a gravar `git_commit` e `git_dirty`. As pastas antigas não têm esse
  campo; o `PROVENANCE` registra o commit em que elas foram exportadas.
- **Por fonte PQC:** os `VENDOR.txt` de cada `pqc/<alg>/<variante>/`.
- **Tags no release:** `parcial`, `final` (e `final-v2`, se houver reentrega).

## `release/export.py`

```
python release/export.py --dest ../cmp223-pqc-avr [--dry-run]
```

1. Recusa rodar se a árvore de trabalho tiver mudanças não commitadas.
2. Roda `catalog.py` e lê o `catalog.csv` para escolher as pastas `bench`.
3. Apaga o conteúdo do destino (menos `.git/`) e copia o que está no manifesto.
4. Copia `release/README.md` para a raiz do destino.
5. Grava `PROVENANCE`.
6. `--dry-run` só lista o que seria copiado.

O commit e a tag no repo de release são feitos à mão, depois de revisar o diff.

## README do release (conteúdo mínimo)

1. Pergunta e objeto de estudo, em um parágrafo.
2. **Reproduzir sem hardware** (análise, artigo e slides):
   ```
   py -3.13 -m venv .venv
   .venv\Scripts\python -m pip install -r src/analysis/requirements-notebook.txt
   .venv\Scripts\python -m jupyter nbconvert --to notebook --execute --inplace src/analysis/analise.ipynb
   cd artigo; pdflatex main; bibtex main; pdflatex main; pdflatex main
   npm ci; npm run pdf
   ```
   (equivalente com `nix develop` quando as pendências 1 e 2 estiverem
   resolvidas)
3. **Coletar na bancada** (precisa de Arduino Nano Every na porta serial):
   `vendor-pqc.sh all`, depois `run_experiment.py --mode bench --port <porta>`,
   depois `catalog.py` e o caderno.
4. Mapa dos critérios da disciplina (DOE, REPRO, LIT, …) para os arquivos.
5. Uso de IA (aponta para a seção do artigo).

## CI do release

Um job a partir de clone limpo:
1. Instala Python (`requirements-notebook.txt`), TeX e Node.
2. Executa o caderno e **falha se** `artigo/tables/` ou `artigo/figures/`
   mudarem em relação ao commit (garante que os resultados versionados saem
   dos dados versionados).
3. Compila o artigo e os slides e publica os PDFs como artefato.

A compilação do firmware não entra no CI, porque depende de baixar as fontes
PQC (`vendor-pqc.sh`) e do toolchain AVR. Fica documentada no README.

## Ordem de execução

1. Resolver as pendências 1 a 4 e 6 aqui.
2. Escrever `release/manifest.txt` e `release/export.py`.
3. `export.py --dry-run` e revisar a lista.
4. Exportar para uma pasta local, rodar o fluxo "sem hardware" do README nela.
5. Criar o repo no GitHub, fazer o primeiro push e conferir o CI.
6. Tag `parcial`.
