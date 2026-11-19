# CMP223: Desempenho de criptografia pós-quântica no ATmega4809

Trabalho parcial de **CMP223 (Análise de Desempenho de Sistemas Computacionais)**,
INF/UFRGS, 2026. Autor: Eduardo Silva Abdala.

Este experimento mede latência pura de CPU, pico de pilha (SRAM) e tamanho de
Flash ROM de dois KEMs pós-quânticos (**Kyber-512** e **CTRU-Light**) e de um
baseline clássico (**ECDH secp256r1**, `micro-ecc`) no Arduino Nano Every
(**ATmega4809**, 8 bits single-core, 20 MHz, 6 KB de SRAM, 48 KB de Flash), com
janela física de medição no pino GPIO `PA0` (`D2`) amostrada por Analisador
Lógico de 8 canais / 24 MHz. O projeto é fatorial completo:
**algoritmo × implementação (`ref`, `asm`) × otimização (`-O3`, `-Os`) × operação (`keygen`, `encaps`, `decaps`)**.

Este pacote é uma cópia autocontida e enxuta do repositório. As pastas em
`data/experiments/` guardam **apenas os dados brutos** coletados na bancada
(`raw/telemetry_*.json`, `raw/la_*.csv`, `raw/console_*.log`, `bin/*.hex` e
`schedule.json`); os CSVs *tidy* são extraídos por `src/analysis/prepare.py` e
todas as análises estatísticas, tabelas LaTeX e figuras do artigo (TikZ `.tex`,
`.pdf` e `.png`) e dos slides são construídas pelo caderno Quarto em R
`src/analysis/analise.qmd` (com tema em `src/analysis/R/tema.R`).

## Metodologia

### Classificação da pesquisa

| Critério | Classificação | Por quê |
| :--- | :--- | :--- |
| Natureza | Aplicada | Busca uma resposta prática: qual KEM pós-quântico é viável num MCU de 8 bits. |
| Abordagem | Quantitativa | Mede variáveis numéricas (latência, pilha, Flash) e as analisa com estatística. |
| Objetivo | Explicativa, com parte descritiva | Descreve o desempenho de cada configuração e explica quanto cada fator contribui (η² da ANOVA). |
| Procedimento técnico | Experimental | O pesquisador manipula os fatores (algoritmo, implementação, otimização), controla as condições e mede o efeito. |
| Método científico | Hipotético-dedutivo | Parte de hipóteses (por exemplo, "o algoritmo domina a latência" ou "o assembly reduz o tempo") e as testa com Welch e ANOVA. |
| Desenho | Fatorial completo 3 × 2 × 2 × 3 com repetições (Jain) | Combina todos os níveis de todos os fatores. |
| Ambiente | Bancada, hardware real | É medição, não simulação nem modelagem analítica. |
| Coleta | Instrumentação | Latência por analisador lógico no pino `PA0`; pilha por marcação da memória (`0xAA`); Flash pelos `.hex`. |
| Análise | Estatística descritiva e inferencial | Média, IC 95%, Welch sobre log T, ANOVA tipo II e `emmeans`. |
| Recorte temporal | Transversal, com várias sessões | Foram 19 campanhas entre 04/11 e 13/11, sem acompanhamento ao longo do tempo como objetivo. |

Em resumo: é uma pesquisa aplicada, quantitativa e explicativa, de caráter experimental. Segue o método hipotético-dedutivo e um projeto fatorial completo, com medições em bancada num ATmega4809 e análise estatística inferencial.

### Etapas da metodologia

A metodologia segue a abordagem sistemática de avaliação de desempenho de Raj Jain (*The Art of Computer Systems Performance Analysis*, 1991): cap. 2 para as etapas, cap. 16 a 18 para o projeto fatorial e cap. 12 e 13 para a estatística.

