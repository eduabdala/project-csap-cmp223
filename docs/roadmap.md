---
created: 2026-10-27
status: roadmap de execução
---

# Roadmap de Execução — CMP223

Documento acionável do que ainda precisa ser feito e **como fazer**. Deriva do
`docs/plan.md` (cronograma e SUT) e de `.kiro/specs/cmp223/draft.md` (diagramas
de arquitetura, firmware e metodologia).

Marcos: **Parcial 09/11/2026** · **Final + Artigo 14/12/2026**.

Legenda de status: ⬜ pendente · 🟨 em andamento · ✅ concluído

---

## Visão geral do experimento

| Dimensão | Definição |
|----------|-----------|
| SUT | Arduino Nano Every — ATmega4809 (8-bit AVRxt, 48 KB Flash / 6 KB SRAM / 256 B EEPROM) |
| Fatores (independentes) | Algoritmo {ECDH, CTRU-Light, Kyber-512} · Variante {ref (C), asm (AVR)} · Clock {20, 10, 5 MHz} · Otimização {-Os, -O3} |
| Métricas (dependentes) | Energia por operação `E_op = ∫ V·i dt` (µJ) · Latência/ciclos · Pico de stack (bytes) · Headroom CPU/SRAM (%) |
| Operações medidas | KeyGen · Encaps · Decaps (+ AES-CTR opcional na carga útil) |
| Instrumentação | Osciloscópio (shunt 1 Ω) · Analisador lógico (janela GPIO) · Stack watermarking (0xAA) |
| DoE | N = 30 iterações por combinação · ordem randomizada · IC 95% |
| Automação | Snakemake (build → flash → coleta → parser → estatística) |

---

## Fase 0 — Preparação e setup (meta: ~22/10)

### 0.1 Organização do repositório ✅
Concluído: `docs/`, `artigo/`, `src/`, `slides/` e README criados.

### 0.2 Compras e bancada ⬜
- [ ] Resistor de precisão **1 Ω 1%** (shunt) — *item pendente de compra no draft*.
- [ ] Confirmar disponibilidade: osciloscópio, analisador lógico, bateria Li-Ion 18650.
- **Como:** o shunt vai em série com a alimentação do MCU; a queda de tensão
  `v_shunt` dá a corrente (`i = v_shunt / 1 Ω`). Calibrar o valor real do resistor
  com multímetro de 4½ dígitos antes de usar como constante no parser.

### 0.3 Toolchain AVR 🟨
Ambiente Nix criado (`flake.nix`): `nix develop` entrega avr-gcc, binutils,
avrdude, sigrok-cli, picocom e o stack Python (snakemake + numpy/pandas/scipy/
matplotlib/pyserial). Falta validar na máquina real (gravação UPDI + bancada).

---

## Fase 1 — Port e firmware base (meta: parcial 09/11)

> **Progresso (scaffold criado):** o firmware base, o baseline ECDH, o build
> cross-AVR e o esqueleto do pipeline já existem em `src/`:
> - `src/firmware/` — harness de medição (`main.c`), interface `kem.h`,
>   adaptadores `kem_kyber512.c`, `kem_ctru.c` e `kem_ecdh.c`, `Makefile`
>   parametrizado por **ALG × VARIANT** (6 binários: 3 algoritmos × {ref, asm}).
> - `src/scripts/vendor-pqc.sh` — vendoriza CTRU-Light e Kyber (ref + asm AVR) do
>   artefato CHES 2026 `whYBeKim/CTRU-Light-and-PQC-on-AVR` (MIT) e micro-ecc (ECDH).
> - `src/analysis/` — `Snakefile`, `config.yaml` (variante como fator) e etapas
>   puras (`parse.py`, `aggregate.py`) já testadas offline.
>
> **Protocolo experimental:** cada combinação é buildada, gravada na placa e
> medida **separadamente** — 6 binários × clock × otimização × operação.
>
> **Falta:** rodar `vendor-pqc.sh` (precisa de rede), confirmar os caminhos reais
> das subpastas ref/asm no artefato, compilar com `avr-gcc` (`make size` =
> momento da verdade da SRAM/Flash) e conectar a bancada.
>
> **Achado relevante (do artefato CHES):** o Kyber-512 em C-ref ocupa ~79 KB de
> código — **não cabe nos 48 KB de Flash** do ATmega4809. A variante asm
> (Montgomery) cai para ~22 KB. Ou seja, para o Kyber a variante asm pode ser
> **necessária para caber**, não só mais rápida. Isso reforça tratar ref/asm
> como fator de primeira classe.

