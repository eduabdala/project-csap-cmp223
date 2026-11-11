# CMP223: Desempenho de criptografia pós-quântica no ATmega4809

Trabalho final de **CMP223 (Análise de Desempenho de Sistemas Computacionais)**,
INF/UFRGS, 2026. Autor: Eduardo Silva Abdala.

Este experimento mede latência, pico de pilha e tamanho de flash de dois KEMs
pós-quânticos (Kyber-512 e CTRU-Light) e de um baseline clássico (ECDH,
micro-ecc) no Arduino Nano Every (ATmega4809, 20 MHz, 6 KB de SRAM, 48 KB de
flash). O projeto é fatorial: **algoritmo × implementação (ref, asm) ×
otimização (-O3, -Os) × operação (keygen, encaps, decaps)**.

Este pacote é uma cópia autocontida do repositório de desenvolvimento. Ele
contém só o necessário para refazer a análise a partir dos dados coletados, para
coletar dados novos na bancada e para gerar os slides.

## Conteúdo

| Caminho | Conteúdo |
| :--- | :--- |
| `src/analysis/analise.ipynb` | Análise completa: leitura dos dados, estatística descritiva, IC 95%, ANOVA, figuras e tabelas |
| `src/analysis/requirements-notebook.txt` | Dependências Python com versões fixas |
| `src/analysis/run_experiment.py` | Executor do experimento: compila, grava, coleta e cria a pasta do experimento |
| `src/analysis/catalog.py` | Classifica as pastas de experimento pela origem dos dados (`bench`, `sim`, ...) |
| `src/analysis/design.py`, `config.yaml` | Matriz de fatores (DOE, pyDOE3) |
| `src/analysis/plot_histogram.py` | Histogramas por campanha (chamado pelo executor) |
| `src/analysis/parse.py` | Integrador de energia (E = ∫V·i dt) para capturas do osciloscópio; ainda não usado nos resultados, porque a energia não foi medida |
| `src/scripts/trigger.py` | Disparo serial e telemetria da placa |
| `src/scripts/vendor-pqc.sh` | Baixa as fontes PQC nos commits usados (já incluídas em `src/firmware/pqc/`) |
| `src/firmware/atmega4809/` | Firmware de medição (`main.c`, `Makefile`) e o subconjunto do DFP Microchip 3.3.279 usado na compilação |
| `src/firmware/common/` | Interface KEM comum e adaptadores por algoritmo |
| `src/firmware/pqc/` | Fontes de terceiros; cada pasta tem um `VENDOR.txt` com repositório e commit |
| `data/experiments/` | Dados brutos das 10 campanhas de bancada usadas nos resultados e `catalog.csv` |
| `slides/` | Apresentações em Marp: `01-proposta.md`, `02-parcial.md`, temas e figuras |
| `results/` | Saídas geradas (ver abaixo) |
| `package.json`, `package-lock.json`, `marp.config.mjs` | Ambiente para gerar os slides |
| `flake.nix`, `flake.lock` | Ambiente Nix: toolchain AVR, avrdude, sigrok-cli |

### Onde ficam os resultados

| Pasta | Gerado por | Conteúdo |
| :--- | :--- | :--- |
| `data/experiments/exp_<data>_<tag>_<id>/` | `run_experiment.py` | Uma pasta por campanha: `raw/` (telemetria JSON, logs UART, `runs.csv`), `bin/` (`.hex` gravados), `figures/`, `schedule.json`, `summary.csv`, `report.md` |
| `data/experiments/catalog.csv` | `catalog.py` | Índice das campanhas. O caderno usa só as linhas com `source = bench` |
| `results/processed/` | caderno | CSVs tratados: `bench_tidy.csv`, `summary_bench.csv`, `flash_sizes.csv`, `anova_latency.csv`, comparações `cmp_*.csv` |
| `results/figures/` | caderno | `latency`, `flash`, `tradeoff`, `residuals`, `drift_kyber_asm` (PDF e PNG) |
| `results/tables/` | caderno | `results.tex` e `anova.tex` (tabelas LaTeX do artigo) |
| `results/slides/` | `npm run pdf` | PDFs dos slides |

## 1. Reproduzir a análise (sem hardware)