| Etapa | No projeto |
| :--- | :--- |
| 1. Objetivo e sistema | Avaliar se o Kyber-512 e o CTRU-Light são viáveis num MCU de 8 bits, comparando com o ECDH. O sistema medido é o ATmega4809 (Arduino Nano Every). |
| 2. Serviços e resultados | KeyGen, Encaps, Decaps e MsgCrypt, cada um com resultado válido ou inválido. |
| 3. Métricas | Latência, pico de pilha e Flash ocupada. A energia está prevista. |
| 4. Parâmetros | Tudo o que afeta o desempenho: algoritmo, implementação, otimização, clock, tensão, temperatura, entrada. |
| 5. Fatores e níveis | Algoritmo (3), implementação `ref`/`asm` (2), otimização `-O3`/`-Os` (2), operação (3). Os demais parâmetros ficam fixos (20 MHz, 5 V). |
| 6. Técnica de avaliação | Medição em hardware real. |
| 7. Carga de trabalho | Rodadas K → E → D → M com intervalo fixo, repetidas *n* vezes por configuração. |
| 8. Planejamento | Fatorial completo com repetições (30, depois 150), ordem sorteada (`schedule.json`) e blocos por gravação de firmware (`--blocks`). |
| 9. Coleta | O firmware abre uma janela no `PA0`, o analisador lógico mede a largura do pulso, e a telemetria segue pela UART com a validação do KEM. Os dados brutos ficam versionados em `data/experiments/`. |
| 10. Análise e interpretação | Verificação das hipóteses (4-plots e testes de independência, estacionariedade e normalidade), descrição (média, IC 95%, mediana, CV), comparação (Welch sobre log T), modelo fatorial (ANOVA tipo II sobre log T com η²) e médias marginais (`emmeans`). |
| 11. Apresentação | Figuras, tabelas LaTeX e artigo gerados pelo caderno Quarto, com fluxo reprodutível (Nix, Snakemake). |

O método é cíclico: os resultados de uma rodada revisam as etapas anteriores. Os diagnósticos das baterias #17 a #19 mostraram três falhas de controle:
- a ordem planejada não foi seguida;
- CTRU-Light e ECDH usaram semente fixa;
- o clock do MCU variou sem controle.

Isso volta às etapas 4, 7 e 8: o clock e a temperatura passam a ser parâmetros registrados, a carga ganha aquecimento e sementes registradas, e o planejamento usa blocos sorteados. Depois disso vem uma nova campanha. Detalhes em `docs/diagnostico-4plots.md`.

## Executar tudo de uma vez (via `Snakemake` ou `Make`)

O pacote conta com um [`Snakefile`](Snakefile) declarativo (integrado ao `flake.nix`) e com um [`Makefile`](Makefile) na raiz para automatizar a limpeza e a reconstrução completa do DAG (`catálogo` → `prepare.py` → `analise.qmd` → `tabelas/figuras` → `slides`):

### Com Snakemake (dentro do `nix develop` ou ambiente com Snakemake)
```bash
snakemake -j1 clean        # Limpa CSVs processados, tabelas, figuras, slides e HTML do caderno
snakemake -n               # Dry-run: inspeciona o grafo de dependências (DAG) que será executado
snakemake -j1              # Executa todo o DAG a partir dos dados brutos (catálogo + prepare.py + analise.qmd + slides)
snakemake -j1 experiment   # Roda o EXPERIMENTO COMPLETO na bancada (MCU + LA) + atualiza catálogo, caderno e slides
snakemake -j1 firmware     # Compila os 12 firmwares bare-metal (.elf e .hex) do ATmega4809
```
*(Você também pode customizar parâmetros da coleta via CLI, ex.: `snakemake -j1 experiment --config port=/dev/ttyACM0 iterations=30 blocks=5 tag=minha_campanha`).*

**Campanha complementar sem otimização (`-O0`):** `snakemake -j1 experiment_O0` mede `-O0` e controles `-O3` das mesmas configurações, em blocos sorteados na mesma sessão. Kyber-512 `ref` e CTRU-Light `ref` não cabem nos 48 KB de Flash em `-O0`, e o ECDH `asm` não compila (o *assembly* do micro-ecc exige o registrador `Y`, reservado como *frame pointer* em `-O0`); essas configurações são registradas em `raw/build_failures.csv` e puladas (`--skip-unbuildable --drop-unpaired`). Um bloco que trave (ex.: estouro de pilha) descarta só a sua configuração (`--keep-going`). O resultado fica na seção 10 do caderno (`cmp_O0_vs_O3.csv`, `O0_viabilidade.csv`, figura `O0_vs_O3`).

**Aleatorização em blocos:** as `-n` repetições de cada uma das 12 configurações são divididas em `--blocks` blocos (padrão 5 no Snakefile, 1 na linha de comando) e a ordem de todos os blocos é sorteada com `--seed`. Cada bloco regrava a Flash (12 × 5 = 60 gravações por campanha); dentro do bloco a cadeia K→E→D→M é mantida. O `schedule.json` registra o plano e o status de cada bloco, e os arquivos brutos de cada bloco levam o sufixo `_bNN`.