### 1.1 Definir o algoritmo base e baseline ⬜
- [ ] Escolher o primeiro algoritmo a portar (sugestão: **Kyber-512**, por ser o
  padrão NIST ML-KEM e ter referências em C portáveis).
- [ ] Definir o **baseline clássico**: ECDH (comparação de mesma finalidade — KEM/troca
  de chave) e, opcionalmente, AES-128 como referência de custo simétrico.
- **Decisão em aberto (do draft):** comparar PQC vs. criptografia clássica agrega
  valor, mas cuidado para não comparar algoritmos de propósitos distintos. Manter
  ECDH como par direto do KEM PQC.

### 1.2 Portar a rotina criptográfica para o ATmega4809 ⬜
- [ ] Trazer a implementação de referência em C (ex.: PQClean / pqm4 adaptado).
- [ ] Ajustar para as restrições do AVR: sem FPU, sem divisão por HW, 6 KB SRAM.
  Preferir aritmética de inteiros, evitar `malloc`, controlar uso de stack.
- [ ] Compilar com `avr-gcc` e inspecionar o tamanho com `avr-size`
  (Flash/`.text` + `.data`, SRAM `.data` + `.bss`).
- **Risco crítico:** 6 KB de SRAM é o maior limitante. Se o algoritmo não couber,
  registrar isso como resultado (um dos objetivos é justamente achar o limite de
  aplicabilidade).
- **Estrutura sugerida em `src/`:**
  ```
  src/firmware/    # harness de medição + port PQC
  src/baseline/    # ECDH / AES-128
  src/measure/     # captura osciloscópio / analisador lógico
  src/analysis/    # parser + estatística (Snakemake rules + Python)
  ```

### 1.3 Harness de medição no firmware ⬜
Implementar a máquina de estados do draft (ver diagramas `stateDiagram-v2`):
- [ ] Protocolo serial de disparo: `CMD_KEYGEN`, `CMD_ENCAPS`, `CMD_DECAPS`
  (e `CMD_START_DOWNLINK` / `CMD_START_UPLINK` para o fluxo completo).
- [ ] Janela de medição com GPIO de **1 ciclo** via `VPORTx.OUT` (HIGH antes da
  operação, LOW depois). Nada de I/O serial dentro da janela.
- [ ] Desativar interrupções (`cli()`) durante a janela para medição determinística.
- [ ] **Stack watermarking:** preencher a SRAM livre com `0xAA` antes da operação;
  depois varrer para achar o endereço mínimo tocado → `Stack Peak = RAMEND - end_mín`.
- [ ] Pulsos identificadores (1/2/3 pulsos) antes da janela para o parser saber
  qual operação está sendo medida.
- [ ] Reportar via UART, **fora da janela**: Stack Peak + artefatos (pk/ct).

### 1.4 Bancada de aquisição ⬜
- [ ] Osciloscópio: trigger pela borda de subida do GPIO; amostrar `v_shunt(t)`.
- [ ] Analisador lógico (`sigrok-cli`): medir largura do pulso GPIO → latência.
- [ ] Converter latência em ciclos: `K_cycles = T_exec × F_clock`.
- [ ] Definir taxa de amostragem do osciloscópio adequada à menor operação.

