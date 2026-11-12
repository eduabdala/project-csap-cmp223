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
`schedule.json`); todos os CSVs processados, tabelas LaTeX e figuras do artigo
e dos slides são construídos diretamente pelo caderno `src/analysis/analise.ipynb`.

## Executar tudo de uma vez (via `Snakemake` ou `Make`)

O pacote conta com um [`Snakefile`](Snakefile) declarativo (integrado ao `flake.nix`) e com um [`Makefile`](Makefile) na raiz para automatizar a limpeza e a reconstrução completa do DAG (`catálogo` → `analise.ipynb` → `tabelas/figuras` → `slides`):

### Com Snakemake (dentro do `nix develop` ou ambiente com Snakemake)
```bash
snakemake -j1 clean        # Limpa CSVs processados, tabelas, figuras, slides e outputs do notebook
snakemake -n               # Dry-run: inspeciona o grafo de dependências (DAG) que será executado
snakemake -j1              # Executa todo o DAG a partir dos dados brutos (catálogo + notebook + figuras/tabelas + slides)
snakemake -j1 experiment   # Roda o EXPERIMENTO COMPLETO na bancada (MCU + LA) + atualiza catálogo, notebook e slides
snakemake -j1 firmware     # Compila os 12 firmwares bare-metal (.elf e .hex) do ATmega4809
```
*(Você também pode customizar parâmetros da coleta via CLI, ex.: `snakemake -j1 experiment --config port=/dev/ttyACM0 iterations=30 tag=minha_campanha`).*

### Com Make (atalho direto com ou sem Snakemake)
```bash
make clean        # Limpa todos os CSVs processados, tabelas, figuras, slides e outputs do notebook
make              # Reconstrói tudo do zero: catálogo + analise.ipynb (figuras/tabelas) + slides PDF/HTML
make experiment   # Roda o experimento completo na bancada + reconstrói análise e slides
make clean-all    # (Opcional) Limpa tudo acima e também remove .venv e node_modules
```

### A) Reconstruir toda a análise, figuras, tabelas e slides manualmente (sem `make`)

No **Linux / Nix / WSL** (a partir da raiz deste pacote):

```bash
export LD_LIBRARY_PATH="$(dirname $(find /nix/store -name 'libstdc++.so.6' 2>/dev/null | head -n 1)):$(dirname $(find /nix/store -name 'libz.so.1' 2>/dev/null | head -n 1)):$LD_LIBRARY_PATH"
python3 -m venv .venv && \
  .venv/bin/python -m pip install -r src/analysis/requirements-notebook.txt && \
  .venv/bin/python src/analysis/catalog.py && \
  (cd src/analysis && ../../.venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace analise.ipynb) && \
  npm ci && npm run pdf
```

No **Windows (PowerShell)** (a partir da raiz deste pacote):

```powershell
py -3.13 -m venv .venv; `
  .venv\Scripts\python -m pip install -r src/analysis/requirements-notebook.txt; `
  .venv\Scripts\python src/analysis/catalog.py; `
  Push-Location src/analysis; ..\..\.venv\Scripts\python -m jupyter nbconvert --to notebook --execute --inplace analise.ipynb; Pop-Location; `
  npm ci; npm run pdf
```

### B) Coletar campanha completa na bancada + atualizar catálogo, caderno e slides de uma vez

Com o Arduino Nano Every (`/dev/ttyACM0`) e o Analisador Lógico conectados no Linux:

```bash
nix develop --extra-experimental-features "nix-command flakes" -c bash -c "
  python3 src/analysis/run_experiment.py --mode bench --port /dev/ttyACM0 \
    --alg all --variants asm ref --opts O3 Os --clocks 20 -n 30 --seed 42 \
    --tag bench_campanha_completa_la_nix && \
  python3 src/analysis/catalog.py && \
  (cd src/analysis && jupyter nbconvert --to notebook --execute --inplace analise.ipynb) && \
  npm run pdf
"
```

---

## Conteúdo do pacote

| Caminho | Conteúdo |
| :--- | :--- |
| `src/analysis/analise.ipynb` | Caderno principal: lê os dados brutos das 17 campanhas de bancada, analisa o histórico e a campanha com Analisador Lógico, roda estatística descritiva, IC 95%, Welch e ANOVA, e gera todas as tabelas e figuras (`results/` e `slides/figures/`) |
| `src/analysis/requirements-notebook.txt` | Dependências Python com versões fixas |
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
| `flake.nix`, `flake.lock` | Ambiente declarativo Nix: `avr-gcc 13.2.0`, `avrdude`, `sigrok-cli` e `pyDOE3` |

### Onde ficam os dados brutos e os resultados gerados

| Pasta | Gerado por | Conteúdo |
| :--- | :--- | :--- |
| `data/experiments/exp_<data>_<tag>_<id>/` | `run_experiment.py` | Apenas artefatos brutos: `raw/telemetry_*.json`, `raw/la_*.csv` (capturas 24 MHz), `raw/console_*.log`, `bin/*.hex` e `schedule.json` |
| `data/experiments/catalog.csv` | `catalog.py` | Índice das 17 campanhas de bancada (`source = bench`) |
| `results/processed/` | `analise.ipynb` | CSVs tratados: `bench_tidy.csv`, `bench_history_tidy.csv`, `campaigns_history.csv`, `la_vs_uart_overhead.csv`, `summary_bench.csv`, `summary_history_serial.csv`, `flash_sizes.csv`, `anova_latency.csv`, `cmp_*.csv` |
| `results/figures/` | `analise.ipynb` | `historico_todos_experimentos`, `oscillogram`, `latency`, `flash`, `tradeoff`, `bimodality`, `residuals`, `drift_kyber_asm` (PDF e PNG) |
| `slides/figures/` | `analise.ipynb` | `bancada.jpg` (foto estática) + figuras geradas pelo caderno (`slide_bancada_setup.png`, `slide_tradeoff.png`, `slide_flash.png`, `slide_bimodality.png`, `historico_todos_experimentos.png`) |
| `results/tables/` | `analise.ipynb` | `results.tex` e `anova.tex` (tabelas LaTeX prontas para o artigo) |
| `results/slides/` | `npm run pdf` | PDFs renderizados das apresentações (`01-proposta.pdf`, `02-parcial.pdf`) |

---

## Passo a passo individual

### 1. Rodar apenas o caderno de análise

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r src/analysis/requirements-notebook.txt
cd src/analysis
../../.venv/bin/python -m jupyter nbconvert --to notebook --execute --inplace analise.ipynb
cd ../..
```

Para abrir de forma interativa, execute `jupyter lab src/analysis/analise.ipynb`.

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
    --alg all --variants asm ref --opts O3 Os --clocks 20 -n 30 --seed 42 \
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