### Com Make (atalho direto com ou sem Snakemake)
```bash
make clean        # Limpa todos os CSVs processados, tabelas, figuras, slides e HTML do caderno
make              # Reconstrói tudo do zero: catálogo + prepare.py + analise.qmd (figuras/tabelas) + slides PDF/HTML
make experiment   # Roda o experimento completo na bancada + reconstrói análise e slides
make clean-all    # (Opcional) Limpa tudo acima e também remove .venv e node_modules
```

### A) Reconstruir toda a análise, figuras, tabelas e slides manualmente (sem `make`)

Com **Nix (`nix develop`)** (a partir da raiz deste pacote):

```bash
nix develop --extra-experimental-features "nix-command flakes" -c bash -c "
  python3 src/analysis/catalog.py && \
  python3 src/analysis/prepare.py && \
  quarto render src/analysis/analise.qmd && \
  npm ci && npm run pdf
"
```

### B) Coletar campanha completa na bancada + atualizar catálogo, caderno e slides de uma vez

Com o Arduino Nano Every (`/dev/ttyACM0`) e o Analisador Lógico conectados no Linux:

```bash
nix develop --extra-experimental-features "nix-command flakes" -c bash -c "
  python3 src/analysis/run_experiment.py --mode bench --port /dev/ttyACM0 \
    --alg all --variants asm ref --opts O3 Os --clocks 20 -n 30 --seed 42 --blocks 5 \
    --tag bench_campanha_completa_la_nix && \
  python3 src/analysis/catalog.py && \
  python3 src/analysis/prepare.py && \
  quarto render src/analysis/analise.qmd && \
  npm run pdf
"
```

---

## Conteúdo do pacote

| Caminho | Conteúdo |
| :--- | :--- |
| `src/analysis/prepare.py` | Ingestão dos dados brutos das 17 campanhas de bancada para bases *tidy* em `results/processed/` |
| `src/analysis/analise.qmd` | Caderno Quarto em R: analisa o histórico e a campanha com Analisador Lógico, roda estatística descritiva, IC 95%, Welch, ANOVA tipo II (`car`) e `emmeans`, e gera todas as tabelas e figuras (`results/` e `slides/figures/`) |
| `src/analysis/R/tema.R` | Tema visual `ggplot2` e exportação simultânea em TikZ (`.tex` com fonte Linux Libertine do `acmart`), `.pdf`, `.png` e versão de slide |
| `src/analysis/run_experiment.py` | Executor do experimento: compila, grava via UPDI e coleta na bancada |
| `src/analysis/catalog.py` | Audita `data/experiments/` pela presença de telemetria bruta (`bench`) e gera `catalog.csv` |
| `src/analysis/design.py`, `config.yaml` | Matriz de fatores (DOE, `pyDOE3`) |
| `src/analysis/plot_histogram.py` | Histogramas empíricos auxiliares chamados pelo executor |
| `src/analysis/parse.py` | Integrador de energia ($E = \int V \cdot i\,dt$) preparado para a etapa final com resistor *shunt* |
| `src/scripts/trigger.py` | Disparo serial, decodificador de bordas do Analisador Lógico (`sigrok-cli`) e telemetria |
| `src/scripts/vendor-pqc.sh` | Baixa as fontes PQC nos commits usados (já incluídas em `src/firmware/pqc/`) |
| `src/firmware/atmega4809/` | Firmware bare-metal (`main.c`, `Makefile`) e o DFP Microchip 3.3.279 |
| `src/firmware/common/` | Interface KEM comum (`kem.h`) e adaptadores por algoritmo |
| `src/firmware/pqc/` | Fontes em C e Assembly AVR (`kyber512`, `ctru-light`, `ecdh`), cada uma com `VENDOR.txt` |
| `data/experiments/` | Dados brutos das **17 campanhas reais de bancada** (10.124 observações no total) e `catalog.csv` |
| `slides/` | Apresentações em Marp (`01-proposta.md`, `02-parcial.md`), temas UFRGS e figuras |
| `results/` | Saídas geradas pelo caderno e pelo Marp (`processed/`, `figures/`, `tables/`, `slides/`) |
| `flake.nix`, `flake.lock` | Ambiente declarativo Nix: `avr-gcc 13.2.0`, `avrdude`, `sigrok-cli`, `pyDOE3`, R (`tidyverse`, `ggdist`, `car`, `emmeans`, `tikzDevice`), Quarto e TeX Live |

### Onde ficam os dados brutos e os resultados gerados