### 1.5 Coleta preliminar + slides da parcial ⬜
- [ ] Rodar coleta reduzida (tendências, não exaustiva) de KeyGen/Encaps/Decaps.
- [ ] Gráficos preliminares e levantamento de gargalos.
- [ ] Atualizar `slides/02-parcial.md` com resultados iniciais e ensaiar.

---

## Fase 2 — Execução final e artigo (meta: 14/12)

### 2.1 Automação com Snakemake ⬜
Pipeline reprodutível (ver flowchart "Automação & Execução Fatorial" no draft):
- [ ] `config.yaml` com a **matriz de fatores** (algoritmo × clock × otimização).
- [ ] Regra de **build parametrizado** (`avr-gcc` com flags por combinação + dump `avr-size`).
- [ ] Regra de **flash automático** (`avrdude` via UPDI).
- [ ] Regra de **coleta** (dispara ensaio, captura osciloscópio + LA + dump de stack).
- [ ] **DoE:** 30 iterações por combinação, **ordem randomizada**, com intervalo de
  cool-down entre ensaios (isolamento térmico).
- [ ] Gravar dados brutos com **hash do git + metadados** (rastreabilidade/reprodutibilidade).

### 2.2 Pós-processamento e estatística ⬜
- [ ] Parser dos CSVs do osciloscópio e do analisador lógico.
- [ ] **Integração numérica:** `E_op = ∫ V·i dt` (regra do trapézio sobre `v_shunt`).
- [ ] Cálculo de latência, ciclos e pico de pilha.
- [ ] **Headroom:** `SRAM_livre% = (6144 - Stack Peak)/6144`; `Flash_livre% = (49152 - .text)/49152`.
- [ ] Estatística: média, IC 95%, detecção e auditoria de outliers.
- [ ] Saídas: `summary_table.csv` + gráficos com barras de erro (PDF vetorial).

### 2.3 Artigo LaTeX ⬜
- [ ] Preencher `artigo/main.tex` (esqueleto já criado): Introdução, Fundamentação,
  Metodologia, Resultados, Conclusão.
- [ ] Referenciar diagramas de `diagrams/out/` (ver `diagrams/README.md`).
- [ ] **Organizar referências** (item pendente no draft) — criar `artigo/referencias.bib`
  e habilitar `\bibliography` no `main.tex`.
- [ ] Revisão e fechamento do texto.

### 2.4 Slides finais ⬜
- [ ] Atualizar `slides/03-final.md` com resultados consolidados; ensaiar.

---

## Itens transversais / decisões em aberto

Extraídos das dúvidas do `plan.md` que ainda precisam de resposta:

- [ ] **Variáveis configuráveis** — confirmar o conjunto final: otimização de
  compilação, tamanho dos dados cifrados, quantidade de dados recebidos/decifrados.
- [ ] **Cargas de trabalho** — definir explicitamente (o draft deixou em aberto:
  "As cargas de trabalho serão: ?").
- [ ] **Reprodutibilidade** — garantir que o Snakemake + hash git + `config.yaml`
  permitam reexecução completa por terceiros. Documentar o passo a passo no README.
- [ ] **Tabela de métricas por algoritmo** — montar a tabela comparativa final
  (energia, ciclos, stack, headroom por algoritmo × fator).

---

## Caminho crítico (ordem de ataque sugerida)

1. **Toolchain + bancada validados** (0.3) — nada avança sem isso.
2. **Port do algoritmo base caber na SRAM** (1.2) — maior risco técnico.
3. **Harness de medição confiável** (1.3/1.4) — define a qualidade de todos os dados.
4. **Automação Snakemake** (2.1) — transforma medição manual em coleta reprodutível.
5. **Estatística + artigo** (2.2/2.3) — depende de dados limpos.

O gargalo real é a **SRAM de 6 KB**. Validar cedo se o Kyber-512 cabe; se não,
esse é um resultado publicável (limite de aplicabilidade) e deve redirecionar a
escolha de algoritmos.