Requisitos: Python 3.13 (64 bits). Os comandos abaixo são para o PowerShell no
Windows e partem da raiz deste pacote.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r src/analysis/requirements-notebook.txt
cd src/analysis
..\..\.venv\Scripts\python -m jupyter nbconvert --to notebook --execute --inplace analise.ipynb
cd ../..
```

No Linux ou macOS, use `python3.13 -m venv .venv` e `.venv/bin/python`.

O caderno precisa rodar a partir de `src/analysis/`. Ele procura a raiz do
pacote subindo pastas até achar `data/experiments/` e grava tudo em `results/`.
Para explorar a análise de forma interativa, use `jupyter lab` e abra
`src/analysis/analise.ipynb`.

**Conferência:** `results/tables/results.tex` e `results/tables/anova.tex`
devem sair iguais às tabelas do artigo. Os números são determinísticos, porque
saem só dos arquivos em `data/experiments/`. As figuras usam a fonte Libertinus
Serif quando existe uma distribuição TeX instalada (o caderno a localiza com
`kpsewhich`). Sem ela, as figuras saem em DejaVu Serif, com os mesmos dados.

## 2. Gerar os slides

Requisitos: Node.js 20 ou mais recente. A conversão para PDF usa o Chrome ou o
Edge instalado na máquina.

```powershell
npm ci
npm run pdf     # -> results/slides/*.pdf
npm run pptx    # -> results/slides/*.pptx (opcional)
```

Os temas `inf-ufrgs` e `inf-ufrgs-claro` carregam a fonte Inter do Google
Fonts. Sem internet, o Marp usa uma fonte substituta.

## 3. Coletar dados novos na bancada

Requisitos:
- Arduino Nano Every ligado por USB.
- Linux ou WSL, porque o `trigger.py` usa `termios`/`fcntl`.
- `avr-gcc`, `avrdude` e `make`. Com Nix, `nix develop` traz tudo isso.
- `pyserial` e `pyyaml` no Python.
- Opcional: analisador lógico Saleae compatível com `sigrok-cli`, para usar com `--use-la`.

```bash
nix develop                                   # ou instale as ferramentas à mão
# (opcional) refazer as fontes PQC nos mesmos commits:
# bash src/scripts/vendor-pqc.sh all
python3 src/analysis/run_experiment.py --mode bench --port /dev/ttyACM0 \
    --alg all --variants asm ref --opts O3 Os --clocks 20 -n 30 --seed 42 \
    --tag bench_full_pqc_campaign
python3 src/analysis/catalog.py               # atualiza data/experiments/catalog.csv
```

Depois rode o caderno (seção 1). Ele passa a incluir a nova pasta, porque ela é
classificada como `bench`.

Para cada combinação, o `run_experiment.py`:
1. compila o firmware (`make -C src/firmware/atmega4809`);
2. copia o `.hex` para `bin/`;
3. grava a placa por UPDI;
4. dispara as repetições pelo `trigger.py` e salva telemetria e logs em `raw/`.

O modo `--mode sim` gera dados sintéticos. Ele serve só para testar o fluxo, e o
`catalog.py` marca essas pastas como `sim`, que ficam fora da análise.

### Limitações conhecidas

- **Recompilação do firmware.** O resultado depende da versão do avr-gcc. Com o
  gcc 7.3 do Ubuntu e do toolchain Microchip, o Kyber-512 asm não linka. O
  motivo é que tabelas em `.data` mais o `.bss` passam dos 6 KB de SRAM. Com o
  avr-gcc 14.1 algumas combinações também falham. Os binários exatos usados nas
  medições estão em `data/experiments/*/bin/*.hex`. O tamanho de flash do
  caderno é lido desses arquivos, então a análise não depende de recompilar.
- **Ordem de execução.** O `schedule.json` registra uma ordem aleatória (pela
  semente), mas na bancada as combinações rodam em blocos por binário, porque
  cada binário exige uma gravação nova.
- **Commit do firmware.** As pastas de experimento não registram o commit do
  firmware. A origem das fontes PQC está nos `VENDOR.txt`.

## Fontes de terceiros

| Fonte | Uso | Commit |
| :--- | :--- | :--- |
| [CTRU-Light-and-PQC-on-AVR](https://github.com/whYBeKim/CTRU-Light-and-PQC-on-AVR) (MIT) | Kyber-512 e CTRU-Light, ref e asm | `fb07b9573fcdb0f4f662ad6594191fc09597907a` |
| [micro-ecc](https://github.com/kmackay/micro-ecc) (BSD-2) | ECDH secp256r1, ref e asm | `541b3a78026420a3e369c4c9281c396b5e531113` |
| Microchip ATmega DFP 3.3.279 (Apache-2.0) | Specs, startup e headers do ATmega4809 | `src/firmware/atmega4809/.dfp/Microchip.ATmega_DFP.pdsc` |