| Pasta | Gerado por | Conteúdo |
| :--- | :--- | :--- |
| `data/experiments/exp_<data>_<tag>_<id>/` | `run_experiment.py` | Apenas artefatos brutos: `raw/telemetry_*.json`, `raw/la_*.csv` (capturas 24 MHz), `raw/console_*.log`, `bin/*.hex` e `schedule.json` |
| `data/experiments/catalog.csv` | `catalog.py` | Índice das 17 campanhas de bancada (`source = bench`) |
| `results/processed/` | `prepare.py` + `analise.qmd` | CSVs tratados: `bench_tidy.csv`, `bench_history_tidy.csv`, `campaigns_history.csv`, `la_vs_uart_overhead.csv`, `summary_bench.csv`, `flash_sizes.csv`, `anova_latency.csv`, `emmeans_ref_vs_asm.csv`, `cmp_*.csv` |
| `results/figures/` | `analise.qmd` | `historico_todos_experimentos`, `oscillogram`, `latency`, `flash`, `tradeoff`, `bimodality`, `residuals`, `drift_kyber_asm` (`.tex` TikZ, `.pdf` e `.png`) |
| `slides/figures/` | `analise.qmd` | `bancada.jpg` (foto estática) + figuras geradas pelo caderno (`slide_bancada_setup.png`, `slide_oscillogram.png`, `slide_tradeoff.png`, `slide_flash.png`, `slide_bimodality.png`, `historico_todos_experimentos.png`) |
| `results/tables/` | `analise.qmd` | `results.tex` e `anova.tex` (tabelas LaTeX prontas para o artigo) |
| `results/slides/` | `npm run pdf` | PDFs renderizados das apresentações (`01-proposta.pdf`, `02-parcial.pdf`) |

---

## Passo a passo individual

### 1. Rodar apenas o caderno de análise (Python + R/Quarto)

```bash
nix develop
python3 src/analysis/prepare.py
quarto render src/analysis/analise.qmd
```

### 2. Gerar apenas os slides (PDF / PPTX / HTML)

```bash
npm ci
npm run pdf     # -> results/slides/*.pdf
npm run pptx    # -> results/slides/*.pptx (opcional)
npm run html    # -> results/slides/*.html (opcional)
```

### 3. Coletar novos dados na bancada

```bash
nix develop
python3 src/analysis/run_experiment.py --mode bench --port /dev/ttyACM0 \
    --alg all --variants asm ref --opts O3 Os --clocks 20 -n 30 --seed 42 --blocks 5 \
    --tag bench_full_pqc_campaign
python3 src/analysis/catalog.py
```

---

## Notas técnicas e Uso de Ferramentas de IA (Req. 5.3)

- **Isolamento da janela física (`PA0`):** o analisador lógico de 24 MHz (configurado a 100 kS/s via `sigrok-cli`, resolução de $10\,\mu\text{s}$) mede a largura exata do pulso no pino `PA0` (`D2`) com interrupções mascaradas (`cli()`/`sei()`), eliminando os 22 a 31 ms de atraso da serialização UART.
- **Adequação aos 48 KB de Flash e assistência de IA:** a implementação original em C de referência do Kyber-512 ocupava ~79 KB de Flash e o CTRU-Light `ref -O3` excedia os 48 KB por 148 bytes no `avr-gcc 13.2.0`. Utilizei o Claude como assistente de *pair programming* para migrar tabelas constantes para `PROGMEM`, unificar buffers intermediários, ajustar as flags de *linker relaxation* (`-mrelax -mcall-prologues`) e automatizar a decodificação dos pulsos do `sigrok-cli`. Toda a montagem física da bancada, execução nas placas e análise estatística foram feitas e conferidas por mim.

## Fontes de terceiros

| Fonte | Uso | Commit / Versão |
| :--- | :--- | :--- |
| [CTRU-Light-and-PQC-on-AVR](https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR) (MIT) | Kyber-512 e CTRU-Light, `ref` e `asm` | `fb07b9573fcdb0f4f662ad6594191fc09597907a` |
| [micro-ecc](https://github.com/kmackay/micro-ecc) (BSD-2) | ECDH secp256r1, `ref` e `asm` | `541b3a78026420a3e369c4c9281c396b5e531113` |
| Microchip ATmega DFP 3.3.279 (Apache-2.0) | Headers, startup e specs do ATmega4809 | `src/firmware/atmega4809/.dfp/Microchip.ATmega_DFP.pdsc` |
